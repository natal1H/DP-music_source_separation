from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from utils import changeWidgetColor

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
