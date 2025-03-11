from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math

# Global variables
width, height = 800, 600
num_raindrops = 3000
raindrops = [(random.uniform(-3, 3), random.uniform(-3, 3)) for _ in range(num_raindrops)]
rain_angle = 0.0  # Initial angle (0 = vertical)
max_angle = 45  # Maximum slant angle
angle_step = 2  # Angle increment for each key press
transition_progress = 0.0  # Tracks the current progress
transition_speed = 0.01  # Speed of transition
current_phase = 0  # Index for the current phase (0-5)
phases = ["morning", "noon", "afternoon", "evening", "midnight", "early_dawn"]

# Sun and moon positions based on phases
celestial_positions = {
    "morning": (-0.8, 0.8),
    "noon": (0.0, 0.9),
    "afternoon": (0.8, 0.8),
    "evening": (-0.8, 0.8),
    "midnight": (0.0, 0.9),
    "early_dawn": (0.8, 0.8),
}

# Converts angle in degrees to radians
def to_radians(angle):
    return angle * math.pi / 180

# (for sun and moon)
def draw_circle(x, y, radius, color):
    glColor3f(*color)
    aspect_ratio = width / height
    glBegin(GL_POLYGON)
    for angle in range(0, 360, 10):
        rad = to_radians(angle)
        glVertex2f(x + radius * math.cos(rad) / aspect_ratio, y + radius * math.sin(rad))
    glEnd()

#sun or moon
def draw_celestial_body():
    x, y = celestial_positions[phases[current_phase]]
    color = (1.0, 1.0, 0.0) if current_phase < 3 else (0.9, 0.9, 1.0)
    draw_circle(x, y, 0.1, color)

# Draw a house for reference
def draw_house():
    # house
    glColor3f(1.0, 0.5, 0.0)
    glBegin(GL_QUADS)
    glVertex2f(-0.5, -0.5)
    glVertex2f(0.5, -0.5)
    glVertex2f(0.5, 0.0)
    glVertex2f(-0.5, 0.0)
    glEnd()

    #roof
    glColor3f(0.7, 0.2, 0.0)
    glBegin(GL_TRIANGLES)
    glVertex2f(-0.55, 0.0)
    glVertex2f(0.55, 0.0)
    glVertex2f(0.0, 0.5)
    glEnd()

   #gate
    glColor3f(0.3, 0.2, 0.1)
    glBegin(GL_QUADS)
    glVertex2f(-0.15, -0.5)
    glVertex2f(0.15, -0.5)
    glVertex2f(0.15, -0.2)
    glVertex2f(-0.15, -0.2)
    glEnd()


# Draw raindrops with slant
def draw_raindrops():
    glColor3f(0.0, 0.0, 1.0)
    angle_radians = to_radians(rain_angle)
    x_offset = math.tan(angle_radians) * 0.05
    glBegin(GL_LINES)
    for x, y in raindrops:
        glVertex2f(x, y)
        glVertex2f(x + x_offset, y - 0.05)
    glEnd()

# Update raindrops' positions
def update_raindrops():
    global raindrops
    angle_radians = to_radians(rain_angle)
    x_offset = math.tan(angle_radians) * 0.02

    for i in range(len(raindrops)):
        x, y = raindrops[i]
        x += x_offset
        y -= 0.02

        # Reset raindrops when out of bounds
        if y < -3 or x < -3 or x > 3:
            x = random.uniform(-3, 3)
            y = 1
        raindrops[i] = (x, y)

# Update background color based on the phase
def update_background_color():
    global transition_progress
    target_progress = current_phase / 5  # Normalize phases to [0.0, 1.0]
    if transition_progress < target_progress:
        transition_progress += transition_speed
        if transition_progress > target_progress:
            transition_progress = target_progress
    elif transition_progress > target_progress:
        transition_progress -= transition_speed
        if transition_progress < target_progress:
            transition_progress = target_progress

def get_background_color():
    if current_phase == 0:  # Morning
        return [0.8, 0.6, 0.3]
    elif current_phase == 1:  # Noon
        return [0.5, 0.7, 1.0]
    elif current_phase == 2:  # Afternoon
        return [0.8, 0.3, 0.3]
    elif current_phase == 3:  # Evening
        return [0.5, 0.4, 0.6]
    elif current_phase == 4:  # Midnight
        return [0.1, 0.1, 0.2]
    elif current_phase == 5:  # Early Dawn
        return [0.3, 0.4, 0.5]

def idle_function():
    update_raindrops()
    update_background_color()
    glutPostRedisplay()

# Keyboard controls
def keyboard(key, x, y):
    global current_phase, rain_angle
    if key == b'\x1b':  # Escape key to exit
        glutLeaveMainLoop()
    elif key == b'n':  # Next phase
        current_phase = (current_phase + 1) % len(phases)
    elif key == b'p':  # Previous phase
        current_phase = (current_phase - 1) % len(phases)

def special_keys(key, x, y):
    global rain_angle
    if key == GLUT_KEY_LEFT:  # Left arrow to increase leftward slant
        rain_angle = max(-max_angle, rain_angle - angle_step)
    elif key == GLUT_KEY_RIGHT:  # Right arrow to increase rightward slant
        rain_angle = min(max_angle, rain_angle + angle_step)

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(*get_background_color(), 1.0)  # Update background color
    draw_house()
    draw_raindrops()
    draw_celestial_body()
    glutSwapBuffers()


glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(width, height)
glutCreateWindow(b"Rain Simulation with Adjustable Slant")
glClearColor(0.0, 0.0, 0.2, 1.0)  # Start in midnight mode
glutDisplayFunc(display)
glutIdleFunc(idle_function)
glutKeyboardFunc(keyboard)
glutSpecialFunc(special_keys)
glutMainLoop()