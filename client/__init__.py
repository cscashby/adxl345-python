import urllib
from Game import Game

def getGame():
    return currentGame

def resetGame(gameName):
    global currentGame
    currentGame = Game(gameName)

resetGame("")
