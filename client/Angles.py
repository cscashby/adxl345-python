import threading
import urllib
from Game import Game
LOCK_ANGLES = threading.Lock()

class Angles(threading.Thread):
    # TODO: Handle timeouts better - currently if the server has hung then the app hangs...
    def __init__( self, url ):
        threading.Thread.__init__(self)
        self.link = url
        self.daemon = True
        self.update()

    def run(self):
        global paused
        while True:
            if not paused:
                self.update()
            time.sleep(ANGLE_WAITTIME)
    
    def update(self):
        LOCK_ANGLES.acquire()
        f = urllib.urlopen(self.link)
        myfile = f.read()
        angles = myfile.split(" ")
        self.x = float(angles[0])
        self.y = float(angles[1])
        # This version is for constrained tilt (i.e. pitch only)
        self.tilt = abs(float(angles[1]))
        currentGame.score = currentGame.score + Game.SCORE_TIMEADDITION
        currentGame.score = currentGame.score + self.getScore()
        LOCK_ANGLES.release()

    def getColor(self):
        for angle, color in iter(sorted(ANGLE_COLORS.iteritems(), reverse=True)):
            if self.tilt >= angle:
                return color
        return RGBA_WHITE

    def getScore(self):
        for angle, score in iter(sorted(ANGLE_SCORES.iteritems(), reverse=True)):
            if self.tilt >= angle:
                return score
        return 0