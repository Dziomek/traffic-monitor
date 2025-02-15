import threading
from sniffer import Sniffer
from collector import Collector
import time

class Worker:
    def __init__(self, iface, filter_expr="tcp", max_queue_size=1000):
        self.iface = iface
        self.collector = Collector(max_size=max_queue_size)
        self.sniffer = Sniffer(iface=self.iface, filter_expr=filter_expr, collector_function=self.collector.add_packet)
        self.running = False
        self.thread = threading.Thread(target=self.process_packets, daemon=True)

    def start(self):
        if not self.running:
            self.running = True
            self.sniffer.start()
            self.thread.start()
            print(f'Worker for {self.iface} starts')

    def stop(self):
        self.running = False
        self.sniffer.stop()
        print(f"Worker for {self.iface} stopped")

    def process_packets(self):
        while self.running:
            print(f'Message from worker on interface {self.iface}: size of the collector is {self.collector.size()}')
            time.sleep(5)
