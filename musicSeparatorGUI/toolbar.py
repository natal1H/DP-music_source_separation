from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QSlider, QLabel
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer
from utils import changeWidgetColor
from player import Player

""" Application for Guitar Sound Separation from Music Recording

    Author:         Natália Holková
    Login:          xholko02
    File:           toolbar.py
    Description:    Toolbar with options related to audio control
"""

class Toolbar(QWidget):

    def __init__(self, player: Player):
        super().__init__()

        # Media player
        self.player = player

        # Fill with color to see borders
        changeWidgetColor(self, QColor("#CACACA"))

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 0, 0)  # Left, top, right, bottom

        # Play/Pause button
        self.playPauseButton = QPushButton(clicked=self.play_pause_song)
        self.playPauseButton.setFixedSize(QSize(30, 30))
        self.playPauseButton.setIcon(QIcon('img/play_icon.png'))
        self.playPauseButton.setStyleSheet("QPushButton {background-color: #A5A5A5; border-radius: 4px;}"
                                           "QPushButton::hover {background-color : #8C8C8C;}")

        # Jump to beginning button
        self.jumpToBeginningButton = QPushButton(clicked=self.jump_to_beginning)
        self.jumpToBeginningButton.setFixedSize(QSize(30, 30))
        self.jumpToBeginningButton.setIcon(QIcon('img/to_start.png'))
        self.jumpToBeginningButton.setStyleSheet("QPushButton {background-color: #A5A5A5; border-radius: 4px;}"
                                           "QPushButton::hover {background-color : #8C8C8C;}")

        # Jump to end button
        self.jumpToEndButton = QPushButton(clicked=self.jump_to_end)
        self.jumpToEndButton.setFixedSize(QSize(30, 30))
        self.jumpToEndButton.setIcon(QIcon('img/to_end.png'))
        self.jumpToEndButton.setStyleSheet("QPushButton {background-color: #A5A5A5; border-radius: 4px;}"
                                           "QPushButton::hover {background-color : #8C8C8C;}")

        # Split button
        self.splitButton = QPushButton("SPLIT")
        self.splitButton.setFixedSize(QSize(60, 30))
        self.splitButton.setStyleSheet("color: #414141; background-color: #A5A5A5; border-radius: 4px;")
        self.splitButton.setStyleSheet("QPushButton {background-color: #A5A5A5; border-radius: 4px;}"
                                           "QPushButton::hover {background-color : #8C8C8C; color: white}")


        # Master volume slider, volume icon & labels
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setSingleStep(1)
        self.volumeSlider.setValue(self.player.volume())
        self.volumeSlider.valueChanged.connect(self.change_volume)

        volumeIcon = QLabel()
        volumeIcon.setFixedSize(QSize(30, 30))
        volumeIcon.setPixmap(QPixmap('img/volume_icon.png'))

        volumeLabelMin = QLabel(str(self.volumeSlider.minimum()))
        volumeLabelMax = QLabel(str(self.volumeSlider.maximum()))

        # add all widgets to toolbar in order
        layout.addWidget(self.playPauseButton)
        layout.addWidget(self.jumpToBeginningButton)
        layout.addWidget(self.jumpToEndButton)
        layout.addWidget(self.splitButton)
        layout.addWidget(volumeIcon)
        layout.addWidget(volumeLabelMin)
        layout.addWidget(self.volumeSlider)
        layout.addWidget(volumeLabelMax)

        layout.addStretch(1)  # adds a spacer that expands horizontally from the left to the right
        self.setLayout(layout)

        # Set max toolbar height
        self.setFixedHeight(50)

    def play_pause_song(self):
        # Check if player has loaded audio
        if self.player.isAudioAvailable():
            if self.player.state() == QMediaPlayer.State.PlayingState:
                self.player.pause()
                self.playPauseButton.setIcon(QIcon('img/play_icon.png'))
            elif self.player.state() == QMediaPlayer.State.PausedState:
                self.player.play()
                self.playPauseButton.setIcon(QIcon('img/pause_icon.png'))
            else:  # was stopped
                if self.player.position() == self.player.duration():
                    self.player.setPosition(0)
                self.player.play()
                self.playPauseButton.setIcon(QIcon('img/pause_icon.png'))

    def change_volume(self):
        self.player.setVolume(self.volumeSlider.value())

    def jump_to_beginning(self):
        self.player.setPosition(0)

    def jump_to_end(self):
        self.player.stop()
        self.player.setPosition(self.player.duration())
        self.playPauseButton.setIcon(QIcon('img/play_icon.png'))
