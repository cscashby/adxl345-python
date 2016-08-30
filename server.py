#!/usr/bin/python
import web
import math
from adxl345 import ADXL345

urls = (
    '/', 'index'
)

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)


class index:
    def GET(self):
	adxl345 = ADXL345()
	axes = adxl345.getAxes(True)
        accel_xout = axes['x']
        accel_yout = axes['y']
        accel_zout = axes['z']

        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        return str(get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))+" "+str(get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
