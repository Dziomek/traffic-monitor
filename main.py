from scapy.all import get_if_list, get_if_addr
from sniffer import Sniffer
import time
from worker import Worker

def list_interfaces():
    interfaces = get_if_list()
    print(interfaces)

    return interfaces

if __name__ == "__main__":
    interfaces = list_interfaces()

    if not interfaces:
        print("No interfaces")
        exit(1)

    # my_int = interfaces[5]

    # Tworzymy workerów dla każdego interfejsu
    workers = [Worker(iface, filter_expr="tcp") for iface in interfaces]

    # Uruchamiamy workerów
    for worker in workers:
        worker.start()

    try:
        while any(worker.running for worker in workers):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Zatrzymywanie workerów...")
        for worker in workers:
            worker.stop()
