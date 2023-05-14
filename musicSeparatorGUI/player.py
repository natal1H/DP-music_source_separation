from PyQt5.QtMultimedia import QMediaPlayer

""" Application for Guitar Sound Separation from Music Recording

    Author:         Natália Holková
    Login:          xholko02
    File:           player.py
    Description:    Modified Media player
"""

class Player(QMediaPlayer):

    def movePositionByMs(self, ms):
        current_position = self.position()
        new_position = max(min(current_position + ms, self.duration()), 0)
        self.setPosition(new_position)
