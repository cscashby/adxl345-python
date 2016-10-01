import sys
import threading
import time
import json
import web
import web.form as form

##################################################################################
## Web server for display / game functionality
##################################################################################
form_newuser = form.Form(
    form.Textbox('initials'),
    form.Button('search/new'),
)
render = web.template.render('templates/')

class Index:
    def GET(self):
        return "Nothing to see here, bye"

class User:
    def GET(self, action):
        if action == "new":
            f = form_newuser()
            return render.trimitright_form(f)
    def POST(self, action):
        global currentUser
        global currentScore
        if action == "new":
            f = form_newuser()
            if not f.validates():
                return render.trimitright_form(f)
            else:
                params = web.input()
                initials = params.initials
                out = urlPost(SERVER_URL + "user/exists?initials={}".format(initials))
                if out == "":
                    # User doesn't exist
                    email = ""
                    print(email)
                    if email == "":
                        return
                    userName = ""
                    print(userName)
                    if userName == "":
                        return
                    data = {
                        "name": userName,
                        "email": email,
                        "initials": initials
                    }
                    post = urlPost(SERVER_URL + "user/new", data)
                    if post != "":
                        print "Error returned by server: {}".format(post)
                    currentUser = data
                    currentScore = 0.0
                    return "game started for " + currentUser['name']
                else:
                    if debug:
                        print out
                    currentUser = json.loads(out)
                    currentScore = 0.0
                    return "game started for " + currentUser['name']

def startWeb():
    urls = (
        '/', 'Index',
        '/user/(.+)', 'User',
    )
    app = web.application(urls,globals())
    t = threading.Thread(target=app.run)
    t.setDaemon(True)
    t.setName('web-thread')
    t.start()
