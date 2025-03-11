import socket
import struct
import utils


# Receiver Class
class Receiver:
    def __init__(self, receiver_socket, simulator_address):
        self.sock = receiver_socket
        self.simulator_address = simulator_address
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
                self.sock.sendto(struct.pack("!I", seq_num), self.simulator_address)  # Send ACK to Network Simulator
                self.expected_seq_num += 1

                while self.expected_seq_num in self.buffer:
                    print(f"Delivering buffered packet {self.expected_seq_num}")
                    received_data[self.expected_seq_num] = self.buffer[self.expected_seq_num]
                    del self.buffer[self.expected_seq_num]
                    self.expected_seq_num += 1
            elif seq_num > self.expected_seq_num:
                print(f"Out of order packet {seq_num}, buffering...")
                self.buffer[seq_num] = data
                self.sock.sendto(struct.pack("!I", seq_num), self.simulator_address)  # Send ACK to Network Simulator
            else:
                self.sock.sendto(struct.pack("!I", seq_num), self.simulator_address)  # Send ACK to


def main():
    # Initialize the receiver socket and network simulator address
    receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_sock.bind(("localhost", 9998))  # Listen on this port

    # The network simulator forwards to the sender, so we send to the simulator's address
    simulator_address = ("localhost", 9999)  # The address of the network simulator (sending to the simulator)

    receiver = Receiver(receiver_sock, simulator_address)

    # Start the receiver to begin receiving packets
    receiver.start()


if __name__ == "__main__":
    main()