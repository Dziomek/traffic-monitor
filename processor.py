from scapy.all import IP, TCP, UDP, ICMP
import os
import csv
from datetime import datetime

class Processor:
    def __init__(self, model, output_folder="records", output_file="benign_flow_01_03.csv"):
        self.model = model
        self.output_folder = output_folder
        self.output_file = os.path.join(output_folder, output_file)

        os.makedirs(self.output_folder, exist_ok=True)

        self.fields = [
            "src_ip", "dst_ip", "src_port", "dst_port", "protocol", "flow_duration", "packet_count", "byte_count", "avg_packet_size",
            "time_between_packets_mean", "num_syn_flags", "num_rst_flags", "num_fin_flags", "tcp_flags_count",
            "packets_src_to_dst", "packets_dst_to_src", "bytes_src_to_dst", "bytes_dst_to_src", "label"
        ]

        if not os.path.exists(self.output_file):
            with open(self.output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.fields)
    
    def extract_features(self, flow):
        first_packet = flow["packets"][0]
        last_packet = flow["packets"][-1]

        # time
        flow_start_time = datetime.fromtimestamp(flow["first_packet_timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
        flow_end_time = datetime.fromtimestamp(flow["last_packet_timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
        flow_duration = flow["last_packet_timestamp"] - flow["first_packet_timestamp"]

        # size/count
        packet_count = len(flow["packets"])
        byte_count = sum(len(pkt) for pkt in flow["packets"])
        avg_packet_size = byte_count / packet_count if packet_count > 0 else 0

        # time differences
        if packet_count > 1:
            time_diffs = [flow["packets"][i+1].time - flow["packets"][i].time for i in range(len(flow["packets"])-1)]
            time_between_packets_mean = sum(time_diffs) / len(time_diffs)
        else:
            time_between_packets_mean = 0

        # ip adresses
        src_ip = first_packet[IP].src if first_packet.haslayer(IP) else None
        dst_ip = first_packet[IP].dst if first_packet.haslayer(IP) else None

        # ports/protocols
        protocol = first_packet[IP].proto if first_packet.haslayer(IP) else None
        src_port = first_packet[TCP].sport if first_packet.haslayer(TCP) else (first_packet[UDP].sport if first_packet.haslayer(UDP) else None)
        dst_port = first_packet[TCP].dport if first_packet.haslayer(TCP) else (first_packet[UDP].dport if first_packet.haslayer(UDP) else None)

        # TCP flags
        num_syn_flags = sum(1 for pkt in flow["packets"] if pkt.haslayer(TCP) and "S" in pkt[TCP].flags)
        num_rst_flags = sum(1 for pkt in flow["packets"] if pkt.haslayer(TCP) and "R" in pkt[TCP].flags)
        num_fin_flags = sum(1 for pkt in flow["packets"] if pkt.haslayer(TCP) and "F" in pkt[TCP].flags)
        tcp_flags_count = num_syn_flags + num_rst_flags + num_fin_flags

        # both direction stats
        src_ip = first_packet[IP].src if first_packet.haslayer(IP) else None
        dst_ip = first_packet[IP].dst if first_packet.haslayer(IP) else None
        packets_src_to_dst = sum(1 for pkt in flow["packets"] if pkt[IP].src == src_ip) if src_ip else 0
        packets_dst_to_src = sum(1 for pkt in flow["packets"] if pkt[IP].src == dst_ip) if dst_ip else 0
        bytes_src_to_dst = sum(len(pkt) for pkt in flow["packets"] if pkt[IP].src == src_ip) if src_ip else 0
        bytes_dst_to_src = sum(len(pkt) for pkt in flow["packets"] if pkt[IP].src == dst_ip) if dst_ip else 0

        # to change manually for attacks
        label = "benign"

        row = [
            src_ip, dst_ip, src_port, dst_port, protocol, flow_duration, packet_count, byte_count, avg_packet_size,
            time_between_packets_mean, num_syn_flags, num_rst_flags, num_fin_flags, tcp_flags_count,
            packets_src_to_dst, packets_dst_to_src, bytes_src_to_dst, bytes_dst_to_src, label
        ]

        return row

    def process_flow(self, flow):
        if not flow["packets"]:
            return
        
        row = self.extract_features(flow)

        with open(self.output_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        print(f"Flow saved to CSV")
        
        
            