from scapy.all import IP, TCP, UDP, ICMP

class Processor:
    def __init__(self, model):
        self.model = model

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