from scapy.all import get_if_list, get_if_hwaddr
from sniffer import Sniffer
import time
from worker import Worker

TARGET_MAC = "0A:00:27:00:00:04"

if __name__ == "__main__":
    interfaces = get_if_list()

    if not interfaces:
        print("No interfaces")
        exit(1)

    # my_int = interfaces[5]

    workers = [Worker(iface, filter_expr="") for iface in interfaces]

    for worker in workers:
        worker.start()

    try:
        while any(worker.running for worker in workers):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Zatrzymywanie workerów...")
        for worker in workers:
            worker.stop()
