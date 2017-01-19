import json
import urllib
from constants import *
from util import urlPost

debug = False

def findUser(email = "", initials = ""):
    if email != "":
        out = urlPost(SERVER_URL + "user/exists?email={}".format(email))
    elif initials != "":
        out = urlPost(SERVER_URL + "user/exists?initials={}".format(initials))
    else:
        return False

    # Returns null string if no user returned
    if out == "":
        return False
    else:
        return parseUser(json.loads(out))

def parseUser(u):
    if debug:
        print u
    return User(u['name'], u['email'], u['initials'], u['id'])

class User(object):
    def __init__( self, userName, email, initials = "", id=None ):
        self.userName = userName
        self.email = email
        self.initials = initials
        self.id = id

    def save(self):
        if self.id == None:
            data = {
                "name" : self.userName,
                "email" : self.email,
                "initials" : self.initials,
            }

            post = urlPost(SERVER_URL + "user/new", data)

            if post != "":
                print "Error returned by server: {}".format(post)
            else:
                # Populate our ID back from DB now the user exists
                self.id = findUser(email = self.email).id
        else:
            print "Attempted, and refused to save User with ID: {}".format(self.id)
