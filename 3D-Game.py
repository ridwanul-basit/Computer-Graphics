import sys
import random
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

# Game state
player_life = 5
score = 0
bullets_missed = 0
game_over = False
cheat_mode = False

# Player position and rotation
player_pos = [0, 0, 0]
player_rotation = 0
gun_rotation = 0

# Camera settings
camera_distance = 10
camera_angle = 45
camera_height = 3
first_person = False

# Game objects
bullets = []
enemies = []
grid_size = 20

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    
    # Initialize enemies
    for _ in range(5):
        spawn_enemy()
    
    # Lighting setup
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, [1, 1, 1, 0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1, 1, 1, 1])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1])
    glEnable(GL_COLOR_MATERIAL)

def spawn_enemy():
    half = grid_size/2 - 2
    enemies.append({
        'x': random.uniform(-half, half),
        'y': 0.5,
        'z': random.uniform(-half, half),
        'size': random.uniform(0.3, 0.6),
        'growing': True,
        'speed': random.uniform(0.01, 0.03)
    })

def draw_player():
    glPushMatrix()
    glTranslatef(*player_pos)
    glRotatef(player_rotation, 0, 1, 0)
    
    # HEAD - Sphere (size: 0.25 units)
    glPushMatrix()
    glColor3f(0.8, 0.6, 0.4)  # Skin color
    glTranslatef(0, 1.75, 0)  # Position above body
    glutSolidSphere(0.25, 20, 20)
    glPopMatrix()
    
    # BODY - Cuboid (size: 0.5w × 1.0h × 0.3d)
    glPushMatrix()
    glColor3f(0.1, 0.3, 0.8)  # Shirt color
    glTranslatef(0, 1.0, 0)
    glScalef(0.5, 1.0, 0.3)
    glutSolidCube(1.0)
    glPopMatrix()
    
    # LEGS - Two Cylinders
    glPushMatrix()
    glColor3f(0.2, 0.2, 0.2)  # Pants color
    # Left leg
    glPushMatrix()
    glTranslatef(-0.15, 0.5, 0)
    glutSolidCylinder(0.12, 0.8, 10, 10)
    glPopMatrix()
    # Right leg
    glPushMatrix()
    glTranslatef(0.15, 0.5, 0)
    glutSolidCylinder(0.12, 0.8, 10, 10)
    glPopMatrix()
    glPopMatrix()
    
    # ARMS - Two Cylinders
    glPushMatrix()
    glColor3f(0.8, 0.6, 0.4)  # Skin color
    # Left arm
    glPushMatrix()
    glTranslatef(-0.35, 1.25, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidCylinder(0.08, 0.5, 10, 10)
    glPopMatrix()
    
    # Right arm with gun
    glPushMatrix()
    glTranslatef(0.35, 1.25, 0)
    glRotatef(90, 0, 1, 0)
    glutSolidCylinder(0.08, 0.5, 10, 10)
    
    # GUN - Combination of cylinder and cuboid
    glPushMatrix()
    glTranslatef(0, 0, 0.5)  # Position at end of arm
    glRotatef(gun_rotation, 0, 1, 0)  # Gun rotation
    
    # Gun barrel - Cylinder
    glColor3f(0.3, 0.3, 0.3)
    glutSolidCylinder(0.05, 0.7, 10, 10)
    
    # Gun handle - Cuboid
    glColor3f(0.2, 0.2, 0.2)
    glTranslatef(0, -0.1, 0.35)
    glScalef(0.2, 0.15, 0.4)
    glutSolidCube(1.0)
    
    glPopMatrix()  # Gun
    glPopMatrix()  # Right arm
    glPopMatrix()  # Arms
    
    glPopMatrix()  # Player

def draw_enemy(x, y, z, size):
    glPushMatrix()
    glTranslatef(x, y, z)
    
    # Main body - Sphere
    glColor3f(0.2, 0.8, 0.2)
    glutSolidSphere(size, 20, 20)
    
    # Eye - Smaller sphere
    glColor3f(1, 1, 1)
    glTranslatef(0, 0, size)
    glutSolidSphere(size/3, 10, 10)
    
    glPopMatrix()

def draw_bullet(x, y, z):
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1, 1, 0)
    glutSolidCube(0.1)
    glPopMatrix()

def draw_grid():
    cell_size = grid_size / 10
    half = grid_size / 2
    
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    
    # Grid lines
    for i in range(11):
        pos = -half + i*cell_size
        glVertex3f(pos, 0, -half)
        glVertex3f(pos, 0, half)
        glVertex3f(-half, 0, pos)
        glVertex3f(half, 0, pos)
    
    # Boundaries
    glColor3f(0.8, 0.8, 0.8)
    height = 1.0
    for boundary in [(-half, half), (half, half), (-half, -half), (half, -half)]:
        x, z = boundary
        glVertex3f(x, 0, z)
        glVertex3f(x, height, z)
    
    glEnd()

def update_game(value=0):
    global player_life, score, bullets_missed, game_over
    
    if not game_over:
        # Update enemies
        for enemy in enemies[:]:
            # Movement
            dx = player_pos[0] - enemy['x']
            dz = player_pos[2] - enemy['z']
            dist = math.sqrt(dx*dx + dz*dz)
            
            if dist > 0.5:
                enemy['x'] += dx/dist * enemy['speed']
                enemy['z'] += dz/dist * enemy['speed']
            
            # Pulsing effect
            if enemy['growing']:
                enemy['size'] += 0.005
                if enemy['size'] > 0.6:
                    enemy['growing'] = False
            else:
                enemy['size'] -= 0.005
                if enemy['size'] < 0.3:
                    enemy['growing'] = True
            
            # Collision with player
            if dist < 0.8:
                player_life -= 1
                if player_life <= 0:
                    game_over = True
                enemy['x'] = random.uniform(-8, 8)
                enemy['z'] = random.uniform(-8, 8)
        
        # Update bullets
        for bullet in bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['z'] += bullet['dz']
            bullet['distance'] += 0.2
            
            # Check hits
            hit = False
            for enemy in enemies[:]:
                dist = math.sqrt((bullet['x']-enemy['x'])**2 + 
                               (bullet['z']-enemy['z'])**2)
                if dist < enemy['size'] + 0.1:
                    enemies.remove(enemy)
                    spawn_enemy()
                    score += 10
                    hit = True
                    break
            
            if hit:
                bullets.remove(bullet)
            elif bullet['distance'] > 30:
                bullets.remove(bullet)
                bullets_missed += 1
                if bullets_missed >= 10:
                    game_over = True
        
        # Cheat mode
        if cheat_mode:
            global gun_rotation
            gun_rotation += 5
            
            # Auto-fire
            for enemy in enemies:
                angle = math.degrees(math.atan2(
                    enemy['x']-player_pos[0], 
                    enemy['z']-player_pos[2]))
                if abs((player_rotation + gun_rotation - angle) % 360) < 15:
                    fire_bullet()
                    break
    
    glutPostRedisplay()
    glutTimerFunc(16, update_game, 0)

def fire_bullet():
    if game_over:
        return
    
    angle = math.radians(player_rotation + gun_rotation)
    
    # Calculate bullet starting position (from gun barrel)
    bullet_x = player_pos[0] + 0.35 + math.sin(math.radians(player_rotation)) * 0.5
    bullet_z = player_pos[2] + math.cos(math.radians(player_rotation)) * 0.5
    bullet_x -= math.sin(angle) * 0.7  # Adjust for gun length
    bullet_z -= math.cos(angle) * 0.7
    
    bullets.append({
        'x': bullet_x,
        'y': player_pos[1] + 1.25,  # Gun height
        'z': bullet_z,
        'dx': -math.sin(angle) * 0.3,
        'dz': -math.cos(angle) * 0.3,
        'distance': 0
    })

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Camera setup
    if first_person:
        # First-person view from player's eyes
        eye_x = player_pos[0]
        eye_y = player_pos[1] + 1.5  # Eye level
        eye_z = player_pos[2]
        look_x = eye_x - math.sin(math.radians(player_rotation + gun_rotation))
        look_z = eye_z - math.cos(math.radians(player_rotation + gun_rotation))
        gluLookAt(eye_x, eye_y, eye_z, look_x, eye_y, look_z, 0, 1, 0)
    else:
        # Third-person view
        rad = math.radians(camera_angle)
        eye_x = player_pos[0] + camera_distance * math.sin(rad)
        eye_z = player_pos[2] + camera_distance * math.cos(rad)
        gluLookAt(eye_x, camera_height, eye_z, *player_pos, 0, 1, 0)
    
    # Projection
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (glutGet(GLUT_WINDOW_WIDTH)/glutGet(GLUT_WINDOW_HEIGHT)), 0.1, 100)
    glMatrixMode(GL_MODELVIEW)
    
    # Draw scene
    draw_grid()
    draw_player()
    
    for enemy in enemies:
        draw_enemy(enemy['x'], enemy['y'], enemy['z'], enemy['size'])
    
    for bullet in bullets:
        draw_bullet(bullet['x'], bullet['y'], bullet['z'])
    
    # HUD
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, glutGet(GLUT_WINDOW_WIDTH), 0, glutGet(GLUT_WINDOW_HEIGHT))
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glColor3f(1, 1, 1)
    render_text(10, glutGet(GLUT_WINDOW_HEIGHT)-20, f"Lives: {player_life}")
    render_text(10, glutGet(GLUT_WINDOW_HEIGHT)-40, f"Score: {score}")
    render_text(10, glutGet(GLUT_WINDOW_HEIGHT)-60, f"Missed: {bullets_missed}")
    
    if game_over:
        glColor3f(1, 0, 0)
        render_text(glutGet(GLUT_WINDOW_WIDTH)//2-50, glutGet(GLUT_WINDOW_HEIGHT)//2, "GAME OVER")
        glColor3f(1, 1, 1)
        render_text(glutGet(GLUT_WINDOW_WIDTH)//2-70, glutGet(GLUT_WINDOW_HEIGHT)//2-30, "Press R to restart")
    
    if cheat_mode:
        glColor3f(0, 1, 0)
        render_text(glutGet(GLUT_WINDOW_WIDTH)-150, glutGet(GLUT_WINDOW_HEIGHT)-20, "CHEAT MODE")
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glutSwapBuffers()

def render_text(x, y, text):
    glRasterPos2f(x, y)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))

def keyboard(key, x, y):
    global player_rotation, gun_rotation, camera_angle, camera_height
    global cheat_mode, first_person, game_over
    global player_life, score, bullets_missed, player_pos
    
    key = key.decode('utf-8').lower()
    
    if key == 'a': player_rotation += 5
    elif key == 'd': player_rotation -= 5
    elif key == 'w':
        rad = math.radians(player_rotation)
        player_pos[0] -= math.sin(rad) * 0.5
        player_pos[2] -= math.cos(rad) * 0.5
    elif key == 's':
        rad = math.radians(player_rotation)
        player_pos[0] += math.sin(rad) * 0.5
        player_pos[2] += math.cos(rad) * 0.5
    elif key == 'c': cheat_mode = not cheat_mode
    elif key == 'r' and game_over:
        # Reset game
        player_life = 5
        score = 0
        bullets_missed = 0
        game_over = False
        player_pos = [0, 0, 0]
        player_rotation = 0
        gun_rotation = 0
        bullets.clear()
        enemies.clear()
        for _ in range(5): spawn_enemy()
    
    glutPostRedisplay()

def special_keys(key, x, y):
    global camera_angle, camera_height, first_person
    
    if key == GLUT_KEY_LEFT: camera_angle += 5
    elif key == GLUT_KEY_RIGHT: camera_angle -= 5
    elif key == GLUT_KEY_UP: camera_height += 0.5
    elif key == GLUT_KEY_DOWN: camera_height -= 0.5
    
    glutPostRedisplay()

def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        fire_bullet()
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        global first_person
        first_person = not first_person
    
    glutPostRedisplay()

# ... [imports and initializations remain unchanged]

# Add this new function for drawing boundary walls
def draw_boundary_walls():
    wall_height = 2.0
    wall_thickness = 0.2
    half = grid_size / 2

    glColor3f(0.3, 0.3, 0.3)  # Wall color
    glPushMatrix()

    # Front wall (positive Z)
    glPushMatrix()
    glTranslatef(0, wall_height / 2, half)
    glScalef(grid_size, wall_height, wall_thickness)
    glutSolidCube(1.0)
    glPopMatrix()

    # Back wall (negative Z)
    glPushMatrix()
    glTranslatef(0, wall_height / 2, -half)
    glScalef(grid_size, wall_height, wall_thickness)
    glutSolidCube(1.0)
    glPopMatrix()

    # Left wall (negative X)
    glPushMatrix()
    glTranslatef(-half, wall_height / 2, 0)
    glScalef(wall_thickness, wall_height, grid_size)
    glutSolidCube(1.0)
    glPopMatrix()

    # Right wall (positive X)
    glPushMatrix()
    glTranslatef(half, wall_height / 2, 0)
    glScalef(wall_thickness, wall_height, grid_size)
    glutSolidCube(1.0)
    glPopMatrix()

    glPopMatrix()

# Update this function to call wall drawing
def draw_grid():
    cell_size = grid_size / 10
    half = grid_size / 2

    # Grid lines
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    for i in range(11):
        pos = -half + i*cell_size
        glVertex3f(pos, 0, -half)
        glVertex3f(pos, 0, half)
        glVertex3f(-half, 0, pos)
        glVertex3f(half, 0, pos)
    glEnd()

    # Draw boundary walls as 3D objects
    draw_boundary_walls()


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Bullet Frenzy - 3D Game")
    
    init()
    
    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse)
    glutTimerFunc(0, update_game, 0)
    
    glutMainLoop()

if __name__ == "__main__":
    main()