from PyQt5.QtWidgets import QApplication
from mainWindow import MainWindow
import tempfile
import sys


# The main application
class Application(QApplication):

    def __init__(self, args):
        QApplication.__init__(self, args)
        self.temp_dir = tempfile.TemporaryDirectory()
        print(self.temp_dir.name)  # todo remove

    def clean_up(self):
        print('closing')
        self.temp_dir.cleanup()


# Start Qt event loop
if __name__ == '__main__':
    app = Application(sys.argv)
    app.aboutToQuit.connect(app.clean_up)

    window = MainWindow(app.temp_dir)
    window.show()

    app.exec_()
