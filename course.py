import math
import os
import re

from OpenGL.GL import *


class Course(object):

    courses = []

    def __init__(self, data, number=0, title=None, prependRows=0, appendRows=0):
        self.data = data
        self.title = title
        self.number = number
        self.bottomSide = 2

        for i in range(len(data)):
            data[i] = '1'*prependRows + data[i] + '1'*appendRows

    def expand(self, position, rows):
        position = int(position) + 1
        for i in range(16):
            self.data[i] = self.data[i][0:position] + '1'*rows + self.data[i][position:]

    def appendCourse(self, course):
        for i in range(16):
            self.data[i] += course.data[i]

    def draw(self, progress, rowsToDraw):
        distanceMultiplier = .5
        for i in range(4):
            side = (self.bottomSide + i - 2) % 4
            glPushMatrix()

            if i == 0: # top
                glTranslate(4, 4, 0)
                glRotatef(180, 0, 0, 1)
            elif i == 1: # right
                glTranslate(4, 0, 0)
                glRotatef(90, 0, 0, 1)
            elif i == 3: # left
                glTranslate(0, 4, 0)
                glRotatef(-90, 0, 0, 1)

            minRow = max(0, int(math.floor(progress)) - 5)
            maxRow = int(min(len(self.data[0]), minRow + rowsToDraw))

            for column in range(4):
                lastZPosition = -minRow
                for row in range(minRow, maxRow):
                    distance = row - (progress + 1)
                    minDistance = rowsToDraw - ((progress + 1) - minRow)
                    distanceMultiplier = self._mapRange(distance, 0, rowsToDraw - minDistance, 0, 2)
                    if not distanceMultiplier or distanceMultiplier < 0:
                        distanceMultiplier = 0

                    nearZ = lastZPosition
                    farZ = lastZPosition - (1+distanceMultiplier*distance)
                    lastZPosition = farZ

                    if self.data[side*4 + column][row] == '1':
                        sideColorDifference = (3 - side)*.02
                        distance = row - progress + 3
                        cutoff = 20
                        darken = min(distance, cutoff)*.03 + max(distance-cutoff, 0)*.02
                        darken = distance*self._mapRange(distance, 0, rowsToDraw, .03, 10.0/rowsToDraw)
                        color = 1 - darken - sideColorDifference
                        glColor3f(color, 0, 0)

                        glBegin(GL_QUADS)
                        glVertex3f(column, 0, nearZ)
                        glVertex3f(column+1, 0, nearZ)
                        glVertex3f(column+1, 0, farZ)
                        glVertex3f(column, 0, farZ)
                        glEnd()
            glPopMatrix()

    @staticmethod
    def loadCourses(prependRows, appendRows):
        Course.courses = []
        for filename in os.listdir('courses'):
            lines = [line.rstrip('\n') for line in open(os.path.join('courses', filename))]
            matches = re.match('(-?[0-9]+(?:[.][0-9]+)?)(?: - ([^\.]*))?(?:\..+)?', filename)
            try:
                courseTitle = matches.group(2)
            except IndexError:
                courseTitle = None
            courseData = lines[0:4] + lines[5:9] + lines[10:14] + lines[15:19]
            course = Course(courseData, matches.group(1), courseTitle, prependRows, appendRows)
            Course.courses.append(course)
        Course.courses = sorted(Course.courses, key=lambda c: float(c.number))

    @staticmethod
    def getMasterCourse():
        masterData = ['' for _ in range(16)]
        for course in Course.courses:
            for i in range(16):
                masterData[i] += course.data[i]
        return Course(masterData, 'Master Course')

    def _mapRange(self, value, oldMin, oldMax, newMin, newMax):
        try:
            leftSpan = oldMax - oldMin
            rightSpan = newMax - newMin
            valueScaled = float(value - oldMin) / float(leftSpan)
            return newMin + (valueScaled * rightSpan)
        except:
            return None
