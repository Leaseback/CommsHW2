# Sender Class
import socket
import struct
import sys
import threading
import time

from utils import make_packet, WINDOW_SIZE, TIMEOUT, PACKET_SIZE

import socket
import struct
import threading
import time
import os

from utils import make_packet, WINDOW_SIZE, TIMEOUT, PACKET_SIZE


class Sender:
    def __init__(self, sender_socket, simulator_address, file_path):
        self.sock = sender_socket
        self.simulator_address = simulator_address
        self.base = 0
        self.next_seq_num = 0
        self.window = {}
        self.lock = threading.Lock()
        self.ack_event = threading.Event()
        self.file_path = file_path

    def send_packet(self, seq_num, data):
        """Send a packet and store it in the window."""
        packet = make_packet(seq_num, data)
        self.sock.sendto(packet, self.simulator_address)  # Send to the network simulator
        self.window[seq_num] = (packet, time.time())
        print(f"Sender: Sent packet {seq_num} to Network Simulator")
        time.sleep(0.5)  # Delay of 0.5 seconds before sending the next packet

    def start(self):
        """Start sending packets from the file."""
        with open(self.file_path, "rb") as file:
            file_data = file.read()

        data_chunks = [file_data[i:i + PACKET_SIZE] for i in range(0, len(file_data), PACKET_SIZE)]

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
        self.sock.sendto(end_signal, self.simulator_address)  # Send to Network Simulator
        print("Sender: Sent end-of-transmission signal to Network Simulator")

    def receive_acks(self):
        """Listen for acknowledgments."""
        while True:
            ack_packet, _ = self.sock.recvfrom(PACKET_SIZE + 5)
            ack_seq_num = struct.unpack("!I", ack_packet[:4])[0]
            with self.lock:
                if ack_seq_num in self.window:
                    print(f"Sender: Received ACK for {ack_seq_num}")
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
                print(f"Sender: Timeout for packet {seq_num}, retransmitting...")
                self.sock.sendto(packet, self.simulator_address)  # Retransmit to Network Simulator
                self.window[seq_num] = (packet, time.time())


def main():
    # Get file path from command-line argument
    if len(sys.argv) != 2:
        print("Sender: Usage: python sender.py <file_path>")
        return

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"Sender: File {file_path} does not exist.")
        return

    # Initialize the sender socket and network simulator address
    sender_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    simulator_address = ("localhost", 9999)  # The address of the network simulator (sending to the simulator)

    sender = Sender(sender_sock, simulator_address, file_path)

    # Bind the sender to a port for receiving ACKs (or a random ephemeral port)
    sender_sock.bind(("0.0.0.0", 9997))  # Bind to an ephemeral port (change this if needed)

    # Start the sender to send packets
    sender.start()


if __name__ == "__main__":
    main()