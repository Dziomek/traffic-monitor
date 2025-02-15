from scapy.all import sniff
import threading

class Sniffer:
    def __init__(self, iface, count=0, filter_expr=""):
        """
        Creates Sniffer instance for the given interface.

        :param iface: network interface
        :param count: number of packets to catch (0 = infinity)
        :param filter_expr: BPF (Berkeley Packet Filter) (f.ex. 'tcp', 'udp')
        """
        self.iface = iface
        self.count = count
        self.filter_expr = filter_expr
        self.running = False
        self.thread = None

    def packet_callback(self, packet):
        """Handles sniffed packets"""
        print(f"[{self.iface}] {packet.summary()}")

    def start(self):
        """Starts sniffer in separate thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._sniff, daemon=True)
            self.thread.start()
            print(f"Sniffer ran at interface: {self.iface}")

    def _sniff(self):
        """Catches packets"""
        sniff(iface=self.iface, prn=self.packet_callback, count=self.count, filter=self.filter_expr)
        self.running = False

    def stop(self):
        """Stops the sniffer"""
        self.running = False
        print(f"Sniffer on {self.iface} stopped")
