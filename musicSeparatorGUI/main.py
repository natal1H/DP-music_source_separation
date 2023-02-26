from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, \
    QHBoxLayout, QVBoxLayout, QSlider, QLabel, QProgressBar, QFrame, QSizePolicy, QAction
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPalette, QColor, QIcon, QPixmap

import sys


def changeWidgetColor(widget, color):
    widget.setAutoFillBackground(True)
    palette = widget.palette()
    palette.setColor(QPalette.Window, color)
    widget.setPalette(palette)


class QHSeparationLine(QFrame):
    """
    Horizontal separation line
    """
    def __init__(self):
        super().__init__()
        self.setFixedSize(QSize(1120, 20))
        self.setFrameShape(QFrame.HLine)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.setLineWidth(2)
        self.setContentsMargins(15, 0, 15, 0)


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


class Timeline(QWidget):
    def __init__(self):
        super().__init__()

        # Fill with color to see borders
        changeWidgetColor(self, QColor("#E8E8E8"))

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)  # Left, top, right, bottom

        currentTimeLabel = QLabel("Current time")
        totalTimeLabel = QLabel("Total time")
        totalTimeLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(currentTimeLabel)
        layout.addWidget(totalTimeLabel)

        self.setLayout(layout)

        # Set fixed height
        self.setFixedHeight(30)


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
        infoFrame.setObjectName("infoFrame");
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Music Separator")
        self.setMinimumSize(QSize(1120, 670))

        ### Menu
        button_action = QAction("&Open", self)
        button_action.setStatusTip("Open file")
        button_action2 = QAction("Export", self)
        button_action2.setStatusTip("Export song")
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(button_action)
        file_menu.addSeparator()
        file_menu.addAction(button_action2)
        ###


        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Left, top, right, bottom
        layout.setSpacing(0)

        toolbar = Toolbar()
        timeline = Timeline()
        mixture_track = Track("Mixture")
        bass_track = Track("Bass")
        drums_track = Track("Drums")
        guitars_track = Track("Guitars")
        vocals_track = Track("Vocals")
        other_track = Track("Other")

        separatorHorizontal = QHSeparationLine()

        layout.addWidget(toolbar)
        layout.addWidget(timeline)
        layout.addWidget(mixture_track)
        layout.addWidget(separatorHorizontal)
        layout.addWidget(bass_track)
        layout.addWidget(drums_track)
        layout.addWidget(guitars_track)
        layout.addWidget(vocals_track)
        layout.addWidget(other_track)
        layout.addStretch(1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

# Start the event loop
app.exec()
