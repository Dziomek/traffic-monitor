from scapy.all import IP, TCP, UDP, ICMP
import os
import csv
from datetime import datetime
import statistics
import joblib
import numpy as np
import pandas as pd

class Processor:
    def __init__(self, output_folder, csv_filename, model_path="model/rf_model.pkl", encoder_path="model/label_encoder.pkl"):
        self.model = joblib.load(model_path)
        self.encoder = joblib.load(encoder_path)
        self.output_folder = output_folder
        self.output_file = None

        if csv_filename:
            self.output_file = os.path.join(self.output_folder, csv_filename)

        self.fields = [
            "src_ip", "dst_ip", "src_port", "dst_port", "protocol", "flow_duration", "packet_rate",
            "byte_rate", "packet_count", "byte_count", "avg_packet_size", "min_packet_size", "max_packet_size", "std_packet_size",
            "time_between_packets_mean", "num_syn_flags", "num_rst_flags", "num_fin_flags", "num_urg_flags", "num_psh_flags", "num_ack_flags", 
            "initial_window_size", "incomplete_handshake", "tcp_flags_count", "packets_src_to_dst", "packets_dst_to_src", "bytes_src_to_dst", "bytes_dst_to_src", "label"
        ]

        self.columns_to_ignore = ["src_ip", "dst_ip", "label"]

        if self.output_file:
            if not os.path.exists(self.output_file):
                try:
                    with open(self.output_file, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(self.fields)
                except Exception as e:
                    print(f"Błąd przy tworzeniu pliku CSV: {e}")
    
    def predict_label(self, model_row):
        feature_df = pd.DataFrame([model_row])
        prediction = self.model.predict(feature_df)[0]
        label = self.encoder.inverse_transform([prediction])[0]
        return label

    def extract_features(self, flow):
        first_packet = flow["packets"][0]
        last_packet = flow["packets"][-1]

        # time
        flow_start_time = datetime.fromtimestamp(flow["first_packet_timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
        flow_end_time = datetime.fromtimestamp(flow["last_packet_timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
        flow_duration = flow["last_packet_timestamp"] - flow["first_packet_timestamp"]
        flow_duration = max(flow_duration, 1e-6) # prevents division by 0

        # size/count
        packet_count = len(flow["packets"])
        byte_count = sum(len(pkt) for pkt in flow["packets"])
        avg_packet_size = byte_count / packet_count if packet_count > 0 else 0

        # packet rate & byte rate
        packet_rate = packet_count / flow_duration
        byte_rate = byte_count / flow_duration

        # stats of size
        packet_sizes = [len(pkt) for pkt in flow["packets"]]
        min_packet_size = min(packet_sizes, default=0)
        max_packet_size = max(packet_sizes, default=0)
        std_packet_size = statistics.stdev(packet_sizes) if packet_count > 1 else 0

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
        num_urg_flags = sum(1 for pkt in flow["packets"] if pkt.haslayer(TCP) and "U" in pkt[TCP].flags)
        num_psh_flags = sum(1 for pkt in flow["packets"] if pkt.haslayer(TCP) and "P" in pkt[TCP].flags)
        num_ack_flags = sum(1 for pkt in flow["packets"] if pkt.haslayer(TCP) and "A" in pkt[TCP].flags)
        tcp_flags_count = num_syn_flags + num_rst_flags + num_fin_flags + num_urg_flags + num_psh_flags + num_ack_flags

        # Initial Window Size (from first TCP packet)
        initial_window_size = first_packet[TCP].window if first_packet.haslayer(TCP) else None

        # Incomplete Handshake (SYN without SYN-ACK-ACK)
        incomplete_handshake = 1 if (num_syn_flags > 0 and num_ack_flags == 0) else 0

        # both direction stats
        src_ip = first_packet[IP].src if first_packet.haslayer(IP) else None
        dst_ip = first_packet[IP].dst if first_packet.haslayer(IP) else None
        packets_src_to_dst = sum(1 for pkt in flow["packets"] if pkt[IP].src == src_ip) if src_ip else 0
        packets_dst_to_src = sum(1 for pkt in flow["packets"] if pkt[IP].src == dst_ip) if dst_ip else 0
        bytes_src_to_dst = sum(len(pkt) for pkt in flow["packets"] if pkt[IP].src == src_ip) if src_ip else 0
        bytes_dst_to_src = sum(len(pkt) for pkt in flow["packets"] if pkt[IP].src == dst_ip) if dst_ip else 0

        # to change manually for attacks
        label = "benign"

        # pełny wiersz do CSV
        csv_row = [
            src_ip, dst_ip, src_port, dst_port, protocol, flow_duration, packet_rate, byte_rate, 
            packet_count, byte_count, avg_packet_size, min_packet_size, max_packet_size, std_packet_size,
            time_between_packets_mean, num_syn_flags, num_rst_flags, num_fin_flags, num_urg_flags, num_psh_flags, num_ack_flags,
            initial_window_size, incomplete_handshake, tcp_flags_count, packets_src_to_dst, packets_dst_to_src, bytes_src_to_dst, bytes_dst_to_src, label
        ]

        model_row = {
            k: v for k, v in zip(self.fields, csv_row)
            if k not in self.columns_to_ignore
        }

        return {
            "csv_row": csv_row,
            "model_row": model_row
        }

    def process_flow(self, flow):
        if not flow["packets"]:
            return

        # Wyciągnięcie cech
        features = self.extract_features(flow)
        csv_row = features["csv_row"]
        model_row = features["model_row"]

        # Predykcja
        predicted_label = self.predict_label(model_row)
        # csv_row[-1] = predicted_label
        csv_row[-1] = "benign"

        # Zapis do pliku
        if self.output_file:
            with open(self.output_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(csv_row)
            print(f"Flow classified as '{predicted_label}' and saved to {self.output_file}")
        else:
            print(f"Flow classified as '{predicted_label}'")
        
            