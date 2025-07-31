'''Version 5 Adding GUI on sword'''
import pygame
import sys
import math

# Initialize pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Precise Sword Damage")

# Colors
BACKGROUND = (30, 30, 40)
PLAYER_RED = (255, 80, 80)      # #ff5050 (player appearance)
PLAYER_BLUE = (80, 80, 255)     # #5050ff (player appearance)
WHITE = (255, 255, 255)

def check_sword_hit(attacker_x, attacker_y, attacker_angle, defender_x, defender_y, defender_radius=20):
    sword_tip_x = attacker_x + 50 * math.cos(math.radians(attacker_angle))
    sword_tip_y = attacker_y + 50 * math.sin(math.radians(attacker_angle))
    
    # Calculate distance between sword tip and defender
    distance = math.sqrt((sword_tip_x - defender_x)**2 + (sword_tip_y - defender_y)**2)
    return distance < defender_radius

class Player:
    def __init__(self, x, y, size, color, is_player, controls, sword_img, is_circle=True):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.is_player = is_player
        self.controls = controls
        self.sword_img = sword_img
        self.is_circle = is_circle
        self.health = 100
        self.sword_angle = 0 if is_player else 180
        self.hit_cooldown = 0
        self.sword_length = 80
        
    def move(self, keys):
        if keys[self.controls[0]] and self.x > self.size//2:  # Left
            self.x -= 5
        if keys[self.controls[1]] and self.x < WIDTH - self.size//2:  # Right
            self.x += 5
        if keys[self.controls[2]] and self.y > self.size//2:  # Up
            self.y -= 5
        if keys[self.controls[3]] and self.y < HEIGHT - self.size//2:  # Down
            self.y += 5
    
    def update(self, target=None):
        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1
        
        # Auto-face the opponent (optional - you can remove this if you want manual control)
        if target:
            dx = target.x - self.x
            dy = target.y - self.y
            self.sword_angle = math.degrees(math.atan2(dy, dx))
    
    def get_sword_tip(self):
        tip_x = self.x + self.sword_length * math.cos(math.radians(self.sword_angle))
        tip_y = self.y + self.sword_length * math.sin(math.radians(self.sword_angle))
        return (tip_x, tip_y)
    
    def check_sword_hit(self, other_player):
        if self.hit_cooldown > 0:
            return False
            
        # Use Version 4's simple distance check
        hit = check_sword_hit(
            self.x, self.y, self.sword_angle,
            other_player.x, other_player.y,
            other_player.size//2
        )
        
        if hit:
            self.hit_cooldown = 30  # Slightly longer cooldown than Version 4
        return hit
    
    def draw(self, surface):
        # Draw fighter body
        if self.is_circle:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size//2)
        else:
            pygame.draw.rect(surface, self.color,
                           (self.x - self.size//2,
                            self.y - self.size//2,
                            self.size, self.size))
        
        # Draw sword
        if self.sword_img:
            rotated_sword = pygame.transform.rotate(self.sword_img, -self.sword_angle)
            sword_rect = rotated_sword.get_rect(center=(self.x, self.y))
            surface.blit(rotated_sword, sword_rect)
        else:
            tip_x, tip_y = self.get_sword_tip()
            pygame.draw.line(surface, WHITE, (self.x, self.y)), (tip_x, tip_y), 5
        
        # Draw health bar
        pygame.draw.rect(surface, WHITE, (self.x - 50, self.y - 60, 100, 10))
        health_width = max(0, int((self.health / 100) * 100))
        pygame.draw.rect(surface, self.color, (self.x - 50, self.y - 60, health_width, 10))

def main():
    # Load sword images
    try:
        player_sword = pygame.image.load("Sword_Player.png").convert_alpha()
        player_sword = pygame.transform.scale(player_sword, (120, 25))
        player_sword = pygame.transform.rotate(player_sword, 180)
        enemy_sword = pygame.image.load("Sword_Enemy.png").convert_alpha()
        enemy_sword = pygame.transform.scale(enemy_sword, (120, 25))
    except:
        print("Using rectangles instead of sword images")
        player_sword = None
        enemy_sword = None
    
    # Create players
    player1 = Player(WIDTH//3, HEIGHT//2, 40, PLAYER_RED, True,
                    [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s], player_sword, True)
    player2 = Player(2*WIDTH//3, HEIGHT//2, 40, PLAYER_BLUE, False,
                    [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN], enemy_sword, False)
    
    clock = pygame.time.Clock()
    game_font = pygame.font.SysFont('Arial', 24)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Movement
        keys = pygame.key.get_pressed()
        player1.move(keys)
        player2.move(keys)
        
        # Update
        player1.update(player2)
        player2.update(player1)
        
        # Damage checks (using Version 4's sword mechanics)
        if player1.check_sword_hit(player2):
            player2.health = max(0, player2.health - 10)  # Matches Version 4's damage
        
        if player2.check_sword_hit(player1):
            player1.health = max(0, player1.health - 10)  # Matches Version 4's damage
        
        # Drawing
        screen.fill(BACKGROUND)
        player1.draw(screen)
        player2.draw(screen)
        
        # Draw UI
        p1_text = game_font.render("Player 1: WASD", True, PLAYER_RED)
        p2_text = game_font.render("Player 2: Arrows", True, PLAYER_BLUE)
        screen.blit(p1_text, (20, 20))
        screen.blit(p2_text, (WIDTH - p2_text.get_width() - 20, 20))
        
        # Game over check
        if player1.health <= 0 or player2.health <= 0:
            font = pygame.font.SysFont(None, 72)
            if player1.health <= 0 and player2.health <= 0:
                text = font.render("DRAW!", True, WHITE)
            elif player1.health <= 0:
                text = font.render("BLUE WINS!", True, PLAYER_BLUE)
            else:
                text = font.render("RED WINS!", True, PLAYER_RED)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2))
            pygame.display.flip()
            pygame.time.wait(3000)
            running = False
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()