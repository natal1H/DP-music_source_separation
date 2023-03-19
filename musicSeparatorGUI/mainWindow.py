from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QAction, QFileDialog
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtGui import QIcon
from toolbar import Toolbar
from timeline import Timeline
from track import Track
from player import Player
from utils import QHSeparationLine, save_waveform_plot, overlay_tracks
from separate import separate_track
import tempfile
import os


class MainWindow(QMainWindow):
    def __init__(self, temp_dir: tempfile.TemporaryFile, player: Player):
        super().__init__()

        self.temp_dir = temp_dir
        self.mixture_file_name = None
        self.active_tracks = []

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
        self.player = player
        self.player.setVolume(50)

        self.toolbar = Toolbar(self.player)
        self.toolbar.setEnabled(False)
        self.toolbar.splitButton.clicked.connect(self.split_song)

        self.timeline = Timeline(self.player)
        self.mixture_track = Track("Mixture", self.player)
        self.mixture_track.hide()
        self.bass_track = Track("Bass", self.player)
        self.bass_track.hide()
        self.drums_track = Track("Drums", self.player)
        self.drums_track.hide()
        self.guitars_track = Track("Guitars", self.player)
        self.guitars_track.hide()
        self.vocals_track = Track("Vocals", self.player)
        self.vocals_track.hide()
        self.other_track = Track("Other", self.player)
        self.other_track.hide()

        self.separator_horizontal = QHSeparationLine()
        self.separator_horizontal.hide()

        layout.addWidget(self.toolbar)
        layout.addWidget(self.timeline)
        layout.addWidget(self.mixture_track)
        layout.addWidget(self.separator_horizontal)
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
        dialog.setNameFilter("Audio files (*.mp3)")
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            self.mixture_file_name = dialog.selectedFiles()[0]
            print("Selected mixture filename: ", self.mixture_file_name)
            # load the audio file
            mixture_url = QUrl.fromLocalFile(self.mixture_file_name)
            mixture_content = QMediaContent(mixture_url)

            self.player.setMedia(mixture_content)
            # create the waveform plot of mixture
            save_waveform_plot(self.mixture_file_name, os.path.join(self.temp_dir.name, "mixture.png"))
            self.mixture_track.set_progress_bar_image(os.path.join(self.temp_dir.name, "mixture.png"))

            self.mixture_track.show()

            # Enable toolbar now
            self.toolbar.setEnabled(True)

    def split_song(self):
        print("Split song called from main window.")

        # Stop playing the mixture song
        self.player.stop()
        self.toolbar.playPauseButton.setIcon(QIcon('img/play_icon.png'))
        separate_track(self.mixture_file_name, self.temp_dir.name)

        # Disable Mixture track
        self.mixture_track.setEnabled(False)
        self.mixture_track.hide()

        # Enable other tracks & create plots
        # TODO uncomment
        save_waveform_plot(os.path.join(self.temp_dir.name, "bass.mp3"), os.path.join(self.temp_dir.name, "bass.png"))
        save_waveform_plot(os.path.join(self.temp_dir.name, "drums.mp3"), os.path.join(self.temp_dir.name, "drums.png"))
        save_waveform_plot(os.path.join(self.temp_dir.name, "guitars.mp3"), os.path.join(self.temp_dir.name, "guitars.png"))
        save_waveform_plot(os.path.join(self.temp_dir.name, "vocals.mp3"), os.path.join(self.temp_dir.name, "vocals.png"))
        save_waveform_plot(os.path.join(self.temp_dir.name, "other.mp3"), os.path.join(self.temp_dir.name, "other.png"))

        self.bass_track.set_progress_bar_image(os.path.join(self.temp_dir.name, "bass.png"))
        self.drums_track.set_progress_bar_image(os.path.join(self.temp_dir.name, "drums.png"))
        self.guitars_track.set_progress_bar_image(os.path.join(self.temp_dir.name, "guitars.png"))
        self.vocals_track.set_progress_bar_image(os.path.join(self.temp_dir.name, "vocals.png"))
        self.other_track.set_progress_bar_image(os.path.join(self.temp_dir.name, "other.png"))

        self.bass_track.muteButton.clicked.connect(self.toggle_bass_track)
        self.drums_track.muteButton.clicked.connect(self.toggle_drums_track)
        self.guitars_track.muteButton.clicked.connect(self.toggle_guitars_track)
        self.vocals_track.muteButton.clicked.connect(self.toggle_vocals_track)
        self.other_track.muteButton.clicked.connect(self.toggle_other_track)


        self.bass_track.show()
        self.drums_track.show()
        self.guitars_track.show()
        self.vocals_track.show()
        self.other_track.show()

        self.active_tracks = ["bass", "drums", "guitars", "vocals", "other"]
        # overlay all tracks into one
        tmp_locs = [os.path.join(self.temp_dir.name, name + ".mp3") for name in self.active_tracks]
        overlay_tracks(tmp_locs, self.temp_dir.name)

        # load new media
        # load the audio file
        split_mix_url = QUrl.fromLocalFile(os.path.join(self.temp_dir.name, "mixed.mp3"))
        split_mix_content = QMediaContent(split_mix_url)

        self.player.setMedia(split_mix_content)

        # Disable Split button - cannot split multiple times
        self.toolbar.splitButton.setEnabled(False)
        print("End split song")

    def toggle_bass_track(self):
        self.player.stop()
        if "bass" in self.active_tracks:
            print("Mute bass track")
            self.active_tracks.remove("bass")
            self.bass_track.muteButton.setIcon(QIcon('img/mute_icon.png'))
        else:
            print("Unmute bass track")
            self.active_tracks.append("bass")
            self.bass_track.muteButton.setIcon(QIcon('img/not_mute_icon.png'))
        tmp_locs = [os.path.join(self.temp_dir.name, name + ".mp3") for name in self.active_tracks]
        overlay_tracks(tmp_locs, self.temp_dir.name)
        split_mix_url = QUrl.fromLocalFile(os.path.join(self.temp_dir.name, "mixed.mp3"))
        split_mix_content = QMediaContent(split_mix_url)
        self.player.setMedia(split_mix_content)

    def toggle_drums_track(self):
        self.player.stop()
        if "drums" in self.active_tracks:
            print("Mute drums track")
            self.active_tracks.remove("drums")
            self.drums_track.muteButton.setIcon(QIcon('img/mute_icon.png'))
        else:
            print("Unmute drums track")
            self.active_tracks.append("drums")
            self.drums_track.muteButton.setIcon(QIcon('img/not_mute_icon.png'))
        tmp_locs = [os.path.join(self.temp_dir.name, name + ".mp3") for name in self.active_tracks]
        overlay_tracks(tmp_locs, self.temp_dir.name)
        split_mix_url = QUrl.fromLocalFile(os.path.join(self.temp_dir.name, "mixed.mp3"))
        split_mix_content = QMediaContent(split_mix_url)
        self.player.setMedia(split_mix_content)

    def toggle_guitars_track(self):
        self.player.stop()
        if "guitars" in self.active_tracks:
            print("Mute guitars track")
            self.active_tracks.remove("guitars")
            self.guitars_track.muteButton.setIcon(QIcon('img/mute_icon.png'))
        else:
            print("Unmute guitars track")
        tmp_locs = [os.path.join(self.temp_dir.name, name + ".mp3") for name in self.active_tracks]
        overlay_tracks(tmp_locs, self.temp_dir.name)
        split_mix_url = QUrl.fromLocalFile(os.path.join(self.temp_dir.name, "mixed.mp3"))
        split_mix_content = QMediaContent(split_mix_url)
        self.player.setMedia(split_mix_content)

    def toggle_vocals_track(self):
        self.player.stop()
        if "vocals" in self.active_tracks:
            print("Mute vocals track")
            self.active_tracks.remove("vocals")
            self.vocals_track.muteButton.setIcon(QIcon('img/mute_icon.png'))
        else:
            print("Unmute vocals track")
            self.active_tracks.append("vocals")
            self.vocals_track.muteButton.setIcon(QIcon('img/not_mute_icon.png'))
        tmp_locs = [os.path.join(self.temp_dir.name, name + ".mp3") for name in self.active_tracks]
        overlay_tracks(tmp_locs, self.temp_dir.name)
        split_mix_url = QUrl.fromLocalFile(os.path.join(self.temp_dir.name, "mixed.mp3"))
        split_mix_content = QMediaContent(split_mix_url)
        self.player.setMedia(split_mix_content)

    def toggle_other_track(self):
        self.player.stop()
        if "other" in self.active_tracks:
            print("Mute other track")
            self.active_tracks.remove("other")
            self.other_track.muteButton.setIcon(QIcon('img/mute_icon.png'))
        else:
            print("Unmute other track")
            self.active_tracks.append("other")
            self.other_track.muteButton.setIcon(QIcon('img/not_mute_icon.png'))
        tmp_locs = [os.path.join(self.temp_dir.name, name + ".mp3") for name in self.active_tracks]
        overlay_tracks(tmp_locs, self.temp_dir.name)
        split_mix_url = QUrl.fromLocalFile(os.path.join(self.temp_dir.name, "mixed.mp3"))
        split_mix_content = QMediaContent(split_mix_url)
        self.player.setMedia(split_mix_content)
