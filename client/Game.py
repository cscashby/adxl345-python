SCORE_TIMEADDITION = 0.1

GAME_NONE = 0
GAME_WAITING = 1
GAME_RUNNING = 2

class Game():
    def __init__( self ):
        self.score = 0.0
        self.state = GAME_NONE

    def setUser( self, user ):
        self.user = user
