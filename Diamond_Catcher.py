
import pygame
import random
from time import time
from sys import exit

def main():
    # Initialize game window
    pygame.init()
    win_width, win_height = 800, 600
    screen = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption("Diamond Catcher")

    # Game colors
    bg_color = (25, 25, 35)
    white = (240, 240, 240)
    red = (220, 50, 50)
    teal = (45, 220, 220) 
    amber = (255, 180, 0)

    # Game objects
    class Diamond:
        def __init__(self):
            self.size = 18
            self.reset()
            self.color = self.random_color()
        
        def random_color(self):
            r = random.randint(150, 255)
            g = random.randint(100, 255)
            b = random.randint(100, 255)
            return (r, g, b)
        
        def reset(self):
            self.x = random.randint(50, win_width - 50)
            self.y = -self.size
            self.color = self.random_color()
        
        def draw(self):
            # Custom line drawing for diamond shape
            points = [
                (self.x, self.y - self.size),
                (self.x + self.size, self.y),
                (self.x, self.y + self.size),
                (self.x - self.size, self.y)
            ]
            pygame.draw.lines(screen, self.color, True, points, 2)

    class Catcher:
        def __init__(self):
            self.width = 65
            self.height = 12
            self.x = win_width // 2
            self.y = win_height - 50
            self.color = white
        
        def draw(self):
            # Custom shape for catcher
            points = [
                (self.x - self.width//2, self.y),
                (self.x - self.width//4, self.y - self.height),
                (self.x + self.width//4, self.y - self.height),
                (self.x + self.width//2, self.y)
            ]
            pygame.draw.lines(screen, self.color, True, points, 2)

    # Game state
    diamond = Diamond()
    catcher = Catcher()
    score = 0
    game_active = True
    paused = False
    fall_speed = 3.0
    speed_increase = 0.02
    last_time = time()
    font = pygame.font.SysFont('Arial', 28)

    # Game buttons
    button_size = 38
    button_y = 30

    def draw_button(x, color, shape):
        rect = pygame.Rect(x - button_size//2, button_y - button_size//2, 
                          button_size, button_size)
        pygame.draw.rect(screen, color, rect, 2)
        
        if shape == "restart":
            # Left arrow
            pygame.draw.line(screen, color, 
                           (x, button_y), (x + 10, button_y - 10), 2)
            pygame.draw.line(screen, color, 
                           (x, button_y), (x + 10, button_y + 10), 2)
            pygame.draw.line(screen, color, 
                           (x - 10, button_y), (x + 10, button_y), 2)
        elif shape == "play_pause":
            if paused:
                # Play icon
                pygame.draw.polygon(screen, color, [
                    (x - 10, button_y - 10),
                    (x - 10, button_y + 10),
                    (x + 10, button_y)
                ], 2)
            else:
                # Pause icon
                pygame.draw.line(screen, color, 
                               (x - 8, button_y - 10), (x - 8, button_y + 10), 2)
                pygame.draw.line(screen, color, 
                               (x + 8, button_y - 10), (x + 8, button_y + 10), 2)
        elif shape == "exit":
            # X shape
            pygame.draw.line(screen, color, 
                           (x - 10, button_y - 10), (x + 10, button_y + 10), 2)
            pygame.draw.line(screen, color, 
                           (x - 10, button_y + 10), (x + 10, button_y - 10), 2)

    # Main game loop
    clock = pygame.time.Clock()
    while True:
        current_time = time()
        delta_time = current_time - last_time
        last_time = current_time
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Check button clicks
                if 20 <= mouse_x <= 20 + button_size and 10 <= mouse_y <= 10 + button_size:
                    # Restart game
                    diamond.reset()
                    catcher.color = white
                    score = 0
                    game_active = True
                    paused = False
                    fall_speed = 3.0
                    print("Game restarted")
                
                elif win_width//2 - button_size//2 <= mouse_x <= win_width//2 + button_size//2 and 10 <= mouse_y <= 10 + button_size:
                    # Toggle pause
                    paused = not paused
                    print("Game paused" if paused else "Game resumed")
                
                elif win_width - 20 - button_size <= mouse_x <= win_width - 20 and 10 <= mouse_y <= 10 + button_size:
                    # Exit game
                    print(f"Final score: {score}")
                    pygame.quit()
                    exit()
        
        # Game logic when active and not paused
        if game_active and not paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and catcher.x - catcher.width//2 > 0:
                catcher.x -= 8
            if keys[pygame.K_RIGHT] and catcher.x + catcher.width//2 < win_width:
                catcher.x += 8
            
            # Move diamond
            diamond.y += fall_speed * delta_time * 60
            
            # Check collision
            if (abs(diamond.x - catcher.x) < (diamond.size + catcher.width//2) and
                abs(diamond.y - catcher.y) < (diamond.size + catcher.height)):
                score += 1
                fall_speed += speed_increase
                diamond.reset()
                print(f"Score: {score}")
            
            # Check if diamond missed
            if diamond.y - diamond.size > win_height:
                game_active = False
                catcher.color = red
                print(f"Game over! Score: {score}")

        # Drawing
        screen.fill(bg_color)
        
        # Draw UI buttons
        draw_button(30, teal, "restart")
        draw_button(win_width//2, amber, "play_pause")
        draw_button(win_width - 30, red, "exit")
        
        # Draw game objects
        diamond.draw()
        catcher.draw()
        
        # Draw score
        score_text = font.render(f"Score: {score}", True, white)
        screen.blit(score_text, (win_width - 150, win_height - 40))
        
        # Game over message
        if not game_active:
            game_over_text = font.render("GAME OVER - Click left arrow to restart", True, red)
            screen.blit(game_over_text, (win_width//2 - 180, win_height//2 - 50))
        
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()