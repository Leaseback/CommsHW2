# Sender Class
import socket
import struct
import threading
import time

from utils import make_packet, WINDOW_SIZE, TIMEOUT, PACKET_SIZE


class Sender:
    def __init__(self, sender_socket, receiver_address):
        self.sock = sender_socket
        self.receiver_address = receiver_address
        self.base = 0
        self.next_seq_num = 0
        self.window = {}
        self.lock = threading.Lock()
        self.ack_event = threading.Event()

    def send_packet(self, seq_num, data):
        """Send a packet and store it in the window."""
        packet = make_packet(seq_num, data)
        self.sock.sendto(packet, self.receiver_address)
        self.window[seq_num] = (packet, time.time())
        print(f"Sent packet {seq_num}")

    def start(self, data_chunks):
        """Start sending packets."""
        threading.Thread(target=self.receive_acks, daemon=True).start()

        while self.base < len(data_chunks):
            with self.lock:
                while self.next_seq_num < self.base + WINDOW_SIZE and self.next_seq_num < len(data_chunks):
                    self.send_packet(self.next_seq_num, data_chunks[self.next_seq_num])
                    self.next_seq_num += 1

            self.ack_event.wait(TIMEOUT)
            self.handle_timeouts()

        # Send end-of-transmission packet
        self.send_end_of_transmission()

    def send_end_of_transmission(self):
        """Send an empty packet with a special sequence number to indicate end-of-transmission."""
        end_signal = struct.pack("!I", 99999999)  # Unique large sequence number as end signal
        self.sock.sendto(end_signal, self.receiver_address)
        print("Sent end-of-transmission signal")

    def receive_acks(self):
        """Listen for acknowledgments."""
        while True:
            ack_packet, _ = self.sock.recvfrom(1024)
            ack_seq_num = struct.unpack("!I", ack_packet[:4])[0]
            with self.lock:
                if ack_seq_num in self.window:
                    print(f"Received ACK for {ack_seq_num}")
                    del self.window[ack_seq_num]
                    if ack_seq_num == self.base:
                        while self.base not in self.window and self.base < self.next_seq_num:
                            self.base += 1
                    self.ack_event.set()

    def handle_timeouts(self):
        """Retransmit packets that have timed out."""
        current_time = time.time()
        for seq_num, (packet, timestamp) in list(self.window.items()):
            if current_time - timestamp > TIMEOUT:
                print(f"Timeout for packet {seq_num}, retransmitting...")
                self.sock.sendto(packet, self.receiver_address)
                self.window[seq_num] = (packet, time.time())


def main():
    # Initialize the sender socket and receiver address
    sender_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_address = ("localhost", 9998)  # Change to simulator address
    sender = Sender(sender_sock, receiver_address)

    # Example data chunks to send
    data_chunks = [b"Hello", b"World", b"This", b"is", b"RDT"]
    sender_sock.bind(("0.0.0.0", 9997))  # Bind to an ephemeral port
    sender.start(data_chunks)


if __name__ == "__main__":
    main()