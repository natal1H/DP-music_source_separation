from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QSlider, QLabel
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from utils import changeWidgetColor


class Toolbar(QWidget):
    player = None

    def __init__(self):
        super().__init__()

        # Fill with color to see borders
        changeWidgetColor(self, QColor("#CACACA"))

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 0, 0)  # Left, top, right, bottom

        # Play/Pause button
        self.playPauseButton = QPushButton(clicked=self.play_pause_song)
        self.playPauseButton.setFixedSize(QSize(30, 30))
        self.playPauseButton.setIcon(QIcon('img/play_icon.png'))
        self.playPauseButton.setStyleSheet("background-color: #A5A5A5; border-radius: 4px;")

        # Jump to beginning button
        self.jumpToBeginningButton = QPushButton()
        self.jumpToBeginningButton.setFixedSize(QSize(30, 30))
        self.jumpToBeginningButton.setIcon(QIcon('img/to_start.png'))
        self.jumpToBeginningButton.setStyleSheet("background-color: #A5A5A5; border-radius: 4px;")

        # Jump to end button
        self.jumpToEndButton = QPushButton()
        self.jumpToEndButton.setFixedSize(QSize(30, 30))
        self.jumpToEndButton.setIcon(QIcon('img/to_end.png'))
        self.jumpToEndButton.setStyleSheet("background-color: #A5A5A5; border-radius: 4px;")

        # Split button
        self.splitButton = QPushButton("SPLIT")
        self.splitButton.setFixedSize(QSize(60, 30))
        self.splitButton.setStyleSheet("color: #414141; background-color: #A5A5A5; border-radius: 4px;")

        # Master volume slider, volume icon & labels
        self.volumeSlider = QSlider(Qt.Horizontal)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setSingleStep(1)

        volumeIcon = QLabel()
        volumeIcon.setFixedSize(QSize(30, 30))
        volumeIcon.setPixmap(QPixmap('img/volume_icon.png'))

        volumeLabelMin = QLabel(str(self.volumeSlider.minimum()))
        volumeLabelMax = QLabel(str(self.volumeSlider.maximum()))

        # Media player
        #self.player = None

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

    def set_player(self, player: QMediaPlayer):
        self.player = player

    def play_pause_song(self):
        # Check if player has loaded audio
        if self.player.isAudioAvailable():
            if self.player.state() == QMediaPlayer.State.PlayingState:
                self.playPauseButton.setIcon(QIcon('img/play_icon.png'))
                self.player.pause()
            else:
                self.playPauseButton.setIcon(QIcon('img/pause_icon.png'))
                self.player.play()
