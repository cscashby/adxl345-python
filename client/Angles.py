import threading
import time
import datetime
import urllib
import Game
from constants import *
from client import getGame, resetGame

LOCK_ANGLES = threading.Lock()

ANGLE_COLORS = { 0: RGBA_GREEN, 1: RGBA_ORANGE, 10: RGBA_RED }
ANGLE_SCORES = { 0: +0.1, 1: -0.1, 2: -0.2, 4: -0.3, 6: -0.4, 8: -0.5, 10: -0.6 }

ANGLE_WAITTIME = 0.1

class Angles(threading.Thread):
    # TODO: Handle timeouts better - currently if the server has hung then the app hangs...
    def __init__( self, url ):
        threading.Thread.__init__(self)
        self.calibrate_angle = 0.0
        self.link = url
        self.daemon = True
        self.update()
        self.paused = False
        self.setStartTime()
        self.tilt = 0

    def run(self):
        while True:
            if not self.isPaused():
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
        #print "Tilt: %.2f" % self.tilt
        if getGame().state == Game.GAME_RUNNING:
            getGame().score = getGame().score + Game.SCORE_TIMEADDITION
            getGame().score = getGame().score + self.getScore()
            getGame().duration = self.getDuration()
        #print "Game Score: %.2f" % getGame().score
        #print "Score: %.2f" % self.getScore()
        LOCK_ANGLES.release()

    def setStartTime(self):
        self.startTime = datetime.datetime.now()

    def getDuration(self):
        return (datetime.datetime.now() - self.startTime).total_seconds()

    def getColor(self):
        for angle, color in iter(sorted(ANGLE_COLORS.iteritems(), reverse=True)):
            if self.getAngle() >= angle:
                return color
        return RGBA_WHITE

    def getScore(self):
        for angle, score in iter(sorted(ANGLE_SCORES.iteritems(), reverse=True)):
            if self.getAngle() >= angle:
                return score
        return 0

    def calibrate(self):
        self.calibrate_angle = self.tilt

    def getAngle(self):
        return self.tilt - self.calibrate_angle

    def isPaused(self):
        return self.paused

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False
