import sys
import threading
import time
import json
import web
import web.form as form
from User import *
from Game import *
from util import urlPost
from client import getGame, resetGame

##################################################################################
## Web server for display / game functionality
##################################################################################
form_newuser = form.Form(
    form.Textbox('email', description="Email Address"),
    form.Button('Search/New'),
)
form_stopgame = form.Form(
    form.Button("Cancel"),
    form.Button("Finish"),
)
render = web.template.render('templates/')

class Index:
    def GET(self):
        return "Nothing to see here, bye"

class GameStatus:
    def GET(self):
        if getGame().state == GAME_RUNNING:
            print("Game running for {}".format(getGame().user.userName))
            f = form_stopgame()
        else:
            f = form_newuser()
        return render.trimitright_form(f)
    def POST(self):
        params = web.input()
        f = form_newuser()
        if not f.validates():
            return render.trimitright_form(f)
        else:
            if 'email' in params:
                email = params.email
                user = findUser(email=email)
                if not user:
                    # User doesn't exist
                    email = ""
                    print(email)
                    if email == "":
                        return
                    userName = ""
                    print(userName)
                    if userName == "":
                        return
                    
                    user = User(userName, email, initials)
                    user.save()
                    if post != "":
                        print "Error returned by server: {}".format(post)
                resetGame(getGame().gameName)
                getGame().setUser(user)
                getGame().state = GAME_RUNNING
            elif 'Cancel' in params:
                resetGame(getGame().gameName)
                getGame().state = GAME_NONE
            elif 'Finish' in params:
                getGame().save()
                resetGame(getGame().gameName)
                getGame().state = GAME_NONE
        
        web.redirect("/game", '302 Found')

def startWeb():
    urls = (
        '/', 'Index',
        '/game', 'GameStatus',
    )
    app = web.application(urls,globals())
    t = threading.Thread(target=app.run)
    t.setDaemon(True)
    t.setName('web-thread')
    t.start()
