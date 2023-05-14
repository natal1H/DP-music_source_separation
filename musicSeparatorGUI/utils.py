import os.path
from PyQt5.QtGui import QPalette
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pydub
import json
from PIL import Image
from pydub import AudioSegment

""" Application for Guitar Sound Separation from Music Recording

    Author:         Natália Holková
    Login:          xholko02
    File:           utils.py
    Description:    Utility functions
"""


def read_mp3(filepath):
    """MP3 to numpy array"""
    sound = pydub.AudioSegment.from_mp3(filepath)
    sound = sound.set_channels(1)
    y = np.array(sound.get_array_of_samples())
    return sound.frame_rate, y


def save_waveform_plot(mp3_path, save_location, width_px=1200, height_px=90):
    """
    Generates the waveform graph and save the figure to chosen location
    """

    signal_framerate, signal = read_mp3(mp3_path)

    time = np.linspace(0, len(signal) / signal_framerate, num=len(signal))

    # set the correct aspect ratio
    dpi = matplotlib.rcParams["figure.dpi"]
    plt.figure(figsize=(width_px / dpi, height_px / dpi))
    plt.axis('off')
    plt.gca()
    plt.margins(x=0)
    plt.plot(time, signal, "k")
    plt.savefig(save_location, pad_inches=0, bbox_inches='tight')
    plt.close()

    image = Image.open(save_location)
    new_image = image.resize((width_px, height_px))
    new_image.save(save_location)


def changeWidgetColor(widget, color):
    widget.setAutoFillBackground(True)
    palette = widget.palette()
    palette.setColor(QPalette.Window, color)
    widget.setPalette(palette)


def formatTime(ms):
    """
    Formats time in ms to minutes:seconds
    """
    seconds = ms / 1000
    minutes = str(int(seconds / 60))
    seconds = int(seconds % 60)
    seconds = "0" + str(seconds) if seconds < 10 else str(seconds)
    return f"{minutes}:{seconds}"


def overlay_tracks(tracks_locations, save_location, save_name="mixed.mp3"):
    """
    Sums multiple audio files into single audio
    """

    audios = []
    for track_location in tracks_locations:
        audios.append(AudioSegment.from_file(track_location))
    mixed = audios[0]
    for audio in audios[1:]:
        mixed = mixed.overlay(audio)
    mixed.export(os.path.join(save_location, save_name), format='mp3')


def load_json_file(json_location):
    f = open(json_location)
    data = json.load(f)
    f.close()
    return data


def save_json_file(data, json_location):
    with open(json_location, 'w') as fp:
        json.dump(data, fp)
