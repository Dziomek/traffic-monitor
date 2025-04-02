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
    parser.add_argument('--csv_file', help="Nazwa pliku CSV (bez rozszerzenia)")
    parser.add_argument('--output_folder', help="Nazwa folderu, do którego zapisywane są pliki", default="records")
    parser.add_argument('--filter_expr', help="Wyrażenie BPF do filtrowania pakietów (np. 'tcp or udp')", default="")
    parser.add_argument('--interface', nargs='*', help="Lista interfejsów do nasłuchu (np. eth0 enp0s3)")
    parser.add_argument('--flow_timeout', type=int, help="Timeout nieaktywnego flowa (s)", default=15)
    parser.add_argument('--flow_max_duration', type=int, help="Maksymalny czas trwania flowa (s)", default=15)
    args = parser.parse_args()

    interfaces = args.interface if args.interface else get_active_interfaces()

    os.makedirs(args.output_folder, exist_ok=True)

    config = {
        "csv_file": f"{args.csv_file}.csv" if args.csv_file else None,
        "output_folder": args.output_folder,
        "filter_expr": args.filter_expr,
        "flow_timeout": args.flow_timeout,
        "flow_max_duration": args.flow_max_duration,
        "interfaces": interfaces
    }
    return config