from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from utils import changeWidgetColor


class StatusBar(QWidget):
    def __init__(self):
        super().__init__()

        changeWidgetColor(self, QColor("#E8E8E8"))

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)  # Left, top, right, bottom
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Set fixed height
        self.setFixedHeight(30)

    def change_text(self, new_text):
        self.label.setText(new_text)
