from PyQt5.QtWidgets import QProgressBar

""" Application for Guitar Sound Separation from Music Recording

    Author:         Natália Holková
    Login:          xholko02
    File:           progressbar.py
    Description:    Modified progress bar
"""
class ProgressBar(QProgressBar):

    def mousePressEvent(self, event):
        super(ProgressBar, self).mousePressEvent(event)
        clicked_x_position = event.x()
        percent_x_position = clicked_x_position / self.width()
        mainWindow = self.parent().parent().parent()
        mainWindow.move_song_to_position(percent_x_position)