#!/usr/bin/python
import web
import math
import json
from sqlite3 import IntegrityError
from adxl345 import ADXL345

debug = True
DB_FILENAME = "db/trim-it-right.db"

urls = (
    '/', 'Index',
    '/user/(.+)', 'User',
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
    return math.degrees(math.acos(abs(z / math.sqrt(x**2+y**2+z**2))))

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

        return str(get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)) + " " + \
            str(get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)) + " " + \
            str(get_tilt(axes['x'], axes['y'], axes['z']))

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
            if "initials" in params:
                self.initials = params.initials
            else:
                raise WebError("No initials: Can't search for user")
            try:
                user = self.db.select("user", where="initials='{}'".format(self.initials))[0]
            except IndexError:
                return ""
            self.name = user.name
            self.email = user.email
            return self.to_JSON()
        else:
            return "unknown"

    def __init__(self):
        self.db = openDB()

    def to_JSON(self):
        o = {
            "initials": self.initials,
            "email": self.email,
            "name": self.name
        }
        return json.dumps(o, sort_keys=True, indent=4)

class WebError(web.HTTPError):
    def __init__(self, errorString):
        status = "400 Bad Request"
        headers = {'Content-Type': 'text/html'}
        data = "<h1>Bad Request</h1><p>" + errorString + "</p>"
        if debug:
            print "Web error 400: " + errorString
        web.HTTPError.__init__(self, status, headers, data)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
