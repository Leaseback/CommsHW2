import struct



# Receiver Class
class Receiver:
    def __init__(self, receiver_socket, sender_address):
        self.sock = receiver_socket
        self.sender_address = sender_address
        self.expected_seq_num = 0
        self.buffer = {}

    def start(self):
        """Start receiving packets."""
        while True:
            packet, _ = self.sock.recvfrom(PACKET_SIZE)
            if is_corrupted(packet):
                print("Received corrupted packet, ignoring...")
                continue

            seq_num, _, data = parse_packet(packet)
            if seq_num == self.expected_seq_num:
                print(f"Received packet {seq_num}, delivering...")
                self.sock.sendto(struct.pack("!I", seq_num), self.sender_address)
                self.expected_seq_num += 1

                while self.expected_seq_num in self.buffer:
                    print(f"Delivering buffered packet {self.expected_seq_num}")
                    del self.buffer[self.expected_seq_num]
                    self.expected_seq_num += 1
            elif seq_num > self.expected_seq_num:
                print(f"Out of order packet {seq_num}, buffering...")
                self.buffer[seq_num] = data
                self.sock.sendto(struct.pack("!I", seq_num), self.sender_address)
            else:
                self.sock.sendto(struct.pack("!I", seq_num), self.sender_address)