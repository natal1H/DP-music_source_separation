from PyQt5.QtWidgets import QPushButton, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar, QFrame
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor, QIcon
from utils import changeWidgetColor


class Track(QWidget):
    def __init__(self, name, imageUrl="img/tmp_soundwave.png"):
        super().__init__()

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

        trackName = QLabel(name)
        trackName.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        muteButton = QPushButton()
        muteButton.setFixedSize(QSize(20, 20))
        muteButton.setIcon(QIcon('img/mute_icon.png'))
        muteButton.setStyleSheet("background-color: #D9D9D9; border: none;")

        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setFormat("")
        progress_bar.setValue(30)  # todo - temporary
        progress_bar.setFixedSize(QSize(1020, 90))
        progress_bar.setStyleSheet(f"QProgressBar {{background-image : url({imageUrl}); border : 1px solid #5F5F5F;}}"
                                   "QProgressBar::chunk {background : rgba(0, 255, 0, 100);}")

        # Add widgets to layouts
        infoLayout.addWidget(trackName)
        infoLayout.addWidget(muteButton, alignment=Qt.AlignHCenter)
        infoFrame.setLayout(infoLayout)
        mainLayout.addWidget(infoFrame)
        mainLayout.addWidget(progress_bar)

        self.setLayout(mainLayout)
        mainLayout.addStretch(1)  # adds a spacer that expands horizontally from the left to the right

        # Set fixed height
        self.setFixedHeight(90)
