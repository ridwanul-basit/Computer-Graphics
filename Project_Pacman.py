from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# Camera-related variables
camera_pos = (0, 0, 300)
camera_angle = 0
camera_height = 300
camera_mode = 'third'

# Game state variables
player_pos = [50, 50, 20]  # Player position (x, y, z) in maze
player_angle = 0
life = 5
score = 0
bullets_missed = 0
game_over = False

# Maze and game constants
MAZE_SIZE = 600
WALL_HEIGHT = 50
fovY = 90  # Reduced FOV for maze navigation
BULLET_SPEED = 3
ENEMY_SPEED = 0.5
ENEMY_COUNT = 4
POWERUP_COUNT = 2

# Game objects
bullets = []  # [x, y, z, angle]
enemies = []  # [x, y, z]
powerups = []  # [x, y, z]
last_time = time.time()

# Maze layout: list of [x1, y1, x2, y2, height] for walls
maze_walls = [
    # Outer walls
    [-300, -300, 300, -300, WALL_HEIGHT],  # Bottom
    [-300, 300, 300, 300, WALL_HEIGHT],    # Top
    [-300, -300, -300, 300, WALL_HEIGHT],  # Left
    [300, -300, 300, 300, WALL_HEIGHT],    # Right
    # Inner walls (simple maze layout)
    [-100, -300, -100, 100, WALL_HEIGHT],  # Vertical left
    [100, -100, 100, 300, WALL_HEIGHT],    # Vertical right
    [-300, 0, 0, 0, WALL_HEIGHT],          # Horizontal middle-left
    [100, 100, 300, 100, WALL_HEIGHT],     # Horizontal top-right
]

def init_game():
    """Initialize or reset game state."""
    global player_pos, player_angle, life, score, bullets_missed, game_over, bullets, enemies, powerups, camera_mode, camera_pos, camera_height, camera_angle
    player_pos = [50, 50, 20]
    player_angle = 0
    life = 5
    score = 0
    bullets_missed = 0
    game_over = False
    camera_mode = 'third'
    camera_pos = (0, 0, 300)
    camera_height = 300
    camera_angle = 0
    bullets = []
    enemies = []
    powerups = []
    for _ in range(ENEMY_COUNT):
        spawn_enemy()
    for _ in range(POWERUP_COUNT):
        spawn_powerup()

def spawn_enemy():
    """Spawn an enemy at a random valid position within maze borders."""
    while True:
        x = random.uniform(-290, 290)  # Within maze borders (-300 + 10, 300 - 10)
        y = random.uniform(-290, 290)
        if is_valid_position(x, y, 20) and math.hypot(x - player_pos[0], y - player_pos[1]) > 100:
            enemies.append([x, y, 20])
            break

def spawn_powerup():
    """Spawn a power-up at a random valid position."""
    while True:
        x = random.uniform(-290, 290)
        y = random.uniform(-290, 290)
        if is_valid_position(x, y, 10):
            powerups.append([x, y, 20])
            break

def is_valid_position(x, y, radius):
    """Check if position is valid (no collision with walls)."""
    for wall in maze_walls:
        x1, y1, x2, y2, _ = wall
        if x1 == x2:  # Vertical wall
            if abs(x - x1) < radius and min(y1, y2) - radius < y < max(y1, y2) + radius:
                return False
        elif y1 == y2:  # Horizontal wall
            if abs(y - y1) < radius and min(x1, x2) - radius < x < max(x1, x2) + radius:
                return False
    return True

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_player():
    """Draw Pacman with animated mouth."""
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
    glRotatef(player_angle, 0, 0, 1)
    
    if game_over:
        glRotatef(90, 1, 0, 0)  # Lie flat
    
    # Pacman: yellow sphere with animated mouth
    glColor3f(1, 1, 0)  # Yellow
    mouth_angle = 45 + 15 * math.sin(time.time() * 5)  # Animate mouth (30–60 degrees)
    quad = gluNewQuadric()
    gluPartialDisk(quad, 0, 20, 20, 20, mouth_angle / 2, 360 - mouth_angle)  # Wedge shape
    glPopMatrix()

def draw_enemy(x, y, z):
    """Draw an enemy as a red sphere."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1, 0, 0)
    gluSphere(gluNewQuadric(), 15, 10, 10)
    glPopMatrix()

def draw_powerup(x, y, z):
    """Draw a power-up as a green cube."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(0, 1, 0)
    scale = 1.0 + 0.2 * math.sin(time.time() * 5)  # Pulsing effect
    glScalef(scale, scale, scale)
    glutSolidCube(10)
    glPopMatrix()

def draw_maze():
    """Draw the maze walls."""
    glBegin(GL_QUADS)
    glColor3f(0, 0, 1)  # Blue walls
    for wall in maze_walls:
        x1, y1, x2, y2, height = wall
        if x1 == x2:  # Vertical wall
            glVertex3f(x1 - 10, y1, 0)
            glVertex3f(x1 + 10, y1, 0)
            glVertex3f(x1 + 10, y1, height)
            glVertex3f(x1 - 10, y1, height)
            for y in range(int(min(y1, y2)), int(max(y1, y2)), 10):
                glVertex3f(x1 - 10, y, 0)
                glVertex3f(x1 + 10, y, 0)
                glVertex3f(x1 + 10, y, height)
                glVertex3f(x1 - 10, y, height)
        elif y1 == y2:  # Horizontal wall
            glVertex3f(x1, y1 - 10, 0)
            glVertex3f(x1, y1 + 10, 0)
            glVertex3f(x1, y1 + 10, height)
            glVertex3f(x1, y1 - 10, height)
            for x in range(int(min(x1, x2)), int(max(x1, x2)), 10):
                glVertex3f(x, y1 - 10, 0)
                glVertex3f(x, y1 + 10, 0)
                glVertex3f(x, y1 + 10, height)
                glVertex3f(x, y1 - 10, height)
    glEnd()

def keyboardListener(key, x, y):
    """Handle keyboard inputs."""
    global player_pos, player_angle
    if game_over:
        if key == b'r':
            init_game()
        return
    
    speed = 5
    if key == b'w':  # Move forward
        rad = math.radians(player_angle)
        new_x = player_pos[0] + speed * math.sin(rad)
        new_y = player_pos[1] + speed * math.cos(rad)
        if is_valid_position(new_x, new_y, 20):
            player_pos[0] = new_x
            player_pos[1] = new_y
    if key == b's':  # Move backward
        rad = math.radians(player_angle)
        new_x = player_pos[0] - speed * math.sin(rad)
        new_y = player_pos[1] - speed * math.cos(rad)
        if is_valid_position(new_x, new_y, 20):
            player_pos[0] = new_x
            player_pos[1] = new_y
    if key == b'a':  # Turn left (counterclockwise)
        player_angle = (player_angle + 5) % 360
    if key == b'd':  # Turn right (clockwise)
        player_angle = (player_angle - 5) % 360

def specialKeyListener(key, x, y):
    """Handle arrow keys for camera."""
    global camera_height, camera_angle
    if game_over:
        return
    if key == GLUT_KEY_UP:
        camera_height = min(camera_height + 10, 600)
    if key == GLUT_KEY_DOWN:
        camera_height = max(camera_height - 10, 100)
    if key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle + 5) % 360
    if key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle - 5) % 360

def mouseListener(button, state, x, y):
    """Handle mouse inputs."""
    if game_over:
        return
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        rad = math.radians(player_angle)
        bx = player_pos[0] + 20 * math.sin(rad)
        by = player_pos[1] + 20 * math.cos(rad)
        bz = player_pos[2]
        bullets.append([bx, by, bz, player_angle])
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        global camera_mode
        camera_mode = 'first' if camera_mode == 'third' else 'third'

def setupCamera():
    """Configure camera projection and view."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if camera_mode == 'third':
        rad = math.radians(camera_angle)
        cx = player_pos[0] + 200 * math.sin(rad)  # Follow player
        cy = player_pos[1] + 200 * math.cos(rad)
        cz = camera_height
        gluLookAt(cx, cy, cz, player_pos[0], player_pos[1], player_pos[2], 0, 0, 1)
    else:
        rad = math.radians(player_angle)
        cx = player_pos[0] - 30 * math.sin(rad)  # Closer for first-person
        cy = player_pos[1] - 30 * math.cos(rad)
        cz = player_pos[2]
        tx = player_pos[0] + 100 * math.sin(rad)
        ty = player_pos[1] + 100 * math.cos(rad)
        tz = player_pos[2]
        gluLookAt(cx, cy, cz, tx, ty, tz, 0, 0, 1)

def update_game():
    """Update game state."""
    global bullets, enemies, powerups, life, bullets_missed, game_over, score, last_time
    if game_over:
        return
    
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time
    
    # Update bullets
    new_bullets = []
    for bullet in bullets:
        bx, by, bz, angle = bullet
        rad = math.radians(angle)
        bx += BULLET_SPEED * math.sin(rad) * dt * 60
        by += BULLET_SPEED * math.cos(rad) * dt * 60
        if -MAZE_SIZE < bx < MAZE_SIZE and -MAZE_SIZE < by < MAZE_SIZE and is_valid_position(bx, by, 5):
            new_bullets.append([bx, by, bz, angle])
        else:
            bullets_missed += 1
            if bullets_missed >= 10:
                game_over = True
    bullets = new_bullets
    
    # Update enemies
    for enemy in enemies:
        ex, ey, ez = enemy
        dx = player_pos[0] - ex
        dy = player_pos[1] - ey
        dist = math.hypot(dx, dy)
        if dist > 5:
            dx /= dist
            dy /= dist
            new_x = ex + ENEMY_SPEED * dx * dt * 60
            new_y = ey + ENEMY_SPEED * dy * dt * 60
            if is_valid_position(new_x, new_y, 15):
                enemy[0] = new_x
                enemy[1] = new_y
    
    # Check collisions
    new_enemies = []
    for enemy in enemies:
        ex, ey, ez = enemy
        hit = False
        bullets_to_remove = []
        for bullet in bullets:
            bx, by, bz, _ = bullet
            if math.hypot(bx - ex, by - ey) < 20 and abs(bz - ez) < 20:
                hit = True
                bullets_to_remove.append(bullet)
                score += 10
                break
        if math.hypot(ex - player_pos[0], ey - player_pos[1]) < 35 and abs(ez - player_pos[2]) < 20:
            life -= 1
            hit = True
            if life <= 0:
                game_over = True
        if not hit:
            new_enemies.append(enemy)
        else:
            spawn_enemy()
    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)
    enemies = new_enemies
    
    # Check power-up collisions
    new_powerups = []
    for powerup in powerups:
        px, py, pz = powerup
        if math.hypot(px - player_pos[0], py - player_pos[1]) < 30 and abs(pz - player_pos[2]) < 20:
            if life < 5:
                life += 1
                spawn_powerup()
        else:
            new_powerups.append(powerup)
    powerups = new_powerups

def draw_bullet(x, y, z):
    """Draw a bullet as a white cube."""
    glPushMatrix()
    glTranslatef(x, y, z)
    glColor3f(1, 1, 1)
    scale = 1.0 + 0.2 * math.sin(time.time() * 5)
    glScalef(scale, scale, scale)
    glutSolidCube(8)
    glPopMatrix()

def idle():
    """Update game and redraw."""
    update_game()
    glutPostRedisplay()

def showScreen():
    """Render the game scene."""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    
    draw_maze()
    draw_player()
    for enemy in enemies:
        draw_enemy(*enemy)
    for powerup in powerups:
        draw_powerup(*powerup)
    for bullet in bullets:
        draw_bullet(bullet[0], bullet[1], bullet[2])
    
    # HUD
    draw_text(10, 770, f"Lives: {life}")
    draw_text(10, 740, f"Score: {score}")
    draw_text(10, 710, f"Bullets Missed: {bullets_missed}")
    draw_text(10, 680, f"Camera: {'First-Person' if camera_mode == 'first' else 'Third-Person'}")
    if game_over:
        draw_text(400, 400, "Game Over! Press R to Restart")
    
    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"3D Pacman")
    
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    init_game()
    
    glutMainLoop()

if __name__ == "__main__":
    main()