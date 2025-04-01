import argparse
import os

def get_config():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_file', help="Nazwa pliku CSV (bez rozszerzenia)")
    parser.add_argument('--filter_expr', help="Wyrażenie BPF do filtrowania pakietów (np. 'tcp or udp')", default="")
    args = parser.parse_args()

    output_folder = "records"
    flow_timeout = 15 #s
    flow_max_duration = 15 #s

    os.makedirs(output_folder, exist_ok=True)

    config = {
        "csv_file": f"{args.csv_file}.csv" if args.csv_file else None,
        "output_folder": "records",
        "filter_expr": args.filter_expr,
        "flow_timeout": flow_timeout,
        "flow_max_duration": flow_max_duration
    }
    return config