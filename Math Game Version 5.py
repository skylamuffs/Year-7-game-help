'''Version 5 - Adding the Sword GUI '''
import pygame
import sys
import math

class Player:
    def __init__(self, x, y, size, color, is_player, controls, sword_img, is_circle=True):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.is_player = is_player
        self.controls = controls
        self.facing_right = is_player 
        self.sword_img = sword_img
        self.is_circle = is_circle
        self.sword_offset_x = 15 
        self.sword_offset_y = 0
        self.health = 100
        self.last_movement = 'right' if is_player else 'left'
        self.attacking = False
        self.attack_cooldown = 0
        self.attack_duration = 15
        self.attack_range = 70
    
    def move(self, keys):
        moved = False
        
        if keys[self.controls[0]] and self.x > self.size//2:  # Left
            self.x -= 5
            self.facing_right = False
            self.last_movement = 'left'
            moved = True
        if keys[self.controls[1]] and self.x < WIDTH - self.size//2:  # Right
            self.x += 5
            self.facing_right = True
            self.last_movement = 'right'
            moved = True
        if keys[self.controls[2]] and self.y > self.size//2:  # Up
            self.y -= 5
            moved = True
        if keys[self.controls[3]] and self.y < HEIGHT - self.size//2:  # Down
            self.y += 5
            moved = True
            
        # Attack controls (Space for player 1, RCTRL for player 2)
        attack_key = pygame.K_SPACE if self.is_player else pygame.K_RCTRL
        if keys[attack_key] and self.attack_cooldown == 0:
            self.attacking = True
            self.attack_cooldown = self.attack_duration + 20  # Attack duration + cooldown
            
        return moved
    
    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            if self.attack_cooldown <= 20:  # After attack duration
                self.attacking = False
    
    def get_sword_position(self):
        if self.last_movement == 'right':
            return (self.x + self.size//2, self.y)
        else:
            return (self.x - self.size//2, self.y)
    
    def check_sword_hit(self, other_player):
        if not self.attacking or self.attack_cooldown > 20:  # Only during active attack frames
            return False
            
        # Get sword position
        sword_x, sword_y = self.get_sword_position()
        
        # Calculate distance to other player
        distance = math.sqrt((sword_x - other_player.x)**2 + (sword_y - other_player.y)**2)
        
        # Check if sword is in range and facing the opponent
        if distance < self.attack_range:
            if (self.last_movement == 'right' and self.x < other_player.x) or \
               (self.last_movement == 'left' and self.x > other_player.x):
                return True
        return False
    
    def draw(self, screen):
        # Draw player body
        if self.is_circle:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size//2)
        else:
            pygame.draw.rect(screen, self.color, 
                           (self.x - self.size//2, self.y - self.size//2, 
                            self.size, self.size))
        
        # Draw sword if available
        if self.sword_img:
            # Automatically face the direction of last movement
            if self.last_movement == 'right':
                sword = self.sword_img
                sword_pos = (self.x + self.size//2 - self.sword_offset_x, 
                            self.y - self.sword_img.get_height()//2 + self.sword_offset_y)
            else:
                sword = pygame.transform.flip(self.sword_img, True, False)
                sword_pos = (self.x - self.size//2 - self.sword_img.get_width() + self.sword_offset_x, 
                            self.y - self.sword_img.get_height()//2 + self.sword_offset_y)
            
            # Add attack animation effect
            if self.attacking and self.attack_cooldown > 20:
                if self.last_movement == 'right':
                    sword_pos = (sword_pos[0] + 10, sword_pos[1])
                else:
                    sword_pos = (sword_pos[0] - 10, sword_pos[1])
            
            screen.blit(sword, sword_pos)
        
        # Draw health bar above player
        pygame.draw.rect(screen, WHITE, (self.x - 50, self.y - 60, 100, 10))
        health_width = int((self.health / 100) * 100)
        pygame.draw.rect(screen, self.color, (self.x - 50, self.y - 60, health_width, 10))

def main():
    # Initialize Pygame
    pygame.init()
    
    # Screen dimensions
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Samurai Math")
    
    # Colors
    global WHITE
    BACKGROUND = (30, 30, 40)
    RED = (255, 80, 80)
    BLUE = (80, 80, 255)
    WHITE = (255, 255, 255)
    
    # Load sword image (same for both)
    try:
        sword_img = pygame.image.load("Sword_Enemy.png").convert_alpha()
        sword_img = pygame.transform.scale(sword_img, (60, 60))
        player_sword = sword_img
        antagonist_sword = sword_img  # Use same image, facing will be handled in drawing
    except:
        print("Sword image not found, using rectangles")
        sword_img = None
        player_sword = None
        antagonist_sword = None
    
    # Game variables
    game_font = pygame.font.SysFont('Arial', 24)
    
    # Create players - Circle (Player 1) and Square (Player 2)
    player1 = Player(WIDTH//3, HEIGHT//2, 50, RED, True,
                    [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s], player_sword, True)
    player2 = Player(2*WIDTH//3, HEIGHT//2, 50, BLUE, False,
                    [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN], antagonist_sword, False)
    
    # Make square player face left initially
    player2.facing_right = False
    player2.last_movement = 'left'
    
    clock = pygame.time.Clock()
    
    def draw_ui():
        """Draw user interface elements"""
        p1_text = game_font.render("Player 1 (Circle): WASD + SPACE", True, RED)
        p2_text = game_font.render("Player 2 (Square): Arrows + RCTRL", True, BLUE)
        screen.blit(p1_text, (20, 20))
        screen.blit(p2_text, (WIDTH - 250, 20))
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Handle keyboard input
        keys = pygame.key.get_pressed()
        player1.move(keys)
        player2.move(keys)
        
        # Update player states
        player1.update()
        player2.update()
        
        # Check for sword hits
        if player1.check_sword_hit(player2):
            player2.health = max(0, player2.health - 10)
        
        if player2.check_sword_hit(player1):
            player1.health = max(0, player1.health - 10)
        
        # Fill screen with dark background
        screen.fill(BACKGROUND)
        
        # Draw players (including their health bars)
        player1.draw(screen)
        player2.draw(screen)
        
        # Draw UI
        draw_ui()
        
        # Game over check
        if player1.health <= 0 or player2.health <= 0:
            font = pygame.font.SysFont(None, 72)
            if player1.health <= 0 and player2.health <= 0:
                text = font.render("DRAW!", True, WHITE)
            elif player1.health <= 0:
                text = font.render("BLUE WINS!", True, BLUE)
            else:
                text = font.render("RED WINS!", True, RED)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
        
        # Update display
        pygame.display.flip()
        
        # Cap at 60 FPS
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()