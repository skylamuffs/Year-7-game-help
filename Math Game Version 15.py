"""Version 15 - Adding level 2"""
import pygame
import sys
import random
import os
import time
import math
from fractions import Fraction

# Initialize pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2)
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
pixel_font = pygame.font.SysFont('Arial', 24)

# Heart settings
HEART_SIZE = 30
HEART_SPACING = 5
MAX_HEALTH = 50
HEARTS = 5
HEALTH_PER_HEART = MAX_HEALTH // HEARTS

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
level1_bg = load_image("Level_1.jpg", (WIDTH, HEIGHT), alpha=False) or pygame.Surface((WIDTH, HEIGHT))
dungeon_bg = load_image("dungeon_background.jpg", (WIDTH, HEIGHT), alpha=False) or pygame.Surface((WIDTH, HEIGHT))
castle_bg = load_image("castle_backdrop.jpg", (WIDTH, HEIGHT), alpha=False) or pygame.Surface((WIDTH, HEIGHT))

# Load heart images
heart_full = load_image("heart_full.png", (HEART_SIZE, HEART_SIZE)) or pygame.Surface((HEART_SIZE, HEART_SIZE), pygame.SRCALPHA)
heart_empty = load_image("heart_empty.png", (HEART_SIZE, HEART_SIZE)) or pygame.Surface((HEART_SIZE, HEART_SIZE), pygame.SRCALPHA)

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
    
    def update(self, dt=None, keys=None):
        if keys is None:
            keys = pygame.key.get_pressed()
        if dt is None:
            dt = 1/60  # Default delta time
            
        if keys[pygame.K_d]:
            self.x += self.speed
            self.direction = 1
            self.frame_counter += self.animation_speed * dt * 60
        elif keys[pygame.K_a]:
            self.x -= self.speed
            self.direction = -1
            self.frame_counter += self.animation_speed * dt * 60
        else:
            self.frame_counter = 0
            self.current_frame = 0
        
        self.x = max(self.width//2, min(WIDTH - self.width//2, self.x))
        
        if self.frame_counter >= 1:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.frame_counter = 0
    
    def draw(self, surface):
        current_image = self.frames[self.current_frame]
        if self.direction == -1:
            current_image = pygame.transform.flip(current_image, True, False)
        surface.blit(current_image, (self.x - self.width//2, self.y - self.height//2))

class Fighter:
    def __init__(self, x, y, size, color, is_player, enemy_type=1):
        self.x = x
        self.y = y
        self.color = color
        self.original_pos = (x, y)
        self.health = MAX_HEALTH
        self.is_attacking = False
        self.attack_progress = 0
        self.is_player = is_player
        self.speed = 5 * (WIDTH / 800)
        self.size = size
        self.enemy_type = enemy_type  # Add enemy type
        
        self.sword_img = load_image("Sword_Enemy.png", (60, 60)) or pygame.Surface((60, 60), pygame.SRCALPHA)
        self.player_sword = self.sword_img
        self.antagonist_sword = pygame.transform.flip(self.sword_img, True, False)
        
        if is_player:
            self.animation = PlayerAnimation(x, y)
            self.animation.y = HEIGHT//2 - 40
            self.width = self.animation.width
            self.height = self.animation.height
            self.idle_sword_pos = (25, -25)
            self.attack_sword_pos = (60, -15)
        else:
            self.y = HEIGHT//2 + 60
            # Load different enemy image based on type
            enemy_img_file = f"Enemy_{enemy_type}.png" if enemy_type > 1 else "Enemy_1.png"
            self.enemy_img = load_image(enemy_img_file, (100, 150)) or pygame.Surface((100, 150), pygame.SRCALPHA)
            if not os.path.exists(enemy_img_file):
                pygame.draw.rect(self.enemy_img, color, (0, 0, 100, 150))
            self.enemy_img = pygame.transform.flip(self.enemy_img, True, False)
            self.width = 100
            self.height = 150
            self.idle_sword_pos = (-25, -25)
            self.attack_sword_pos = (-60, -15)

    def update(self, target, dt=None, keys=None):
        """Update character state and return True if attack completes"""
        if hasattr(self, 'animation'):
            self.animation.x = self.x
            self.animation.y = self.y
            self.animation.update(dt, keys)
        
        if self.is_attacking:
            self.attack_progress = min(1.0, self.attack_progress + 0.08)
            
            move_progress = math.sin(self.attack_progress * math.pi/2)
            
            self.x = self.original_pos[0] + (target.x - self.original_pos[0]) * move_progress
            self.y = self.original_pos[1] + (target.y - self.original_pos[1]) * move_progress
            
            if self.attack_progress >= 1:
                self.is_attacking = False
                self.x, self.y = self.original_pos
                return True
        return False

    def draw(self, surface):
        if self.is_player:
            if hasattr(self, 'animation'):
                self.animation.draw(surface)
        else:
            enemy_rect = self.enemy_img.get_rect(center=(self.x, self.y))
            surface.blit(self.enemy_img, enemy_rect)
        
        current_sword = self.player_sword if self.is_player else self.antagonist_sword
        attack_progress = math.sin(self.attack_progress * math.pi) if self.is_attacking else 0
        
        if self.is_attacking:
            sword_rot = -45 - 20 * attack_progress if self.is_player else 45 + 20 * attack_progress
            sword = pygame.transform.rotate(current_sword, sword_rot)
            
            base_x, base_y = self.attack_sword_pos
            pos = (
                self.x + base_x * (1 + attack_progress * 0.5),
                self.y + base_y - 15 * attack_progress
            )
        else:
            sword = current_sword
            base_x, base_y = self.idle_sword_pos
            pos = (self.x + base_x, self.y + base_y)
        
        sword_rect = sword.get_rect(center=pos)
        surface.blit(sword, sword_rect)

    def attack(self, target):
        if not self.is_attacking:
            self.is_attacking = True
            self.attack_progress = 0

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        try:
            pygame.mixer.Sound("hit.wav").play()
        except:
            pass
        return self.health <= 0

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
        self.y = HEIGHT - self.height - 40
        
        self.player_bg = (65, 105, 225)
        self.enemy_bg = (220, 20, 60)
        self.neutral_bg = (40, 40, 60)
        
        self.border_color = (90, 90, 90)
        self.text_color = (240, 240, 240)
        self.speaker_color = (255, 255, 0)
        self.border_radius = 8
        self.padding = 25
        
        self.current_text = ""
        self.display_text = ""
        self.char_index = 0
        self.speed = 0.05
        self.timer = 0
        
        self.active = False
        self.speaker = None

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
            
        bg_color = {
            "player": self.player_bg,
            "enemy": self.enemy_bg
        }.get(self.speaker, self.neutral_bg)
        
        if self.speaker in ("player", "enemy"):
            speaker_label = f"{self.speaker.upper()}:"
            speaker_surface = button_font.render(speaker_label, True, self.speaker_color)
            surface.blit(speaker_surface, (self.x + 10, self.y - 30))
        
        pygame.draw.rect(surface, bg_color,
                        (self.x, self.y, self.width, self.height),
                        border_radius=self.border_radius)
        pygame.draw.rect(surface, self.border_color,
                        (self.x, self.y, self.width, self.height),
                        2, border_radius=self.border_radius)
        
        for i, line in enumerate(self._wrap_text(self.display_text)):
            text_surface = pixel_font.render(line, True, self.text_color)
            surface.blit(text_surface, (self.x + self.padding, self.y + self.padding + i * 28))

    def draw_continue_prompt(self, surface):
        if self.is_complete():
            instruction_font = pygame.font.SysFont('Arial', 20)
            instruction_text = instruction_font.render("Press ENTER to continue", True, (180, 180, 180))
            surface.blit(instruction_text, 
                        (self.x + self.width - instruction_text.get_width() - 20,
                         self.y + self.height - instruction_text.get_height() - 10))

    def _wrap_text(self, text):
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if pixel_font.size(test_line)[0] <= self.width - (self.padding * 2):
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        lines.append(' '.join(current_line))
        return lines

    def is_complete(self):
        return self.char_index >= len(self.current_text)

    def complete(self):
        self.display_text = self.current_text
        self.char_index = len(self.current_text)

    def hide(self):
        self.active = False

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

def show_pre_battle_dialog():
    fight_bg = load_image("sword_fight_bg.jpg", (WIDTH, HEIGHT), alpha=False) or pygame.Surface((WIDTH, HEIGHT))
    player_img = load_image("Player_ (1).png", (150, 200)) or pygame.Surface((150, 200), pygame.SRCALPHA)
    enemy_img = load_image("Enemy_1.png", (150, 200)) or pygame.Surface((150, 200), pygame.SRCALPHA)
    enemy_img = pygame.transform.flip(enemy_img, True, False)
    
    dialog = DialogBox()
    dialog_lines = [
        ("Well, well, well, look who we have here?", "enemy",),
        ("Where did you hide my son!? GIVE IT BACK!", "player"),
        ("Hah, since your husband kill our master's son\nwe can't give it back this easily", "enemy"),
        ("Then what do you want so you can get out of my way", "player"),
        ("Simple,all you do just answer my math questions correctly", "enemy"),
        ("Tsk, thats easy I can solve it really quickly", "player"),
        ("Alright then, if you say so", "enemy")
    ]

    current_line = 0
    dialog.show(dialog_lines[current_line][0], dialog_lines[current_line][1])
    
    instruction_font = pygame.font.SysFont('Arial', 20)
    instruction_text = instruction_font.render("Press ENTER to continue", True, (180, 180, 180))
    
    clock = pygame.time.Clock()
    waiting = True
    
    while waiting:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if dialog.is_complete():
                        current_line += 1
                        if current_line < len(dialog_lines):
                            dialog.show(dialog_lines[current_line][0], dialog_lines[current_line][1])
                        else:
                            waiting = False
                    else:
                        dialog.complete()
        
        screen.blit(fight_bg, (0, 0))
        screen.blit(player_img, (WIDTH//4 - 75, HEIGHT//2 - 100))
        screen.blit(enemy_img, (3*WIDTH//4 - 75, HEIGHT//2 - 100))
        
        dialog.update(dt)
        dialog.draw(screen)
        
        if dialog.is_complete():
            screen.blit(instruction_text, 
                       (dialog.x + dialog.width - instruction_text.get_width() - 20,
                        dialog.y + dialog.height - instruction_text.get_height() - 10))
        
        pygame.display.flip()
    
    return True

def generate_sound(frequency=440, duration=0.5, volume=0.5):
    sample_rate = 22050
    samples = int(sample_rate * duration)
    buffer = pygame.sndarray.make_sound(bytearray(samples * 2))
    
    for i in range(samples):
        t = float(i) / sample_rate
        wave = int(32767 * volume * math.sin(2 * math.pi * frequency * t))
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

def generate_math_question():
    categories = ['fraction', 'decimal', 'percentage', 'algebra', 'measurement', 'geometry', 'statistics']
    category = random.choice(categories)
    
    if category == 'fraction':
        a = Fraction(random.randint(1,5), random.randint(2,8))
        b = Fraction(random.randint(1,5), random.randint(2,8))
        op = random.choice(['+', '-', '×', '÷'])
        question = f"{a} {op} {b} = ?"
        if op == '+': answer = a + b
        elif op == '-': answer = a - b
        elif op == '×': answer = a * b
        else: answer = a / b
    
    elif category == 'decimal':
        a = round(random.uniform(1, 10), 2)
        b = round(random.uniform(1, 5), 2)
        op = random.choice(['+', '-', '×', '÷'])
        question = f"{a} {op} {b} = ?"
        if op == '+': answer = round(a + b, 2)
        elif op == '-': answer = round(a - b, 2)
        elif op == '×': answer = round(a * b, 2)
        else: answer = round(a / b, 2)
    
    elif category == 'percentage':
        percent = random.randint(5, 30) * 5
        amount = random.randint(10, 200)
        question = f"{percent}% of {amount} = ?"
        answer = round(amount * percent / 100, 2)
    
    elif category == 'algebra':
        x = random.randint(2, 6)
        coeff = random.randint(2, 5)
        const = random.randint(1, 10)
        question = f"If {coeff}x + {const} = {coeff*x + const}, x = ?"
        answer = x
    
    elif category == 'measurement':
        l = random.randint(5, 15)
        w = random.randint(3, 10)
        question = f"Area of {l}cm × {w}cm rectangle (cm²)?"
        answer = l * w
    
    elif category == 'geometry':
        shapes = ["triangle", "square", "pentagon"]
        shape = random.choice(shapes)
        question = f"Angles in {shape} sum to ?°"
        answer = 180 if "triangle" in shape else 360 if "square" in shape else 540
    
    elif category == 'statistics':
        nums = sorted([random.randint(10, 50) for _ in range(4)])
        question = f"Range of {', '.join(map(str, nums))} = ?"
        answer = nums[-1] - nums[0]
    
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

def generate_question():
    categories = [
        'fraction', 'decimal', 'percentage', 
        'algebra', 'measurement', 'geometry', 
        'statistics', 'maori'
    ]
    category = random.choice(categories)
    
    if category == 'fraction':
        a = Fraction(random.randint(1,5), random.randint(2,8))
        b = Fraction(random.randint(1,5), random.randint(2,8))
        op = random.choice(['+', '-', '×', '÷'])
        question = f"{a} {op} {b} = ?"
        if op == '+': answer = a + b
        elif op == '-': answer = a - b
        elif op == '×': answer = a * b
        else: answer = a / b
    
    elif category == 'decimal':
        a = round(random.uniform(1, 10), 2)
        b = round(random.uniform(1, 5), 2)
        op = random.choice(['+', '-', '×', '÷'])
        question = f"{a} {op} {b} = ?"
        if op == '+': answer = round(a + b, 2)
        elif op == '-': answer = round(a - b, 2)
        elif op == '×': answer = round(a * b, 2)
        else: answer = round(a / b, 2)
    
    elif category == 'percentage':
        percent = random.randint(5, 30) * 5
        amount = random.randint(10, 200)
        if random.choice([True, False]):
            question = f"{percent}% of {amount} = ?"
            answer = round(amount * percent / 100, 2)
        else:
            question = f"{amount} increased by {percent}% = ?"
            answer = round(amount * (1 + percent/100), 2)
    
    elif category == 'algebra':
        x = random.randint(2, 6)
        coeff = random.randint(2, 5)
        const = random.randint(1, 10)
        question = f"If {coeff}x + {const} = {coeff*x + const}, x = ?"
        answer = x
    
    elif category == 'measurement':
        l = random.randint(5, 15)
        w = random.randint(3, 10)
        if random.choice([True, False]):
            question = f"Area of {l}cm × {w}cm rectangle (cm²)?"
            answer = l * w
        else:
            question = f"Perimeter of {l}cm × {w}cm rectangle (cm)?"
            answer = 2 * (l + w)
    
    elif category == 'geometry':
        shapes = ["triangle", "square", "pentagon"]
        shape = random.choice(shapes)
        question = f"Angles in {shape} sum to ?°"
        answer = 180 if "triangle" in shape else 360 if "square" in shape else 540
    
    elif category == 'statistics':
        nums = sorted([random.randint(10, 50) for _ in range(4)])
        if random.choice([True, False]):
            question = f"Range of {', '.join(map(str, nums))} = ?"
            answer = nums[-1] - nums[0]
        else:
            question = f"Mean of {', '.join(map(str, nums))} = ?"
            answer = sum(nums) / len(nums)
    
    else:  # maori
        maori_nums = {'tahi':1, 'rua':2, 'toru':3, 'whā':4, 'rima':5}
        n1, n2 = random.sample(list(maori_nums.items()), 2)
        op = random.choice(['+', '×'])
        question = f"{n1[0]} {op} {n2[0]} = ?" 
        answer = n1[1] + n2[1] if op == '+' else n1[1] * n2[1]
    
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
    pygame.mixer.stop()  # Stop any previous sounds/music
    waiting = True
    clock = pygame.time.Clock()
    
    victory_font = pygame.font.SysFont('Arial', 72, bold=True)
    instruction_font = pygame.font.SysFont('Arial', 36, bold=True)

    if player_won:
        # Play custom victory sound
        try:
            if os.path.exists("sound of victory.mp3"):
                victory_sound = pygame.mixer.Sound("sound of victory.mp3")
                victory_sound.play()
            else:
                print("Victory sound file not found.")
        except Exception as e:
            print(f"Error playing victory sound: {e}")

        # Load custom victory background
        victory_img_custom = load_image("win.jpg", (WIDTH, HEIGHT), alpha=False)
        if victory_img_custom:
            victory_img_to_use = victory_img_custom
        else:
            print("Victory image not found, using fallback.")
            victory_img_to_use = pygame.Surface((WIDTH, HEIGHT))
            victory_img_to_use.fill((0, 100, 0))
    else:
        # Play defeat sound
        try:
            if os.path.exists("defeat.mp3"):
                defeat_sound = pygame.mixer.Sound("defeat.mp3")
                defeat_sound.play()
            else:
                print("Defeat sound not found.")
        except Exception as e:
            print(f"Error playing defeat sound: {e}")

        victory_img_to_use = game_over_img if game_over_img else pygame.Surface((WIDTH, HEIGHT))
        if not game_over_img:
            victory_img_to_use.fill((100, 0, 0))

    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                pygame.mixer.stop()
                waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.mixer.stop()
                waiting = False

        # Draw background
        screen.blit(victory_img_to_use, (0, 0))

        if player_won:
            victory_text = victory_font.render("VICTORY!", True, (0, 255, 0))
        else:
            victory_text = victory_font.render("YOU LOSE", True, (255, 0, 0))

        text_rect = victory_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        
        # Outline
        outline_color = (0, 100, 0) if player_won else (100, 0, 0)
        for offset in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
            outline_rect = text_rect.move(offset[0], offset[1])
            outline_text = victory_font.render(victory_text.get_text(), True, outline_color)
            screen.blit(outline_text, outline_rect)

        screen.blit(victory_text, text_rect)

        continue_text = instruction_font.render("Press ENTER to Continue", True, (200, 200, 200))
        continue_rect = continue_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        screen.blit(continue_text, continue_rect)

        pygame.display.flip()
        clock.tick(60)


def show_game_over_screen(player_won):
    """Display a victory or defeat screen with appropriate sounds and visuals"""
    pygame.mixer.stop()  # Stop any previous sounds/music
    
    # Sound setup
    try:
        if player_won:
            # Try to load victory sound
            try:
                victory_sound = pygame.mixer.Sound("victory.mp3")
                victory_sound.set_volume(0.7)
            except:
                print("Could not load victory.mp3, using generated sound")
                victory_sound = generate_sound(880, 1.5)  # Fallback sound
        else:
            # Try to load defeat sound
            try:
                defeat_sound = pygame.mixer.Sound("defeat.mp3")
                defeat_sound.set_volume(0.7)
            except:
                print("Could not load defeat.mp3, using generated sound")
                defeat_sound = generate_sound(220, 2.0)  # Fallback sound
    except Exception as e:
        print(f"Error setting up sounds: {e}")

    # Play appropriate sound
    if player_won:
        try:
            victory_sound.play()
        except:
            print("Could not play victory sound")
    else:
        try:
            defeat_sound.play()
        except:
            print("Could not play defeat sound")

    # Visual setup
    waiting = True
    clock = pygame.time.Clock()
    
    # Font setup
    victory_font = pygame.font.SysFont('Arial', 72, bold=True)
    instruction_font = pygame.font.SysFont('Arial', 36, bold=True)

    # Background setup
    if player_won:
        try:
            victory_img_to_use = pygame.image.load("win.jpg").convert()
            victory_img_to_use = pygame.transform.scale(victory_img_to_use, (WIDTH, HEIGHT))
        except:
            victory_img_to_use = pygame.Surface((WIDTH, HEIGHT))
            victory_img_to_use.fill((0, 80, 0))  # Dark green background
    else:
        try:
            victory_img_to_use = pygame.image.load("game_over.jpg").convert()
            victory_img_to_use = pygame.transform.scale(victory_img_to_use, (WIDTH, HEIGHT))
        except:
            victory_img_to_use = pygame.Surface((WIDTH, HEIGHT))
            victory_img_to_use.fill((80, 0, 0))  # Dark red background

    # Main display loop
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Changed from ENTER to SPACE
                    waiting = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

        # Draw background
        screen.blit(victory_img_to_use, (0, 0))

        # Draw victory/defeat text with outline effect
        if player_won:
            text_color = (0, 255, 0)  # Green for victory
            outline_color = (0, 100, 0)  # Dark green outline
            text = "VICTORY!"
        else:
            text_color = (255, 0, 0)  # Red for defeat
            outline_color = (100, 0, 0)  # Dark red outline
            text = "GAME OVER"

        # Render text with outline
        text_surface = victory_font.render(text, True, text_color)
        outline_surface = victory_font.render(text, True, outline_color)
        
        # Text position
        text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        
        # Draw outline
        for offset in [(-2,-2), (2,-2), (-2,2), (2,2)]:
            screen.blit(outline_surface, text_rect.move(offset[0], offset[1]))
        
        # Draw main text
        screen.blit(text_surface, text_rect)

        # Draw continue prompt - BLACK when won, gray when lost
        if player_won:
            continue_color = (0, 0, 0)  # Black for victory
            continue_text = instruction_font.render("PRESS SPACE TO CONTINUE", True, continue_color)
        else:
            continue_color = (200, 200, 200)  # Gray for defeat
            continue_text = instruction_font.render("PRESS SPACE TO CONTINUE", True, continue_color)
        
        continue_rect = continue_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        
        # Add outline to continue text if needed (optional)
        if player_won:
            outline_continue = instruction_font.render("PRESS SPACE TO CONTINUE", True, (255, 255, 255))
            for offset in [(-1,-1), (1,-1), (-1,1), (1,1)]:
                screen.blit(outline_continue, continue_rect.move(offset[0], offset[1]))
        
        screen.blit(continue_text, continue_rect)

        pygame.display.flip()
        clock.tick(60)


def show_victory_dialog():
    """Show dialog where enemy reveals next location"""
    dialog = DialogBox()
    dialog_lines = [
        ("You defeated me... I'll tell you where your son is.", "enemy"),
        ("He's in the castle dungeon. But you'll never make it past the guards!", "enemy"),
        ("I'll take my chances. Thank you for the information.", "player")
    ]

    current_line = 0
    dialog.show(dialog_lines[current_line][0], dialog_lines[current_line][1])
    
    clock = pygame.time.Clock()
    waiting = True
    
    while waiting:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if dialog.is_complete():
                        current_line += 1
                        if current_line < len(dialog_lines):
                            dialog.show(dialog_lines[current_line][0], dialog_lines[current_line][1])
                        else:
                            waiting = False
                    else:
                        dialog.complete()
        
        screen.blit(level1_bg, (0, 0))  # Keep battle background
        dialog.update(dt)
        dialog.draw(screen)
        dialog.draw_continue_prompt(screen)
        pygame.display.flip()
    
    return True  # Signal to proceed to level 2

def generate_dungeon_question():
    """Generate challenging dungeon-level math questions"""
    categories = ['fraction', 'decimal', 'percentage', 'algebra', 'measurement', 'geometry', 'statistics']
    category = random.choice(categories)
    
    if category == 'fraction':
        a = Fraction(random.randint(3,8), random.randint(4,12))
        b = Fraction(random.randint(3,8), random.randint(4,12))
        op = random.choice(['+', '-', '×', '÷'])
        question = f"Simplify: {a} {op} {b} = ?"
        if op == '+': answer = a + b
        elif op == '-': answer = a - b
        elif op == '×': answer = a * b
        else: answer = a / b
        # Simplify the answer
        if isinstance(answer, Fraction):
            answer = answer.limit_denominator()
    
    elif category == 'decimal':
        a = round(random.uniform(5, 20), 2)
        b = round(random.uniform(2, 10), 2)
        op = random.choice(['+', '-', '×', '÷'])
        question = f"{a} {op} {b} = ? (2 decimal places)"
        if op == '+': answer = round(a + b, 2)
        elif op == '-': answer = round(a - b, 2)
        elif op == '×': answer = round(a * b, 2)
        else: answer = round(a / b, 2)
    
    elif category == 'percentage':
        percent = random.randint(15, 40) * 5
        amount = random.randint(50, 300)
        if random.choice([True, False]):
            question = f"{percent}% of {amount} = ?"
            answer = round(amount * percent / 100, 2)
        else:
            question = f"{amount} increased by {percent}% then decreased by {percent}% = ?"
            change = 1 + percent/100
            answer = round(amount * change * (1 - percent/100), 2)
    
    elif category == 'algebra':
        x = random.randint(3, 8)
        coeff = random.randint(3, 7)
        const = random.randint(5, 15)
        if random.choice([True, False]):
            question = f"Solve for x: {coeff}x + {const} = {coeff*x + const}"
            answer = x
        else:
            question = f"Solve for x: {coeff}(x + {const}) = {coeff*(x + const + 1)}"
            answer = 1
    
    elif category == 'measurement':
        l = random.randint(8, 20)
        w = random.randint(5, 15)
        h = random.randint(4, 10)
        if random.choice([True, False]):
            question = f"Volume of {l}cm × {w}cm × {h}cm box (cm³)?"
            answer = l * w * h
        else:
            question = f"Surface area of {l}cm × {w}cm × {h}cm box (cm²)?"
            answer = 2 * (l*w + l*h + w*h)
    
    elif category == 'geometry':
        shapes = ["triangle", "square", "pentagon", "hexagon"]
        shape = random.choice(shapes)
        question = f"Angles in regular {shape} sum to ?°"
        answer = 180 if "triangle" in shape else 360 if "square" in shape else 540 if "pentagon" in shape else 720
    
    elif category == 'statistics':
        nums = sorted([random.randint(20, 100) for _ in range(5)])
        if random.choice([True, False]):
            question = f"Mean of {', '.join(map(str, nums))} = ? (2 decimal places)"
            answer = round(sum(nums) / len(nums), 2)
        else:
            question = f"Median of {', '.join(map(str, nums))} = ?"
            answer = nums[2]
    
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

def dungeon_battle():
    """Second level battle in the dungeon"""
    player = Fighter(WIDTH//4, HEIGHT//2 + 75, 60, PLAYER_COLOR, True)
    # Use enemy_type=2 for the dungeon enemy (different color and image)
    antagonist = Fighter(3*WIDTH//4, HEIGHT//2 + 75, 60, (150, 50, 50), False, enemy_type=2)
    
    dialog = DialogBox()
    dialog.show("The dungeon guard challenges you to harder questions!")

    current_question, correct_answer, answers = generate_dungeon_question()

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

    running = True
    clock = pygame.time.Clock()
    while running:
        dt = clock.tick(60) / 1000.0
        keys = pygame.key.get_pressed()
        
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
                            dialog.show("Correct! You strike the guard!", "player")
                        else:
                            antagonist.attack(player)
                            dialog.show("Wrong! The guard attacks you!", "enemy")
                        current_question, correct_answer, answers = generate_dungeon_question()
                        for i, btn in enumerate(buttons):
                            btn.answer = answers[i]
        
        player_attack_hit = player.update(antagonist, dt, keys)
        antagonist_attack_hit = antagonist.update(player, dt, keys)
        dialog.update(dt)
        
        if player_attack_hit:
            if antagonist.take_damage(10):  
                dialog.show("You defeated the dungeon guard!", "player")
                show_game_over_screen(True)  
                running = False
                return True

        if antagonist_attack_hit:
            if player.take_damage(10):  
             dialog.show("The dungeon guard defeated you...", "enemy")
             show_game_over_screen(False)
             retry = show_defeat_dialog()
             if retry:
                player.health = MAX_HEALTH
                antagonist.health = MAX_HEALTH
                current_question, correct_answer, answers = generate_dungeon_question()
                for i, btn in enumerate(buttons):
                 btn.answer = answers[i]
            dialog.show("Let's try this again!", "player")
        else:
            running = False
        
        screen.blit(dungeon_bg, (0, 0))
        
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
        if dialog.active:  
            dialog.draw_continue_prompt(screen)
        
        pygame.display.flip()
    
    return False

def show_dungeon_intro():
    """Show dungeon intro scene with dialog before level 2 battle"""
    dialog = DialogBox()
    
    # Load images - using Enemy_2.png for the dungeon enemy
    dungeon_bg_img = load_image("dungeon_background.jpg", (WIDTH, HEIGHT), alpha=False) or pygame.Surface((WIDTH, HEIGHT))
    player_img = load_image("Player_ (1).png", (150, 200)) or pygame.Surface((150, 200), pygame.SRCALPHA)
    enemy_img = load_image("Enemy_2.png", (150, 200)) or pygame.Surface((150, 200), pygame.SRCALPHA)
    enemy_img = pygame.transform.flip(enemy_img, True, False)  # Face player
    
    # Dialog lines (first is narrator)
    dungeon_dialog_lines = [
        ("You enter the dark, damp dungeon...", None),
        ("The air is thick with the smell of mold and despair.", "player"),
        ("*clank* *clank* The sound of armor echoes through the halls.", None),
        ("Halt! Who dares enter the dungeon?", "enemy"),
        ("I'm here for my son! Let us pass!", "player"),
        ("Not so fast! Answer my questions first!", "enemy")
    ]
    
    current_line = 0
    dialog.show(dungeon_dialog_lines[current_line][0], dungeon_dialog_lines[current_line][1])
    
    clock = pygame.time.Clock()
    waiting = True
    
    while waiting:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN:
                    if dialog.is_complete():
                        current_line += 1
                        if current_line < len(dungeon_dialog_lines):
                            dialog.show(dungeon_dialog_lines[current_line][0], dungeon_dialog_lines[current_line][1])
                        else:
                            waiting = False
                            return True  # Explicitly return True when done
                    else:
                        dialog.complete()
        
        # Draw background + characters
        screen.blit(dungeon_bg_img, (0, 0))
        screen.blit(player_img, (WIDTH//4 - 75, HEIGHT//2 - 100))
        screen.blit(enemy_img, (3*WIDTH//4 - 75, HEIGHT//2 - 100))
        
        # Draw dialog
        dialog.update(dt)
        dialog.draw(screen)
        if dialog.active:
            dialog.draw_continue_prompt(screen)
        
def show_dungeon_intro():
    global dungeon_intro_shown
    if dungeon_intro_shown:
        return True  # skip dialog if already seen
    dungeon_intro_shown = True

    pygame.display.flip()
    
    return True

def show_castle_scene():
    """Let the player move through the castle before teleporting to dungeon."""
    player = PlayerAnimation(WIDTH//4, HEIGHT - 150)
    dialog = DialogBox()
    
    castle_dialog_lines = [
        ("This must be the castle the enemy mentioned...", "player"),
        ("I need to find the dungeon entrance.", "player"),
        ("There! That must be the way down to the dungeon.", "player")
    ]
    
    current_line = 0
    show_dialog = True
    dialog.show(castle_dialog_lines[current_line][0], castle_dialog_lines[current_line][1])
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        keys = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN and show_dialog:
                    if dialog.is_complete():
                        current_line += 1
                        if current_line < len(castle_dialog_lines):
                            dialog.show(castle_dialog_lines[current_line][0], castle_dialog_lines[current_line][1])
                        else:
                            show_dialog = False
                    else:
                        dialog.complete()
        
        # Movement after dialog finishes
        if not show_dialog:
            player.update(dt, keys)
            if player.x + player.width//2 >= WIDTH:  # reached the right edge
                # Teleport to dungeon intro
                return show_dungeon_intro()
        
        # Draw background and player
        screen.blit(castle_bg, (0, 0))
        player.draw(screen)
        
        # Draw dialog if still active
        if show_dialog:
            dialog.update(dt)
            dialog.draw(screen)
            dialog.draw_continue_prompt(screen)
        
        pygame.display.flip()
    
    return True

def show_defeat_dialog():
    dialog = DialogBox()
    dialog_lines = [
        ("Hahaha! You're too weak to save your son!", "enemy"),
        ("...I'll be back. This isn't over.", "player"),
        ("Come back anytime you want to lose again!", "enemy"),
        ("Would you like to try again?", "player")
    ]

    current_line = 0
    dialog.show(dialog_lines[current_line][0], dialog_lines[current_line][1])
    
    yes_button = AnswerButton(WIDTH//2 - 150, HEIGHT - 100, 120, 50, "Yes", 0)
    no_button = AnswerButton(WIDTH//2 + 30, HEIGHT - 100, 120, 50, "No", 1)
    
    waiting = True
    retry = False
    clock = pygame.time.Clock()
    
    while waiting:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if dialog.is_complete():
                        current_line += 1
                        if current_line < len(dialog_lines):
                            dialog.show(dialog_lines[current_line][0], dialog_lines[current_line][1])
                        else:
                            pass
                    else:
                        dialog.complete()
            
            if current_line >= len(dialog_lines) - 1:
                if yes_button.is_clicked(event):
                    waiting = False
                    retry = True
                if no_button.is_clicked(event):
                    waiting = False
                    retry = False
        
        screen.fill(BACKGROUND)
        dialog.update(dt)
        dialog.draw(screen)
        
        if current_line < len(dialog_lines) - 1:  # Only show prompt for non-choice dialogs
            dialog.draw_continue_prompt(screen)
        
        if current_line >= len(dialog_lines) - 1 and dialog.is_complete():
            yes_button.draw(screen)
            no_button.draw(screen)
        
        pygame.display.flip()
    
    if not retry:
        dialog.show("Too scared to try again? Your son will be disappointed!", "enemy")
        waiting = True
        clock = pygame.time.Clock()
        while waiting:
            dt = clock.tick(60) / 1000.0
        
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
        
            screen.fill(BACKGROUND)
            dialog.update(dt)  # Add this line to update the dialog
            dialog.draw(screen)
            pygame.display.flip()
    
    return retry

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

def show_ending_scene():
    """Show the final scene where player finds their son"""
    player = PlayerAnimation(WIDTH//4, HEIGHT - 150)
    son_img = load_image("son.png", (80, 120)) or pygame.Surface((80, 120), pygame.SRCALPHA)
    dialog = DialogBox()
    
    ending_dialog_lines = [
        ("Mother! You came for me!", "son"),
        ("Of course I did! Are you hurt?", "player"),
        ("I'm okay, just scared. Let's get out of here!", "son"),
        ("Hold on tight, we're leaving this place!", "player")
    ]
    
    current_line = 0
    show_dialog = True
    dialog.show(ending_dialog_lines[current_line][0], ending_dialog_lines[current_line][1])
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN and show_dialog:
                    if dialog.is_complete():
                        current_line += 1
                        if current_line < len(ending_dialog_lines):
                            dialog.show(ending_dialog_lines[current_line][0], ending_dialog_lines[current_line][1])
                        else:
                            show_dialog = False
                            running = False
                    else:
                        dialog.complete()
        
        screen.blit(dungeon_bg, (0, 0))
        player.draw(screen)
        screen.blit(son_img, (3*WIDTH//4 - 40, HEIGHT - 170))
        
        if show_dialog:
            dialog.update(dt)
            dialog.draw(screen)
            dialog.draw_continue_prompt(screen)
        
        pygame.display.flip()
    
    return True

def show_character_scene():
    character = PlayerAnimation(WIDTH//2, HEIGHT - 150)
    background = AnimatedBackground()
    dialog = DialogBox()
    
    instruction_font = pygame.font.SysFont('Arial', 28, bold=True)
    instruction_text = instruction_font.render("Press D to move right", True, (255, 255, 0))
    instruction_shadow = instruction_font.render("Press D to move right", True, (0, 0, 0))
    
    show_instructions = True
    dialog_timer = 1.0
    show_dialog = False
    
    running = True
    clock = pygame.time.Clock()
    
    while running:
        dt = clock.tick(60) / 1000.0
        keys = pygame.key.get_pressed()
        
        if not show_dialog:
            dialog_timer -= dt
            if dialog_timer <= 0:
                dialog.show("Let's go save my son!", "player")
                show_dialog = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key == pygame.K_RETURN and show_dialog:
                    if dialog.active:
                        if dialog.is_complete():
                            dialog.hide()
                        else:
                            dialog.complete()
        
        character.update(dt, keys)
        background.update()
        if show_dialog:
            dialog.update(dt)
        
        if character.x + character.width//2 >= WIDTH:
            return True
        
        background.draw(screen)
        character.draw(screen)
        
        if show_instructions:
            screen.blit(instruction_shadow, (WIDTH//2 - instruction_shadow.get_width()//2 + 2, 20 + 2))
            screen.blit(instruction_text, (WIDTH//2 - instruction_text.get_width()//2, 20))
        
        if show_dialog and dialog.active:
            dialog.draw(screen)
        
        pygame.display.flip()
    
    return False

# inside main_game function
def main_game(level=1):
    if level == 1:
        player = Fighter(WIDTH//4, HEIGHT//2 + 75, 60, PLAYER_COLOR, True)
        antagonist = Fighter(3*WIDTH//4, HEIGHT//2 + 75, 60, ENEMY_COLOR, False)
        
        if not show_pre_battle_dialog():
            return False
        
        dialog = DialogBox()
        current_question, correct_answer, answers = generate_math_question()

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

        dialog.show("Answer the question to defeat the enemy")
        
        running = True
        clock = pygame.time.Clock()
        while running:
            dt = clock.tick(60) / 1000.0
            keys = pygame.key.get_pressed()
            
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
                                dialog.show("Correct! You attacked!", "player")
                            else:
                                antagonist.attack(player)
                                dialog.show("Wrong! The enemy attacks you!", "enemy")
                            current_question, correct_answer, answers = generate_math_question()
                            for i, btn in enumerate(buttons):
                                btn.answer = answers[i]
            
            player_attack_hit = player.update(antagonist, dt, keys)
            antagonist_attack_hit = antagonist.update(player, dt, keys)
            dialog.update(dt)
            
            if player_attack_hit:
                if antagonist.take_damage(10):
                    # Show clear victory message first
                    show_game_over_screen(True)  # Fixed: Added player_won=True argument
                    # Then show the dialog where enemy reveals next location
                    if show_victory_dialog():
                        running = False
                        return True  # Proceed to level 2
                    
            if antagonist_attack_hit:
                if player.take_damage(10):
                    dialog.show("You were defeated...", "enemy")
                    show_game_over_screen(False)
                    retry = show_defeat_dialog()
                    if retry:
                        player.health = MAX_HEALTH
                        antagonist.health = MAX_HEALTH
                        current_question, correct_answer, answers = generate_math_question()
                        for i, btn in enumerate(buttons):
                            btn.answer = answers[i]
                        dialog.show("Let's try this again!", "player")
                    else:
                        running = False
            
            screen.blit(level1_bg, (0, 0))
            
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
            if dialog.active:  
                dialog.draw_continue_prompt(screen)
            
            pygame.display.flip()
        
        return False
    
    elif level == 2:
        # Show castle scene first
        if show_castle_scene():
            # Then show dungeon intro dialog before the battle
            if show_dungeon_intro():
                # Then proceed to dungeon battle
                if dungeon_battle():
                    # If dungeon battle is won, show ending scene
                    show_ending_scene()
                    return True
        return False

def main():
    global story
    try:
        story = StoryNarration()
        
        show_title_screen()
        while True:
            if show_character_scene():
                # Play level 1 - initial battle
                if main_game(level=1):
                    # If level 1 completed, play level 2 (castle and dungeon)
                    main_game(level=2)
                show_title_screen()
            else:
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