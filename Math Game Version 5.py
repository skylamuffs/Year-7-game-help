'''Version 5 - adding math problems '''

import pygame
import sys
import random

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Samurai Math")

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

# Combatants
class Fighter:
    def __init__(self, x, y, size, color, speed, is_player):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.speed = speed
        self.original_pos = (x, y)
        self.health = 100
        self.is_attacking = False
        self.attack_progress = 0
        self.is_player = is_player
        
    def draw(self, surface):
        # Draw fighter body
        pygame.draw.rect(surface, self.color, 
                        (self.x - self.size//2, 
                         self.y - self.size//2, 
                         self.size, self.size))
        
        # Draw sword
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
        self.is_attacking = True
        self.attack_progress = 0
        
    def update(self):
        if self.is_attacking:
            self.attack_progress += 0.1
            if self.attack_progress < 1:
                # Move toward opponent during attack
                if self.is_player:
                    self.x = self.original_pos[0] + (antagonist.x - self.original_pos[0]) * self.attack_progress
                    self.y = self.original_pos[1] + (antagonist.y - self.original_pos[1]) * self.attack_progress
                else:
                    self.x = self.original_pos[0] + (player.x - self.original_pos[0]) * self.attack_progress
                    self.y = self.original_pos[1] + (player.y - self.original_pos[1]) * self.attack_progress
            else:
                # Return to original position
                self.is_attacking = False
                self.x, self.y = self.original_pos
                return True  
        return False

# Create fighters
player = Fighter(WIDTH//4, HEIGHT//2, 40, RED, 5, True)
antagonist = Fighter(3*WIDTH//4, HEIGHT//2, 50, BLUE, 5, False)

# Math system
def generate_question():
    a, b = random.randint(1, 10), random.randint(1, 10)
    op = random.choice(['+', '-', '*'])
    answer = eval(f"{a}{op}{b}")
    question = f"{a} {op} {b} = ?"
    
    # Generate 2 wrong answers
    answers = [answer]
    while len(answers) < 3:
        wrong = answer + random.choice([-1,1]) * random.randint(1,5)
        if wrong != answer and wrong not in answers:
            answers.append(wrong)
    random.shuffle(answers)
    return question, answer, answers

class AnswerButton:
    def __init__(self, x, y, width, height, answer, index):
        self.rect = pygame.Rect(x, y, width, height)
        self.answer = answer
        self.color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.font = pygame.font.SysFont('Arial', 24)
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered() else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2)
        
        text = self.font.render(str(self.answer), True, WHITE)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# Game setup
current_question, correct_answer, answers = generate_question()
buttons = [AnswerButton(200 + i*150, HEIGHT-80, 100, 50, answers[i], i) for i in range(3)]
font = pygame.font.SysFont('Arial', 32)
damage_font = pygame.font.SysFont('Arial', 24, bold=True)
clock = pygame.time.Clock()

# Game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                
        # Answer selection
        if not player.is_attacking and not antagonist.is_attacking:
            for button in buttons:
                if button.is_clicked(event):
                    if button.answer == correct_answer:
                        player.attack(antagonist)
                    else:
                        antagonist.attack(player)
                    # New question
                    current_question, correct_answer, answers = generate_question()
                    for i, btn in enumerate(buttons):
                        btn.answer = answers[i]
    
    # Movement (only when not attacking)
    keys = pygame.key.get_pressed()
    if not player.is_attacking:
        if keys[pygame.K_a] and player.x > player.size//2:
            player.x -= player.speed
            player.original_pos = (player.x, player.y)
        if keys[pygame.K_d] and player.x < WIDTH - player.size//2:
            player.x += player.speed
            player.original_pos = (player.x, player.y)
        if keys[pygame.K_w] and player.y > player.size//2:
            player.y -= player.speed
            player.original_pos = (player.x, player.y)
        if keys[pygame.K_s] and player.y < HEIGHT - player.size//2:
            player.y += player.speed
            player.original_pos = (player.x, player.y)
    
    if not antagonist.is_attacking:
        if keys[pygame.K_LEFT] and antagonist.x > antagonist.size//2:
            antagonist.x -= antagonist.speed
            antagonist.original_pos = (antagonist.x, antagonist.y)
        if keys[pygame.K_RIGHT] and antagonist.x < WIDTH - antagonist.size//2:
            antagonist.x += antagonist.speed
            antagonist.original_pos = (antagonist.x, antagonist.y)
        if keys[pygame.K_UP] and antagonist.y > antagonist.size//2:
            antagonist.y -= antagonist.speed
            antagonist.original_pos = (antagonist.x, antagonist.y)
        if keys[pygame.K_DOWN] and antagonist.y < HEIGHT - antagonist.size//2:
            antagonist.y += antagonist.speed
            antagonist.original_pos = (antagonist.x, antagonist.y)
    
    # Update attacks
    if player.update():  # Returns True when attack completes
        antagonist.health -= 10
    if antagonist.update():
        player.health -= 10
    
    # Drawing
    screen.fill(BACKGROUND)
    
    # Health bars
    pygame.draw.rect(screen, RED, (20, 20, player.health * 2, 20))
    pygame.draw.rect(screen, BLUE, (WIDTH-220, 20, antagonist.health * 2, 20))
    health_text = font.render(f"{player.health}", True, WHITE)
    screen.blit(health_text, (20, 45))
    health_text = font.render(f"{antagonist.health}", True, WHITE)
    screen.blit(health_text, (WIDTH-70, 45))
    
    # Question
    question_text = font.render(current_question, True, WHITE)
    screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 50))
    
    # Answer buttons
    if not player.is_attacking and not antagonist.is_attacking:
        for button in buttons:
            button.draw(screen)
    
    # Draw fighters
    player.draw(screen)
    antagonist.draw(screen)
    
    # Damage indicators
    if player.is_attacking and player.attack_progress > 0.9:
        damage_text = damage_font.render("-10", True, RED)
        screen.blit(damage_text, (antagonist.x-15, antagonist.y-50))
    if antagonist.is_attacking and antagonist.attack_progress > 0.9:
        damage_text = damage_font.render("-10", True, BLUE)
        screen.blit(damage_text, (player.x-15, player.y-50))
    
    # Game over checks
    if player.health <= 0 or antagonist.health <= 0:
        if player.health <= 0:
            result = "DEFEAT!"
            color = BLUE
        else:
            result = "VICTORY!"
            color = RED
        
        game_over_text = font.render(result, True, color)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()