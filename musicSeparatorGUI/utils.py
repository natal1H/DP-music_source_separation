from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QFrame, QSizePolicy
from PyQt5.QtCore import QSize
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pydub


def read_mp3(filepath):
    """MP3 to numpy array"""
    sound = pydub.AudioSegment.from_mp3(filepath)
    sound = sound.set_channels(1)
    y = np.array(sound.get_array_of_samples())
    return sound.frame_rate, y


def save_waveform_plot(mp3_path, save_location):
    signal_framerate, signal = read_mp3(mp3_path)

    time = np.linspace(0, len(signal) / signal_framerate, num=len(signal))

    # set the correct aspect ratio
    dpi = matplotlib.rcParams["figure.dpi"]
    plt.figure(figsize=(1200 / dpi, 90 / dpi))
    plt.axis('off')
    plt.gca()
    plt.margins(x=0)
    plt.plot(time, signal, "k")
    plt.savefig(save_location, pad_inches=0, bbox_inches='tight')
    plt.close()


def changeWidgetColor(widget, color):
    widget.setAutoFillBackground(True)
    palette = widget.palette()
    palette.setColor(QPalette.Window, color)
    widget.setPalette(palette)


def formatTime(ms: int):
    # TODO: add option for hours
    seconds = ms / 1000
    minutes = int(seconds / 60)
    seconds = int(seconds % 60)
    return f"{minutes}:{seconds}"


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
