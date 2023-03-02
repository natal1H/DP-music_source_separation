from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QAction, QFileDialog
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
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
        self.export_action = QAction("Export", self)
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self.open_action)
        self.open_action.triggered.connect(self.choose_file)
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

        # Player for playing songs
        self.player = QMediaPlayer()
        self.toolbar.set_player(self.player)

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

    def choose_file(self):
        print("get_file()")

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Audio files (*.mp3)")  # todo: later add option for at least .wav
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            mixture_file_name = dialog.selectedFiles()[0]
            print("Selected mixture filename: ", mixture_file_name)

            # load the audio file
            mixture_url = QUrl.fromLocalFile(mixture_file_name)
            mixture_content = QMediaContent(mixture_url)

            self.player.setMedia(mixture_content)
