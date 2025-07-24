'''Version 8 - from simple math to year 7 math '''
import pygame
import sys
import random
from fractions import Fraction

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Samurai Math")

# Colors
BACKGROUND = (30, 30, 40)
PLAYER_COLOR = (255, 80, 80)    # Red
ENEMY_COLOR = (80, 80, 255)     # Blue
WHITE = (255, 255, 255)
TITLE_COLOR = (255, 215, 0)     # Gold color for text

# Fonts
title_font = pygame.font.SysFont('Arial', 64, bold=True)
subtitle_font = pygame.font.SysFont('Arial', 36, bold=True)
question_font = pygame.font.SysFont('Arial', 32, bold=True)
button_font = pygame.font.SysFont('Arial', 24)
health_font = pygame.font.SysFont('Arial', 20, bold=True)
start_font = pygame.font.SysFont('Arial', 28, bold=True)

# Load images
try:
    sword_img = pygame.image.load("Sword_Enemy.png").convert_alpha()
    sword_img = pygame.transform.scale(sword_img, (60, 60))
    player_sword = sword_img
    antagonist_sword = pygame.transform.flip(sword_img, True, False)
except:
    print("Sword image not found, using rectangles")
    sword_img = None

try:
    title_background = pygame.image.load("Title_page.jpg").convert()  
    title_background = pygame.transform.scale(title_background, (WIDTH, HEIGHT))
except:
    print("Background image not found, using solid color")
    title_background = None

# Title Screen Button
class StartButton:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - 100, HEIGHT - 150, 200, 60)
        self.color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.text_color = WHITE
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered() else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2, border_radius=10)
        
        text = start_font.render("START", True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

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
            wrong = round(wrong, 2) if isinstance(answer, float) else wrong
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
        pygame.draw.rect(surface, self.color, 
                       (self.x - self.size//2, 
                        self.y - self.size//2, 
                        self.size, self.size))
        
        if sword_img:
            if self.is_attacking:
                if self.is_player:
                    sword = pygame.transform.rotate(player_sword, -45) 
                    pos = (self.x + self.size//2 + 20, self.y) 
                else:
                    sword = pygame.transform.rotate(antagonist_sword, 45) 
                    pos = (self.x - self.size//2 - 20, self.y)  
            else:
                sword = player_sword if self.is_player else antagonist_sword
                pos = (self.x + self.size//2, self.y) if self.is_player else (self.x - self.size//2, self.y)
            
            sword_rect = sword.get_rect(center=pos)
            surface.blit(sword, sword_rect)
    
    def attack(self, target):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_progress = 0
            
    def update(self):
        if self.is_attacking:
            self.attack_progress += 0.08
            
            target_x = WIDTH//4 if self.is_player else 3*WIDTH//4
            target_y = HEIGHT//2
            self.x = self.original_pos[0] + (target_x - self.original_pos[0]) * self.attack_progress
            self.y = self.original_pos[1] + (target_y - self.original_pos[1]) * self.attack_progress
            
            if self.attack_progress >= 1:
                self.is_attacking = False
                self.x, self.y = self.original_pos
                return True  
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
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2, border_radius=5)
        
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
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

def show_title_screen():
    start_button = StartButton()
    waiting = True
    
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_RETURN:
                    waiting = False
            if start_button.is_clicked(event):
                waiting = False
        
        # Draw title screen
        if title_background:
            screen.blit(title_background, (0, 0))
        else:
            screen.fill(BACKGROUND)
        
        # Draw title text
        title_text = title_font.render("SAMURAI MATH", True, TITLE_COLOR)
        subtitle_text = subtitle_font.render("Year 7 Math Challenge", True, WHITE)
        
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
        screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//3 + 50))
        
        # Draw start button
        start_button.draw(screen)
        pygame.display.flip()

# Main game function
def main_game():
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
            HEIGHT - 120,
            button_width,
            button_height,
            answers[i],
            i
        ) for i in range(3)
    ]

    # Game loop
    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            if not player.is_attacking and not antagonist.is_attacking:
                for button in buttons:
                    if button.is_clicked(event):
                        if button.answer == correct_answer:
                            player.attack(antagonist)
                        else:
                            antagonist.attack(player)
                        current_question, correct_answer, answers = generate_math_question()
                        for i, btn in enumerate(buttons):
                            btn.answer = answers[i]
        
        # Update attacks
        player_attack_hit = player.update()
        antagonist_attack_hit = antagonist.update()
        
        if player_attack_hit:
            antagonist.health = max(0, antagonist.health - 10)
        if antagonist_attack_hit:
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
        if player_attack_hit:
            damage_text = health_font.render("-10", True, PLAYER_COLOR)
            screen.blit(damage_text, (antagonist.x-15, antagonist.y-50))
        if antagonist_attack_hit:
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

# Run the game
show_title_screen()
main_game()

pygame.quit()
sys.exit()
