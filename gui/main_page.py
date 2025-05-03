from PyQt5 import QtCore, QtGui, QtWidgets

class MainPage(QtWidgets.QWidget):
    def __init__(self, workers, parent=None):
        super().__init__(parent)
        self.running = False
        self.workers = workers

        for w in self.workers:
            w.processor.flow_result.connect(self.handle_result)

        self.setupUi()

    def toggle_workers(self):
        if not self.running:
            for w in self.workers:
                w.start()
            self.running = True
            self.startStopButton.setText("Stop")
            # self.startStopButton.setIcon(QtGui.QIcon("assets/cancel_24.svg"))
            self.startStopButton.setStyleSheet("border-radius: 10px; background-color: #4c3a40; color: white")
        else:
            for w in self.workers:
                w.stop()
            self.running = False
            self.startStopButton.setText("Start")
            # self.startStopButton.setIcon(QtGui.QIcon("assets/play_arrow_24.svg"))
            self.startStopButton.setStyleSheet("border-radius: 10px; background-color: #3a4c3f; color: white")

    def setupUi(self):
        self.setObjectName("mainPage")
        self.resize(471, 331)

        # Status
        self.textEdit = QtWidgets.QTextEdit(self)
        self.textEdit.setGeometry(QtCore.QRect(20, 20, 81, 31))
        self.textEdit.setStyleSheet("color: white; border: none")
        self.textEdit.setHtml("<p><span style='font-size:12pt;'>Status:</span></p>")

        self.statusLabel = QtWidgets.QLabel(self)
        self.statusLabel.setGeometry(QtCore.QRect(110, 20, 31, 31))
        self.statusLabel.setPixmap(QtGui.QPixmap("assets/check_circle_24.svg"))
        self.statusLabel.setAlignment(QtCore.Qt.AlignCenter)

        # Interfaces
        self.textEdit2 = QtWidgets.QTextEdit(self)
        self.textEdit2.setGeometry(QtCore.QRect(20, 60, 111, 31))
        self.textEdit2.setStyleSheet("color: white; border: none")
        self.textEdit2.setHtml("<p><span style='font-size:12pt;'>Interface(s):</span></p>")

        self.interfaceLabel = QtWidgets.QTextEdit(self)
        self.interfaceLabel.setGeometry(QtCore.QRect(130, 60, 61, 31))
        self.interfaceLabel.setStyleSheet("color: white; border: none")
        self.interfaceLabel.setHtml("<p align='center'><span style='font-size:10pt; font-weight:600;'>eth0</span></p>")

        # Console
        self.consoleWindow = QtWidgets.QTextEdit(self)
        self.consoleWindow.setGeometry(QtCore.QRect(10, 110, 451, 221))
        self.consoleWindow.setStyleSheet(
            "background-color: #1e1e1e; color: #00ff00; font-family: Consolas;"
            " font-size: 8pt; border: 1px solid #444; padding: 8px;"
        )

        # Stop button
        # self.stopButton = QtWidgets.QPushButton("Stop", self)
        # self.stopButton.setGeometry(QtCore.QRect(350, 40, 93, 28))
        # self.stopButton.setStyleSheet("border-radius: 10px; background-color: #4c3a40")
        # self.stopButton.setIcon(QtGui.QIcon("assets/cancel_24.svg"))

        self.startStopButton = QtWidgets.QPushButton("Start", self)
        self.startStopButton.setGeometry(QtCore.QRect(350, 40, 93, 28))
        self.startStopButton.setStyleSheet("border-radius: 10px; background-color: #3a4c3f; color: white")
        self.startStopButton.setIcon(QtGui.QIcon("assets/desktop_windows_24.svg"))
        self.startStopButton.clicked.connect(self.toggle_workers)

    def handle_result(self, result):
        msg = (
            f"<span style='color:#00ff00;'>[FLOW]</span> "
            f"<span style='color:#4caf50;'>{result['src_ip']}</span>"
            f"<span style='color:#a5d6a7;'>:{result['src_port']}</span> → "
            f"<span style='color:#4caf50;'>{result['dst_ip']}</span>"
            f"<span style='color:#a5d6a7;'>:{result['dst_port']}</span> | "
            f"<span style='color:#81c784; font-weight:bold;'>Label:</span> "
            f"<span style='color:#c5e1a5; font-style:italic;'>{result['predicted_label']}</span>"
        )

        self.consoleWindow.append(msg)
