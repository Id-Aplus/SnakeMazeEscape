import pygame

class ModeSelector:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 36)
        
        self.selected_mode = 0
        self.modes = ['EASY', 'NORMAL', 'ADVANCED']
        self.mode_descriptions = [
            'Base game - Perfect for beginners',
            'Enhanced gameplay with new features',
            'Maximum challenge - Coming soon!'
        ]
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 150, 255)
        self.GRAY = (128, 128, 128)
        self.BLACK = (0, 0, 0)
        self.YELLOW = (255, 255, 0)
    
    def handle_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_mode = (self.selected_mode - 1) % len(self.modes)
            elif event.key == pygame.K_DOWN:
                self.selected_mode = (self.selected_mode + 1) % len(self.modes)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.modes[self.selected_mode] == 'ADVANCED':
                    return None  # Not implemented yet
                return {'action': 'select_mode', 'mode': self.modes[self.selected_mode].lower()}
            elif event.key == pygame.K_ESCAPE:
                return {'action': 'back_to_menu'}
        elif event.type == pygame.MOUSEMOTION:
            mouse_y = event.pos[1]
            # Check which mode mouse is over
            y_start = 250
            for i in range(len(self.modes)):
                mode_y = y_start + i * 80
                if mode_y - 30 <= mouse_y <= mode_y + 30:
                    self.selected_mode = i
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.modes[self.selected_mode] == 'ADVANCED':
                    return None  # Not implemented yet
                return {'action': 'select_mode', 'mode': self.modes[self.selected_mode].lower()}
        return None
    
    def draw(self):
        self.screen.fill(self.BLACK)
        
        # Title
        title_text = self.font_large.render("SELECT DIFFICULTY", True, self.GREEN)
        title_rect = title_text.get_rect(center=(400, 150))
        self.screen.blit(title_text, title_rect)
        
        # Mode options
        y_start = 250
        for i, mode in enumerate(self.modes):
            color = self.WHITE if i == self.selected_mode else self.GRAY
            
            # Special handling for Advanced
            if mode == 'ADVANCED':
                color = self.GRAY
                mode_text = f"{mode} (Coming Soon)"
            else:
                mode_text = mode
            
            mode_surface = self.font_medium.render(mode_text, True, color)
            mode_rect = mode_surface.get_rect(center=(400, y_start + i * 80))
            self.screen.blit(mode_surface, mode_rect)
            
            # Description
            desc_color = self.YELLOW if i == self.selected_mode else self.GRAY
            desc_surface = self.font_small.render(self.mode_descriptions[i], True, desc_color)
            desc_rect = desc_surface.get_rect(center=(400, y_start + i * 80 + 30))
            self.screen.blit(desc_surface, desc_rect)
            
            # Highlight selected
            if i == self.selected_mode and mode != 'ADVANCED':
                pygame.draw.rect(self.screen, self.BLUE, mode_rect, 3)
        
        # Instructions
        inst_text = self.font_small.render("↑↓ Navigate | ENTER/SPACE Select | ESC Back", True, self.WHITE)
        inst_rect = inst_text.get_rect(center=(400, 520))
        self.screen.blit(inst_text, inst_rect)