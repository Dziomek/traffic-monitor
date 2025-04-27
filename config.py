import argparse
import os
import netifaces
from enum import Enum

class AllFeatures(str, Enum):
    SRC_IP = "src_ip"
    DST_IP = "dst_ip"
    SRC_PORT = "src_port"
    DST_PORT = "dst_port"
    PROTOCOL = "protocol"
    FLOW_DURATION = "flow_duration"
    PACKET_COUNT = "packet_count"
    BYTE_COUNT = "byte_count"
    PACKET_RATE = "packet_rate"
    BYTE_RATE = "byte_rate"
    AVG_PACKET_SIZE = "avg_packet_size"
    MIN_PACKET_SIZE = "min_packet_size"
    MAX_PACKET_SIZE = "max_packet_size"
    STD_PACKET_SIZE = "std_packet_size"
    IAT_MEAN = "iat_mean"
    IAT_STD = "iat_std"
    IAT_MIN = "iat_min"
    IAT_MAX = "iat_max"
    NUM_SYN_FLAGS = "num_syn_flags"
    NUM_RST_FLAGS = "num_rst_flags"
    NUM_FIN_FLAGS = "num_fin_flags"
    NUM_URG_FLAGS = "num_urg_flags"
    NUM_PSH_FLAGS = "num_psh_flags"
    NUM_ACK_FLAGS = "num_ack_flags"
    TCP_FLAGS_COUNT = "tcp_flags_count"
    INITIAL_WINDOW_SIZE = "initial_window_size"
    INCOMPLETE_HANDSHAKE = "incomplete_handshake"
    LABEL = "label"

class ExcludedFeatures(str, Enum):
    SRC_IP = "src_ip"
    DST_IP = "dst_ip"
    SRC_PORT = "src_port"
    DST_PORT = "dst_port"
    LABEL = "label"

def get_active_interfaces(exclude=("lo", "docker0", "vboxnet0")):
    active = []
    for iface in netifaces.interfaces():
        if iface in exclude:
            continue
        try:
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                active.append(iface)
        except Exception as e:
            print(f"[!] Błąd sprawdzania interfejsu {iface}: {e}")
    return active

def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["collect", "detect"], default="detect", help="Tryb działania programu")
    parser.add_argument("--attack", type=str, default="benign", help="Attack label to assign in collect mode")
    parser.add_argument("--attacker_ip", type=str, default=None, help="IP of attacker (used for labeling during collect)")
    parser.add_argument('--filter_expr', help="Wyrażenie BPF do filtrowania pakietów (np. 'tcp or udp')", default="")
    parser.add_argument('--flow_timeout', type=int, help="Timeout nieaktywnego flowa (s)", default=15)
    parser.add_argument('--flow_max_duration', type=int, help="Maksymalny czas trwania flowa (s)", default=15)
    args = parser.parse_args()

    if args.mode == "collect":
        if not args.attack or not args.attacker_ip:
            parser.error("--attack and --attacker_ip are required in collect mode.")

    all_features = [f.value for f in AllFeatures]
    excluded = {f.value for f in ExcludedFeatures}
    model_features = [f for f in all_features if f not in excluded]

    config = {
        "mode": args.mode,
        "attack": args.attack,
        "attacker_ip": args.attacker_ip,
        "filter_expr": args.filter_expr,
        "flow_timeout": args.flow_timeout,
        "flow_max_duration": args.flow_max_duration,
        "INTERFACES": get_active_interfaces(),
        "CSV_FILENAME": f"{args.attack}_{args.flow_max_duration}s_{args.flow_timeout}s.csv" if args.attack else None,
        "OUTPUT_FOLDER": "dataset",
        "MODEL_PATH": "model/rf_model.pkl",
        "ENCODER_PATH": "model/label_encoder.pkl",
        "ALL_FEATURES": all_features,
        "MODEL_FEATURES": model_features,
    }

    os.makedirs(config["OUTPUT_FOLDER"], exist_ok=True)

    return config