from PyQt5 import QtWidgets, QtGui, QtCore
from gui.gui import Ui_MainWindow  # <-- Twoja wygenerowana klasa
from config import get_config
from workers.worker import Worker
from datetime import datetime

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.ui.setupUi(self)

        self.config = get_config()
        self.interfaces = self.config["INTERFACES"]

        self.display_mode = "all"
        self.flow_logs = []

        self.ui.allButton.clicked.connect(self.show_all_logs)
        self.ui.threatsOnlyButton.clicked.connect(self.show_threats_only)

        self.workers = [
            Worker(iface, self.config)
            for iface in self.interfaces
        ]

        for w in self.workers:
            w.status_change.connect(self.on_worker_status_changed)
            w.processor.flow_result.connect(self.handle_result)
            w.interface_information.connect(self.handle_interface_information)

        self.ui.pushButton_4.clicked.connect(self.toggle_workers)

        self.on_worker_status_changed()

        self.STOP_STYLE = """
QPushButton {
    background-color: #24262e;
    color: #e57373;
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: 500;
    border-top: 1px solid #393a3b;
    border-bottom: 1px solid black;
}
QPushButton:hover {
    background-color: #292933;
}
"""
        self.START_STYLE = """
QPushButton {
    background-color: #24262e;
    color: #2a9b80;
    border-radius: 8px;
    padding: 6px 12px;
    font-weight: 500;
    border-top: 1px solid #393a3b;
    border-bottom: 1px solid black;
}
QPushButton:hover {
    background-color: #292933;
}
"""
        self.ACTIVE_BUTTON_STYLE = """
QPushButton {
    color: white;
    background-color: black;
    border: 1px solid #1b1d23;
    border-radius: 6px;
}
"""

        self.INACTIVE_BUTTON_STYLE = """
QPushButton {
    color: white;
    background-color: transparent;
    border: none;
    border-radius: 6px;
}
QPushButton:hover {
    background-color: #292933;
}
"""
    def show_all_logs(self):
        self.display_mode = "all"
        self.ui.consoleTextEdit.clear()
        for result in self.flow_logs:
            self.append_formatted_flow(result)

        self.ui.allButton.setStyleSheet(self.ACTIVE_BUTTON_STYLE)
        self.ui.threatsOnlyButton.setStyleSheet(self.INACTIVE_BUTTON_STYLE)

    def show_threats_only(self):
        self.display_mode = "threats"
        self.ui.consoleTextEdit.clear()
        for result in self.flow_logs:
            self.append_formatted_flow(result)
        
        self.ui.threatsOnlyButton.setStyleSheet(self.ACTIVE_BUTTON_STYLE)
        self.ui.allButton.setStyleSheet(self.INACTIVE_BUTTON_STYLE)

    def toggle_workers(self):
        if any(w.running for w in self.workers):
            for w in self.workers:
                w.stop()
            self.ui.pushButton_4.setText("Start")
            self.ui.pushButton_4.setStyleSheet(self.START_STYLE)
        else:
            for w in self.workers:
                w.start()
            self.ui.pushButton_4.setText("Stop")
            self.ui.pushButton_4.setStyleSheet(self.STOP_STYLE)

    def on_worker_status_changed(self):
        if all(w.running for w in self.workers):
            self.ui.statusIcon.setPixmap(QtGui.QPixmap("assets/running.svg"))
            self.ui.statusLabel.setText("Running")
            self.ui.statusLabel.setStyleSheet("color: #2a9b80;")
        else:
            self.ui.statusIcon.setPixmap(QtGui.QPixmap("assets/pending.svg"))
            self.ui.statusLabel.setText("Stopped")
            self.ui.statusLabel.setStyleSheet("color: #e57373;")
    
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

        self.flow_logs.append(result)
        self.append_formatted_flow(result)

    def append_formatted_flow(self, result):
        if self.display_mode == "threats" and result["predicted_label"].lower() == "benign":
            return
        timestamp = datetime.now().strftime("%H:%M:%S")

        color_label = "#2a9b80" if result['predicted_label'].lower() == "benign" else "#e57373"

        msg = (
            f"<span style='font-family: Segoe UI; color: #6c6f7f;'>[{timestamp}] [FLOW]</span> "
            f"<span style='font-family: Segoe UI; color: #9ccfd8;'>{result['src_ip']}:</span>"
            f"<span style='font-family: Segoe UI; color: #89b4fa;'>{result['src_port']}</span> "
            f"<span style='font-family: Segoe UI; color: #6c6f7f;'>→</span> "
            f"<span style='font-family: Segoe UI; color: #9ccfd8;'>{result['dst_ip']}:</span>"
            f"<span style='font-family: Segoe UI; color: #89b4fa;'>{result['dst_port']}</span> "
            f"<span style='font-family: Segoe UI; color: {color_label}; font-weight: bold;'>| {result['predicted_label'].upper()}</span>"
        )

        self.ui.consoleTextEdit.append(msg)

    def handle_interface_information(self, interface_information):
        formatted_msg = (
            f"<span style='font-family: Segoe UI; color: #8ab4f8;'>"
            f"[WORKER] </span>"
            f"<span style='font-family: Segoe UI; color: #d4d4d4;'>{interface_information}</span>"
        )

        self.ui.consoleTextEdit.append(formatted_msg)

