'''Version 11 - Adding Tutorial System'''
'''Samurai Math Game - Complete Version with Sound Effects'''
import pygame
import sys
import random
import os
import time
import numpy
from fractions import Fraction

# Initialize pygame
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Samurai Math")

# Colors
BACKGROUND = (30, 30, 40)
PLAYER_COLOR = (255, 80, 80)
ENEMY_COLOR = (80, 80, 255)
WHITE = (255, 255, 255)
TITLE_COLOR = (255, 215, 0)
BLACK = (0, 0, 0)
TUTORIAL_COLOR = (50, 70, 90)

# Fonts
title_font = pygame.font.SysFont('Arial', 64, bold=True)
subtitle_font = pygame.font.SysFont('Arial', 32, bold=True)
question_font = pygame.font.SysFont('Arial', 28, bold=True)
button_font = pygame.font.SysFont('Arial', 24)
health_font = pygame.font.SysFont('Arial', 20, bold=True)
start_font = pygame.font.SysFont('Arial', 28, bold=True)
result_font = pygame.font.SysFont('Arial', 48, bold=True)
warning_font_large = pygame.font.SysFont('Arial', 72, bold=True)
warning_font = pygame.font.SysFont('Arial', 28)
tutorial_font = pygame.font.SysFont('Arial', 22)
tutorial_title_font = pygame.font.SysFont('Arial', 36, bold=True)
tutorial_math_font = pygame.font.SysFont('Arial', 24, bold=True)

def load_image(filename, scale=None, alpha=True):
    try:
        if alpha:
            img = pygame.image.load(filename).convert_alpha()
        else:
            img = pygame.image.load(filename).convert()
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except pygame.error as e:
        print(f"Error loading image {filename}: {e}")
        if scale:
            surf = pygame.Surface(scale, pygame.SRCALPHA if alpha else 0)
        else:
            surf = pygame.Surface((100, 100), pygame.SRCALPHA if alpha else 0)
        surf.fill((0, 0, 0, 0))
        return surf

# Load game images
sword_img = load_image("Sword_Enemy.png", (60, 60)) or pygame.Surface((60, 60), pygame.SRCALPHA)
player_sword = sword_img
antagonist_sword = pygame.transform.flip(sword_img, True, False)

title_background = load_image("Title_page.jpg", (WIDTH, HEIGHT), alpha=False) or pygame.Surface((WIDTH, HEIGHT))
game_over_img = load_image("Game_Over.jpg", (WIDTH, HEIGHT)) or pygame.Surface((WIDTH, HEIGHT))
victory_img = load_image("Win.jpg", (WIDTH, HEIGHT)) or pygame.Surface((WIDTH, HEIGHT))
warning_img = load_image("Warning.png", (WIDTH, HEIGHT)) or pygame.Surface((WIDTH, HEIGHT))

def generate_beep_sound(frequency=440, duration=0.5):
    """Generate a simple beep sound using pygame's mixer"""
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
    
    for s in range(n_samples):
        t = float(s) / sample_rate
        buf[s][0] = int(32767 * numpy.sin(2 * numpy.pi * frequency * t))
        buf[s][1] = int(32767 * numpy.sin(2 * numpy.pi * frequency * t))
    
    return pygame.sndarray.make_sound(buf)

class StoryNarration:
    def __init__(self):
        self.story_segments = [
            {"audio": "Voice_1.mp3", "duration": 23.0, "images": [
                ("Voice_1_image.png", 8.0),
                ("Voice_1_image_2.png", 7.5),
                ("Voice_1_image_3.png", 7.5)]},
            {"audio": "Voice_2.mp3", "duration": 21.0, "images": [
                ("Voice_2_image.png", 7.0),
                ("Voice_2_image_2.png", 7.0),
                ("Voice_2_image_3.png", 7.0)]},
            {"audio": "Voice_3.mp3", "duration": 15.0, "images": [
                ("Voice_3_image.png", 15.0)]},
            {"audio": "Voice_4.mp3", "duration": 21.0, "images": [
                ("Voice_4_image.png", 10.0),
                ("Voice_4_image_2.png", 11.0)]}
        ]
        self.current_segment = 0
        self.current_image = 0
        self.active = False
        self.sounds = []
        self.images = {}
        self.start_time = 0
        self.image_start_time = 0
        self.load_assets()
        
    def load_assets(self):
        for segment in self.story_segments:
            for img_file, _ in segment["images"]:
                if img_file not in self.images:
                    loaded_img = load_image(img_file, (WIDTH, HEIGHT))
                    self.images[img_file] = loaded_img if loaded_img else pygame.Surface((WIDTH, HEIGHT))
        
        for segment in self.story_segments:
            audio_file = segment["audio"]
            try:
                if os.path.exists(audio_file):
                    sound = pygame.mixer.Sound(audio_file)
                    self.sounds.append(sound)
                else:
                    print(f"Audio file not found: {audio_file}")
                    self.sounds.append(None)
            except pygame.error as e:
                print(f"Error loading sound {audio_file}: {e}")
                self.sounds.append(None)
    
    def start(self):
        self.current_segment = 0
        self.current_image = 0
        self.active = True
        self.start_time = time.time()
        self.image_start_time = time.time()
        self.play_current_audio()
    
    def play_current_audio(self):
        pygame.mixer.stop()
        if 0 <= self.current_segment < len(self.sounds) and self.sounds[self.current_segment]:
            self.sounds[self.current_segment].play()
    
    def update_image(self):
        segment = self.story_segments[self.current_segment]
        current_image_duration = segment["images"][self.current_image][1]
        
        if time.time() - self.image_start_time > current_image_duration:
            self.current_image += 1
            self.image_start_time = time.time()
            
            if self.current_image >= len(segment["images"]):
                self.next_segment()
    
    def next_segment(self):
        pygame.mixer.stop()
        self.current_segment += 1
        self.current_image = 0
        self.image_start_time = time.time()
        self.start_time = time.time()
        
        if self.current_segment < len(self.story_segments):
            self.play_current_audio()
        else:
            self.active = False
    
    def update(self):
        if not self.active:
            return False
            
        segment = self.story_segments[self.current_segment]
        
        if time.time() - self.start_time > segment["duration"]:
            self.next_segment()
        else:
            self.update_image()
        
        return self.active
    
    def draw(self, surface):
        if not self.active:
            return
            
        segment = self.story_segments[self.current_segment]
        img_file = segment["images"][self.current_image][0]
        bg = self.images.get(img_file, pygame.Surface((WIDTH, HEIGHT)))
        
        surface.blit(bg, (0, 0))

class StartButton:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - 120, HEIGHT - 180, 240, 60)
        self.color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.text_color = WHITE
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered() else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 3, border_radius=10)
        
        text = start_font.render("START", True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

class TutorialButton:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2 - 120, HEIGHT - 100, 240, 60)
        self.color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.text_color = WHITE
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered() else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 3, border_radius=10)
        
        text = start_font.render("TUTORIAL", True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
    def is_hovered(self):
        return self.rect.collidepoint(pygame.mouse.get_pos())
    
    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

def show_tutorial_screen():
    tutorial_pages = [
        [
            "HOW TO PLAY",
            "",
            "• You are a math samurai fighting against an enemy",
            "• Answer math questions correctly to attack",
            "• Wrong answers let the enemy attack you",
            "• Reduce enemy health to 0 to win",
            "• Keep your health above 0 to survive",
            "",
            "Controls:",
            "• Click on answers with mouse",
            "• ESC to return to title screen"
        ],
        [
            "MATH CONCEPTS IN THE GAME",
            "",
            "left:Fraction Addition:|right:Basic Algebra:",
            "left:   Example: 1/2 + 1/4 = 3/4|right:   Example: If 2x + 3 = 7, then x = 2",
            "",
            "left:Decimal Conversion:|right:Fraction of Quantity:",
            "left:   Example: 1/4 = 0.25|right:   Example: 1/3 of 30 = 10",
            "",
            "left:Percentages:",
            "left:   Example: 20% of 50 = 10",
            "",
            "Page 2/3"
        ],
        [
            "TIPS FOR SUCCESS",
            "",
            "• Take your time - no time limit",
            "• Simplify fractions when possible",
            "• For decimal conversions, think of fractions as division",
            "• For percentages, remember 'of' means multiply",
            "• Check your work before answering",
            "",
            "Press any key to continue..."
        ]
    ]
    
    current_page = 0
    waiting = True
    clock = pygame.time.Clock()
    
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                else:
                    current_page += 1
                    if current_page >= len(tutorial_pages):
                        waiting = False
                        current_page = len(tutorial_pages) - 1
            if event.type == pygame.MOUSEBUTTONDOWN:
                current_page += 1
                if current_page >= len(tutorial_pages):
                    waiting = False
                    current_page = len(tutorial_pages) - 1
        
        current_page = max(0, min(current_page, len(tutorial_pages) - 1)
        
        screen.fill(TUTORIAL_COLOR)
        
        page_content = tutorial_pages[current_page]
        title = tutorial_title_font.render(page_content[0], True, TITLE_COLOR)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        
        y_pos = 100
        
        for line in page_content[1:]:
            if line.strip() == "":
                y_pos += 20
                continue
            
            if line.startswith("Page"):
                page_text = button_font.render(line, True, WHITE)
                screen.blit(page_text, (WIDTH - 100, HEIGHT - 40))
                continue
            
            if "|" in line:
                left_part, right_part = line.split("|")
                left_text = left_part.replace("left:", "")
                right_text = right_part.replace("right:", "")
                
                if left_text.strip():
                    text = tutorial_font.render(left_text, True, WHITE)
                    screen.blit(text, (WIDTH//4 - text.get_width()//2, y_pos))
                
                if right_text.strip():
                    text = tutorial_font.render(right_text, True, WHITE)
                    screen.blit(text, (3*WIDTH//4 - text.get_width()//2, y_pos))
                
                y_pos += 30
            else:
                if line.startswith("left:"):
                    line = line.replace("left:", "")
                
                text = tutorial_font.render(line, True, WHITE)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, y_pos))
                y_pos += 30
        
        if current_page == len(tutorial_pages) - 1:
            continue_text = button_font.render("Click or press any key to continue...", True, TITLE_COLOR)
            screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT - 80))
        
        pygame.display.flip()
        clock.tick(60)

def fade_in_out_warning():
    clock = pygame.time.Clock()
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill(BLACK)
    
    for alpha in range(0, 256, 5):
        if warning_img:
            screen.blit(warning_img, (0, 0))
        else:
            screen.fill(BLACK)
            warning_title = warning_font_large.render("WARNING", True, (255, 80, 80))
            screen.blit(warning_title, (WIDTH//2 - warning_title.get_width()//2, HEIGHT//4))
        
        fade_surface.set_alpha(255 - alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return
    
    if warning_img:
        screen.blit(warning_img, (0, 0))
    else:
        screen.fill(BLACK)
        warning_title = warning_font_large.render("WARNING", True, (255, 80, 80))
        screen.blit(warning_title, (WIDTH//2 - warning_title.get_width()//2, HEIGHT//4))
        
        warning_lines = [
            "This game contains intense math battles!",
            "Prepare your brain for the challenge!",
            "",
            "Press any key to continue..."
        ]
        
        for i, line in enumerate(warning_lines):
            text = warning_font.render(line, True, WHITE)
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + i * 40))
    
    pygame.display.flip()
    
    start_time = pygame.time.get_ticks()
    waiting = True
    while waiting:
        current_time = pygame.time.get_ticks()
        if current_time - start_time > 2000:
            waiting = False
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        clock.tick(60)
    
    for alpha in range(0, 256, 5):
        if warning_img:
            screen.blit(warning_img, (0, 0))
        else:
            screen.fill(BLACK)
            warning_title = warning_font_large.render("WARNING", True, (255, 80, 80))
            screen.blit(warning_title, (WIDTH//2 - warning_title.get_width()//2, HEIGHT//4))
            
            for i, line in enumerate(warning_lines):
                text = warning_font.render(line, True, WHITE)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + i * 40))
        
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

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
        self.speed = 5 * (WIDTH / 800)
        
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
                pos = (self.x + self.size//2 + 5, self.y) if self.is_player else (self.x - self.size//2 - 5, self.y)
            
            sword_rect = sword.get_rect(center=pos)
            surface.blit(sword, sword_rect)
    
    def attack(self, target):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_progress = 0
            
    def update(self, target):
        if self.is_attacking:
            self.attack_progress += 0.08
            self.x = self.original_pos[0] + (target.x - self.original_pos[0]) * self.attack_progress
            self.y = self.original_pos[1] + (target.y - self.original_pos[1]) * self.attack_progress
            
            if self.attack_progress >= 1:
                self.is_attacking = False
                self.x, self.y = self.original_pos
                return True
        return False

class AnswerButton:
    def __init__(self, x, y, width, height, answer, index):
        self.rect = pygame.Rect(x, y, width, height)
        self.answer = answer
        self.color = (70, 70, 70)
        self.hover_color = (100, 100, 100)
        self.text_color = WHITE
        
    def draw(self, surface):
        color = self.hover_color if self.is_hovered() else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 2, border_radius=6)
        
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

def show_game_over_screen(player_won):
    waiting = True
    clock = pygame.time.Clock()
    
    # Generate simple victory/defeat sounds
    try:
        if player_won:
            # High-pitched victory sound (G5 to C6)
            victory_sound1 = generate_beep_sound(784, 0.3)
            victory_sound1.play()
            pygame.time.delay(100)
            victory_sound2 = generate_beep_sound(1046, 0.3)
            victory_sound2.play()
        else:
            # Low-pitched defeat sound (A3 to G3)
            defeat_sound1 = generate_beep_sound(220, 0.5)
            defeat_sound1.play()
            pygame.time.delay(300)
            defeat_sound2 = generate_beep_sound(196, 0.5)
            defeat_sound2.play()
    except:
        print("Could not generate game over sound")
    
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        
        if player_won:
            if victory_img:
                screen.blit(victory_img, (0, 0))
            else:
                screen.fill(BACKGROUND)
                result_text = result_font.render("VICTORY!", True, (0, 0, 0))
                screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 - 50))
        else:
            if game_over_img:
                screen.blit(game_over_img, (0, 0))
            else:
                screen.fill(BACKGROUND)
                result_text = result_font.render("DEFEAT", True, (200, 150, 0))
                screen.blit(result_text, (WIDTH//2 - result_text.get_width()//2, HEIGHT//2 - 50))
        
        if player_won:
            message = subtitle_font.render("You defeated the enemy!", True, (0, 0, 0))
        else:
            message = subtitle_font.render("You were defeated in battle...", True, (200, 150, 0))
        
        screen.blit(message, (WIDTH//2 - message.get_width()//2, HEIGHT - 150))
        continue_text = button_font.render("Press any key to continue", True, TITLE_COLOR)
        screen.blit(continue_text, (WIDTH//2 - continue_text.get_width()//2, HEIGHT - 100))
        
        pygame.display.flip()
        clock.tick(60)

def show_title_screen():
    global story
    start_button = StartButton()
    tutorial_button = TutorialButton()
    
    if not hasattr(show_title_screen, "story_shown"):
        story.start()
        show_title_screen.story_shown = True
    
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
                    story.active = False
                    fade_in_out_warning()
                    waiting = False
                else:
                    story.active = False
            if start_button.is_clicked(event):
                story.active = False
                fade_in_out_warning()
                waiting = False
            if tutorial_button.is_clicked(event):
                story.active = False
                show_tutorial_screen()
        
        if story.active:
            if not story.update():
                story.active = False
        
        if story.active:
            story.draw(screen)
        else:
            if title_background:
                screen.blit(title_background, (0, 0))
            else:
                screen.fill(BACKGROUND)
            
            title_text = title_font.render("SAMURAI MATH", True, TITLE_COLOR)
            subtitle_text = subtitle_font.render("Year 7 Math Challenge", True, WHITE)
            
            screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
            screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//3 + 60))
            
            start_button.draw(screen)
            tutorial_button.draw(screen)
        
        pygame.display.flip()

def main_game():
    player = Fighter(WIDTH//4, HEIGHT//2, 60, PLAYER_COLOR, True)
    antagonist = Fighter(3*WIDTH//4, HEIGHT//2, 60, ENEMY_COLOR, False)

    current_question, correct_answer, answers = generate_math_question()

    button_width = 180
    button_height = 60
    button_margin = 20
    total_buttons_width = 3 * button_width + 2 * button_margin
    start_x = (WIDTH - total_buttons_width) // 2

    buttons = [
        AnswerButton(
            start_x + i * (button_width + button_margin),
            HEIGHT - 130,
            button_width,
            button_height,
            answers[i],
            i
        ) for i in range(3)
    ]

    running = True
    clock = pygame.time.Clock()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    return False
            
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
        
        player_attack_hit = player.update(antagonist)
        antagonist_attack_hit = antagonist.update(player)
        
        if player_attack_hit:
            antagonist.health = max(0, antagonist.health - 10)
        if antagonist_attack_hit:
            player.health = max(0, player.health - 10)
        
        screen.fill(BACKGROUND)
        
        pygame.draw.rect(screen, (50, 50, 50), (50, 40, 250, 20), 2)
        pygame.draw.rect(screen, PLAYER_COLOR, (52, 42, 2.5*player.health, 16))
        pygame.draw.rect(screen, (50, 50, 50), (WIDTH-300, 40, 250, 20), 2)
        pygame.draw.rect(screen, ENEMY_COLOR, (WIDTH-298, 42, 2.5*antagonist.health, 16))
        
        health_text = health_font.render(f"Health: {player.health}", True, WHITE)
        screen.blit(health_text, (50, 70))
        health_text = health_font.render(f"Health: {antagonist.health}", True, WHITE)
        screen.blit(health_text, (WIDTH-250, 70))
        
        question_text = question_font.render(current_question, True, WHITE)
        screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 60))
        
        if not player.is_attacking and not antagonist.is_attacking:
            for button in buttons:
                button.draw(screen)
        
        player.draw(screen)
        antagonist.draw(screen)
        
        if player.is_attacking and player.attack_progress > 0.9:
            damage_text = health_font.render("-10", True, PLAYER_COLOR)
            screen.blit(damage_text, (antagonist.x-20, antagonist.y-60))
        if antagonist.is_attacking and antagonist.attack_progress > 0.9:
            damage_text = health_font.render("-10", True, ENEMY_COLOR)
            screen.blit(damage_text, (player.x-20, player.y-60))
        
        if player.health <= 0 or antagonist.health <= 0:
            show_game_over_screen(player.health > 0)
            running = False
        
        pygame.display.flip()
        clock.tick(60)
    
    return True

def main():
    global story
    try:
        # Initialize story narration
        story = StoryNarration()
        
        show_title_screen()
        while True:
            if not main_game():
                show_title_screen()
    except SystemExit:
        pass
    except Exception as e:
        print(f"Error in main game loop: {e}")
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()