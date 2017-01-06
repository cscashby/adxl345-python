#!/usr/bin/python
import web
import math
import json
import time
from sqlite3 import IntegrityError
from adxl345 import ADXL345
from JSONUtils import PythonObjectEncoder

HASPHAT = True
try:
    import scrollphat
except ImportError:
    HASPHAT = True

debug = True
DB_FILENAME = "db/trim-it-right.db"

LISTEN_ADDRESS = "0.0.0.0"
LISTEN_PORT = 8180

urls = (
    '/', 'Index',
    '/user/(.+)', 'User',
    '/game/(.+)', 'Game',
)

def openDB():
    db = web.database(dbn='sqlite', db=DB_FILENAME)
    db.query("PRAGMA foreign_keys=ON")
    return db

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

def get_tilt(x,y,z):
    # We want abs here to get a number 0-90 degrees (never 90-180 degrees)
    # This is the 3 dimensional tilt number.
    # Use y rotation for 2 dimensional (i.e. constrained to pitch only)
    deg = math.degrees(math.acos(abs(z / math.sqrt(x**2+y**2+z**2))))
    return deg

class Index:
    def GET(self):
        adxl345 = ADXL345()
        axes = adxl345.getAxes(True)
        accel_xout = axes['x']
        accel_yout = axes['y']
        accel_zout = axes['z']

        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        x = get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
        y = get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
        tilt = get_tilt(axes['x'], axes['y'], axes['z'])

        if HASPHAT:
            a = []
            for i in range(0,11):
                a.append(abs(y))
            scrollphat.graph(a, 0, 75)

        return str(x) + " " + str(y) + " " + str(tilt)

class User:
    def POST(self, action):
        if action == "new":
            params = web.input()
            if "name" in params:
                self.name = params.name
            else:
                raise WebError("No name: Can't create user")
            if "email" in params:
                self.email = params.email
            else:
                raise WebError("No email address: Can't create user")
            if "initials" in params:
                self.initials = params.initials
            else:
                raise WebError("No initials: Can't create user")
            self.score = 0
            if debug:
                print "New user: " + self.name + "\n\t" + self.initials + "\n\t" + self.email + "\n\tScore: 0"
            try:
                self.db.insert("user", email=self.email, initials=self.initials, name=self.name)
            except IntegrityError as err:
                etxt = "{}".format(err)
                print(etxt)
                return etxt
            return ""
        else:
            return "unknown"
    def GET(self, action):
        if action == "exists":
            params = web.input()
            try:
                if "initials" in params:
                    self.initials = params.initials
                    user = self.db.select("user", where="initials='{}'".format(self.initials))[0]
                    self.email = user.email
                else:
                    if "email" in params:
                        self.email = params.email
                        user = self.db.select("user", where="email='{}'".format(self.email))[0]
                        self.initials = user.initials
                    else:
                        raise WebError("No email address or initials: Can't search for user")
            except IndexError:
                return ""
            self.name = user.name
            self.id = user.id
            return self.to_JSON()
        else:
            return "unknown"

    def __init__(self):
        self.db = openDB()

    def to_JSON(self):
        o = {
            "initials": self.initials,
            "email": self.email,
            "name": self.name,
            "id": self.id
        }
        return json.dumps(o, sort_keys=True, indent=4)

QUERY_GAMELISTALL = """
    SELECT u.email, u.name, u.initials, g.date, g.score, g.gameName, g.duration
    FROM game g
    JOIN user u
    WHERE g.user_id = u.id
    ORDER BY g.score DESC, g.date DESC
"""

QUERY_GAMELIST = """
    SELECT u.email, u.name, u.initials, g.date, g.score, g.gameName, g.duration
    FROM game g
    JOIN user u
    WHERE g.user_id = u.id
        AND g.gameName = $gameName
    ORDER BY g.score DESC, g.date DESC
"""

class Game:
    def GET(self, action):
        if action == "getNames":
            gameNames = self.db.query("SELECT DISTINCT gameName FROM game")
            return json.dumps({"gameNames": list(gameNames)}, cls=PythonObjectEncoder)
        if action == "getGames":
            params = web.input()
            if params and "gameName" in params:
                games = self.db.query(QUERY_GAMELIST, vars={'gameName':params['gameName']})
                return json.dumps({"games": list(games)}, cls=PythonObjectEncoder)
            else:
                games = self.db.query(QUERY_GAMELISTALL)
                return json.dumps({"games": list(games)}, cls=PythonObjectEncoder)
    def POST(self, action):
        if action == "new":
            params = web.input()
            if "gameName" in params:
                self.gameName = params.gameName
            else:
                raise WebError("No game name: Can't create game")
            if "score" in params:
                self.score = params.score
            else:
                raise WebError("No score: Can't create game")
            if "duration" in params:
                self.duration = params.duration
            else:
                raise WebError("No duration: Can't create game")
            if "userID" in params:
                self.userID= params.userID
            else:
                raise WebError("No userID: Can't create game")
            if debug:
                print "New game: {}, {}, {}, {}".format(self.gameName, self.score, self.duration, self.userID)
            try:
                self.db.insert("game", gameName=self.gameName, user_id=self.userID, date=web.SQLLiteral("datetime()"), score=self.score, duration=self.duration, success=True)
            except IntegrityError as err:
                etxt = "{}".format(err)
                print(etxt)
                return etxt
            return ""
        else:
            return "unknown"

    def __init__(self):
        self.db = openDB()

class ServerApplication(web.application):
    def run(self, port=8080, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, (LISTEN_ADDRESS, LISTEN_PORT))

class WebError(web.HTTPError):
    def __init__(self, errorString):
        status = "400 Bad Request"
        headers = {'Content-Type': 'text/html'}
        data = "<h1>Bad Request</h1><p>" + errorString + "</p>"
        if debug:
            print "Web error 400: " + errorString
        web.HTTPError.__init__(self, status, headers, data)

def scrollonce(str):
    scrollphat.write_string(str, 11)
    length = scrollphat.buffer_len()
    for i in range(length):
        scrollphat.scroll()
        time.sleep(0.1)

if __name__ == "__main__":
    app = ServerApplication(urls, globals())
    if HASPHAT:
        scrollphat.clear()
        scrollphat.set_brightness(20)
        scrollonce("OK")
    app.run()
