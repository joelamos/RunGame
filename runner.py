from OpenGL.GL import *


class Runner(object):

    runner = None

    def __init__(self, size):
        self.size = size + 0.0
        self.reset(2)

    def reset(self, progress):
        self.progress = progress
        self.x = 2 - self.size / 2
        self.y = 0
        self.dy = 0

    @staticmethod
    def getRunner(size):
        if Runner.runner == None:
            Runner.runner = Runner(size)
        return Runner.runner

    def draw(self):
        OpenGL.GL.glBegin(GL_QUADS)

        glColor3f(0.0, 0.0, 1.0)
        # top
        glVertex3f(self.size, self.size, 0)
        glVertex3f(0, self.size, 0)
        glVertex3f(0, self.size, -self.size)
        glVertex3f(self.size, self.size, -self.size)

        glColor3f(1.0,1.0,0.0)
        # bottom
        glVertex3f(self.size, 0, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(0, 0, -self.size)
        glVertex3f(self.size, 0, -self.size)

        glColor3f(0.0, 1.0, 0.0)
        # front
        glVertex3f(self.size, self.size, 0)
        glVertex3f(0, self.size, 0)
        glVertex3f(0, 0, 0)
        glVertex3f(self.size, 0, 0)

        glColor3f(0.0, 1.0, 1.0)
        # left side
        glVertex3f(0, self.size, -self.size) 
        glVertex3f(0, self.size, 0)
        glVertex3f(0, 0, 0) 
        glVertex3f(0, 0, -self.size)

        glColor3f(1.0,0.0,1.0)
        #right side
        glVertex3f(self.size, self.size, 0) 
        glVertex3f(self.size, self.size, -self.size)
        glVertex3f(self.size, 0, -self.size)
        glVertex3f(self.size, 0, 0)

        glEnd()
