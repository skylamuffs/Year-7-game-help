'''Version 6 - from simple math to year 7 math '''
import pygame
import sys
import random
from fractions import Fraction

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Samurai Math Duel")

# Colors
BACKGROUND = (30, 30, 40)
PLAYER_COLOR = (255, 80, 80)    # Red
ENEMY_COLOR = (80, 80, 255)     # Blue
WHITE = (255, 255, 255)

# Fonts
question_font = pygame.font.SysFont('Arial', 32, bold=True)
button_font = pygame.font.SysFont('Arial', 24)
health_font = pygame.font.SysFont('Arial', 20, bold=True)

# Load sword images
try:
    sword_img = pygame.image.load("Sword_Enemy.png").convert_alpha()
    sword_img = pygame.transform.scale(sword_img, (60, 60))
    player_sword = sword_img
    antagonist_sword = pygame.transform.flip(sword_img, True, False)
except:
    print("Sword image not found, using rectangles")
    sword_img = None

# Math Question Generator
def generate_math_question():
    question_type = random.choice([
        'fraction_addition', 
        'decimal_conversion', 
        'percentage', 
        'basic_algebra',
        'fraction_of_quantity'
    ])
    
    if question_type == 'fraction_addition':
        a = Fraction(random.randint(1, 3), random.randint(2, 4))
        b = Fraction(random.randint(1, 3), random.randint(2, 4))
        question = f"{a} + {b} = ?"
        answer = a + b
    elif question_type == 'decimal_conversion':
        frac = Fraction(random.randint(1, 4), random.randint(2, 5))
        question = f"Convert {frac} to a decimal"
        answer = float(frac)
    elif question_type == 'percentage':
        num = random.randint(1, 20) * 5
        quantity = random.randint(10, 100)
        question = f"{num}% of {quantity} = ?"
        answer = round(num / 100 * quantity, 2)
    elif question_type == 'basic_algebra':
        x = random.randint(2, 5)
        coeff = random.randint(2, 5)
        const = random.randint(1, 10)
        question = f"If {coeff}x + {const} = {coeff*x + const}, x = ?"
        answer = x
    elif question_type == 'fraction_of_quantity':
        frac = Fraction(random.randint(1, 3), random.randint(2, 4))
        quantity = random.randint(10, 50)
        question = f"Find {frac} of {quantity}"
        answer = frac * quantity
    
    # Generate wrong answers
    answers = [answer]
    while len(answers) < 3:
        if isinstance(answer, (int, float)):
            wrong = answer * random.choice([0.5, 1.5, 2])
        elif isinstance(answer, Fraction):
            wrong = answer + Fraction(1, random.randint(2, 5))
        if wrong not in answers:
            answers.append(wrong)
    
    random.shuffle(answers)
    return question, answer, answers

# Fighter class
class Fighter:
    def __init__(self, x, y, size, color, is_player):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.original_pos = (x, y)
        self.health = 100
        self.is_attacking = False
        self.attack_progress = 0
        self.is_player = is_player
        self.speed = 5
        
    def draw(self, surface):
        # Draw fighter body
        pygame.draw.rect(surface, self.color, 
                       (self.x - self.size//2, 
                        self.y - self.size//2, 
                        self.size, self.size))
        
        # Draw sword if image exists
        if sword_img:
            if self.is_attacking:
                # Rotate sword when attacking
                if self.is_player:
                    sword = pygame.transform.rotate(player_sword, -45)  # Player swings forward
                    pos = (self.x + self.size//2 + 20, self.y)  # Position during attack
                else:
                    sword = pygame.transform.rotate(antagonist_sword, 45)  # Enemy swings forward
                    pos = (self.x - self.size//2 - 20, self.y)  # Position during attack
            else:
                # Normal sword position when not attacking
                sword = player_sword if self.is_player else antagonist_sword
                pos = (self.x + self.size//2, self.y) if self.is_player else (self.x - self.size//2, self.y)
            
            # Draw the sword
            sword_rect = sword.get_rect(center=pos)
            surface.blit(sword, sword_rect)
    
    def attack(self, target):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_progress = 0
            
    def update(self):
        if self.is_attacking:
            self.attack_progress += 0.08
            
            target = antagonist if self.is_player else player
            self.x = self.original_pos[0] + (target.x - self.original_pos[0]) * self.attack_progress
            self.y = self.original_pos[1] + (target.y - self.original_pos[1]) * self.attack_progress
            
            if self.attack_progress >= 1:
                self.is_attacking = False
                self.x, self.y = self.original_pos
                return True  # Attack completed
        return False

# Button class
class AnswerButton:
    def __init__(self, x, y, width, height, answer, index):
        self.rect = pygame.Rect(x, y, width, height)
        self.answer = answer
        self.color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.text_color = WHITE
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered() else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2)
        
        if isinstance(self.answer, Fraction):
            answer_text = f"{self.answer.numerator}/{self.answer.denominator}"
        else:
            answer_text = str(round(self.answer, 2)) if isinstance(self.answer, float) else str(self.answer)
        
        text = button_font.render(answer_text, True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# Create fighters
player = Fighter(WIDTH//4, HEIGHT//2, 50, PLAYER_COLOR, True)
antagonist = Fighter(3*WIDTH//4, HEIGHT//2, 50, ENEMY_COLOR, False)

# Game setup
current_question, correct_answer, answers = generate_math_question()

# Centered button configuration
button_width = 160
button_height = 60
button_margin = 20
total_buttons_width = 3 * button_width + 2 * button_margin
start_x = (WIDTH - total_buttons_width) // 2

buttons = [
    AnswerButton(
        start_x + i * (button_width + button_margin),
        HEIGHT - 120,  # Moved up slightly from bottom
        button_width,
        button_height,
        answers[i],
        i
    ) for i in range(3)
]

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        
        # Handle button clicks
        if not player.is_attacking and not antagonist.is_attacking:
            for button in buttons:
                if button.is_clicked(event):
                    if button.answer == correct_answer:
                        player.attack(antagonist)
                    else:
                        antagonist.attack(player)
                    # Generate new question
                    current_question, correct_answer, answers = generate_math_question()
                    for i, btn in enumerate(buttons):
                        btn.answer = answers[i]
    
    # Update attacks
    if player.update():
        antagonist.health = max(0, antagonist.health - 10)
    if antagonist.update():
        player.health = max(0, player.health - 10)
    
    # Draw everything
    screen.fill(BACKGROUND)
    
    # Draw health bars
    pygame.draw.rect(screen, (50, 50, 50), (20, 20, 204, 24), 2)
    pygame.draw.rect(screen, PLAYER_COLOR, (22, 22, 2*player.health, 20))
    pygame.draw.rect(screen, (50, 50, 50), (WIDTH-224, 20, 204, 24), 2)
    pygame.draw.rect(screen, ENEMY_COLOR, (WIDTH-222, 22, 2*antagonist.health, 20))
    
    health_text = health_font.render(f"Health: {player.health}", True, WHITE)
    screen.blit(health_text, (20, 50))
    health_text = health_font.render(f"Health: {antagonist.health}", True, WHITE)
    screen.blit(health_text, (WIDTH-150, 50))
    
    # Draw question
    question_text = question_font.render(current_question, True, WHITE)
    screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 50))
    
    # Draw buttons
    if not player.is_attacking and not antagonist.is_attacking:
        for button in buttons:
            button.draw(screen)
    
    # Draw fighters with swords
    player.draw(screen)
    antagonist.draw(screen)
    
    # Draw damage numbers
    if player.is_attacking and player.attack_progress > 0.9:
        damage_text = health_font.render("-10", True, PLAYER_COLOR)
        screen.blit(damage_text, (antagonist.x-15, antagonist.y-50))
    if antagonist.is_attacking and antagonist.attack_progress > 0.9:
        damage_text = health_font.render("-10", True, ENEMY_COLOR)
        screen.blit(damage_text, (player.x-15, player.y-50))
    
    # Check for game over
    if player.health <= 0 or antagonist.health <= 0:
        if player.health <= 0:
            result = "You got killed by the Enemy"
            color = ENEMY_COLOR
        else:
            result = "You have defeated an Enemy"
            color = PLAYER_COLOR
        
        game_over_text = question_font.render(result, True, color)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()