from PyQt5 import QtWidgets, QtGui
from gui.gui import Ui_MainWindow  # <-- Twoja wygenerowana klasa
from config import get_config
from workers.worker import Worker

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.config = get_config()
        self.interfaces = self.config["INTERFACES"]

        self.workers = [
            Worker(iface, self.config)
            for iface in self.interfaces
        ]

        for w in self.workers:
            w.status_change.connect(self.on_worker_status_changed)
            w.processor.flow_result.connect(self.handle_result)

        self.ui.pushButton_4.clicked.connect(self.toggle_workers)

        self.on_worker_status_changed()

    def toggle_workers(self):
        if any(w.running for w in self.workers):
            for w in self.workers:
                w.stop()
            self.ui.pushButton_4.setText("Start")
        else:
            for w in self.workers:
                w.start()
            self.ui.pushButton_4.setText("Stop")

    def on_worker_status_changed(self):
        if all(w.running for w in self.workers):
            self.ui.statusIcon.setPixmap(QtGui.QPixmap("assets/check_circle_24.svg"))
            self.ui.statusLabel.setText("Running")
        else:
            self.ui.statusIcon.setPixmap(QtGui.QPixmap("assets/pending_24.svg"))
            self.ui.statusLabel.setText("Stopped")
    
    def handle_result(self, result):
        color_label = "#2a9b80" if result['predicted_label'].lower() == "benign" else "#e57373"

        msg = (
            f"<span style='font-family: Segoe UI; color: #6c6f7f;'>[FLOW]</span> "
            f"<span style='font-family: Segoe UI; color: #9ccfd8;'>{result['src_ip']}:</span>"
            f"<span style='font-family: Segoe UI; color: #89b4fa;'>{result['src_port']}</span> "
            f"<span style='font-family: Segoe UI; color: #6c6f7f;'>→</span> "
            f"<span style='font-family: Segoe UI; color: #9ccfd8;'>{result['dst_ip']}:</span>"
            f"<span style='font-family: Segoe UI; color: #89b4fa;'>{result['dst_port']}</span> "
            f"<span style='font-family: Segoe UI; color: {color_label}; font-weight: bold;'>| {result['predicted_label'].upper()}</span>"
        )


        self.ui.consoleTextEdit.append(msg)
