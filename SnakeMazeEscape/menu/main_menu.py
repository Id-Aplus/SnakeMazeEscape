import pygame
import sys

class MainMenu:
    def __init__(self, screen, sound_manager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 40)
        self.font_small = pygame.font.Font(None, 28)
        
        # Menu state
        self.selected_option = 0
        self.difficulty = 'normal'
        self.timer_minutes = 3
        self.timer_enabled = True
        self.music_on = True
        self.sfx_on = True
        
        # Menu options
        self.menu_options = [
            "Start Game",
            "Select Difficulty",
            "Set Timer",
            "How to Play",
            "Music",
            "SFX",
            "Fullscreen",
            "Exit Game"
        ]
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 150, 255)
        self.GRAY = (128, 128, 128)
        self.BLACK = (0, 0, 0)
        
        # Initialize menu rects for mouse clicking
        self.menu_rects = []
    
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self.select_option()
            elif event.key == pygame.K_LEFT:
                self.handle_left_right(-1)
            elif event.key == pygame.K_RIGHT:
                self.handle_left_right(1)
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            # Check which menu option mouse is over using stored rects
            for i, rect in enumerate(self.menu_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_option = i
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                return self.select_option()
        return None
    
    def handle_left_right(self, direction):
        if self.selected_option == 1:  # Difficulty
            difficulties = ['easy', 'normal', 'advanced']
            current_index = difficulties.index(self.difficulty)
            self.difficulty = difficulties[(current_index + direction) % len(difficulties)]
        elif self.selected_option == 2:  # Timer
            if direction == -1 and self.timer_minutes == 1:
                self.timer_enabled = False
            elif direction == 1 and not self.timer_enabled:
                self.timer_enabled = True
                self.timer_minutes = 1
            elif self.timer_enabled:
                self.timer_minutes = max(1, min(30, self.timer_minutes + direction))
        elif self.selected_option == 4:  # Sound Settings - Music
            self.music_on = not self.music_on
            if self.music_on:
                pygame.mixer.music.set_volume(0.3)
            else:
                pygame.mixer.music.set_volume(0.0)
        elif self.selected_option == 5:  # Sound Settings - SFX
            self.sfx_on = not self.sfx_on
            self.sound_manager.set_volume(0.7 if self.sfx_on else 0.0)
    
    def select_option(self):
        if self.selected_option == 0:  # Start Game
            return {'action': 'start_game', 'difficulty': self.difficulty, 'timer': self.timer_minutes}
        elif self.selected_option == 3:  # How to Play
            return {'action': 'show_controls'}
        elif self.selected_option == 4:  # Music Toggle
            self.music_on = not self.music_on
            if self.music_on:
                pygame.mixer.music.set_volume(0.3)
            else:
                pygame.mixer.music.set_volume(0.0)
            return None
        elif self.selected_option == 5:  # SFX Toggle
            self.sfx_on = not self.sfx_on
            self.sound_manager.set_volume(0.7 if self.sfx_on else 0.0)
            return None
        elif self.selected_option == 6:  # Fullscreen Toggle
            return {'action': 'toggle_fullscreen'}
        elif self.selected_option == 7:  # Exit
            return {'action': 'exit'}
        return None
    
    def draw(self):
        self.screen.fill(self.BLACK)
        
        # Game Title
        title_text = self.font_large.render("SNAKEY MAZE", True, self.GREEN)
        title_rect = title_text.get_rect(center=(400, 100))
        self.screen.blit(title_text, title_rect)
        
        # Menu Options with proper 50px spacing
        y_start = 160
        self.menu_rects = []  # Store rects for mouse clicking
        
        for i, option in enumerate(self.menu_options):
            color = self.WHITE if i == self.selected_option else self.GRAY
            
            # Special handling for options with values
            if i == 1:  # Difficulty
                text = f"{option}: {self.difficulty.upper()}"
            elif i == 2:  # Timer
                if self.timer_enabled:
                    text = f"{option}: {self.timer_minutes} min"
                else:
                    text = f"{option}: OFF"
            elif i == 4:  # Music
                music_status = "ON" if self.music_on else "OFF"
                text = f"{option}: {music_status}"
            elif i == 5:  # SFX
                sfx_status = "ON" if self.sfx_on else "OFF"
                text = f"{option}: {sfx_status}"
            elif i == 6:  # Fullscreen
                text = f"{option}: Toggle"
            else:
                text = option
            
            option_text = self.font_medium.render(text, True, color)
            option_rect = option_text.get_rect(center=(400, y_start + i * 50))
            self.screen.blit(option_text, option_rect)
            
            # Store clickable area (expanded for easier clicking)
            clickable_rect = pygame.Rect(option_rect.left - 20, option_rect.top - 10, 
                                       option_rect.width + 40, option_rect.height + 20)
            self.menu_rects.append(clickable_rect)
            
            # Highlight selected option
            if i == self.selected_option:
                pygame.draw.rect(self.screen, self.BLUE, option_rect, 3)
        
        # Instructions
        instructions = [
            "↑↓ Navigate | ← → Adjust | ENTER/SPACE Select",
            "Use LEFT/RIGHT on Difficulty and Timer | ENTER/SPACE to toggle Music/SFX"
        ]
        
        # Navigation instructions - positioned below all menu items
        nav_instructions = [
            "↑↓ Navigate | ← → Adjust | ENTER/SPACE Select | Mouse Click",
            "Use LEFT/RIGHT on Difficulty and Timer | ENTER/SPACE to toggle Music/SFX"
        ]
        
        instructions_y_start = y_start + len(self.menu_options) * 50 + 30  # 30px gap after menu
        for i, instruction in enumerate(nav_instructions):
            inst_text = self.font_small.render(instruction, True, self.WHITE)
            inst_rect = inst_text.get_rect(center=(400, instructions_y_start + i * 25))
            self.screen.blit(inst_text, inst_rect)

class ControlsScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.YELLOW = (255, 255, 0)
        self.BLACK = (0, 0, 0)
    
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                return {'action': 'back_to_menu'}
        return None
    
    def draw(self):
        self.screen.fill(self.BLACK)
        
        # Title
        title_text = self.font_large.render("HOW TO PLAY", True, self.GREEN)
        title_rect = title_text.get_rect(center=(400, 80))
        self.screen.blit(title_text, title_rect)
        
        # Controls
        controls = [
            "MOVEMENT:",
            "  Arrow Keys or WASD - Change Direction",
            "  Snake moves automatically",
            "",
            "COMBAT:",
            "  SPACE - Shoot from tail",
            "  Collect food for ammo",
            "  Hit enemy 3 times to stun",
            "",
            "OBJECTIVE:",
            "  Navigate maze from START to EXIT",
            "  Avoid being caught by enemy",
            "  Use ammo wisely!"
        ]
        
        y_start = 150
        for i, control in enumerate(controls):
            if control.endswith(":"):
                color = self.YELLOW
                font = self.font_medium
            elif control == "":
                continue
            else:
                color = self.WHITE
                font = self.font_small
            
            control_text = font.render(control, True, color)
            self.screen.blit(control_text, (100, y_start + i * 35))
        
        # Back instruction - moved to top right
        back_text = self.font_small.render("ESC: Back to Menu", True, self.WHITE)
        self.screen.blit(back_text, (600, 20))