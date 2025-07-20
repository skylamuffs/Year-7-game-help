'''Version 4 - Adding sticks and health bars '''
import pygame
import sys
import math

def check_sword_hit(attacker_x, attacker_y, attacker_angle, defender_x, defender_y, defender_radius=20):
    sword_tip_x = attacker_x + 50 * math.cos(math.radians(attacker_angle))
    sword_tip_y = attacker_y + 50 * math.sin(math.radians(attacker_angle))
    
    # Calculate distance between sword tip and defender
    distance = math.sqrt((sword_tip_x - defender_x)**2 + (sword_tip_y - defender_y)**2)
    return distance < defender_radius

def main():
    # Initialize Pygame
    pygame.init()
    
    # Screen dimensions
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Samurai Math")
    
 # Colors
    BACKGROUND = (30, 30, 40)
    RED = (255, 80, 80)      # Player 1 (circle)
    BLUE = (80, 80, 255)     # Player 2 (square)     
    WHITE = (255, 255, 255)  
    GRAY = (128, 128, 128)  
    
    # Protagonist (red stick figure)
    protagonist_x, protagonist_y = WIDTH // 4, HEIGHT // 2
    protagonist_speed = 5
    protagonist_health = 100
    protagonist_sword_angle = 0
    protagonist_cooldown = 0
    
    # Antagonist (green stick figure)
    antagonist_x, antagonist_y = 3 * WIDTH // 4, HEIGHT // 2
    antagonist_speed = 5
    antagonist_health = 100
    antagonist_sword_angle = 180
    antagonist_cooldown = 0
    
    clock = pygame.time.Clock()
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Cooldown timers
        if protagonist_cooldown > 0:
            protagonist_cooldown -= 1
        if antagonist_cooldown > 0:
            antagonist_cooldown -= 1
        
        # Handle keyboard input for protagonist movement (arrow keys)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and protagonist_x > 30:
            protagonist_x -= protagonist_speed
        if keys[pygame.K_RIGHT] and protagonist_x < WIDTH - 30:
            protagonist_x += protagonist_speed
        if keys[pygame.K_UP] and protagonist_y > 60:
            protagonist_y -= protagonist_speed
        if keys[pygame.K_DOWN] and protagonist_y < HEIGHT - 90:
            protagonist_y += protagonist_speed
        
        # Handle keyboard input for antagonist movement (WASD)
        if keys[pygame.K_a] and antagonist_x > 30:
            antagonist_x -= antagonist_speed
        if keys[pygame.K_d] and antagonist_x < WIDTH - 30:
            antagonist_x += antagonist_speed
        if keys[pygame.K_w] and antagonist_y > 60:
            antagonist_y -= antagonist_speed
        if keys[pygame.K_s] and antagonist_y < HEIGHT - 90:
            antagonist_y += antagonist_speed
        
        # Sword angle controls (Q/E for protagonist, Z/C for antagonist)
        if keys[pygame.K_q]:
            protagonist_sword_angle = (protagonist_sword_angle - 5) % 360
        if keys[pygame.K_e]:
            protagonist_sword_angle = (protagonist_sword_angle + 5) % 360
        if keys[pygame.K_z]:
            antagonist_sword_angle = (antagonist_sword_angle - 5) % 360
        if keys[pygame.K_c]:
            antagonist_sword_angle = (antagonist_sword_angle + 5) % 360
        
        # Check for sword hits
        if protagonist_cooldown == 0 and check_sword_hit(
            protagonist_x, protagonist_y, protagonist_sword_angle, 
            antagonist_x, antagonist_y
        ):
            antagonist_health = max(0, antagonist_health - 10)
            protagonist_cooldown = 30  
        
        if antagonist_cooldown == 0 and check_sword_hit(
            antagonist_x, antagonist_y, antagonist_sword_angle, 
            protagonist_x, protagonist_y
        ):
            protagonist_health = max(0, protagonist_health - 10)
            antagonist_cooldown = 30
        
        # Fill screen with blue
        screen.fill(BACKGROUND)
        
        # Draw protagonist (red stick figure with sword)
        # Head
        pygame.draw.circle(screen, RED, (protagonist_x, protagonist_y - 30), 15)
        # Body
        pygame.draw.line(screen, WHITE, (protagonist_x, protagonist_y - 15), 
                         (protagonist_x, protagonist_y + 20), 3)
        # Legs
        pygame.draw.line(screen, WHITE, (protagonist_x, protagonist_y + 20), 
                         (protagonist_x - 15, protagonist_y + 40), 3)
        pygame.draw.line(screen, WHITE, (protagonist_x, protagonist_y + 20), 
                         (protagonist_x + 15, protagonist_y + 40), 3)
        # Arms
        pygame.draw.line(screen, WHITE, (protagonist_x, protagonist_y), 
                         (protagonist_x - 20, protagonist_y + 10), 3)
        # Sword arm (can rotate)
        sword_end_x = protagonist_x + 30 * math.cos(math.radians(protagonist_sword_angle))
        sword_end_y = protagonist_y + 30 * math.sin(math.radians(protagonist_sword_angle))
        pygame.draw.line(screen, WHITE, (protagonist_x, protagonist_y), 
                         (sword_end_x, sword_end_y), 3)
        # Sword blade
        pygame.draw.line(screen, GRAY, (sword_end_x, sword_end_y), 
                         (sword_end_x + 20 * math.cos(math.radians(protagonist_sword_angle)), 
                          sword_end_y + 20 * math.sin(math.radians(protagonist_sword_angle))), 5)
        
        # Draw antagonist (green stick figure with sword)
        # Head
        pygame.draw.circle(screen, BLUE, (antagonist_x, antagonist_y - 30), 15)
        # Body
        pygame.draw.line(screen, WHITE, (antagonist_x, antagonist_y - 15), 
                         (antagonist_x, antagonist_y + 20), 3)
        # Legs
        pygame.draw.line(screen, WHITE, (antagonist_x, antagonist_y + 20), 
                         (antagonist_x - 15, antagonist_y + 40), 3)
        pygame.draw.line(screen, WHITE, (antagonist_x, antagonist_y + 20), 
                         (antagonist_x + 15, antagonist_y + 40), 3)
        # Arms
        pygame.draw.line(screen, WHITE, (antagonist_x, antagonist_y), 
                         (antagonist_x + 20, antagonist_y + 10), 3)
        # Sword arm (can rotate)
        sword_end_x = antagonist_x + 30 * math.cos(math.radians(antagonist_sword_angle))
        sword_end_y = antagonist_y + 30 * math.sin(math.radians(antagonist_sword_angle))
        pygame.draw.line(screen, WHITE, (antagonist_x, antagonist_y), 
                         (sword_end_x, sword_end_y), 3)
        # Sword blade
        pygame.draw.line(screen, GRAY, (sword_end_x, sword_end_y), 
                         (sword_end_x + 20 * math.cos(math.radians(antagonist_sword_angle)), 
                          sword_end_y + 20 * math.sin(math.radians(antagonist_sword_angle))), 5)
        
        # Draw health bars
        # Protagonist health bar background
        pygame.draw.rect(screen, WHITE, (protagonist_x - 50, protagonist_y - 60, 100, 10))
        # Protagonist health bar
        health_width = int((protagonist_health / 100) * 100)
        pygame.draw.rect(screen, RED, (protagonist_x - 50, protagonist_y - 60, health_width, 10))
        
        # Antagonist health bar background
        pygame.draw.rect(screen, WHITE, (antagonist_x - 50, antagonist_y - 60, 100, 10))
        # Antagonist health bar
        health_width = int((antagonist_health / 100) * 100)
        pygame.draw.rect(screen, BLUE, (antagonist_x - 50, antagonist_y - 60, health_width, 10))
        
        # Game over check
        if protagonist_health <= 0 or antagonist_health <= 0:
            font = pygame.font.SysFont(None, 72)
            if protagonist_health <= 0 and antagonist_health <= 0:
                text = font.render("DRAW!", True, WHITE)
            elif protagonist_health <= 0:
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