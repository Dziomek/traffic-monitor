from scapy.all import get_if_list, get_if_addr
from sniffer import Sniffer
import time

def list_interfaces():
    interfaces = get_if_list()
    print(interfaces)

    return interfaces

if __name__ == "__main__":
    interfaces = list_interfaces()

    if not interfaces:
        print("No interfaces")
        exit(1)

    my_int = interfaces[5]

    print(f"\nStarting sniffer on {my_int}")

    sniffer = Sniffer(iface=my_int, count=0, filter_expr="icmp")
    sniffer.start()

    try:
        while sniffer.running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping sniffer...")
        sniffer.stop()
