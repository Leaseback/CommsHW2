import random
import socket
import time

from utils import PACKET_SIZE, LOSS_PROBABILITY, CORRUPTION_PROBABILITY, REORDER_PROBABILITY


# Network Simulator
class NetworkSimulator:
    def __init__(self, listen_address, forward_address):
        self.listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.listen_socket.bind(listen_address)
        self.forward_address = forward_address

    def start(self):
        """Start forwarding packets with simulated impairments."""
        while True:
            packet, addr = self.listen_socket.recvfrom(PACKET_SIZE + 5)
            if random.random() < LOSS_PROBABILITY:
                print("Packet lost!")
                continue
            if random.random() < CORRUPTION_PROBABILITY:
                packet = bytearray(packet)
                packet[0] ^= 0xFF  # Corrupt data
                packet = bytes(packet)
                print("Packet corrupted!")
            if random.random() < REORDER_PROBABILITY:
                time.sleep(0.5)
                print("Packet reordered!")

            # Forwarding logic
            # If packet is from sender, forward to receiver
            self.listen_socket.sendto(packet, self.forward_address)
            print(f"Forwarded packet to receiver at {self.forward_address}")

            # If packet is from receiver, forward to sender
            self.listen_socket.sendto(packet, addr)
            print(f"Forwarded packet back to sender at {addr}")


def main():
    listen_address = ("localhost", 9999)  # The port the simulator listens on (receiving from sender and receiver)
    forward_address = ("localhost", 9998)  # The address to forward packets to (receiver's address)

    simulator = NetworkSimulator(listen_address, forward_address)

    # Start the network simulator to handle packet forwarding and impairments
    simulator.start()


if __name__ == "__main__":
    main()
