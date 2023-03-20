from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QAction, QFileDialog
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtGui import QIcon
from PyQt5.Qt import Qt
from toolbar import Toolbar
from timeline import Timeline
from track import Track
from player import Player
from utils import QHSeparationLine, save_waveform_plot, overlay_tracks
from separate import separate_track
import tempfile
import os
import shutil


class MainWindow(QMainWindow):
    def __init__(self, temp_dir: tempfile.TemporaryFile, player: Player):
        super().__init__()

        self.temp_dir = temp_dir
        self.mixture_file_name = None
        self.active_tracks = []

        self.setWindowTitle("Music Separator")
        self.setMinimumSize(QSize(1120, 580))

        # Menu
        self.open_action = QAction("&Open", self)
        self.export_action = QAction("Export", self)
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self.open_action)
        self.open_action.triggered.connect(self.choose_file)
        self.export_action.triggered.connect(self.export_mixture)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)

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

        # Add widgets to layout
        for widget in [self.toolbar, self.timeline, self.mixture_track, self.bass_track, self.drums_track, self.guitars_track, self.vocals_track, self.other_track]:
            layout.addWidget(widget)

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
        # Stop playing the mixture song
        self.player.stop()
        self.toolbar.playPauseButton.setIcon(QIcon('img/play_icon.png'))
        separate_track(self.mixture_file_name, self.temp_dir.name)

        # Disable Mixture track
        self.mixture_track.setEnabled(False)
        self.mixture_track.hide()

        # Enable other tracks & create plots
        for instrument, track_widget in [["bass", self.bass_track], ["drums", self.drums_track], ["guitars", self.guitars_track], ["vocals", self.vocals_track], ["other", self.other_track]]:
            save_waveform_plot(os.path.join(self.temp_dir.name, instrument + ".mp3"), os.path.join(self.temp_dir.name, instrument + ".png"))
            track_widget.set_progress_bar_image(os.path.join(self.temp_dir.name, instrument + ".png"))
            track_widget.muteButton.clicked.connect(self.toggle_track)
            track_widget.show()

        # overlay all tracks into one
        self.active_tracks = ["bass", "drums", "guitars", "vocals", "other"]
        overlay_tracks([os.path.join(self.temp_dir.name, name + ".mp3") for name in self.active_tracks], self.temp_dir.name)

        # load new media
        split_mix_url = QUrl.fromLocalFile(os.path.join(self.temp_dir.name, "mixed.mp3"))
        split_mix_content = QMediaContent(split_mix_url)

        self.player.setMedia(split_mix_content)

        # Disable Split button - cannot split multiple times
        self.toolbar.splitButton.setEnabled(False)
        print("End split song")

    def toggle_track(self):
        track_widget = self.sender().parent().parent()
        instrument_name = track_widget.name.lower()

        prev_position = self.player.position()
        self.player.stop()
        self.toolbar.playPauseButton.setIcon(QIcon('img/play_icon.png'))
        if instrument_name in self.active_tracks:
            self.active_tracks.remove(instrument_name)
            track_widget.muteButton.setIcon(QIcon('img/mute_icon.png'))
        else:
            self.active_tracks.append(instrument_name)
            track_widget.muteButton.setIcon(QIcon('img/not_mute_icon.png'))
        overlay_tracks([os.path.join(self.temp_dir.name, name + ".mp3") for name in self.active_tracks], self.temp_dir.name)
        split_mix_url = QUrl.fromLocalFile(os.path.join(self.temp_dir.name, "mixed.mp3"))
        split_mix_content = QMediaContent(split_mix_url)
        self.player.setMedia(split_mix_content)
        self.player.setPosition(prev_position)

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Space:
            self.toolbar.play_pause_song()
        elif key == Qt.Key_Left:  # move song position back by 5s
            self.player.movePositionByMs(-5000)
        elif key == Qt.Key_Right:  # move song position forward by 5s
            self.player.movePositionByMs(5000)
        elif key == Qt.Key_Up:  # increase volume by 5
            new_volume = 100 if (self.player.volume() + 5 > 100) else self.player.volume() + 5
            self.player.setVolume(new_volume)
            self.toolbar.volumeSlider.setValue(new_volume)
        elif key == Qt.Key_Down:  # decrease volume by 5
            new_volume = 0 if (self.player.volume() - 5 < 0) else self.player.volume() - 5
            self.player.setVolume(new_volume)
        elif key == Qt.Key_M:  # mute song
            self.player.setVolume(0)
            self.toolbar.volumeSlider.setValue(0)

    def export_mixture(self):
        if len(self.active_tracks) == 0:
            print("Need to split first/select some tracks")
        else:
            print("Going to save currently selected mixture")
            dialog = QFileDialog()
            save_location = dialog.getSaveFileName(self, 'Save File')
            shutil.copy(os.path.join(self.temp_dir.name, "mixed.mp3"), save_location[0])
