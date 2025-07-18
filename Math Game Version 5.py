'''Version 5 - Fixing by the feedback '''
import pygame
import sys

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
        self.is_attacking = False
    
    def move(self, keys):
        if keys[self.controls[0]] and self.x > self.size//2: 
            self.x -= 5
            self.facing_right = False
        if keys[self.controls[1]] and self.x < WIDTH - self.size//2: 
            self.x += 5
            self.facing_right = True
        if keys[self.controls[2]] and self.y > self.size//2:  
            self.y -= 5
        if keys[self.controls[3]] and self.y < HEIGHT - self.size//2:  
            self.y += 5
    
    def draw(self, screen):
        # Draw player body
        if self.is_circle:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size//2)
        else:
            pygame.draw.rect(screen, self.color, 
                           (self.x - self.size//2, self.y - self.size//2, 
                            self.size, self.size))
        
        # Draw sword
        if self.sword_img:
            if self.is_attacking:
                sword = pygame.transform.rotate(self.sword_img, -45 if self.facing_right else 45)
            else:
                sword = self.sword_img
            
            if not self.facing_right:
                sword = pygame.transform.flip(sword, True, False)
            
            sword_pos = (self.x + self.size//2 - self.sword_offset_x if self.facing_right 
                        else self.x - self.size//2 - sword.get_width() + self.sword_offset_x,
                        self.y - sword.get_height()//2 + self.sword_offset_y)
            
            screen.blit(sword, sword_pos)
        else:
            # Fallback: draw simple sword shape
            sword_length = self.size + 10
            if self.facing_right:
                end_x = self.x + self.size//2 + sword_length
            else:
                end_x = self.x - self.size//2 - sword_length
            pygame.draw.line(screen, self.color, 
                           (self.x, self.y), 
                           (end_x, self.y), 3)

def main():
    # Initialize Pygame
    pygame.init()
    
    # Screen dimensions
    global WIDTH, HEIGHT
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Circle vs Square Duel")
    
    # Colors
    BACKGROUND = (30, 30, 40)
    RED = (255, 80, 80)
    BLUE = (80, 80, 255)
    WHITE = (255, 255, 255)
    
    # Load sword image (same for both)
    try:
        sword_img = pygame.image.load("Sword_Enemy.png").convert_alpha()
        sword_img = pygame.transform.scale(sword_img, (60, 60))
        player_sword = sword_img
        antagonist_sword = pygame.transform.flip(sword_img, True, False)
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
    
    clock = pygame.time.Clock()
    
    def draw_ui():
        """Draw user interface elements"""
        p1_text = game_font.render("Player 1 (Circle): WASD", True, RED)
        p2_text = game_font.render("Player 2 (Square): Arrows", True, BLUE)
        screen.blit(p1_text, (20, 20))
        screen.blit(p2_text, (WIDTH - 220, 20))
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    player1.is_attacking = True
                elif event.key == pygame.K_RCTRL:
                    player2.is_attacking = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player1.is_attacking = False
                elif event.key == pygame.K_RCTRL:
                    player2.is_attacking = False
        
        # Handle keyboard input
        keys = pygame.key.get_pressed()
        player1.move(keys)
        player2.move(keys)
        
        # Fill screen with dark background
        screen.fill(BACKGROUND)
        
        # Draw players
        player1.draw(screen)
        player2.draw(screen)
        
        # Draw UI
        draw_ui()
        
        # Update display
        pygame.display.flip()
        
        # Cap at 60 FPS
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()