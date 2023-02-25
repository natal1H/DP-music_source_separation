from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, \
    QWidget, QHBoxLayout, QVBoxLayout, QSlider, QLabel
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QPalette, QColor

import sys

def changeWidgetColor(widget, color):
    widget.setAutoFillBackground(True)
    palette = widget.palette()
    palette.setColor(QPalette.Window, color)
    widget.setPalette(palette)

class Toolbar(QWidget):
    def __init__(self):
        super().__init__()

        # Fill with color to see borders
        changeWidgetColor(self, QColor("red"))

        layout = QHBoxLayout()

        # Play/Pause button
        playPauseButton = QPushButton("Play/Pause")

        # Jump to beginning button
        jumpToBeginningButton = QPushButton("To Beginning")

        # Jump to end button
        jumpToEndButton = QPushButton("To End")

        # Split button
        splitButton = QPushButton("SPLIT")

        # Master volume slider, volume icon & labels
        volumeSlider = QSlider(Qt.Horizontal)
        volumeSlider.setRange(0, 100)
        volumeSlider.setSingleStep(1)

        volumeIcon = QLabel()
        volumeIcon.setFixedWidth(25)
        volumeIcon.setFixedHeight(25)
        #volumeIcon.setProperty("color", "green")
        volumeIcon.setStyleSheet("background: green")

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
        changeWidgetColor(self, QColor("blue"))

        # Set fixed height
        self.setFixedHeight(20)


class Track(QWidget):
    def __init__(self, name):
        super().__init__()

        # Fill with color to see borders
        changeWidgetColor(self, QColor("yellow"))

        mainLayout = QHBoxLayout()  # Main horizontal layout

        # Left part with information
        infoWidget = QWidget()
        infoLayout = QVBoxLayout()
        trackName = QLabel(name)

        # Add widgets to layouts
        infoLayout.addWidget(trackName)
        infoWidget.setLayout(infoLayout)
        mainLayout.addWidget(infoWidget)

        self.setLayout(mainLayout)

        # Set fixed height
        self.setFixedHeight(90)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Music Separator")

        layout = QVBoxLayout()

        toolbar = Toolbar()
        timeline = Timeline()
        mixture_track = Track("Mixture")

        layout.addWidget(toolbar)
        layout.addWidget(timeline)
        layout.addWidget(mixture_track)
        layout.addStretch(1)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

# Start the event loop
app.exec()