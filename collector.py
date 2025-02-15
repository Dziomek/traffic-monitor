import queue

class Collector:
    def __init__(self, max_size=1000):
        self.packet_queue = queue.Queue(maxsize=max_size)

    def add_packet(self, packet):
        if not self.packet_queue.full():
            self.packet_queue.put(packet)
            print(packet, 'added to the collector', self)
        else:
            print("Collector is full. Packet not added")

    def get_packet(self):
        """Gets packet from the queue (if accessible)"""
        if not self.packet_queue.empty():
            return self.packet_queue.get()
        return None

    def size(self):
        """Gets packet queue size"""
        return self.packet_queue.qsize()
