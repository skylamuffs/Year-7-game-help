"""Version 13 - Adding Dialogs to the game"""
import pygame
import sys
import random
import os
import time
import math
from fractions import Fraction

# Initialize pygame
pygame.init()
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    sound_enabled = True
except pygame.error as e:
    print(f"Sound initialization failed: {e}")
    sound_enabled = False

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Samurai Math")
pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN])

# Game states
class GameState:
    TITLE = 0
    STORY = 1
    TUTORIAL = 2
    CHARACTER = 3
    BATTLE = 4
    GAME_OVER = 5

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
pixel_font = pygame.font.SysFont('Arial', 72)

# Heart settings
HEART_SIZE = 30
HEART_SPACING = 5
MAX_HEALTH = 100
HEARTS = 5
HEALTH_PER_HEART = MAX_HEALTH // HEARTS

def load_image(filename, scale=None, alpha=True):
    try:
        if not os.path.exists(filename):
            print(f"Image file not found: {filename}")
            raise FileNotFoundError
            
        if alpha:
            img = pygame.image.load(filename).convert_alpha()
        else:
            img = pygame.image.load(filename).convert()
            
        if scale:
            img = pygame.transform.scale(img, scale)
        return img
    except Exception as e:
        print(f"Error loading image {filename}: {e}")
        # Create a placeholder surface
        if scale:
            surf = pygame.Surface(scale, pygame.SRCALPHA if alpha else 0)
        else:
            surf = pygame.Surface((100, 100), pygame.SRCALPHA if alpha else 0)
            
        # Fill with a noticeable color for missing assets
        if alpha:
            surf.fill((255, 0, 255, 128))  # Semi-transparent magenta
        else:
            surf.fill((255, 0, 255))  # Solid magenta
            
        # Add text indicating missing file
        font = pygame.font.Font(None, 20)
        text = font.render(os.path.basename(filename), True, (0, 0, 0))
        surf.blit(text, (5, 5))
        return surf

# Load game images
sword_img = load_image("Sword_Enemy.png", (60, 60)) or pygame.Surface((60, 60), pygame.SRCALPHA)
player_sword = sword_img
antagonist_sword = pygame.transform.flip(sword_img, True, False)

title_background = load_image("Title_page.jpg", (WIDTH, HEIGHT), alpha=False) or pygame.Surface((WIDTH, HEIGHT))
game_over_img = load_image("Game_Over.jpg", (WIDTH, HEIGHT)) or pygame.Surface((WIDTH, HEIGHT))
victory_img = load_image("Win.jpg", (WIDTH, HEIGHT)) or pygame.Surface((WIDTH, HEIGHT))
warning_img = load_image("Warning.png", (WIDTH, HEIGHT)) or pygame.Surface((WIDTH, HEIGHT))

# Load heart images
heart_full = load_image("heart_full.png", (HEART_SIZE, HEART_SIZE)) or pygame.Surface((HEART_SIZE, HEART_SIZE), pygame.SRCALPHA)
heart_empty = load_image("heart_empty.png", (HEART_SIZE, HEART_SIZE)) or pygame.Surface((HEART_SIZE, HEART_SIZE), pygame.SRCALPHA)

# Create heart shapes if images not found
if not os.path.exists("heart_full.png"):
    heart_full = pygame.Surface((HEART_SIZE, HEART_SIZE), pygame.SRCALPHA)
    points = [
        (HEART_SIZE//2, HEART_SIZE//6),
        (HEART_SIZE//6, HEART_SIZE//2),
        (HEART_SIZE//2, HEART_SIZE*5//6),
        (HEART_SIZE*5//6, HEART_SIZE//2)
    ]
    pygame.draw.polygon(heart_full, (255, 0, 0), points)
    pygame.draw.polygon(heart_full, (255, 0, 0), [
        (HEART_SIZE//2, HEART_SIZE//6),
        (HEART_SIZE*5//6, HEART_SIZE//2),
        (HEART_SIZE//2, HEART_SIZE*5//6),
        (HEART_SIZE//6, HEART_SIZE//2)
    ])

if not os.path.exists("heart_empty.png"):
    heart_empty = pygame.Surface((HEART_SIZE, HEART_SIZE), pygame.SRCALPHA)
    pygame.draw.polygon(heart_empty, (100, 100, 100), points, 2)
    pygame.draw.polygon(heart_empty, (100, 100, 100), [
        (HEART_SIZE//2, HEART_SIZE//6),
        (HEART_SIZE*5//6, HEART_SIZE//2),
        (HEART_SIZE//2, HEART_SIZE*5//6),
        (HEART_SIZE//6, HEART_SIZE//2)
    ], 2)

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
                if os.path.exists(audio_file) and sound_enabled:
                    sound = pygame.mixer.Sound(audio_file)
                    self.sounds.append(sound)
                else:
                    print(f"Audio file not found or sound disabled: {audio_file}")
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
        if 0 <= self.current_segment < len(self.sounds) and self.sounds[self.current_segment] and sound_enabled:
            self.sounds[self.current_segment].play()
    
    def update(self):
        if not self.active:
            return False
            
        segment = self.story_segments[self.current_segment]
        
        if time.time() - self.start_time > segment["duration"]:
            self.next_segment()
        else:
            self.update_image()
        
        return self.active
    
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
    
    def draw(self, surface):
        if not self.active:
            return
            
        segment = self.story_segments[self.current_segment]
        img_file = segment["images"][self.current_image][0]
        bg = self.images.get(img_file, pygame.Surface((WIDTH, HEIGHT)))
        
        surface.blit(bg, (0, 0))

class DialogBox:
    def __init__(self):
        self.width = WIDTH - 100
        self.height = 120
        self.x = 50
        self.y = HEIGHT - self.height - 20
        self.border_color = (100, 100, 100)
        self.bg_color = (30, 30, 50)
        self.text_color = (220, 220, 220)
        self.current_text = ""
        self.display_text = ""
        self.char_index = 0
        self.speed = 0.05
        self.timer = 0
        self.active = False
        self.speaker = None
        self.speaker_pos = {
            "player": (self.x + 20, self.y - 50),
            "enemy": (self.x + self.width - 50, self.y - 50)
        }
        
    def show(self, text, speaker=None):
        self.current_text = text
        self.display_text = ""
        self.char_index = 0
        self.timer = 0
        self.active = True
        self.speaker = speaker
        
    def update(self, dt):
        if not self.active:
            return
            
        self.timer += dt
        if self.timer > self.speed and self.char_index < len(self.current_text):
            self.display_text += self.current_text[self.char_index]
            self.char_index += 1
            self.timer = 0
            
    def draw(self, surface):
        if not self.active:
            return
            
        # Draw dialog box
        pygame.draw.rect(surface, self.bg_color, 
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, self.border_color, 
                        (self.x, self.y, self.width, self.height), 3)
                        
        # Draw speaker indicator
        if self.speaker and self.speaker in self.speaker_pos:
            pos = self.speaker_pos[self.speaker]
            pygame.draw.polygon(surface, self.border_color, [
                (pos[0], pos[1]),
                (pos[0] + 20, pos[1]),
                (pos[0] + 10, pos[1] + 15)
            ])
        
        # Draw text with word wrapping
        words = self.display_text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if pixel_font.size(test_line)[0] <= self.width - 40:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        
        # Render wrapped text
        for i, line in enumerate(lines):
            line_surface = pixel_font.render(line, True, self.text_color)
            surface.blit(line_surface, (self.x + 20, self.y + 20 + i * 25))
            
    def is_complete(self):
        return self.char_index >= len(self.current_text)
        
    def complete(self):
        self.display_text = self.current_text
        self.char_index = len(self.current_text)
        
    def hide(self):
        self.active = False

class PlayerAnimation:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.2
        self.frame_counter = 0
        self.direction = 1
        self.speed = 5
        self.width = 100
        self.height = 150
        self.load_frames()
        
    def load_frames(self):
        for i in range(1, 7):
            try:
                frame = load_image(f"Player_ ({i}).png")
                if frame:
                    self.frames.append(frame)
                    if i == 1:
                        self.width = frame.get_width()
                        self.height = frame.get_height()
            except:
                print(f"Failed to load Player_ ({i}).png")
                surf = pygame.Surface((100, 150), pygame.SRCALPHA)
                pygame.draw.rect(surf, (255, 0, 0), (0, 0, 100, 150))
                self.frames.append(surf)
        
        while len(self.frames) < 6:
            surf = pygame.Surface((100, 150), pygame.SRCALPHA)
            pygame.draw.rect(surf, (255, 0, 0), (0, 0, 100, 150))
            self.frames.append(surf)
    
    def update(self):
        keys = pygame.key.get_pressed()
        moving = False
        
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.direction = 1
            moving = True
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.direction = -1
            moving = True
            
        if moving:
            self.frame_counter += self.animation_speed
            if self.frame_counter >= 1:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.frame_counter = 0
        else:
            self.current_frame = 0
        
        self.x = max(self.width//2, min(WIDTH - self.width//2, self.x))
    
    def draw(self, surface):
        current_image = self.frames[self.current_frame]
        if self.direction == -1:
            current_image = pygame.transform.flip(current_image, True, False)
        surface.blit(current_image, (self.x - self.width//2, self.y - self.height//2))

class AnimatedBackground:
    def __init__(self, base_name="Background_1", num_frames=70):
        self.base_name = base_name
        self.num_frames = num_frames
        self.frames = []
        self.current_frame = 0
        self.animation_speed = 0.5
        self.frame_counter = 0
        self.load_frames()
        
    def load_frames(self):
        for i in range(1, self.num_frames + 1):
            try:
                img = load_image(f"{self.base_name} ({i}).jpg", (WIDTH, HEIGHT), alpha=False)
                self.frames.append(img)
            except:
                surf = pygame.Surface((WIDTH, HEIGHT))
                color = (i % 255, (i * 2) % 255, (i * 3) % 255)
                pygame.draw.rect(surf, color, (0, 0, WIDTH, HEIGHT))
                self.frames.append(surf)
    
    def update(self):
        self.frame_counter += self.animation_speed
        if self.frame_counter >= 1:
            self.current_frame = (self.current_frame + 1) % self.num_frames
            self.frame_counter = 0
    
    def draw(self, surface):
        surface.blit(self.frames[self.current_frame], (0, 0))

class Fighter:
    def __init__(self, x, y, size, color, is_player):
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.original_pos = (x, y)
        self.health = MAX_HEALTH
        self.is_attacking = False
        self.attack_progress = 0
        self.is_player = is_player
        self.speed = 5 * (WIDTH / 800)
        if is_player:
            self.animation = PlayerAnimation(x, y)
        
    def draw(self, surface):
        if self.is_player and hasattr(self, 'animation'):
            self.animation.draw(surface)
        else:
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
            
    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        return self.health <= 0
            
    def update(self, target):
        if self.is_player and hasattr(self, 'animation'):
            self.animation.x = self.x
            self.animation.y = self.y
            self.animation.update()
        
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

def generate_sound(frequency=440, duration=0.5, volume=0.5):
    """Generate a simple sine wave sound using pygame"""
    if not sound_enabled:
        return None
        
    sample_rate = 22050
    samples = int(sample_rate * duration)
    buffer = pygame.sndarray.make_sound(bytearray(samples * 2))
    
    # Manually generate sine wave
    for i in range(samples):
        t = float(i) / sample_rate
        wave = int(32767 * volume * math.sin(2 * math.pi * frequency * t))
        # Write to both channels (stereo)
        buffer.set_at(i, (wave, wave))
    
    return buffer

def show_tutorial_screen():
    pygame.mixer.stop()
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
            "left:Percentages:|right:Measurement:",
            "left:   Example: 20% of 50 = 10|right:   Example: Area of 5cm × 4cm = 20cm²",
            "",
            "left:Geometry:|right:Statistics:",
            "left:   Example: △ angles sum to 180°|right:   Example: Range of 10,15,20 is 10",
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
        
        current_page = max(0, min(current_page, len(tutorial_pages) - 1))
        
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
    pygame.mixer.stop()
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

def generate_nz_math_question():
    """Generates NZ Year 7 appropriate math questions"""
    categories = [
        ('fraction', 3), ('decimal', 3), ('percentage', 2), 
        ('algebra', 2), ('measurement', 2), ('geometry', 1), 
        ('statistics', 1), ('maori', 1)
    ]
    
    # Weighted random selection
    total_weight = sum(weight for _, weight in categories)
    r = random.uniform(0, total_weight)
    upto = 0
    for category, weight in categories:
        if upto + weight >= r:
            break
        upto += weight
    
    # Fraction problems
    if category == 'fraction':
        a = Fraction(random.randint(1,5), random.randint(2,8))
        b = Fraction(random.randint(1,5), random.randint(2,8))
        op = random.choice(['+', '-', '×', '÷'])
        question = f"{a} {op} {b} = ?"
        if op == '+': answer = a + b
        elif op == '-': answer = a - b
        elif op == '×': answer = a * b
        else: answer = a / b
    
    # Decimal problems
    elif category == 'decimal':
        a = round(random.uniform(1, 10), 2)
        b = round(random.uniform(1, 5), 2)
        op = random.choice(['+', '-', '×', '÷'])
        question = f"{a} {op} {b} = ?"
        if op == '+': answer = round(a + b, 2)
        elif op == '-': answer = round(a - b, 2)
        elif op == '×': answer = round(a * b, 2)
        else: answer = round(a / b, 2)
    
    # Percentage problems
    elif category == 'percentage':
        percent = random.randint(5, 30) * 5
        amount = random.randint(10, 200)
        if random.choice([True, False]):
            question = f"{percent}% of {amount} = ?"
            answer = round(amount * percent / 100, 2)
        else:
            question = f"{amount} increased by {percent}% = ?"
            answer = round(amount * (1 + percent/100), 2)
    
    # Algebra problems
    elif category == 'algebra':
        x = random.randint(2, 6)
        coeff = random.randint(2, 5)
        const = random.randint(1, 10)
        question = f"If {coeff}x + {const} = {coeff*x + const}, x = ?"
        answer = x
    
    # Measurement problems
    elif category == 'measurement':
        l = random.randint(5, 15)
        w = random.randint(3, 10)
        if random.choice([True, False]):
            question = f"Area of {l}cm × {w}cm rectangle (cm²)?"
            answer = l * w
        else:
            question = f"Perimeter of {l}cm × {w}cm rectangle (cm)?"
            answer = 2 * (l + w)
    
    # Geometry problems (simplified)
    elif category == 'geometry':
        shapes = ["triangle", "square", "pentagon"]  # Simple shape names
        shape = random.choice(shapes)
        question = f"Angles in {shape} sum to ?°"
        answer = 180 if "triangle" in shape else 360 if "square" in shape else 540
    
    # Statistics problems
    elif category == 'statistics':
        nums = sorted([random.randint(10, 50) for _ in range(4)])
        question = f"Range of {', '.join(map(str, nums))} = ?"
        answer = nums[-1] - nums[0]
    
    # Māori number problems (optional)
    else:  # maori
        maori_nums = {'tahi':1, 'rua':2, 'toru':3, 'whā':4, 'rima':5}
        n1, n2 = random.sample(list(maori_nums.items()), 2)
        op = random.choice(['+', '×'])
        question = f"{n1[0]} {op} {n2[0]} = ?" 
        answer = n1[1] + n2[1] if op == '+' else n1[1] * n2[1]
    
    # Generate wrong answers
    answers = [answer]
    while len(answers) < 3:
        if isinstance(answer, (int, float)):
            wrong = answer * random.choice([0.5, 1.5, 0.8, 1.2])
            wrong = round(wrong, 2) if isinstance(answer, float) else wrong
        elif isinstance(answer, Fraction):
            wrong = answer + Fraction(random.randint(1,3), random.randint(2,5))
        if wrong not in answers:
            answers.append(wrong)
    
    random.shuffle(answers)
    return question, answer, answers

def show_game_over_screen(player_won):
    pygame.mixer.stop()
    waiting = True
    clock = pygame.time.Clock()
    
    # Create clearer fonts
    victory_font = pygame.font.SysFont('Arial', 72, bold=True)
    instruction_font = pygame.font.SysFont('Arial', 36, bold=True)
    
    try:
        if player_won:
            if os.path.exists("victory.mp3") and sound_enabled:
                pygame.mixer.Sound("victory.mp3").play()
            else:
                sound1 = generate_sound(784, 0.2)  # G5
                sound2 = generate_sound(1046, 0.3)  # C6
                if sound1 and sound2:
                    sound1.play()
                    pygame.time.delay(200)
                    sound2.play()
        else:
            if os.path.exists("defeat.mp3") and sound_enabled:
                pygame.mixer.Sound("defeat.mp3").play()
            else:
                sound1 = generate_sound(220, 0.3)  # A3
                sound2 = generate_sound(196, 0.4)  # G3
                if sound1 and sound2:
                    sound1.play()
                    pygame.time.delay(300)
                    sound2.play()
    except:
        pass
    
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False
        
        if player_won:
            if victory_img:
                screen.blit(victory_img, (0, 0))
            else:
                screen.fill(BACKGROUND)
                # Main victory text with outline
                victory_text = victory_font.render("VICTORY!", True, (0, 255, 0))
                text_rect = victory_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
                
                # Draw text outline
                outline_color = (0, 100, 0)
                for offset in [(-2,-2), (2,-2), (-2,2), (2,2)]:
                    outline_rect = text_rect.move(offset[0], offset[1])
                    outline_text = victory_font.render("VICTORY!", True, outline_color)
                    screen.blit(outline_text, outline_rect)
                
                # Draw main text
                screen.blit(victory_text, text_rect)
                
                # Instruction text
                continue_text = instruction_font.render("Press ENTER to Continue", True, (200, 200, 200))
                continue_rect = continue_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
                screen.blit(continue_text, continue_rect)
        else:
            if game_over_img:
                screen.blit(game_over_img, (0, 0))
            else:
                screen.fill(BACKGROUND)
                # Main defeat text with outline
                defeat_text = victory_font.render("DEFEAT", True, (255, 0, 0))
                text_rect = defeat_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
                
                # Draw text outline
                outline_color = (100, 0, 0)
                for offset in [(-2,-2), (2,-2), (-2,2), (2,2)]:
                    outline_rect = text_rect.move(offset[0], offset[1])
                    outline_text = victory_font.render("DEFEAT", True, outline_color)
                    screen.blit(outline_text, outline_rect)
                
                # Draw main text
                screen.blit(defeat_text, text_rect)
                
                # Instruction text
                continue_text = instruction_font.render("Press ENTER to Continue", True, (200, 200, 200))
                continue_rect = continue_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
                screen.blit(continue_text, continue_rect)
        
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
                pygame.mixer.stop()
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
                pygame.mixer.stop()
                story.active = False
                fade_in_out_warning()
                waiting = False
            if tutorial_button.is_clicked(event):
                pygame.mixer.stop()
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

def show_character_scene():
    character = PlayerAnimation(WIDTH//2, HEIGHT - 150)
    background = AnimatedBackground()
    dialog = DialogBox()
    
    # Show initial dialog
    dialog.show("Press A/D to move. Press ENTER when ready to fight!", "player")
    
    instruction_font = pygame.font.SysFont('Arial', 32, bold=True)
    instruction_text = instruction_font.render("Math battle awaits!", True, WHITE)
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN:
                    if dialog.active:
                        if dialog.is_complete():
                            dialog.hide()
                            return True
                        else:
                            dialog.complete()
                    else:
                        return True
        
        # Update animations
        character.update()
        background.update()
        dialog.update(dt)
        
        # Draw everything
        background.draw(screen)
        character.draw(screen)
        
        # Draw instruction text if no dialog
        if not dialog.active:
            screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, 50))
        
        # Draw dialog last
        dialog.draw(screen)
        
        pygame.display.flip()
    
    return False

def main_game():
    player = Fighter(WIDTH//4, HEIGHT//2, 60, PLAYER_COLOR, True)
    antagonist = Fighter(3*WIDTH//4, HEIGHT//2, 60, ENEMY_COLOR, False)
    dialog = DialogBox()
    current_question, correct_answer, answers = generate_nz_math_question()

    button_width = 180
    button_height = 60
    button_margin = 20
    buttons = [
        AnswerButton(
            (WIDTH - (3 * button_width + 2 * button_margin)) // 2 + i * (button_width + button_margin),
            HEIGHT - 130,
            button_width,
            button_height,
            answers[i],
            i
        ) for i in range(3)
    ]

    # Show battle start dialog
    dialog.show("Defeat me if you can! Answer correctly to attack!", "enemy")
    
    running = True
    clock = pygame.time.Clock()
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN:
                    if dialog.active:
                        if dialog.is_complete():
                            dialog.hide()
                        else:
                            dialog.complete()
            
            if not dialog.active and not player.is_attacking and not antagonist.is_attacking:
                for button in buttons:
                    if button.is_clicked(event):
                        if button.answer == correct_answer:
                            player.attack(antagonist)
                            dialog.show("Great job! You attacked!", "player")
                        else:
                            antagonist.attack(player)
                            dialog.show("Wrong! The enemy attacks you!", "enemy")
                        current_question, correct_answer, answers = generate_nz_math_question()
                        for i, btn in enumerate(buttons):
                            btn.answer = answers[i]
        
        player_attack_hit = player.update(antagonist)
        antagonist_attack_hit = antagonist.update(player)
        dialog.update(dt)
        
        if player_attack_hit:
            if antagonist.take_damage(10):
                dialog.show("You defeated the enemy!", "player")
                show_game_over_screen(True)
                running = False
        if antagonist_attack_hit:
            if player.take_damage(10):
                dialog.show("You were defeated...", "enemy")
                show_game_over_screen(False)
                running = False
        
        screen.fill(BACKGROUND)
        
        # Draw hearts
        full_hearts_player = player.health // HEALTH_PER_HEART
        for i in range(HEARTS):
            heart = heart_full if i < full_hearts_player else heart_empty
            screen.blit(heart, (50 + i * (HEART_SIZE + HEART_SPACING), 40))
        
        full_hearts_enemy = antagonist.health // HEALTH_PER_HEART
        for i in range(HEARTS):
            heart = heart_full if i < full_hearts_enemy else heart_empty
            screen.blit(heart, (WIDTH - 50 - (HEARTS - i) * (HEART_SIZE + HEART_SPACING), 40))
        
        question_text = question_font.render(current_question, True, WHITE)
        screen.blit(question_text, (WIDTH//2 - question_text.get_width()//2, 60))
        
        if not dialog.active and not player.is_attacking and not antagonist.is_attacking:
            for button in buttons:
                button.draw(screen)
        
        player.draw(screen)
        antagonist.draw(screen)
        dialog.draw(screen)
        
        pygame.display.flip()
    
    return True

def cleanup():
    pygame.mixer.stop()
    pygame.mixer.quit()
    pygame.quit()

def main():
    global story
    current_state = GameState.TITLE
    player_won = False
    
    try:
        story = StoryNarration()
        clock = pygame.time.Clock()
        FPS = 60
        
        while True:
            dt = clock.tick(FPS) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    cleanup()
                    sys.exit()
            
            if current_state == GameState.TITLE:
                show_title_screen()
                current_state = GameState.STORY
                
            elif current_state == GameState.STORY:
                if story.active:
                    story.update()
                    story.draw(screen)
                else:
                    current_state = GameState.CHARACTER
                    
            elif current_state == GameState.CHARACTER:
                if show_character_scene():
                    current_state = GameState.BATTLE
                else:
                    current_state = GameState.TITLE
                    
            elif current_state == GameState.BATTLE:
                player_won = main_game()
                current_state = GameState.GAME_OVER
                
            elif current_state == GameState.GAME_OVER:
                show_game_over_screen(player_won)
                current_state = GameState.TITLE
                
            pygame.display.flip()
            
    except Exception as e:
        print(f"Game error: {e}")
    finally:
        cleanup()

if __name__ == "__main__":
    main()