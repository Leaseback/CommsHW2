# Sender Class
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

    def receive_acks(self):
        """Listen for acknowledgments."""
        while True:
            ack_packet, _ = self.sock.recvfrom(PACKET_SIZE)
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