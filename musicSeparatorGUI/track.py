from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar, QFrame
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QIcon
from utils import changeWidgetColor
from player import Player


class Track(QWidget):
    def __init__(self, name, player):
        super().__init__()

        self.name = name
        self.player = player
        self.player.positionChanged.connect(self.change_progress_bar_pos)
        self.player.durationChanged.connect(self.change_progress_bar_range)

        # Fill with color to see borders
        changeWidgetColor(self, QColor("#E8E8E8"))

        mainLayout = QHBoxLayout()  # Main horizontal layout
        mainLayout.setContentsMargins(10, 0, 10, 0)  # no margins
        mainLayout.setSpacing(0)

        # Left part with information
        infoFrame = QFrame()
        infoFrame.setObjectName("infoFrame")
        infoFrame.setFixedSize(QSize(80, 90))
        infoFrame.setStyleSheet("#infoFrame { border: 1px solid #5F5F5F; background-color: #D9D9D9 }")

        infoLayout = QVBoxLayout()
        infoLayout.setContentsMargins(0, 0, 0, 0)  # no margins

        trackName = QLabel(self.name)
        trackName.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        if self.name != "Mixture":
            self.muteButton = QPushButton()
            self.muteButton.setFixedSize(QSize(20, 20))
            self.muteButton.setIcon(QIcon('img/not_mute_icon.png'))
            self.muteButton.setStyleSheet("background-color: #D9D9D9; border: none;")

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFormat("")
        self.progress_bar.setFixedSize(QSize(1020, 90))
        self.progress_bar.setStyleSheet(f"QProgressBar {{border : 1px solid #5F5F5F;}}"
                                        "QProgressBar::chunk {background : rgba(0, 255, 0, 100);}")

        # Add widgets to layouts
        infoLayout.addWidget(trackName)
        if name != "Mixture":
            infoLayout.addWidget(self.muteButton, alignment=Qt.AlignHCenter)
        infoFrame.setLayout(infoLayout)
        mainLayout.addWidget(infoFrame)
        mainLayout.addWidget(self.progress_bar)

        self.setLayout(mainLayout)
        mainLayout.addStretch(1)  # adds a spacer that expands horizontally from the left to the right

        # Set fixed height
        self.setFixedHeight(90)

    def set_progress_bar_image(self, image_path):
        self.progress_bar.setStyleSheet(
            f"QProgressBar {{background-image : url({image_path}); background-repeat: no-repeat; "
            f"background-position: center; border : 1px solid #5F5F5F;}}"
            "QProgressBar::chunk {background : rgba(0, 255, 0, 100);}")

    def change_progress_bar_range(self):
        self.progress_bar.setRange(0, self.player.duration())
        self.progress_bar.setValue(0)

    def change_progress_bar_pos(self):
        pos_ms = self.player.position()
        self.progress_bar.setValue(pos_ms)
