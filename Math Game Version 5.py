'''Version 5 Adding GUI on sword'''
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
        self.sword_img = sword_img
        self.is_circle = is_circle
        self.health = 100
        self.sword_angle = 0 if is_player else 180
        self.cooldown = 0
        self.sword_length = 60
        self.defender_radius = 20  # Hit detection radius like Version 4
        self.is_attacking = False
        
    def move(self, keys):
        moved = False
        
        if keys[self.controls[0]] and self.x > self.size//2:  # Left
            self.x -= 5
            moved = True
        if keys[self.controls[1]] and self.x < WIDTH - self.size//2:  # Right
            self.x += 5
            moved = True
        if keys[self.controls[2]] and self.y > self.size//2:  # Up
            self.y -= 5
            moved = True
        if keys[self.controls[3]] and self.y < HEIGHT - self.size//2:  # Down
            self.y += 5
            moved = True
            
        # Sword angle controls (Q/E for player 1, Z/C for player 2)
        angle_key1 = pygame.K_q if self.is_player else pygame.K_z
        angle_key2 = pygame.K_e if self.is_player else pygame.K_c
        if keys[angle_key1]:
            self.sword_angle = (self.sword_angle - 5) % 360
        if keys[angle_key2]:
            self.sword_angle = (self.sword_angle + 5) % 360
            
        return moved
    
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
    
    def get_sword_tip(self):
        # Calculate sword tip position 
        tip_x = self.x + self.sword_length * math.cos(math.radians(self.sword_angle))
        tip_y = self.y + self.sword_length * math.sin(math.radians(self.sword_angle))
        return (tip_x, tip_y)
    
    def check_sword_hit(self, other_player):
        if self.cooldown > 0:  
            return False
            
        sword_tip_x, sword_tip_y = self.get_sword_tip()
        distance = math.sqrt((sword_tip_x - other_player.x)**2 + (sword_tip_y - other_player.y)**2)
        
        # Version 4 style hit detection
        if distance < self.defender_radius:
            self.cooldown = 10  
            self.is_attacking = True
            return True
        self.is_attacking = False
        return False
    
    def draw(self, surface):
        # Draw fighter body - circle or rectangle based on is_circle
        if self.is_circle:
            pygame.draw.circle(surface, self.color, (self.x, self.y), self.size//2)
        else:
            pygame.draw.rect(surface, self.color, 
                           (self.x - self.size//2, 
                            self.y - self.size//2, 
                            self.size, self.size))
        
        # Draw sword
        if self.sword_img:
            # Rotate sword based on angle
            rotated_sword = pygame.transform.rotate(self.sword_img, -self.sword_angle)
            # Calculate position to keep sword attached to player
            sword_rect = rotated_sword.get_rect(center=(self.x, self.y))
            surface.blit(rotated_sword, sword_rect)
        else:
            # Fallback: draw sword as a line if image not available
            tip_x, tip_y = self.get_sword_tip()
            pygame.draw.line(surface, WHITE, (self.x, self.y), (tip_x, tip_y), 3)
        
        # Draw health bar
        pygame.draw.rect(surface, WHITE, (self.x - 50, self.y - 60, 100, 10))
        health_width = int((self.health / 100) * 100)
        pygame.draw.rect(surface, self.color, (self.x - 50, self.y - 60, health_width, 10))

def main():
    pygame.init()
    global WIDTH, HEIGHT, WHITE
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Samurai Math")
    
    BACKGROUND = (30, 30, 40)
    RED = (255, 80, 80)
    BLUE = (80, 80, 255)
    WHITE = (255, 255, 255)
    
    # Try to load sword images
    try:
        player_sword = pygame.image.load("Sword_Player.png").convert_alpha()
        player_sword = pygame.transform.scale(player_sword, (60, 20))
        enemy_sword = pygame.image.load("Sword_Enemy.png").convert_alpha()
        enemy_sword = pygame.transform.scale(enemy_sword, (60, 20))
    except:
        print("Sword images not found, using rectangles")
        player_sword = None
        enemy_sword = None
    
    game_font = pygame.font.SysFont('Arial', 24)
    
    # Create players
    player1 = Player(WIDTH//3, HEIGHT//2, 40, RED, True,
                    [pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s], player_sword, True)
    player2 = Player(2*WIDTH//3, HEIGHT//2, 40, BLUE, False,
                    [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN], enemy_sword, False)
    
    clock = pygame.time.Clock()
    
    def draw_ui():
        p1_text = game_font.render("Player 1: WASD + Q/E", True, RED)
        p2_text = game_font.render("Player 2: Arrows + Z/C", True, BLUE)
        screen.blit(p1_text, (20, 20))
        screen.blit(p2_text, (WIDTH - p2_text.get_width() - 20, 20))
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        keys = pygame.key.get_pressed()
        player1.move(keys)
        player2.move(keys)
        
        player1.update()
        player2.update()
        
        # Continuous damage check 
        if player1.check_sword_hit(player2):
            player2.health = max(0, player2.health - 10) 
        
        if player2.check_sword_hit(player1):
            player1.health = max(0, player1.health - 10)
        
        screen.fill(BACKGROUND)
        player1.draw(screen)
        player2.draw(screen)
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
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()