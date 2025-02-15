from scapy.all import sniff
import threading

class Sniffer:
    def __init__(self, iface, collector_function, processor_function, count=0, filter_expr=""):
        self.iface = iface
        self.collector_function = collector_function
        self.processor_function = processor_function
        self.count = count
        self.filter_expr = filter_expr
        self.running = False
        self.thread = None

    def packet_callback(self, packet):
        self.collector_function(packet)
        # self.processor_function(packet)
        # print(f"[{self.iface}] {packet.summary()}")

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._sniff, daemon=True)
            self.thread.start()
            print(f"Sniffer ran at interface: {self.iface}")

    def _sniff(self):
        sniff(iface=self.iface, prn=self.packet_callback, count=self.count, filter=self.filter_expr)
        self.running = False

    def stop(self):
        self.running = False
        print(f"Sniffer on {self.iface} stopped")
