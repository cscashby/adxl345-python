from constants import *
from util import urlPost

SCORE_TIMEADDITION = 0.1

GAME_NONE = 0
GAME_WAITING = 1
GAME_RUNNING = 2

class Game():
    def __init__( self, gameName ):
        self.score = 0.0
        self.state = GAME_NONE
        self.gameName = gameName

    def setUser( self, user ):
        self.user = user

    def setGameName( self, gameName ):
        self.gameName = gameName

    def save(self):
        data = {
            "gameName" : self.gameName,
            "score" : self.score,
            "userID" : self.user.id,
        }

        post = urlPost(SERVER_URL + "game/new", data)

        if post != "":
            print "Error returned by server: {}".format(post)
