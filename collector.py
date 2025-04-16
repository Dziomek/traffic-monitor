import queue
from collections import defaultdict, deque
from scapy.all import IP, TCP, UDP, ICMP
import time
import threading
#NFStream ????????

class Collector:
    def __init__(self, max_queue_size=-1, flow_timeout=15, flow_max_duration=15):
        self.flows = defaultdict(lambda: {"packets": [], "first_packet_timestamp": None, "last_packet_timestamp": None}) # for all flows
        self.packets = [] # for all packets
        self.flow_queue = queue.Queue(maxsize=max_queue_size) # flows to process
        self.flow_timeout = flow_timeout
        self.flow_max_duration = flow_max_duration

        self.cleanup_thread_running = True
        self.cleanup_function_interval = 0.5
        self.cleanup_thread = threading.Thread(target=self.cleanup_flows_loop, daemon=True)
        self.cleanup_thread.start()

    def add_packet(self, packet):
        self.packets.append(packet)

        flow_key = self.get_flow_key(packet)
        if flow_key:
            flow = self.flows[flow_key]
            current_time = time.time()

            if flow["first_packet_timestamp"] is None:
                flow["first_packet_timestamp"] = current_time

            flow["packets"].append(packet)
            flow["last_packet_timestamp"] = current_time

            if self.should_close_flow(flow_key) or self.is_termination_packet(packet, flow_key):
                self.close_flow_and_add_to_queue(flow_key)

    # def get_flow_key(self, packet):
    #     """
    #     Creates flow key for the packet to specify to which flow it belongs 
    #     (for now only 2-tuple approach, I will think about 5-tuple)
    #     """
    #     if packet.haslayer(IP):
    #         return (packet[IP].src, packet[IP].dst)
    #     return None

    def get_flow_key(self, packet):
        """
        Creates a 5-tuple flow key (src_ip, dst_ip, src_port, dst_port, protocol).
        """
        if packet.haslayer(IP):
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            protocol = packet[IP].proto

            src_port = None
            dst_port = None

            if packet.haslayer(TCP):
                src_port = packet[TCP].sport
                dst_port = packet[TCP].dport
            elif packet.haslayer(UDP):
                src_port = packet[UDP].sport
                dst_port = packet[UDP].dport

            return (src_ip, dst_ip, src_port, dst_port, protocol)

        return None  # Jeśli brak warstwy IP, zwracamy None
    
    def should_close_flow(self, flow_key):
        """Cheks if the flow should be closed"""
        current_time = time.time()
        flow = self.flows[flow_key]

        if flow["first_packet_timestamp"] and (current_time - flow["first_packet_timestamp"]) > self.flow_max_duration:
            return True
        
        return False
    
    def is_termination_packet(self, packet, flow_key):
        flow = self.flows[flow_key]
        if packet.haslayer(TCP) and ("F" in packet[TCP].flags or "R" in packet[TCP].flags):
            if len(flow["packets"]) > 1:
                return True
        return False
    
    def close_flow_and_add_to_queue(self, flow_key):
        if flow_key in self.flows:
            self.flow_queue.put(self.flows[flow_key])
            self.cleanup_flow(flow_key)

    def handle_expired_flows(self):
        """
        This function is executed in the cleanup interval
        It pass the expired flows to processing and executes cleanup
        """
        expired_flows = [flow_key for flow_key in list(self.flows.keys()) if self.should_close_flow(flow_key)]

        for flow_key in expired_flows:
            self.close_flow_and_add_to_queue(flow_key)
    
    def cleanup_flows_loop(self):
        """Function for cleanup, ran in the thread"""
        while self.cleanup_thread_running:
            self.handle_expired_flows()
            time.sleep(self.cleanup_function_interval)
    
    def cleanup_flow(self, flow_key):
        """Deletes flow"""
        del self.flows[flow_key]

