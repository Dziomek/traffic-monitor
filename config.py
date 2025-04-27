import argparse
import os
import netifaces

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
        "ENCODER_PATH": "model/label_encoder.pkl"
    }

    os.makedirs(config["OUTPUT_FOLDER"], exist_ok=True)

    return config