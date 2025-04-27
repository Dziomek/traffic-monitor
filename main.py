import time
from worker import Worker
from config import get_config

if __name__ == "__main__":
    config = get_config()
    interfaces = config["interfaces"]

    if not interfaces:
        print("No interfaces")
        exit(1)

    workers = [
        Worker(iface, config)
        for iface in interfaces
    ]

    for worker in workers:
        worker.start()

    try:
        while any(worker.running for worker in workers):
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping workers...")
        for worker in workers:
            worker.stop()
