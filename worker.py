import threading
from sniffer import Sniffer
from collector import Collector
from processor import Processor
import queue

class Worker:
    def __init__(self, iface, filter_expr, csv_filename, output_folder, flow_timeout, flow_max_duration, mode, max_queue_size=1000):
        self.iface = iface
        self.collector = Collector(max_queue_size=max_queue_size, flow_timeout=flow_timeout, flow_max_duration=flow_max_duration)
        self.processor = Processor(output_folder=output_folder, csv_filename=csv_filename, mode=mode)
        self.sniffer = Sniffer(iface=self.iface, filter_expr=filter_expr, collector_function=self.collector.add_packet)
        self.running = False
        self.thread = threading.Thread(target=self.process_flows, daemon=True)

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

    def process_flows(self):
        while self.running: 
            try:
                flow = self.collector.flow_queue.get(timeout=1)  # max 1 s delay
                # print(flow)
                if flow:
                    self.processor.process_flow(flow)
            except queue.Empty:
                pass
