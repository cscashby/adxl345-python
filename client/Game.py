import json
from constants import *
from util import urlPost

SCORE_TIMEADDITION = 0.1

GAME_NONE = 0
GAME_RUNNING = 1
GAME_WAITING = 10

class Game():
    def __init__( self, gameName ):
        self.score = 0.0
        self.state = GAME_NONE
        self.gameName = gameName
        self.duration = 0.0

    def setUser( self, user ):
        self.user = user

    def setGameName( self, gameName ):
        self.gameName = gameName

    def save(self):
        data = {
            "gameName" : self.gameName,
            "score" : self.score,
            "userID" : self.user.id,
            "duration" : self.duration,
        }

        post = urlPost(SERVER_URL + "game/new", data)

        if post != "":
            print "Error returned by server: {}".format(post)

def getNames():
    out = urlPost(SERVER_URL + "game/getNames")
    if out == "":
        return False
    else:
        return json.loads(out)['gameNames']

def getList(gameName):
    if gameName != "":
        out = urlPost(SERVER_URL + "game/getGames?gameName={}".format(gameName))
    else:
        out = urlPost(SERVER_URL + "game/getGames")

    # Returns null string if no list returned
    if out == "":
        return False
    else:
        return json.loads(out)
