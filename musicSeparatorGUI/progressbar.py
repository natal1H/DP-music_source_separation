from PyQt5.QtWidgets import QProgressBar
class ProgressBar(QProgressBar):

    def mousePressEvent(self, event):
        super(ProgressBar, self).mousePressEvent(event)
        clicked_x_position = event.x()
        print("Progress bar clicked at X position:", clicked_x_position, "/", self.width())
        percent_x_position = clicked_x_position / self.width()
        print("Progress bar clicked at % X position:", percent_x_position)
        mainWindow = self.parent().parent().parent()
        mainWindow.move_song_to_position(percent_x_position)