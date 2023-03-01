from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QSlider, QLabel
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QIcon, QPixmap
from utils import changeWidgetColor

class Toolbar(QWidget):
    def __init__(self):
        super().__init__()

        # Fill with color to see borders
        changeWidgetColor(self, QColor("#CACACA"))

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 0, 0)  # Left, top, right, bottom

        # Play/Pause button
        playPauseButton = QPushButton()
        playPauseButton.setFixedSize(QSize(30, 30))
        playPauseButton.setIcon(QIcon('img/play_icon.png'))
        playPauseButton.setStyleSheet("background-color: #A5A5A5; border-radius: 4px;")

        # Jump to beginning button
        jumpToBeginningButton = QPushButton()
        jumpToBeginningButton.setFixedSize(QSize(30, 30))
        jumpToBeginningButton.setIcon(QIcon('img/to_start.png'))
        jumpToBeginningButton.setStyleSheet("background-color: #A5A5A5; border-radius: 4px;")

        # Jump to end button
        jumpToEndButton = QPushButton()
        jumpToEndButton.setFixedSize(QSize(30, 30))
        jumpToEndButton.setIcon(QIcon('img/to_end.png'))
        jumpToEndButton.setStyleSheet("background-color: #A5A5A5; border-radius: 4px;")

        # Split button
        splitButton = QPushButton("SPLIT")
        splitButton.setFixedSize(QSize(60, 30))
        splitButton.setStyleSheet("color: #414141; background-color: #A5A5A5; border-radius: 4px;")

        # Master volume slider, volume icon & labels
        volumeSlider = QSlider(Qt.Horizontal)
        volumeSlider.setRange(0, 100)
        volumeSlider.setSingleStep(1)

        volumeIcon = QLabel()
        volumeIcon.setFixedSize(QSize(30, 30))
        volumeIcon.setPixmap(QPixmap('img/volume_icon.png'))

        volumeLabelMin = QLabel(str(volumeSlider.minimum()))
        volumeLabelMax = QLabel(str(volumeSlider.maximum()))

        # add all widgets to toolbar in order
        layout.addWidget(playPauseButton)
        layout.addWidget(jumpToBeginningButton)
        layout.addWidget(jumpToEndButton)
        layout.addWidget(splitButton)
        layout.addWidget(volumeIcon)
        layout.addWidget(volumeLabelMin)
        layout.addWidget(volumeSlider)
        layout.addWidget(volumeLabelMax)

        layout.addStretch(1)  # adds a spacer that expands horizontally from the left to the right
        self.setLayout(layout)

        # Set max toolbar height
        self.setFixedHeight(50)