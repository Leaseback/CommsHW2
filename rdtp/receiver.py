import socket
import struct
import utils


# Receiver Class
class Receiver:
    def __init__(self, receiver_socket, sender_address):
        self.sock = receiver_socket
        self.sender_address = sender_address
        self.expected_seq_num = 0
        self.buffer = {}

    def start(self):
        """Start receiving packets."""
        received_data = {}  # Store packets in order

        while True:
            packet, _ = self.sock.recvfrom(utils.PACKET_SIZE)


            seq_num, checksum, data = utils.parse_packet(packet)

            if seq_num is None:
                continue  # Ignore invalid packets

            # Handle end-of-transmission packet
            if seq_num == 99999999:
                print("\nAll packets received. Assembling message:")
                full_message = " ".join(received_data[i].decode() for i in sorted(received_data))
                print(full_message)
                break

            elif utils.is_corrupted(packet):
                print("Received corrupted packet, ignoring...")
                continue

            if seq_num == self.expected_seq_num:
                print(f"Received packet {seq_num}, delivering...")
                received_data[seq_num] = data
                self.sock.sendto(struct.pack("!I", seq_num), self.sender_address)
                self.expected_seq_num += 1

                while self.expected_seq_num in self.buffer:
                    print(f"Delivering buffered packet {self.expected_seq_num}")
                    received_data[self.expected_seq_num] = self.buffer[self.expected_seq_num]
                    del self.buffer[self.expected_seq_num]
                    self.expected_seq_num += 1
            elif seq_num > self.expected_seq_num:
                print(f"Out of order packet {seq_num}, buffering...")
                self.buffer[seq_num] = data
                self.sock.sendto(struct.pack("!I", seq_num), self.sender_address)
            else:
                self.sock.sendto(struct.pack("!I", seq_num), self.sender_address)


def main():
    # Initialize the receiver socket and sender address
    receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_sock.bind(("localhost", 9998))  # Listen on this port
    sender_address = ("localhost", 9997)  # Address of the sender or network simulator
    receiver = Receiver(receiver_sock, sender_address)

    receiver.start()


if __name__ == "__main__":
    main()