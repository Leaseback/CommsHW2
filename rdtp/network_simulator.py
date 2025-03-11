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
            packet, addr = self.listen_socket.recvfrom(PACKET_SIZE)
            if random.random() < LOSS_PROBABILITY:
                print("Packet lost!")
                continue
            if random.random() < CORRUPTION_PROBABILITY:
                packet = bytearray(packet)
                packet[5] ^= 0xFF  # Corrupt data
                packet = bytes(packet)
                print("Packet corrupted!")
            if random.random() < REORDER_PROBABILITY:
                time.sleep(0.5)
                print("Packet reordered!")
            self.listen_socket.sendto(packet, self.forward_address)


def main():
    listen_address = ("localhost", 9999)  # The port the simulator listens on
    forward_address = ("localhost", 9998)  # Forwarding address to the receiver

    simulator = NetworkSimulator(listen_address, forward_address)
    simulator.start()


if __name__ == "__main__":
    main()