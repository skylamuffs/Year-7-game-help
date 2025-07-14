'''Version 4 - Fixing by the feedback '''
import pygame
import sys
import random

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
    
    # Load sword image
    try:
        sword_img = pygame.image.load("sword.png").convert_alpha()
        # Scale the sword image if needed (adjust size as necessary)
        sword_img = pygame.transform.scale(sword_img, (50, 50))
    except:
        print("Could not load sword.png, using rectangle instead")
        sword_img = None
    
    # Player 1 (circle) - WASD controls
    circle_radius = 25
    circle_x, circle_y = WIDTH // 3, HEIGHT // 2
    circle_speed = 5
    
    # Player 2 (square) - Arrow keys controls
    square_size = 40
    square_x, square_y = 2 * WIDTH // 3, HEIGHT // 2
    square_speed = 5
    
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
        
        # Handle keyboard input for Player 1 (WASD)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and circle_x > circle_radius:  # Left
            circle_x -= circle_speed
        if keys[pygame.K_d] and circle_x < WIDTH - circle_radius:  # Right
            circle_x += circle_speed
        if keys[pygame.K_w] and circle_y > circle_radius:  # Up
            circle_y -= circle_speed
        if keys[pygame.K_s] and circle_y < HEIGHT - circle_radius:  # Down
            circle_y += circle_speed
        
        # Handle keyboard input for Player 2 (Arrow keys)
        if keys[pygame.K_LEFT] and square_x > square_size//2:  # Left
            square_x -= square_speed
        if keys[pygame.K_RIGHT] and square_x < WIDTH - square_size//2:  # Right
            square_x += square_speed
        if keys[pygame.K_UP] and square_y > square_size//2:  # Up
            square_y -= square_speed
        if keys[pygame.K_DOWN] and square_y < HEIGHT - square_size//2:  # Down
            square_y += square_speed
        
        # Fill screen with dark background
        screen.fill(BACKGROUND)
        
        # Draw Player 2 (blue square with sword)
        if sword_img:
            # Draw the sword image centered on the square
            sword_rect = sword_img.get_rect(center=(square_x, square_y))
            screen.blit(sword_img, sword_rect)
        else:
            # Fallback: Draw blue square if sword image couldn't be loaded
            pygame.draw.rect(screen, BLUE, 
                            (square_x - square_size//2, 
                             square_y - square_size//2, 
                             square_size, square_size))
        
        # Draw Player 1 (red circle)
        pygame.draw.circle(screen, RED, (circle_x, circle_y), circle_radius)
        
        # Draw instructions
        font = pygame.font.SysFont('Arial', 20)
        p1_text = font.render("Player 1: WASD", True, RED)
        p2_text = font.render("Player 2: Arrow Keys", True, BLUE)
        screen.blit(p1_text, (20, 20))
        screen.blit(p2_text, (WIDTH - 180, 20))
        
        # Update display
        pygame.display.flip()
        
        # Cap at 60 FPS
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()