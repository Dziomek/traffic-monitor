import time
from workers.worker import Worker
from config import get_config
from gui.main_window import MainWindow
from PyQt5 import QtWidgets, QtCore
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    # 4) po wyjściu z pętli eventów – zatrzymujemy workery
    exit_code = app.exec_()
    # for w in workers:
    #     w.stop()
    sys.exit(exit_code)
