'''Version 2 - Added player (red circle) and enemy (green square) with movement controls'''
import pygame
import sys

def main():
    # Initialize Pygame
    pygame.init()
    
    # Screen dimensions
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Sumrai Math")
    
    # Colors
    BLUE = (0, 0, 255)  # Background
    RED = (255, 0, 0)    # Player (circle)
    GREEN = (0, 255, 0)  # Enemy (square)
    
    # Player settings
    circle_radius = 30
    circle_x, circle_y = WIDTH // 4, HEIGHT // 2
    circle_speed = 5
    
    # Enemy settings
    square_size = 50
    square_x, square_y = 3 * WIDTH // 4, HEIGHT // 2
    
    clock = pygame.time.Clock()
    
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Handle keyboard input for player movement (arrow keys)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and circle_x > circle_radius:
            circle_x -= circle_speed
        if keys[pygame.K_RIGHT] and circle_x < WIDTH - circle_radius:
            circle_x += circle_speed
        if keys[pygame.K_UP] and circle_y > circle_radius:
            circle_y -= circle_speed
        if keys[pygame.K_DOWN] and circle_y < HEIGHT - circle_radius:
            circle_y += circle_speed
        
        # Fill screen with blue
        screen.fill(BLUE)
        
        # Draw enemy (green square)
        pygame.draw.rect(screen, GREEN, (square_x - square_size//2, square_y - square_size//2, square_size, square_size))
        
        # Draw player (red circle)
        pygame.draw.circle(screen, RED, (circle_x, circle_y), circle_radius)
        
        # Update display
        pygame.display.flip()
        
        # Cap at 60 FPS
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()