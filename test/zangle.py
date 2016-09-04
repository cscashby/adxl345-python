#!/usr/bin/python
# ADXL345 Python example 
#
# author:  Jonathan Williamson
# license: BSD, see LICENSE.txt included in this package
# 
# This is an example to show you how to use our ADXL345 Python library
# http://shop.pimoroni.com/products/adafruit-triple-axis-accelerometer

from adxl345 import ADXL345
import math
  
adxl345 = ADXL345()
    
axes = adxl345.getAxes(True)
print "ADXL345 on address 0x%x:" % (adxl345.address)
print "   x = %.3fG" % ( axes['x'] )
print "   y = %.3fG" % ( axes['y'] )
print "   z = %.3fG" % ( axes['z'] )

p = math.degrees(math.acos(abs(axes['z'] / math.sqrt(axes['x']**2+axes['y']**2+axes['z']**2))))

# Tilt angle given by cos p = z/sqrt(x+y+z)
# See http://cache-uat.freescale.com/files/sensors/doc/app_note/AN3461.pdf eqn 55
print "   p = %.3fdeg" % ( p )
