import socket
import threading
import time
import random
import struct

# Constants
PACKET_SIZE = 1024
WINDOW_SIZE = 4
TIMEOUT = 2  # seconds
LOSS_PROBABILITY = 0.1
CORRUPTION_PROBABILITY = 0.1
REORDER_PROBABILITY = 0.1


# Helper functions
# TODO IMPLEMENT

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



