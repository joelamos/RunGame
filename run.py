import math
import threading

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

from course import Course
from runner import Runner

WIDTH = 1100
HEIGHT = 800

# translation constants
X_TRANSLATION = -2.0
Y_TRANSLATION = -1.0
Z_TRANSLATION = -3.75

# perspective constants
FOV = 45.0
ASPECT = float(WIDTH)/(float(HEIGHT))
Z_NEAR = 0.1
Z_FAR = 100

# game constants
TICKS_PER_SECOND = 30.0
X_VELOCITY = 3/TICKS_PER_SECOND
Z_VELOCITY = 5.8/TICKS_PER_SECOND
JUMP_VELOCITY = 8/TICKS_PER_SECOND
GRAVITY = .65/TICKS_PER_SECOND
ROLL_SPEED = 300.0/TICKS_PER_SECOND
PREPEND_ROWS = 10
APPEND_ROWS = 8

# game variables
keys = {'left': False, 'right': False, 'space': False}
rollingLeft = rollingRight = jumping = False
lastRightAngle = 0
angle = 0
courseNum = 0
courseStart = 0
showCourseTitle = False
won = False

def init():
    global course, runner
    
    Course.loadCourses(PREPEND_ROWS, APPEND_ROWS)
    course = Course.getMasterCourse()
    runner = Runner.getRunner(1.0/3)

    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)

def update():
    global rollingLeft, rollingRight, angle, lastRightAngle, jumping, courseNum, courseStart, showCourseTitle, won

    if math.floor(runner.progress) >= len(course.data[0]) and runner.y >= 0:
        won = True

    isInHole = inHole()

    courseProgress = runner.progress - courseStart
    courseLength = len(Course.courses[courseNum].data[0]) - APPEND_ROWS
    if not isInHole:
        if courseProgress > courseLength + 2 and courseNum + 1 < len(Course.courses):
            courseNum += 1
            courseStart = runner.progress + APPEND_ROWS - 5
            course.bottomSide = 2
        elif courseProgress < 8:
            showCourseTitle = True
        else:
            showCourseTitle = False

    if rollingLeft or rollingRight:
        if rollingLeft:
            angle = min(angle + ROLL_SPEED, lastRightAngle + 90)
            if angle == lastRightAngle + 90:
                lastRightAngle = angle
                rollingLeft = False
                runner.x = 4 - runner.y - runner.size
                runner.y = 0
                course.bottomSide += 1 if course.bottomSide + 1 < 4 else -3
        elif rollingRight:
            angle = max(angle - ROLL_SPEED, lastRightAngle - 90)
            if angle == lastRightAngle - 90:
                lastRightAngle = angle
                rollingRight = False
                runner.x = runner.y
                runner.y = 0
                course.bottomSide -= 1 if course.bottomSide - 1 >= 0 else -3
    else:
        if isInHole:
            if runner.y < -9 and not won:
                restart(True)
            else:
                runner.dy -= GRAVITY
        else:
            if not jumping:
                if keys['space']:
                    jumping = True
                    runner.dy = JUMP_VELOCITY
                else:
                    runner.dy = 0
            if jumping:
                runner.y = max(0, runner.y)
                runner.dy -= GRAVITY

        runner.progress += Z_VELOCITY
        runner.y += runner.dy
    
        if jumping:
            runner.y = max(0, runner.y)

        if keys['left']:
            minLeft = 0
            if runner.x == minLeft and not isInHole:
                rollingLeft = True
                angle += ROLL_SPEED
            runner.x = runner.x - X_VELOCITY if isInHole else max(minLeft, runner.x - X_VELOCITY)
        elif keys['right']:
            maxRight = 4 - runner.size
            if runner.x == maxRight and not isInHole:
                rollingRight = True
                angle -= ROLL_SPEED
            runner.x = runner.x + X_VELOCITY if isInHole else min(runner.x + X_VELOCITY, maxRight)

    jumping = runner.y > 0

    threading.Timer(1.0/TICKS_PER_SECOND, update).start()

def inHole():
    if runner.y < 0 or runner.progress - runner.size < 0 or runner.progress > len(course.data[0]):
        return True
    if runner.y > 0:
        return False

    sideOffset = course.bottomSide * 4
    minRow = max(0, int(math.floor(runner.progress)))
    maxRow = min(int(math.ceil(runner.progress + runner.size)) - 1, len(course.data[0]) - 1)
    minColumn = int(math.floor(runner.x))
    maxColumn = int(math.ceil(runner.x + runner.size)) - 1

    lowerLeft = course.data[sideOffset + minColumn][minRow]
    lowerRight = course.data[sideOffset + maxColumn][minRow]
    upperLeft = course.data[sideOffset + minColumn][maxRow]
    upperRight = course.data[sideOffset + maxColumn][maxRow]

    return lowerLeft == lowerRight == upperLeft == upperRight == '0'

def draw():
    global rollingLeft, rollingRight

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(FOV, ASPECT, Z_NEAR, Z_FAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glTranslatef(X_TRANSLATION, Y_TRANSLATION, Z_TRANSLATION)

    glPushMatrix()

    # translate course relative to runner position
    glTranslatef(2 - (runner.size / 2) - runner.x, -runner.y, runner.progress)
    rotateCourse()
    course.draw(runner.progress, 40)

    glPopMatrix()

    glPushMatrix()
    glTranslatef(2 - runner.size / 2, 0, 0)
    rotateRunner()
    runner.draw()
    glPopMatrix()

    color = (0.0, 1.0, 0.0)
    font = GLUT_STROKE_ROMAN
    nameLines = [{'text': 'Level ' + str(courseNum + 1),   'font': font, 'fontScale': .30, 'color': color}]
    if Course.courses[courseNum].title:
        nameLines.append(
                 {'text': Course.courses[courseNum].title, 'font': font, 'fontScale': .30, 'color': color})
    doneLine =   {'text': 'You done it',                   'font': font, 'fontScale': .30, 'color': color}

    lines = []

    if showCourseTitle:
        lines += nameLines
    elif runner.progress > len(course.data[0]) + 4 and won:
        lines.append(doneLine)

    drawText(lines)

    glutSwapBuffers()

def drawText(lines):
    if len(lines) == 0:
        return

    setOrthographicProjection()

    glPushMatrix()
    glLoadIdentity()
    
    widths = []
    heights = []
    for line in lines:
        widths.append(getTextWidth(line['text'], line['font'], line['fontScale']))
        heights.append(line['fontScale']*glutStrokeHeight(line['font']))

    maxHeight = max(heights)

    glTranslatef(0, HEIGHT/2.0 + maxHeight/2.0 + len(lines) / 2.0 * maxHeight, 0)
    for i in range(len(lines)):
        r, g, b = line['color']
        glColor3f(r, g, b)
        if i != 0:
            glTranslatef(0, -maxHeight, 0)

        glPushMatrix()
        glTranslatef(WIDTH / 2.0 - widths[i] / 2.0, 0, 0)
        glScalef(lines[i]['fontScale'], lines[i]['fontScale'], lines[i]['fontScale'])
        glutStrokeString(lines[i]['font'], lines[i]['text'])
        glPopMatrix()

    glPopMatrix()

    restorePerspectiveProjection()

def getTextWidth(text, font, multiplier):
    width = 0
    for char in text:
        # used glutStrokeWidth because glutStrokeLength provided inconsistent results
        width += glutStrokeWidth(font, ord(char))
    return multiplier*width

def setOrthographicProjection():
    glMatrixMode(GL_PROJECTION);
    glPushMatrix();
    glLoadIdentity();
    gluOrtho2D(0, WIDTH, 0, HEIGHT);
    glMatrixMode(GL_MODELVIEW);

def restorePerspectiveProjection():
    glMatrixMode(GL_PROJECTION);
    glPopMatrix();
    glMatrixMode(GL_MODELVIEW);

def rotateCourse():
    translateX = runner.x + runner.size / 2
    translateY = runner.y + runner.size / 2

    glTranslatef(translateX, translateY, 0)
    rollAngle = (angle % 90) - (90 if rollingRight else 0)
    glRotatef(rollAngle, 0, 0, 1)
    glTranslatef(-translateX, -translateY, 0)

def rotateRunner():
    translateX = runner.size / 2
    translateY = runner.size / 2

    glTranslatef(translateX, translateY, 0)
    glRotatef(angle, 0, 0, 1)
    glTranslatef(-translateX, -translateY, 0)

def restart(level=True):
    global courseNum, courseStart, won

    won = False
    runner.reset(courseStart + 2 if level else 2)
    if not level:
        courseNum = 0
        courseStart = 0
    course.bottomSide = 2

def specialInput(key, x, y):
    global x_translation, y_translation, z_translation, translation_amt

    if key == GLUT_KEY_LEFT:
        keys['left'] = True
    elif key == GLUT_KEY_RIGHT:
        keys['right'] = True

def specialUp(key, x, y):
    if key == GLUT_KEY_LEFT:
        keys['left'] = False
    elif key == GLUT_KEY_RIGHT:
        keys['right'] = False

def keyUp(key, x, y):
    if key == b" ":
        keys['space'] = False

def keyboard(key, x, y):
    if key == b"r":
        restart(False)
    elif key == b" ":
        keys['space'] = True

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGB | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(WIDTH,HEIGHT)
    glutInitWindowPosition(50,50)

    glutCreateWindow(b'Run')

    glutDisplayFunc(draw)
    glutIdleFunc(draw)
    glutKeyboardFunc(keyboard)
    glutKeyboardUpFunc(keyUp)
    glutSpecialFunc(specialInput)
    glutSpecialUpFunc(specialUp)

    init()
    update()
    glutMainLoop()

if __name__ == "__main__":
    main()
