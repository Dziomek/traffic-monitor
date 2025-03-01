from scapy.all import IP, TCP, UDP, ICMP
import os
import csv

class Processor:
    def __init__(self, model, output_folder="records", output_file="network_data.csv"):
        self.model = model
        self.output_folder = output_folder
        self.output_file = os.path.join(output_folder, output_file)

        os.makedirs(self.output_folder, exist_ok=True)

        self.fields = [
            "flow_duration", "packet_count", "byte_count", "avg_packet_size",
            "time_between_packets_mean", "protocol", "src_port", "dst_port",
            "num_syn_flags", "num_rst_flags", "num_fin_flags", "tcp_flags_count",
            "packets_src_to_dst", "packets_dst_to_src", "bytes_src_to_dst", "bytes_dst_to_src",
            "label"
        ]

        if not os.path.exists(self.output_file):
            with open(self.output_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.fields)

    def extract_features(self, packet):
        features = {}

        if packet.haslayer(IP):
            features["src_ip"] = packet[IP].src
            features["dst_ip"] = packet[IP].dst
            features["protocol"] = packet[IP].proto
            features["ttl"] = packet[IP].ttl
            features["length"] = packet[IP].len

        if packet.haslayer(TCP):
            features["src_port"] = packet[TCP].sport
            features["dst_port"] = packet[TCP].dport
            features["flags"] = str(packet[TCP].flags)
            features["window_size"] = packet[TCP].window

        if packet.haslayer(UDP):
            features["src_port"] = packet[UDP].sport
            features["dst_port"] = packet[UDP].dport
            features["length"] = packet[UDP].len

        if packet.haslayer(ICMP):
            features["icmp_type"] = packet[ICMP].type
            features["icmp_code"] = packet[ICMP].code

        features["payload_size"] = len(packet.payload)


        
        return features

    def process_packet(self, packet):

        features = self.extract_features(packet)
        print(f'I managed to get following data from {packet}: {features}')

    def process_flow(self, flow):
        length = len(flow['packets'])
        print('****************************FLOW******************************', length, flow['last_packet_timestamp'] - flow['first_packet_timestamp'])
        
        
            