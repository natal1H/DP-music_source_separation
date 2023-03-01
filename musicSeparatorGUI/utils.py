from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QFrame, QSizePolicy
from PyQt5.QtCore import QSize


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
