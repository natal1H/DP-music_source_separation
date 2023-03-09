from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QAction, QFileDialog
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtMultimedia import QMediaContent
from toolbar import Toolbar
from timeline import Timeline
from track import Track
from player import Player
from utils import QHSeparationLine, save_waveform_plot
import tempfile
import os


class MainWindow(QMainWindow):
    def __init__(self, temp_dir: tempfile.TemporaryFile):
        super().__init__()

        self.temp_dir = temp_dir

        self.setWindowTitle("Music Separator")
        self.setMinimumSize(QSize(1120, 670))

        # Menu
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

        # Player for playing songs
        self.player = Player()
        self.player.setVolume(50)

        self.toolbar = Toolbar(self.player)
        self.toolbar.setEnabled(False)

        self.timeline = Timeline(self.player)
        self.mixture_track = Track("Mixture")
        self.mixture_track.hide()
        self.bass_track = Track("Bass")
        self.bass_track.hide()
        self.drums_track = Track("Drums")
        self.drums_track.hide()
        self.guitars_track = Track("Guitars")
        self.guitars_track.hide()
        self.vocals_track = Track("Vocals")
        self.vocals_track.hide()
        self.other_track = Track("Other")
        self.other_track.hide()

        separator_horizontal = QHSeparationLine()
        separator_horizontal.hide()

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
            # create the waveform plot of mixture
            save_waveform_plot(mixture_file_name, os.path.join(self.temp_dir.name, "mixture.png"))
            self.mixture_track.set_progress_bar_image(os.path.join(self.temp_dir.name, "mixture.png"))

            self.mixture_track.show()

            # Enable toolbar now
            self.toolbar.setEnabled(True)

