#!/usr/bin/python

import pygame
import urllib
import sys
import threading
import time
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from math import radians
from pygame.locals import *

SERVER_URL = "http://pi-dir:8080/"
# This helps my tiny brain
GRID_MINX = -2
GRID_MAXX = 2
GRID_MINY = -1
GRID_MAXY = 1
GRID_MINZ = -1
GRID_MAXZ = 1
COLOR_WHITE = (1.0, 1.0, 1.0)
COLOR_BLACK = (.0, .0, .0)
COLOR_BLUE = (.5, .5, .7)
# RGBA format for Font.render
RGBA_WHITE = (255,255,255,255)
RGBA_BLACK = (0,0,0,255)
RGBA_RED = (255,0,0,255)
RGBA_ORANGE = (255,128,0,255)
RGBA_GREEN = (0,255,0,255)
TEXTORIGIN_ANGLE = (0,GRID_MINY - 0.52,GRID_MAXZ)
TEXTORIGIN_GAMENAME = (GRID_MINX,GRID_MINY - 0.46,GRID_MAXZ)
TEXTORIGIN_INPUTS = (0, 0.1, GRID_MAXZ/2)
TEXTOFFSET_INPUTS = (0, -0.3, 0)
ANGLE_WAITTIME = 0.1

ANGLE_COLORS = { 0: RGBA_GREEN, 1: RGBA_ORANGE, 10: RGBA_RED }
ANGLE_SCORES = { 0: +0.1, 1: -0.1, 2: -0.2, 4: -0.3, 6: -0.4, 8: -0.5, 10: -0.6 }

currentUser = "No current game"
currentScore = 0.0

debug = True

paused = False

def resize(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width) / height, 0.001, 10.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0.0, 0.0, 5.0,
              0.0, 0.0, 0.0,
              0.0, 1.0, 0.0)

def init():
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_BLEND)
    glEnable(GL_POLYGON_SMOOTH)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0));

def getScreenCoords(position):
    model = glGetDoublev(GL_MODELVIEW_MATRIX)
    proj = glGetDoublev(GL_PROJECTION_MATRIX)
    view = glGetIntegerv(GL_VIEWPORT)
    return gluProject(position[0], position[1], position[2], model, proj, view)

def drawText(position, textString, size, centered = True, color = RGBA_WHITE, background = RGBA_BLACK):     
    font = pygame.font.Font (None, size)
    textSurface = font.render(textString, True, color, background)     
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    # Size is in window coordinates, so work in that system     
    screenpos = getScreenCoords(position)
    if centered:
        textpos = (screenpos[0] - (textSurface.get_width()/2), screenpos[1], screenpos[2])
    else:
        textpos = (screenpos[0], screenpos[1], screenpos[2])
    glWindowPos3d(*textpos)     
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def exit():
    pygame.quit()
    sys.exit(0)

def getText(origin, titleText):
    inputting = True
    inputValue = ""
    while inputting:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        drawText(origin, titleText, 32)
        drawText(np.add(origin,TEXTOFFSET_INPUTS), inputValue, 32)
        pygame.display.flip()

        then = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_RETURN:
                inputting = False
                return inputValue
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                inputting = False
                return ""
            if event.type == KEYDOWN and event.key == K_BACKSPACE:
                inputValue = inputValue[:-1]
                break
            if event.type == KEYDOWN:
                inputValue = inputValue + event.unicode

def urlGet(url, params):
    f = urllib.urlopen(url, urllib.urlencode(params))
    out = f.read()
    if out != "":
        print("Error returned by server: " + out)
        return 1
    return 0

def newUser():
    if debug:
        print("New user requested")
    userName = getText(TEXTORIGIN_INPUTS, "New user - initials?")
    print(userName)
    if userName == "":
        return
    email = getText(TEXTORIGIN_INPUTS, "User " + userName + " - email?")
    print(email)
    if email == "":
        return
    initials = getText(TEXTORIGIN_INPUTS, "User " + userName + " - Bottle markings?")
    print(initials)
    if initials == "":
        return
    data = {
        "name": userName,
        "email": email,
        "initials": initials
    }
    urlGet(SERVER_URL + "user/new", data)

def run():
    pygame.init()
    DISPLAY_FLAGS = HWSURFACE | OPENGL | DOUBLEBUF
    SCREEN_SIZE = [0,0]
    info = pygame.display.Info()
    if debug:
        print("Screen width %d, Height %d" % (info.current_w, info.current_h))
    if info.current_w <= 800:
        DISPLAY_FLAGS = DISPLAY_FLAGS | FULLSCREEN | NOFRAME
    else:
        SCREEN_SIZE = [800, 600]
    screen = pygame.display.set_mode( SCREEN_SIZE, DISPLAY_FLAGS )
    newsize = (min(info.current_w, 800), min(info.current_h,600))
    resize(*newsize)
    init()
    clock = pygame.time.Clock()
    backdrop = Backdrop(COLOR_WHITE)
    cube = Cube((0.0, 0.0, 0.0), COLOR_BLUE)

    angles = Angles(SERVER_URL)
    angles.start()

    while True:
        then = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN and (event.key == K_ESCAPE or event.key == K_q):
                exit()
            if event.type == KEYDOWN and event.key == K_n:
                global paused
                paused = True
                newUser()
                paused = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        backdrop.render()
        glPushMatrix()
        glRotate(angles.y, 0, 0, -1)
        cube.render()
        glPopMatrix()
        drawText(TEXTORIGIN_ANGLE, "%.2f" % angles.tilt + u'\N{DEGREE SIGN}', 64, color = angles.getColor())
        drawText(TEXTORIGIN_GAMENAME, currentUser, 32, False)

        pygame.display.flip()

class Backdrop(object):
    def __init__(self, color):
        self.color = color

    def render(self):
        then = pygame.time.get_ticks()
        glColor(self.color)

        glLineWidth(1)
        glBegin(GL_LINES)

        for x in range(-20, 22, 2):
            glVertex3f(x/10.,-1,1)
            glVertex3f(x/10.,-1,-1)
        
        for x in range(-20, 22, 2):
            glVertex3f(x/10.,-1, -1)
            glVertex3f(x/10., 1, -1)
        
        for z in range(-10, 12, 2):
            glVertex3f(-2, -1, z/10.)
            glVertex3f( 2, -1, z/10.)

        for z in range(-10, 12, 2):
            glVertex3f(-2, -1, z/10.)
            glVertex3f(-2,  1, z/10.)

        for z in range(-10, 12, 2):
            glVertex3f( 2, -1, z/10.)
            glVertex3f( 2,  1, z/10.)

        for y in range(-10, 12, 2):
            glVertex3f(-2, y/10., -1)
            glVertex3f( 2, y/10., -1)
        
        for y in range(-10, 12, 2):
            glVertex3f(-2, y/10., -1)
            glVertex3f(-2, y/10., 1)
        
        for y in range(-10, 12, 2):
            glVertex3f(2, y/10., -1)
            glVertex3f(2, y/10., 1)
        
        glEnd()

class Cube(object):

    def __init__(self, position, color):
        self.position = position
        self.color = color

    # Cube information
    num_faces = 6

    vertices = [ (-1.0, -0.05, 0.5),
                 (1.0, -0.05, 0.5),
                 (1.0, 0.05, 0.5),
                 (-1.0, 0.05, 0.5),
                 (-1.0, -0.05, -0.5),
                 (1.0, -0.05, -0.5),
                 (1.0, 0.05, -0.5),
                 (-1.0, 0.05, -0.5) ]

    normals = [ (0.0, 0.0, +1.0),  # front
                (0.0, 0.0, -1.0),  # back
                (+1.0, 0.0, 0.0),  # right
                (-1.0, 0.0, 0.0),  # left
                (0.0, +1.0, 0.0),  # top
                (0.0, -1.0, 0.0) ]  # bottom

    vertex_indices = [ (0, 1, 2, 3),  # front
                       (4, 5, 6, 7),  # back
                       (1, 5, 6, 2),  # right
                       (0, 4, 7, 3),  # left
                       (3, 2, 6, 7),  # top
                       (0, 1, 5, 4) ]  # bottom

    def render(self):
        then = pygame.time.get_ticks()
        glColor(self.color)

        vertices = self.vertices

        # Draw all 6 faces of the cube
        glBegin(GL_QUADS)

        for face_no in xrange(self.num_faces):
            glNormal3dv(self.normals[face_no])
            v1, v2, v3, v4 = self.vertex_indices[face_no]
            glVertex(vertices[v1])
            glVertex(vertices[v2])
            glVertex(vertices[v3])
            glVertex(vertices[v4])
        glEnd()

LOCK_ANGLES = threading.Lock()

class Angles(threading.Thread):
    def __init__( self, url ):
        threading.Thread.__init__(self)
        self.link = url
        self.daemon = True
        self.update()

    def run(self):
        global paused
        while True:
            if not paused:
                self.update()
            time.sleep(ANGLE_WAITTIME)
    
    def update(self):
        LOCK_ANGLES.acquire()
        f = urllib.urlopen(self.link)
        myfile = f.read()
        angles = myfile.split(" ")
        self.x = float(angles[0])
        self.y = float(angles[1])
        # This version is for constrained tilt (i.e. pitch only)
        self.tilt = abs(float(angles[1]))
        LOCK_ANGLES.release()

    def getColor(self):
        for angle, color in iter(sorted(ANGLE_COLORS.iteritems(), reverse=True)):
            if self.tilt >= angle:
                return color
        return RGBA_WHITE

if __name__ == "__main__":
    run()
