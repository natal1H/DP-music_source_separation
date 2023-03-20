from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtCore import Qt

# TODO: ref
# https://stackoverflow.com/questions/63232236/how-qmediaplayer-setposition-works-for-mp3

class Player(QMediaPlayer):
    _delayedPos = 0

    def setPosition(self, pos):
        super().setPosition(pos)
        if pos and not self.isSeekable():
            self._delayedPos = pos
            try:
                # ensure that the connection is done only once
                self.seekableChanged.connect(self.delaySetPosition, Qt.UniqueConnection)
            except:
                pass
        else:
            self._delayedPos = 0

    def delaySetPosition(self, seekable):
        if seekable:
            self.setPosition(self._delayedPos)
        try:
            # just to be safe, in case the media changes before the previous one
            # becomes seekable
            self.seekableChanged.disconnect(self.delaySetPosition)
        except:
            pass

    def movePositionByMs(self, ms):
        current_position = self.position()
        new_position = max(min(current_position + ms, self.duration()), 0)
        self.setPosition(new_position)
