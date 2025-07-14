'''Version 1 - Making a screen '''
import pygame
import sys

def main():
    # Initialize Pygame
    pygame.init()
    
    # Set up the display
    screen_width = 800
    screen_height = 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Samurai Math")
    
    # Main game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Clear the screen with black
        screen.fill((0, 0, 0))
        
        # Update the display
        pygame.display.flip()
    
    # Clean up and quit
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()