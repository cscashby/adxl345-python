from Game import Game

def getGame():
    return currentGame

def resetGame():
    global currentGame
    currentGame = Game()

resetGame()
