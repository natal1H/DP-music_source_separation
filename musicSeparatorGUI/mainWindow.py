from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QAction, QFileDialog
from PyQt5.QtCore import QSize, QUrl, QThreadPool
from PyQt5.QtMultimedia import QMediaContent
from PyQt5.QtGui import QIcon
from PyQt5.Qt import Qt
from toolbar import Toolbar
from timeline import Timeline
from track import Track
from player import Player
from utils import save_waveform_plot, overlay_tracks, save_json_file
from dialogs import showWarningDialog, SplitInputDialog, SettingsDialog
from statusbar import StatusBar
from separate import separate_track
from worker import Worker
import tempfile
import os
import shutil
from pathlib import Path

class MainWindow(QMainWindow):
    def __init__(self, temp_dir: tempfile.TemporaryFile, player: Player):
        super().__init__()

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.temp_dir = temp_dir
        self.mixture_file_name = None
        self.active_tracks = []

        self.setWindowTitle("Music Separator")
        self.setFixedSize(QSize(1120, 600))

        # Menu
        self.open_action = QAction("&Open", self)
        self.export_action = QAction("&Export", self)
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(self.open_action)
        self.open_action.triggered.connect(self.choose_file)
        self.export_action.triggered.connect(self.export_mixture)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)
        self.settings_action = QAction("&Settings", self)
        menu.addAction(self.settings_action)
        self.settings_action.triggered.connect(self.open_settings)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Left, top, right, bottom
        layout.setSpacing(0)

        # Player for playing songs
        self.player = player
        self.player.setVolume(50)
        self.player.stateChanged.connect(self.player_state_changed)

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

        self.instrument_track_dict = {"bass": self.bass_track, "drums": self.drums_track, "guitars": self.guitars_track,
                                      "vocals": self.vocals_track, "other": self.other_track}
        for track_widget in self.instrument_track_dict.values():
            track_widget.muteButton.clicked.connect(self.toggle_track)
        self.statusbar = StatusBar()

        # Add widgets to layout
        for widget in [self.toolbar, self.timeline, self.mixture_track, self.bass_track, self.drums_track,
                       self.guitars_track, self.vocals_track, self.other_track]:
            layout.addWidget(widget)

        layout.addStretch()
        layout.addWidget(self.statusbar)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def reset_window_on_open(self):
        self.mixture_track.hide()
        self.bass_track.hide()
        self.drums_track.hide()
        self.guitars_track.hide()
        self.vocals_track.hide()
        self.other_track.hide()

        self.toolbar.splitButton.setEnabled(True)

    def choose_file(self):

        self.statusbar.change_text("Opening file...")

        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Audio files (*.mp3)")
        dialog.setViewMode(QFileDialog.Detail)

        if dialog.exec_():
            self.reset_window_on_open()

            self.mixture_file_name = dialog.selectedFiles()[0]

            self.setWindowTitle(Path(self.mixture_file_name).stem + " - Music Separator")

            self.statusbar.change_text("Loading audio...")

            # load the audio file
            mixture_url = QUrl.fromLocalFile(self.mixture_file_name)
            mixture_content = QMediaContent(mixture_url)

            self.player.setMedia(mixture_content)
            # create the waveform plot of mixture

            self.statusbar.change_text("Generating waveform graph...")

            save_waveform_plot(self.mixture_file_name, os.path.join(self.temp_dir.name, "mixture.png"))
            self.mixture_track.set_progress_bar_image(os.path.join(self.temp_dir.name, "mixture.png"))

            self.mixture_track.setEnabled(True)
            self.mixture_track.show()

            # Enable toolbar now
            self.toolbar.setEnabled(True)
            self.statusbar.change_text("")

    def split_song(self):
        self.statusbar.change_text("Splitting audio...")

        splitDialog = SplitInputDialog()
        if splitDialog.exec():  # clicked ok
            self.split_selection = splitDialog.getInputs()
            print(self.split_selection)
            # Disable Split button - cannot split multiple times
            self.toolbar.splitButton.setEnabled(False)

            # Pass the function to execute
            worker = Worker(self.split_song_thread)
            worker.signals.finished.connect(self.split_song_thread_complete)
            self.threadpool.start(worker)  # Execute

            showWarningDialog("Splitting song", "Please wait, the song is being separated into individual instruments. "
                                                "Separated tracks will be automaticly displayed when process is finished.")
            print("End split song")

    def split_song_thread(self):
        self.statusbar.change_text("Separating track into individual instruments...")
        separate_track(self.mixture_file_name, self.temp_dir.name)
        instruments_to_be_joined = ["other"]
        self.statusbar.change_text("Generating graphs for separated tracks...")
        for instrument, checked in self.instrument_track_dict.items():
            if checked:
                save_waveform_plot(os.path.join(self.temp_dir.name, instrument + ".mp3"),
                                   os.path.join(self.temp_dir.name, instrument + ".png"))
            else:
                instruments_to_be_joined.append(instrument)
        if len(instruments_to_be_joined) == 1:  # all were checked, no need to overlay into other
            overlay_tracks([os.path.join(self.temp_dir.name, name + ".mp3") for name in instruments_to_be_joined],
                           self.temp_dir.name, "other.mp3")

    def split_song_thread_complete(self):
        print("THREAD COMPLETE!")
        self.statusbar.change_text("Separation complete...")
        self.player.stop()
        self.toolbar.playPauseButton.setIcon(QIcon('img/play_icon.png'))

        # Disable Mixture track
        self.mixture_track.setEnabled(False)
        self.mixture_track.hide()
        # Enable other tracks & create plots
        self.split_selection["other"] = True
        self.active_tracks = []

        overlay_into_other_track = ["other"]
        for instrument, checked in self.split_selection.items():
            if not checked:
                overlay_into_other_track.append(instrument)
        overlay_tracks([os.path.join(self.temp_dir.name, name + ".mp3") for name in overlay_into_other_track],
                       self.temp_dir.name, save_name="other.mp3")

        for instrument, checked in self.split_selection.items():
            if checked:
                track_widget = self.instrument_track_dict[instrument]
                track_widget.set_progress_bar_image(os.path.join(self.temp_dir.name, instrument + ".png"))
                track_widget.show()
                track_widget.overlay.hide()
                track_widget.muteButton.setIcon(QIcon('img/not_mute_icon.png'))
                self.active_tracks.append(instrument)
        print("Activate tracks after split:", self.active_tracks)
        overlay_tracks([os.path.join(self.temp_dir.name, name + ".mp3") for name in self.active_tracks],
                       self.temp_dir.name)

        # load new media
        split_mix_url = QUrl.fromLocalFile(os.path.join(self.temp_dir.name, "mixed.mp3"))
        split_mix_content = QMediaContent(split_mix_url)

        self.player.setMedia(split_mix_content)
        self.statusbar.change_text("")

    def toggle_track(self):
        track_widget = self.sender().parent().parent()
        instrument_name = track_widget.name.lower()

        print("Toggle track clicked", instrument_name)
        print(self.active_tracks)

        if instrument_name in self.active_tracks and len(self.active_tracks) < 2:
            return

        self.statusbar.change_text("Muting track...")
        self.player.blockSignals(True)

        prev_position = self.player.position()
        self.player.stop()
        self.toolbar.playPauseButton.setIcon(QIcon('img/play_icon.png'))

        if instrument_name in self.active_tracks:  # Track will be now MUTED
            print("MUTING")
            if len(self.active_tracks) > 1:
                self.active_tracks.remove(instrument_name)
                track_widget.muteButton.setIcon(QIcon('img/mute_icon.png'))
                track_widget.overlay.show()
        else:
            print("UNMUTING")
            self.active_tracks.append(instrument_name)  # Track will be now UNMUTED
            track_widget.muteButton.setIcon(QIcon('img/not_mute_icon.png'))
            track_widget.overlay.hide()

        active_track_paths = [os.path.join(self.temp_dir.name, name + ".mp3") for name in self.active_tracks]
        overlay_tracks(active_track_paths, self.temp_dir.name)

        split_mix_url = QUrl.fromLocalFile(os.path.join(self.temp_dir.name, "mixed.mp3"))
        split_mix_content = QMediaContent(split_mix_url)
        self.player.setMedia(split_mix_content)
        self.player.setPosition(prev_position)

        self.statusbar.change_text("")
        self.player.blockSignals(False)

    def keyReleaseEvent(self, event):
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
            showWarningDialog("Export warning", "You need to first split song and have at least 1 track unmuted.")
        else:
            dialog = QFileDialog()
            save_location = dialog.getSaveFileName(self, 'Save File')
            if save_location != "":
                shutil.copy(os.path.join(self.temp_dir.name, "mixed.mp3"), save_location[0])

    def open_settings(self):
        settingsDialog = SettingsDialog()
        if settingsDialog.exec():  # clicked ok
            save_json_file(settingsDialog.getInputs(), "./conf/separation_config.json")

    def move_song_to_position(self, percentual_position):
        print("Will move song to this % position:", percentual_position)
        new_pos = int(percentual_position * self.player.duration())
        self.player.setPosition(new_pos)

    def player_state_changed(self):
        print("Player stated changed, now is:", self.player.state())
        if self.player.state() == 0:  # Stopped
            self.toolbar.playPauseButton.setIcon(QIcon('img/play_icon.png'))
            self.statusbar.change_text("Stopped...")
        elif self.player.state() == 1:
            self.statusbar.change_text("")
        elif self.player.state() == 2:
            self.statusbar.change_text("Paused...")