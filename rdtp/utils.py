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
    if data is None:
        return -1
    else:
        return sum(data) % 256


def make_packet(seq_num, data):
    """Create a packet with a sequence number, checksum, and data."""
    checksum = compute_checksum(data)
    return struct.pack("!I B", seq_num, checksum) + data


def parse_packet(packet):
    """Parse a received packet and handle short packets properly."""
    if len(packet) < 4:
        print("Received an invalid or truncated packet, ignoring...")
        return None, None, None  # Return None values to indicate an issue

    seq_num = struct.unpack("!I", packet[:4])[0]

    if len(packet) == 4:  # Special case: End-of-transmission packet
        return seq_num, None, None

    if len(packet) < 5:
        print(f"Received incomplete packet with seq_num {seq_num}, ignoring...")
        return None, None, None

    checksum = struct.unpack("!B", packet[4:5])[0]
    data = packet[5:]
    return seq_num, checksum, data


def is_corrupted(packet):
    """Check if a packet is corrupted."""
    seq_num, checksum, data = parse_packet(packet)
    return compute_checksum(data) != checksum
