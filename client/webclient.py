import sys
import threading
import time
import json
import web
import web.form as form
import web.http as http
from User import *
from Game import *
from util import urlPost
from client import getGame, resetGame

##################################################################################
## Web server for display / game functionality
##################################################################################
form_finduser = form.Form(
    form.Textbox('email', description="Email Address"),
    form.Button('Search/New'),
)
def form_newuser(email):
    return form.Form(
        form.Textbox('email', description="Email Address", value = email),
        form.Textbox('initials', description="Initials"),
        form.Textbox('userName', description="Name"),
        form.Button('Add User'),
)
form_startconfirm = form.Form(
    form.Button("Start"),
    form.Button("Cancel"),
)
form_stopgame = form.Form(
    form.Button("Cancel"),
    form.Button("Finish"),
)
render = web.template.render('templates/', base="base_template")

class Index:
    def GET(self):
        return "Nothing to see here, bye"

class GameStatus:
    def GET(self, action):
        if action == "control":
            body = ""
            if getGame().state == GAME_RUNNING:
                body = "Game running for {}".format(getGame().user.userName)
                f = form_stopgame()
            else:
                f = form_finduser()
            return render.trimitright_form(f, "Game control", body)
        if action == "start":
            body = "Do you want to start a new game for {}?".format(getGame().user.userName)
            f = form_startconfirm()
            return render.trimitright_form(f, "Start game", body)
    def POST(self, action):
        if action == "control":
            formheading = "Game control"
            body = ""
            params = web.input()
            f = form_finduser()
            if not f.validates():
                return render.trimitright_form(f, formheading, body)
            else:
                if 'email' in params:
                    email = params.email
                    user = findUser(email=email)
                    if not user:
                        web.seeother("/user/new?{}".format(http.urlencode({'email':email})))
                        return
                    else:
                        stageGame(user)
                        web.seeother("/game/start")
                        return
                elif 'Cancel' in params:
                    resetGame(getGame().gameName)
                    getGame().state = GAME_NONE
                elif 'Finish' in params:
                    getGame().save()
                    resetGame(getGame().gameName)
                    getGame().state = GAME_NONE
        
            web.seeother("/game/control")
            return
        if action == "start":
            params = web.input()
            if params and 'Start' in params:
                getGame().state = GAME_RUNNING
            web.seeother("/game/control")
            return

class UserForm:
    def GET(self, action):
        if action == "new":
            params = web.input()
            formheading = "Create new user"
            body = ""
            if params and 'email' in params:
                f = form_newuser(params.email)
                return render.trimitright_form(f, formheading, body)
            else:
                return "No email parameter"
    def POST(self, action):
        params = web.input()
        if action == "new":
            if 'initials' in params and 'userName' in params:
                email = params.email                
                initials = params.initials
                userName = params.userName
                user = User(userName, email, initials)
                user.save()
                stageGame(user)
                web.seeother("/game/start")
                return
            else:
                return "Insufficient parameters"

def stageGame(user):
    # We set the user in the game, but don't start it until
    # the user hits the big red go button (tm)
    resetGame(getGame().gameName)
    getGame().setUser(user)

def startWeb():
    urls = (
        '/', 'Index',
        '/game/(.+)', 'GameStatus',
        '/user/(.+)', 'UserForm'
    )
    app = web.application(urls,globals())
    t = threading.Thread(target=app.run)
    t.setDaemon(True)
    t.setName('web-thread')
    t.start()
