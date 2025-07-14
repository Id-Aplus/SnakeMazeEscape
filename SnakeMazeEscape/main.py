import pygame
import sys
from maze import Maze
from snake import Snake
from enemy import Enemy
from sounds import SoundManager
from menu.main_menu import MainMenu, ControlsScreen
from normal_mode import NormalMode

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BLACK = (0, 0, 0)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SNAKEY MAZE")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = 'menu'  # 'menu', 'controls', 'playing', 'game_over', 'victory'
        
        # Screen scaling for fullscreen
        self.fullscreen = False
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Initialize sound system
        self.sound_manager = SoundManager()
        
        # Initialize menu system
        self.main_menu = MainMenu(self.screen, self.sound_manager)
        self.controls_screen = ControlsScreen(self.screen)
        self.normal_mode = None
        
        # Game settings from menu
        self.difficulty = 'normal'
        self.timer_minutes = 3
        self.timer_enabled = True
        self.game_timer = 0
        self.start_time = 0
        
        self.maze = Maze(SCREEN_WIDTH, SCREEN_HEIGHT)
        # Start snake at entrance position
        entrance_x = 1 * 20 + 10  # Center of entrance cell
        entrance_y = 1 * 20 + 10
        self.snake = Snake(entrance_x, entrance_y, self.sound_manager)
        # Enemy timing constants
        self.ENEMY_SPAWN_DELAY = 5000  # 5 seconds initial spawn
        self.ENEMY_HEAD_START = 10000  # 10 seconds before enemy moves
        
        self.enemy = None
        self.enemy_spawn_timer = 0
        self.enemy_start_time = 0  # Track when enemy should start moving
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif self.game_state == 'menu':
                result = self.main_menu.handle_events(event)
                if result:
                    if result['action'] == 'start_game':
                        if result['difficulty'] == 'normal':
                            self.start_normal_game(result['timer'])
                        else:
                            self.start_new_game(result['difficulty'], result['timer'])
                    elif result['action'] == 'show_controls':
                        self.game_state = 'controls'
                    elif result['action'] == 'toggle_fullscreen':
                        self.toggle_fullscreen()
                    elif result['action'] == 'exit':
                        self.running = False
            elif self.game_state == 'controls':
                result = self.controls_screen.handle_events(event)
                if result and result['action'] == 'back_to_menu':
                    self.game_state = 'menu'
            elif self.game_state == 'normal_playing':
                if self.normal_mode:
                    result = self.normal_mode.handle_events(event)
                    if result:
                        if result['action'] == 'restart':
                            self.start_normal_game(self.timer_minutes)
                        elif result['action'] == 'back_to_menu':
                            self.game_state = 'menu'
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (self.game_state == 'game_over' or self.game_state == 'victory' or self.game_state == 'time_up'):
                    self.game_state = 'menu'  # Return to menu
                elif event.key == pygame.K_ESCAPE:
                    if self.game_state == 'playing':
                        self.game_state = 'menu'  # Return to menu during game
                    else:
                        pygame.quit()
                        sys.exit()
                # F1 key removed - fullscreen only via menu button
                
    def start_new_game(self, difficulty, timer_minutes):
        self.difficulty = difficulty
        self.timer_minutes = timer_minutes
        self.timer_enabled = self.main_menu.timer_enabled
        self.game_state = 'playing'
        self.start_time = pygame.time.get_ticks()
        
        # Initialize game objects
        self.maze = Maze(SCREEN_WIDTH, SCREEN_HEIGHT)
        entrance_x = 1 * 20 + 10
        entrance_y = 1 * 20 + 10
        self.snake = Snake(entrance_x, entrance_y, self.sound_manager)
        
        # Enemy timing constants
        self.ENEMY_SPAWN_DELAY = 5000
        self.ENEMY_HEAD_START = 10000
        
        self.enemy = None
        self.enemy_spawn_timer = 0
        self.enemy_start_time = 0
    
    def start_normal_game(self, timer_minutes):
        self.timer_minutes = timer_minutes
        self.normal_mode = NormalMode(self.screen, self.sound_manager, timer_minutes)
        self.game_state = 'normal_playing'
    
    def update(self):
        if self.game_state == 'normal_playing':
            if self.normal_mode:
                self.normal_mode.update()
            return  # Don't run base game logic for Normal mode
        elif self.game_state == 'playing':
            # Base game update logic
            # Check timer (only if enabled)
            if self.timer_enabled:
                elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
                if elapsed_time >= self.timer_minutes * 60:
                    self.sound_manager.play('game_over')
                    self.game_state = 'time_up'
                
            self.snake.update(self.maze)
            
            # Spawn enemy after delay
            if self.enemy is None and pygame.time.get_ticks() - self.enemy_spawn_timer > self.ENEMY_SPAWN_DELAY:
                # Spawn enemy at a random valid position
                spawn_x = 100 + (pygame.time.get_ticks() % 200)
                spawn_y = 100 + (pygame.time.get_ticks() % 150)
                self.enemy = Enemy(spawn_x, spawn_y, self.sound_manager)
                self.enemy_start_time = pygame.time.get_ticks()  # Record spawn time
                
            if self.enemy:
                # Only allow enemy to move after head start period
                if pygame.time.get_ticks() - self.enemy_start_time > self.ENEMY_HEAD_START:
                    self.enemy.update(self.snake.head_x, self.snake.head_y, self.maze)
                else:
                    # Enemy is spawned but not moving yet - just update bullets
                    self.enemy.update_bullets_only(self.maze)
                
                # Check if enemy bullets hit snake (reduces ammo, doesn't kill)
                for bullet in self.enemy.bullets[:]:
                    distance = ((bullet['x'] - self.snake.head_x)**2 + (bullet['y'] - self.snake.head_y)**2)**0.5
                    if distance < 15:
                        self.enemy.bullets.remove(bullet)
                        if self.snake.ammo > 0:
                            self.snake.ammo -= 1
                            self.sound_manager.play('hit')
                            print(f"Hit by enemy! Ammo reduced to: {self.snake.ammo}")
                        else:
                            print("No ammo lost - already at 0!")
                
                # Game over only when ACTIVE enemy physically catches snake
                if not self.enemy.stunned:  # Only check collision if enemy is not stunned
                    distance_to_enemy = ((self.enemy.x - self.snake.head_x)**2 + (self.enemy.y - self.snake.head_y)**2)**0.5
                    if distance_to_enemy < 20:  # Physical contact
                        self.sound_manager.play('game_over')
                        print("GAME OVER! Enemy caught you!")
                        self.game_state = 'game_over'
                        
                # Check if snake bullets hit enemy
                for bullet in self.snake.bullets[:]:
                    distance = ((bullet['x'] - self.enemy.x)**2 + (bullet['y'] - self.enemy.y)**2)**0.5
                    if distance < 15:
                        self.snake.bullets.remove(bullet)
                        self.enemy.take_damage()  # Enemy handles its own stunning/health
                
            # Win condition
            if self.maze.is_exit(self.snake.head_x, self.snake.head_y):
                self.sound_manager.play('victory')
                print("YOU WIN! Reached the exit!")
                self.game_state = 'victory'
        else:
            return
            
    def draw(self):
        self.screen.fill(BLACK)
        
        # Create a surface for the game content
        if self.fullscreen:
            game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            game_surface.fill(BLACK)
        else:
            game_surface = self.screen
        
        if self.game_state == 'menu':
            if self.fullscreen:
                self.main_menu.screen = game_surface
            self.main_menu.draw()
        elif self.game_state == 'controls':
            if self.fullscreen:
                self.controls_screen.screen = game_surface
            self.controls_screen.draw()
        elif self.game_state == 'normal_playing':
            if self.normal_mode:
                if self.fullscreen:
                    self.normal_mode.screen = game_surface
                self.normal_mode.draw()
        elif self.game_state == 'playing':
            draw_surface = game_surface if self.fullscreen else self.screen
            self.maze.draw(draw_surface)
            self.snake.draw(draw_surface)
            
            if self.enemy:
                self.enemy.draw(draw_surface)
                
            # Draw timer (only if enabled)
            timer_font = pygame.font.Font(None, 36)
            draw_surface = game_surface if self.fullscreen else self.screen
            if self.timer_enabled:
                elapsed_time = (pygame.time.get_ticks() - self.start_time) / 1000
                remaining_time = max(0, self.timer_minutes * 60 - elapsed_time)
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                timer_text = timer_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, (255, 255, 255))
                draw_surface.blit(timer_text, (SCREEN_WIDTH - 150, 10))
            
            # Draw difficulty
            diff_text = timer_font.render(f"Difficulty: {self.difficulty.upper()}", True, (255, 255, 255))
            draw_surface.blit(diff_text, (SCREEN_WIDTH - 200, 50))
                
        elif self.game_state == 'time_up':
            # Time Up Screen
            draw_surface = game_surface if self.fullscreen else self.screen
            font = pygame.font.Font(None, 96)
            time_up_text = font.render("TIME UP!", True, (255, 255, 0))
            text_rect = time_up_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            draw_surface.blit(time_up_text, text_rect)
            
            subtitle_font = pygame.font.Font(None, 72)
            subtitle_text = subtitle_font.render("YOU LOSE", True, (255, 0, 0))
            subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            draw_surface.blit(subtitle_text, subtitle_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press R to Restart or ESC to Menu", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            draw_surface.blit(restart_text, restart_rect)
            
        elif self.game_state == 'game_over':
            # Game Over Screen
            draw_surface = game_surface if self.fullscreen else self.screen
            font = pygame.font.Font(None, 96)
            game_over_text = font.render("YOU LOSE !!!", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            draw_surface.blit(game_over_text, text_rect)
            
            subtitle_font = pygame.font.Font(None, 72)
            subtitle_text = subtitle_font.render("GAME OVER", True, (255, 100, 100))
            subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            draw_surface.blit(subtitle_text, subtitle_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press R to Restart or ESC to Quit", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            draw_surface.blit(restart_text, restart_rect)
            
        elif self.game_state == 'victory':
            # Victory Screen
            draw_surface = game_surface if self.fullscreen else self.screen
            font = pygame.font.Font(None, 96)
            victory_text = font.render("YOU WIN !!!", True, (0, 255, 0))
            text_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            draw_surface.blit(victory_text, text_rect)
            
            subtitle_font = pygame.font.Font(None, 72)
            subtitle_text = subtitle_font.render("VICTORY!", True, (100, 255, 100))
            subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            draw_surface.blit(subtitle_text, subtitle_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press R to Play Again or ESC to Quit", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            draw_surface.blit(restart_text, restart_rect)
        
        # Show head start countdown if enemy exists but hasn't started moving
        if (self.game_state == 'playing' and self.enemy and 
            pygame.time.get_ticks() - self.enemy_start_time < self.ENEMY_HEAD_START):
            remaining_time = (self.ENEMY_HEAD_START - (pygame.time.get_ticks() - self.enemy_start_time)) // 1000 + 1
            countdown_font = pygame.font.Font(None, 48)
            countdown_text = countdown_font.render(f"Enemy starts in: {remaining_time}", True, (255, 255, 0))
            draw_surface = game_surface if self.fullscreen else self.screen
            draw_surface.blit(countdown_text, (SCREEN_WIDTH//2 - 150, 80))
            
        # Scale and blit game surface to screen in fullscreen mode
        if self.fullscreen:
            scaled_surface = pygame.transform.scale(game_surface, 
                                                   (int(SCREEN_WIDTH * self.scale_x), 
                                                    int(SCREEN_HEIGHT * self.scale_y)))
            self.screen.blit(scaled_surface, (self.offset_x, self.offset_y))
        
        pygame.display.flip()
    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            # Get desktop resolution
            info = pygame.display.Info()
            desktop_width, desktop_height = info.current_w, info.current_h
            self.screen = pygame.display.set_mode((desktop_width, desktop_height), pygame.FULLSCREEN)
            
            # Calculate scaling to maintain aspect ratio
            self.scale_x = desktop_width / SCREEN_WIDTH
            self.scale_y = desktop_height / SCREEN_HEIGHT
            
            # Use uniform scaling to maintain aspect ratio
            scale = min(self.scale_x, self.scale_y)
            self.scale_x = self.scale_y = scale
            
            # Calculate centering offsets
            scaled_width = SCREEN_WIDTH * scale
            scaled_height = SCREEN_HEIGHT * scale
            self.offset_x = (desktop_width - scaled_width) // 2
            self.offset_y = (desktop_height - scaled_height) // 2
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.scale_x = self.scale_y = 1.0
            self.offset_x = self.offset_y = 0
        
        # Update menu screen references
        self.main_menu.screen = self.screen
        self.controls_screen.screen = self.screen
        
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()