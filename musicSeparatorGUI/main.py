from PyQt5.QtWidgets import QApplication, QFrame, QSizePolicy
from PyQt5.QtCore import QSize
from mainWindow import MainWindow

import sys





app = QApplication(sys.argv)

window = MainWindow()
window.show()

# Start the event loop
app.exec()
