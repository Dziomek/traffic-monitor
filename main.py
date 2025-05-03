import time
from workers.worker import Worker
from config import get_config
from gui.main_window import MainWindow
from PyQt5 import QtWidgets, QtCore
import sys

if __name__ == "__main__":
    config = get_config()
    interfaces = config["INTERFACES"]

    if not interfaces:
        print("No interfaces")
        exit(1)

    workers = [
        Worker(iface, config)
        for iface in interfaces
    ]

    for w in workers:
        w.start()

    # 2) uruchamiamy Qt GUI
    app = QtWidgets.QApplication(sys.argv)

    # 3) przekazujemy listę workerów do naszego MainWindow
    window = MainWindow(workers)
    window.show()

    # 4) po wyjściu z pętli eventów – zatrzymujemy workery
    exit_code = app.exec_()
    for w in workers:
        w.stop()
    sys.exit(exit_code)

    # try:
    #     while any(worker.running for worker in workers):
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("\nStopping workers...")
    #     for worker in workers:
    #         worker.stop()
