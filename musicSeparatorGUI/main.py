from PyQt5.QtWidgets import QApplication
from mainWindow import MainWindow
from player import Player
import tempfile
import sys

""" Application for Guitar Sound Separation from Music Recording

    Author:         Natália Holková
    Login:          xholko02
    File:           main.py
    Description:    Starting point for the GUI application 
"""


# The main application
class Application(QApplication):

    def __init__(self, args):
        QApplication.__init__(self, args)
        self.temp_dir = tempfile.TemporaryDirectory()
        self.player = Player()

    def clean_up(self):
        self.temp_dir.cleanup()
        self.player.stop()


# Start Qt event loop
if __name__ == '__main__':
    app = Application(sys.argv)
    app.aboutToQuit.connect(app.clean_up)

    window = MainWindow(app.temp_dir, app.player)
    window.show()

    app.exec_()
