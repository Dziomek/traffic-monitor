import queue
from collections import defaultdict
from scapy.all import IP, TCP, UDP, ICMP
import time
import threading
#NFStream ????????

class Collector:
    def __init__(self, max_size=-1, flow_timeout=30, flow_max_duration=60):
        self.flows = defaultdict(list) # for all flows
        self.packets = [] # for all packets
        self.flow_queue = queue.Queue(maxsize=max_size) # flows to process
        self.flow_timeout = flow_timeout
        self.flow_max_duration = flow_max_duration
        self.flow_start_time = {}
        self.last_packet_time = {}

        self.cleanup_thread_running = True
        self.cleanup_function_interval = 0.5
        self.cleanup_thread = threading.Thread(target=self.cleanup_flows_loop, daemon=True)
        self.cleanup_thread.start()

    def add_packet(self, packet):
        self.packets.append(packet)

        flow_key = self.get_flow_key(packet)
        if flow_key:
            if flow_key not in self.flows:
                self.flow_start_time[flow_key] = time.time()
            self.flows[flow_key].append(packet)
            self.last_packet_time[flow_key] = time.time()

            if self.should_close_flow(flow_key) or self.is_termination_packet(packet):
                self.close_flow_and_pass_to_process(flow_key)

    def get_flow_key(self, packet):
        """
        Creates flow key for the packet to specify to which flow it belongs 
        (for now only 2-tuple approach, I will think about 5-tuple)
        """
        if packet.haslayer(IP):
            return (packet[IP].src, packet[IP].dst)
        return None
    
    def should_close_flow(self, flow_key):
        """Cheks if the flow should be closed"""
        current_time = time.time()
        flow_age = current_time - self.flow_start_time[flow_key]

        if flow_age > self.flow_max_duration:
            return True
        
        return False
    
    def is_termination_packet(self, packet):
        if packet.haslayer(TCP) and ("F" in packet[TCP].flags or "R" in packet[TCP].flags):
            return True
        return False
    
    def close_flow_and_pass_to_process(self, flow_key):
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
            self.close_flow_and_pass_to_process(flow_key)
    
    def cleanup_flows_loop(self):
        """Function for cleanup, ran in the thread"""
        while self.running:
            self.handle_expired_flows()
            time.sleep(self.cleanup_function_interval)
    
    def cleanup_flow(self, flow_key):
        """Deletes flow"""
        del self.flows[flow_key]
        del self.flow_start_time[flow_key]
        del self.last_packet_time[flow_key]

