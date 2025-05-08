from PyQt5 import QtCore, QtGui, QtWidgets
from config import get_config
from workers.worker import Worker

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.interfaces = self.config["INTERFACES"]

        self.workers = [
            Worker(iface, self.config)
            for iface in self.interfaces
        ]

        for w in self.workers:
           w.status_change.connect(self.on_worker_status_changed)

        self.setupUi()

    def on_worker_status_changed(self):
        if all(w.running for w in self.workers):
            self.statusLabel.setPixmap(QtGui.QPixmap("assets/check_circle_24.svg"))
        else:
            self.statusLabel.setPixmap(QtGui.QPixmap("assets/pending_24.svg"))

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(551, 389)

        # Central widget
        self.centralWidget = QtWidgets.QWidget(self)
        self.centralWidget.setStyleSheet("background-color: #363746")
        self.setCentralWidget(self.centralWidget)

        # Navbar
        self.navbar = QtWidgets.QFrame(self.centralWidget)
        self.navbar.setGeometry(0, 0, 551, 41)
        self.navbar.setStyleSheet("background-color: #3a3b4c")

        # Status icon
        self.statusLabel = QtWidgets.QLabel(self.navbar)
        self.statusLabel.setGeometry(510, 0, 31, 41)
        self.statusLabel.setPixmap(QtGui.QPixmap("assets/pending_24.svg"))
        self.statusLabel.setAlignment(QtCore.Qt.AlignCenter)

        # Interface label
        self.interfaceLabel = QtWidgets.QTextEdit(self.navbar)
        self.interfaceLabel.setGeometry(450, 10, 61, 31)
        self.interfaceLabel.setStyleSheet("color: white; border: none;")
        self.interfaceLabel.setHtml("<p align='center'><span style='font-size:10pt; font-weight:600;'>eth0</span></p>")

        # Sidebar
        self.sidebar = QtWidgets.QFrame(self.centralWidget)
        self.sidebar.setGeometry(0, 30, 81, 361)
        self.sidebar.setStyleSheet("background-color: #3a3b4c")
        self.vbox = QtWidgets.QVBoxLayout(self.sidebar)

        # Buttons
        icons = ["desktop_windows_24.svg", "files_24.svg", "settings_24.svg", "help_24.svg"]
        self.buttons = []
        for ico in icons:
            btn = QtWidgets.QPushButton(self.sidebar)
            btn.setIcon(QtGui.QIcon(f"assets/{ico}"))
            btn.setIconSize(QtCore.QSize(40,40))
            btn.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.vbox.addWidget(btn)
            self.buttons.append(btn)

        # Stacked widget
        self.stackedWidget = QtWidgets.QStackedWidget(self.centralWidget)
        self.stackedWidget.setGeometry(80, 40, 471, 331)

        # Dodajemy strony
        self.mainPage = MainPage(self.workers)
        self.stackedWidget.addWidget(self.mainPage)
        # tu w przyszłości inne widoki:
        # self.filesPage = FilesPage()
        # self.stackedWidget.addWidget(self.filesPage)
        # ...

        # Podłączenie sygnałów
        self.buttons[0].clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.mainPage))
        # analogicznie dla pozostałych



