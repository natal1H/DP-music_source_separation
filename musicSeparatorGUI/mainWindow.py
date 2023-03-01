from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QAction
from PyQt5.QtCore import QSize
from toolbar import Toolbar
from timeline import Timeline
from track import Track
from utils import QHSeparationLine


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Music Separator")
        self.setMinimumSize(QSize(1120, 670))

        ### Menu
        self.open_action = QAction("&Open", self)
        self.open_action.setStatusTip("Open file")
        self.export_action = QAction("Export", self)
        self.export_action.setStatusTip("Export song")
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)
        ###

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Left, top, right, bottom
        layout.setSpacing(0)

        self.toolbar = Toolbar()
        self.timeline = Timeline()
        self.mixture_track = Track("Mixture")
        self.bass_track = Track("Bass")
        self.drums_track = Track("Drums")
        self.guitars_track = Track("Guitars")
        self.vocals_track = Track("Vocals")
        self.other_track = Track("Other")

        separator_horizontal = QHSeparationLine()

        layout.addWidget(self.toolbar)
        layout.addWidget(self.timeline)
        layout.addWidget(self.mixture_track)
        layout.addWidget(separator_horizontal)
        layout.addWidget(self.bass_track)
        layout.addWidget(self.drums_track)
        layout.addWidget(self.guitars_track)
        layout.addWidget(self.vocals_track)
        layout.addWidget(self.other_track)
        layout.addStretch(1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
