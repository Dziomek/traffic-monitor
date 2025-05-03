from scapy.all import IP, TCP, UDP, ICMP
import os
import csv
from datetime import datetime
import statistics
import joblib
import numpy as np
import pandas as pd

from PyQt5.QtCore import QObject, pyqtSignal

class Processor(QObject):
    flow_result = pyqtSignal(dict)

    def __init__(self, output_folder, csv_filename, mode, attack, attacker_ip, all_features, model_features, 
                 model_path="model/rf_model.pkl", encoder_path="model/label_encoder.pkl"):
        
        super().__init__()

        self.mode = mode
        self.attack = attack
        self.attacker_ip = attacker_ip
        self.model = joblib.load(model_path)
        self.encoder = joblib.load(encoder_path)
        self.output_folder = output_folder
        self.output_file = None
        self.all_features = all_features
        self.model_features = model_features

        if csv_filename:
            self.output_file = os.path.join(self.output_folder, csv_filename)

        if self.output_file:
            if not os.path.exists(self.output_file):
                try:
                    with open(self.output_file, "w", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow(self.all_features)
                except Exception as e:
                    print(f"Błąd przy tworzeniu pliku CSV: {e}")
    
    def predict_label(self, model_row):
        feature_df = pd.DataFrame([model_row], columns=self.model_features)
        prediction = self.model.predict(feature_df)[0]
        label = self.encoder.inverse_transform([prediction])[0]
        return label

    def extract_features(self, flow):
        first_packet = flow["packets"][0]

        src_ip = first_packet[IP].src if first_packet.haslayer(IP) else None
        dst_ip = first_packet[IP].dst if first_packet.haslayer(IP) else None
        src_port = first_packet[TCP].sport if first_packet.haslayer(TCP) else (first_packet[UDP].sport if first_packet.haslayer(UDP) else None)
        dst_port = first_packet[TCP].dport if first_packet.haslayer(TCP) else (first_packet[UDP].dport if first_packet.haslayer(UDP) else None)
        protocol = first_packet[IP].proto if first_packet.haslayer(IP) else None
        flow_duration = flow["last_packet_timestamp"] - flow["first_packet_timestamp"]
        flow_duration = max(flow_duration, 1e-6) # prevents division by 0 later
        packet_count = len(flow["packets"])
        byte_count = sum(len(pkt) for pkt in flow["packets"])
        packet_rate = packet_count / flow_duration
        byte_rate = byte_count / flow_duration
        avg_packet_size = byte_count / packet_count if packet_count > 0 else 0
        packet_sizes = [len(pkt) for pkt in flow["packets"]]
        min_packet_size = min(packet_sizes, default=0)
        max_packet_size = max(packet_sizes, default=0)
        std_packet_size = statistics.stdev(packet_sizes) if packet_count > 1 else 0
        if packet_count > 1:
            time_diffs = [flow["packets"][i+1].time - flow["packets"][i].time for i in range(len(flow["packets"])-1)]
            iat_mean = sum(time_diffs) / len(time_diffs)
            iat_std = statistics.stdev(time_diffs) if len(time_diffs) > 1 else 0
            iat_min = min(time_diffs)
            iat_max = max(time_diffs)
        else:
            iat_mean = 0
            iat_std = 0
            iat_min = 0
            iat_max = 0
        num_syn_flags = sum(1 for pkt in flow["packets"] if pkt.haslayer(TCP) and "S" in pkt[TCP].flags)
        num_rst_flags = sum(1 for pkt in flow["packets"] if pkt.haslayer(TCP) and "R" in pkt[TCP].flags)
        num_fin_flags = sum(1 for pkt in flow["packets"] if pkt.haslayer(TCP) and "F" in pkt[TCP].flags)
        num_urg_flags = sum(1 for pkt in flow["packets"] if pkt.haslayer(TCP) and "U" in pkt[TCP].flags)
        num_psh_flags = sum(1 for pkt in flow["packets"] if pkt.haslayer(TCP) and "P" in pkt[TCP].flags)
        num_ack_flags = sum(1 for pkt in flow["packets"] if pkt.haslayer(TCP) and "A" in pkt[TCP].flags)
        tcp_flags_count = num_syn_flags + num_rst_flags + num_fin_flags + num_urg_flags + num_psh_flags + num_ack_flags
        initial_window_size = first_packet[TCP].window if first_packet.haslayer(TCP) else None
        incomplete_handshake = 1 if (num_syn_flags > 0 and num_ack_flags == 0) else 0
        label = "benign"

        all_features_dict = {
            "src_ip": src_ip,
            "dst_ip": dst_ip,
            "src_port": src_port,
            "dst_port": dst_port,
            "protocol": protocol,
            "flow_duration": flow_duration,
            "packet_count": packet_count,
            "byte_count": byte_count,
            "packet_rate": packet_rate,
            "byte_rate": byte_rate,
            "avg_packet_size": avg_packet_size,
            "min_packet_size": min_packet_size,
            "max_packet_size": max_packet_size,
            "std_packet_size": std_packet_size,
            "iat_mean": iat_mean,
            "iat_std": iat_std,
            "iat_min": iat_min,
            "iat_max": iat_max,
            "num_syn_flags": num_syn_flags,
            "num_rst_flags": num_rst_flags,
            "num_fin_flags": num_fin_flags,
            "num_urg_flags": num_urg_flags,
            "num_psh_flags": num_psh_flags,
            "num_ack_flags": num_ack_flags,
            "tcp_flags_count": tcp_flags_count,
            "initial_window_size": initial_window_size,
            "incomplete_handshake": incomplete_handshake,
            "label": label
        }

        return {
            "csv_row": [all_features_dict[f] for f in self.all_features],
            "model_row": [all_features_dict[f] for f in self.model_features]
        }

    def process_flow(self, flow):
        if not flow["packets"]:
            return

        # Wyciągnięcie cech
        features = self.extract_features(flow)
        csv_row = features["csv_row"]
        model_row = features["model_row"]

        # Predykcja
        if(self.mode == "detect"):
            predicted_label = self.predict_label(model_row)
        else:
            src_ip = csv_row[0]  # TODO (be careful about that, here I suppose that src_ip is first column)
            if self.attacker_ip and src_ip == self.attacker_ip:
                predicted_label = self.attack.upper()
            else:
                predicted_label = "benign"

        csv_row[-1] = predicted_label

        # Zapis do pliku
        if self.output_file:
            with open(self.output_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(csv_row)

            print(f"*MODE: {self.mode}* Flow classified as '{predicted_label}' and saved to {self.output_file}")
        else:
            print(f"*MODE: {self.mode}* Flow classified as '{predicted_label}'")

        self.flow_result.emit({
            "predicted_label": predicted_label,
            "src_ip": csv_row[0],
            "dst_ip": csv_row[1],
            "src_port": csv_row[2],
            "dst_port": csv_row[3]
        })
        
            