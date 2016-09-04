#!/usr/bin/python

import pygame
import urllib
from OpenGL.GL import *
from OpenGL.GLU import *
from math import radians
from pygame.locals import *

SCREEN_SIZE = (0,0)
DISPLAYFLAGS = FULLSCREEN | NOFRAME
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
TEXTORIGIN_ANGLE = (0,GRID_MINY - 0.52,GRID_MAXZ)

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

def drawText(position, textString, size):     
    font = pygame.font.Font (None, size)
    textSurface = font.render(textString, True, (255,255,255,255), (0,0,0,255))     
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    # Size is in window coordinates, so work in that system     
    screenpos = getScreenCoords(position)
    centerpos = (screenpos[0] - (textSurface.get_width()/2), screenpos[1], screenpos[2])
    glWindowPos3d(*centerpos)     
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def run():
    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE, HWSURFACE | OPENGL | DOUBLEBUF | DISPLAYFLAGS)
    info = pygame.display.Info()
    newsize = (info.current_w, info.current_h)
    resize(*newsize)
    init()
    clock = pygame.time.Clock()
    backdrop = Backdrop(COLOR_WHITE)
    cube = Cube((0.0, 0.0, 0.0), COLOR_BLUE)
    
    while True:
        then = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYUP and event.key == K_ESCAPE:
                sys.exit()

        angles = Angles("http://localhost:8080")

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        backdrop.render()
        glPushMatrix()
        glRotate(angles.y, 0, 0, -1)
        cube.render()
        glPopMatrix()
        drawText(TEXTORIGIN_ANGLE, "%.2f" % angles.tilt + u'\N{DEGREE SIGN}', 64)

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

class Angles:
    def __init__( self, url ):
        link = "http://localhost:8080/" # Change this address to your settings
        f = urllib.urlopen(link)
        myfile = f.read()
        angles = myfile.split(" ")
        self.x = float(angles[0])
        self.y = float(angles[1])
        # This version is for constrained tilt (i.e. pitch only)
        self.tilt = abs(float(angles[1]))

if __name__ == "__main__":
    run()
