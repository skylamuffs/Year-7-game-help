'''Version 12 - Making a starting screen '''

import pygame
import os
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

def load_image(filename):
    """Load an image with comprehensive error handling"""
    try:
        # Check multiple possible locations
        search_paths = [
            os.path.join(os.path.dirname(__file__), filename),
            os.path.join(os.path.dirname(__file__), 'images', filename),
            filename
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                img = pygame.image.load(path)
                return img.convert()  # Convert for better performance
        
        # If not found anywhere
        raise FileNotFoundError(f"'{filename}' not found in: {search_paths}")
    
    except Exception as e:
        print(f"Error loading {filename}: {str(e)}")
        # Create helpful placeholder
        placeholder = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        placeholder.fill((30, 30, 60))  # Dark blue
        
        font = pygame.font.SysFont('Arial', 24)
        lines = [
            f"Missing: {filename}",
            "Please place the file in:",
            os.path.dirname(__file__),
            "or in an /images subfolder"
        ]
        
        for i, line in enumerate(lines):
            text = font.render(line, True, (255, 255, 255))
            y_pos = SCREEN_HEIGHT//2 - 40 + (i * 30)
            placeholder.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y_pos))
        
        return placeholder

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Samurai Math - Starting Screen")
        
        # Load all screens (but only show starting screen)
        self.screens = {
            'start': pygame.transform.scale(load_image('Starting_screen.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
            # These are loaded but not shown:
            'intro': pygame.transform.scale(load_image('intro.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
            'rules': pygame.transform.scale(load_image('Rules.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
            'game': pygame.transform.scale(load_image('actual_game.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))
        }
        
        self.current_screen = 'start'  # Only showing starting screen
        self.clock = pygame.time.Clock()
        self.running = True
    
    def run(self):
        while self.running:
            self.handle_events()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def render(self):
        # Only show the starting screen
        self.screen.blit(self.screens['start'], (0, 0))
        
        # Optional: Add exit hint (can remove later)
        font = pygame.font.SysFont('Arial', 20)
        hint = font.render("Press ESC to exit", True, (255, 255, 255))
        self.screen.blit(hint, (20, SCREEN_HEIGHT - 30))
        
        pygame.display.flip()

if __name__ == "__main__":
    # Verify starting screen exists
    start_img_path = os.path.join(os.path.dirname(__file__), 'Starting_screen.jpg')
    if not os.path.exists(start_img_path):
        print(f"Warning: Starting screen image not found at {start_img_path}")
        print("A placeholder will be shown instead")
    
    game = Game()
    game.run()