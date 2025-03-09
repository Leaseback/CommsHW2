# Helper functions
import struct

# Constants
PACKET_SIZE = 1024
WINDOW_SIZE = 4
TIMEOUT = 2  # seconds
LOSS_PROBABILITY = 0.1
CORRUPTION_PROBABILITY = 0.1
REORDER_PROBABILITY = 0.1

def compute_checksum(data):
    """Compute a simple checksum."""
    return sum(data) % 256


def make_packet(seq_num, data):
    """Create a packet with a sequence number, checksum, and data."""
    checksum = compute_checksum(data)
    return struct.pack("!I B", seq_num, checksum) + data


def parse_packet(packet):
    """Parse a received packet."""
    seq_num, checksum = struct.unpack("!I B", packet[:5])
    data = packet[5:]
    return seq_num, checksum, data


def is_corrupted(packet):
    """Check if a packet is corrupted."""
    seq_num, checksum, data = parse_packet(packet)
    return compute_checksum(data) != checksum