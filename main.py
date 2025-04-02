from scapy.all import get_if_list, get_if_hwaddr
import time
from worker import Worker
from config import get_config

if __name__ == "__main__":
    config = get_config()

    interfaces = config["interfaces"]

    if not interfaces:
        print("No interfaces")
        exit(1)

    # my_int = interfaces[5]

    workers = [
        Worker(
            iface,
            filter_expr=config["filter_expr"],
            csv_filename=config["csv_file"],
            output_folder=config["output_folder"],
            flow_timeout=config["flow_timeout"],
            flow_max_duration=config["flow_max_duration"]
        )
        for iface in interfaces
    ]

    for worker in workers:
        worker.start()

    try:
        while any(worker.running for worker in workers):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Zatrzymywanie workerów...")
        for worker in workers:
            worker.stop()
