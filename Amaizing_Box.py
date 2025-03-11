from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

# Global variables
width, height = 800, 600
points = []
blinking = False
frozen = False
speed_factor = 0.01


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.dx = random.choice([-1, 1]) * random.uniform(0.01, 0.02)
        self.dy = random.choice([-1, 1]) * random.uniform(0.01, 0.02)
        self.color = [random.random(), random.random(), random.random()]
        self.blink_state = True

    def move(self):
        if not frozen:
            self.x += self.dx * speed_factor
            self.y += self.dy * speed_factor

            # Collision detection (bouncing)
            if self.x > 1 or self.x < -1:
                self.dx *= -1
            if self.y > 1 or self.y < -1:
                self.dy *= -1

    def draw(self):
        if blinking and not self.blink_state:
            return
        glColor3f(*self.color)
        glBegin(GL_POINTS)
        glVertex2f(self.x, self.y)
        glEnd()

    def toggle_blink(self):
        self.blink_state = not self.blink_state


def display():
    glClear(GL_COLOR_BUFFER_BIT)
    for point in points:
        point.draw()
    glutSwapBuffers()


def idle():
    if not frozen:
        for point in points:
            point.move()
            if blinking:
                point.toggle_blink()
    glutPostRedisplay()
    time.sleep(0.05)


def mouse(button, state, x, y):
    global blinking
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN and not frozen:
        # Generate a new point
        px = (x / width) * 2 - 1
        py = -((y / height) * 2 - 1)
        points.append(Point(px, py))
    elif button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not frozen:
        # Toggle blinking
        blinking = not blinking


def keyboard(key, x, y):
    global speed_factor, frozen, blinking
    if key == b' ':  # Spacebar key
        frozen = not frozen
        if frozen:
            blinking = False  # Turn blinking off when frozen
    elif key == GLUT_KEY_UP and not frozen:
        speed_factor += 0.01  # Increase speed
    elif key == GLUT_KEY_DOWN and not frozen:
        speed_factor = max(0.01, speed_factor - 0.01)  # Decrease speed


def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-1, 1, -1, 1)
    glPointSize(10)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(width, height)
    glutCreateWindow(b"Task 2: Amazing Box")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutMouseFunc(mouse)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(keyboard)
    glutMainLoop()


if __name__ == "__main__":
    main()
