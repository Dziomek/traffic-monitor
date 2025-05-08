import time
from workers.worker import Worker
from config import get_config
from gui.new_main_window import MainWindow
from PyQt5 import QtWidgets, QtCore
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    exit_code = app.exec_()
    sys.exit(exit_code)
