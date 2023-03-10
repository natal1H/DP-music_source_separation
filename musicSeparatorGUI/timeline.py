from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from utils import changeWidgetColor, formatTime
from player import Player

class Timeline(QWidget):
    def __init__(self, player: Player):
        super().__init__()
        self.player = player
        self.player.durationChanged.connect(self.change_total_time)
        self.player.positionChanged.connect(self.change_current_time)

        # Fill with color to see borders
        changeWidgetColor(self, QColor("#E8E8E8"))

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)  # Left, top, right, bottom

        self.currentTimeLabel = QLabel("--:--")
        self.totalTimeLabel = QLabel("--:--")
        self.totalTimeLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(self.currentTimeLabel)
        layout.addWidget(self.totalTimeLabel)

        self.setLayout(layout)

        # Set fixed height
        self.setFixedHeight(30)

    def change_total_time(self):
        self.totalTimeLabel.setText(formatTime(self.player.duration()))
        #print("Song duration:", self.player.duration(), "ms")

    def change_current_time(self):
        pos_ms = self.player.position()
        #print("Position changed:", pos_ms)
        self.currentTimeLabel.setText(formatTime(pos_ms))
