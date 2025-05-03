import threading
from workers.sniffer import Sniffer
from workers.collector import Collector
from workers.processor import Processor
import queue
from PyQt5.QtCore import QObject, pyqtSignal

class Worker(QObject):
    status_change = pyqtSignal(bool)

    def __init__(self, iface, config, max_queue_size=1000):

        super().__init__()

        self.iface = iface
        self.collector = Collector(max_queue_size=max_queue_size, flow_timeout=config["flow_timeout"], 
                                   flow_max_duration=config["flow_max_duration"])
        self.processor = Processor(output_folder=config["OUTPUT_FOLDER"], csv_filename=config["CSV_FILENAME"], 
                                   mode=config["mode"], attack=config["attack"], attacker_ip=config["attacker_ip"], 
                                   all_features=config["ALL_FEATURES"], model_features=config["MODEL_FEATURES"],
                                   model_path=config["MODEL_PATH"], encoder_path=config["ENCODER_PATH"])
        self.sniffer = Sniffer(iface=self.iface, filter_expr=config["filter_expr"], collector_function=self.collector.add_packet)
        self.running = False
        self.thread = threading.Thread(target=self.process_flows, daemon=True)

    def start(self):
        if not self.running:
            self.sniffer.start()
            self.thread.start()
            self.running = True
            self.status_change.emit(True)
            print(f'Worker for {self.iface} starts')

    def stop(self):
        self.sniffer.stop()
        self.running = False
        self.status_change.emit(False)
        print(f"Worker for {self.iface} stopped")

    def process_flows(self):
        while self.running: 
            try:
                flow = self.collector.flow_queue.get(timeout=1)  # max 1 s delay
                print(flow)
                if flow:
                    self.processor.process_flow(flow)
            except queue.Empty:
                pass
