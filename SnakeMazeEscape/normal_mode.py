import pygame
import sys
import random
from maze import Maze
from snake import Snake
from enemy import Enemy

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)

class NormalMode:
    def __init__(self, screen, sound_manager, timer_minutes):
        self.screen = screen
        self.sound_manager = sound_manager
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = 'playing'
        self.difficulty = 'normal'
        self.timer_minutes = timer_minutes
        self.timer_enabled = timer_minutes > 0
        self.start_time = pygame.time.get_ticks()
        
        # EXACT COPY FROM BASE GAME - Initialize game objects
        self.maze = Maze(SCREEN_WIDTH, SCREEN_HEIGHT)
        # NORMAL MODE ADDITION: Increase maze complexity
        self.maze.complexity = 1.2
        
        entrance_x = 1 * 20 + 10
        entrance_y = 1 * 20 + 10
        self.snake = Snake(entrance_x, entrance_y, self.sound_manager)
        
        # EXACT COPY FROM BASE GAME - Enemy timing constants
        self.ENEMY_SPAWN_DELAY = 5000
        self.ENEMY_HEAD_START = 10000
        
        # NORMAL MODE ADDITION: Two enemies system
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemy_start_time = 0
        self.second_enemy_spawn_time = 30000  # 30 seconds for second enemy
        self.second_enemy_spawned = False
        
        # NORMAL MODE ADDITION: Special fruits
        self.stun_fruit = None
        self.shield_fruit = None
        self.shield_active = False
        self.shield_start_time = 0
        self.stun_shot_ready = False
        
        # NORMAL MODE ADDITION: Ping alert
        self.ping_alert = False
    
    def update(self):
        if self.game_state != 'playing':
            return
            
        current_time = pygame.time.get_ticks()
        
        # EXACT COPY FROM BASE GAME - Timer check
        if self.timer_enabled:
            elapsed_time = (current_time - self.start_time) / 1000
            if elapsed_time >= self.timer_minutes * 60:
                self.sound_manager.play('game_over')
                self.game_state = 'time_up'
                return
        
        # EXACT COPY FROM BASE GAME - Snake update
        self.snake.update(self.maze)
        
        # EXACT COPY FROM BASE GAME - Enemy spawn logic (modified for two enemies)
        if not self.enemies and current_time - self.enemy_spawn_timer > self.ENEMY_SPAWN_DELAY:
            # Spawn first enemy
            spawn_x = SCREEN_WIDTH - 100
            spawn_y = SCREEN_HEIGHT - 100
            enemy = Enemy(spawn_x, spawn_y, self.sound_manager)
            self.enemies.append(enemy)
            self.enemy_start_time = current_time
        
        # NORMAL MODE ADDITION: Spawn second enemy after 30 seconds
        if (len(self.enemies) == 1 and not self.second_enemy_spawned and 
            current_time - self.enemy_start_time > self.second_enemy_spawn_time):
            spawn_x = 100
            spawn_y = 100
            enemy2 = Enemy(spawn_x, spawn_y, self.sound_manager)
            self.enemies.append(enemy2)
            self.second_enemy_spawned = True
        
        # EXACT COPY FROM BASE GAME - Enemy updates and collision
        for enemy in self.enemies:
            if current_time - self.enemy_start_time > self.ENEMY_HEAD_START:
                enemy.update(self.snake.head_x, self.snake.head_y, self.maze)
            
            # EXACT COPY FROM BASE GAME - Check enemy bullets hitting snake
            for bullet in enemy.bullets[:]:
                distance_to_snake = ((bullet['x'] - self.snake.head_x)**2 + (bullet['y'] - self.snake.head_y)**2)**0.5
                if distance_to_snake < 15:
                    enemy.bullets.remove(bullet)
                    # NORMAL MODE ADDITION: Shield protection
                    if not self.shield_active and self.snake.ammo > 0:
                        self.snake.ammo -= 1
                        self.sound_manager.play('hit')
                        print(f"Hit by enemy! Ammo reduced to: {self.snake.ammo}")
                    else:
                        print("No ammo lost - already at 0!")
            
            # EXACT COPY FROM BASE GAME - Check physical collision
            if current_time - self.enemy_start_time > self.ENEMY_HEAD_START:
                distance_to_enemy = ((enemy.x - self.snake.head_x)**2 + (enemy.y - self.snake.head_y)**2)**0.5
                print(f"DEBUG: Enemy at ({enemy.x}, {enemy.y}), Snake at ({self.snake.head_x}, {self.snake.head_y}), Distance: {distance_to_enemy}")
                # NORMAL MODE ADDITION: Shield protection
                if distance_to_enemy < 20 and not self.shield_active:
                    print(f"DEBUG: COLLISION DETECTED! Distance: {distance_to_enemy}, Shield: {self.shield_active}")
                    self.sound_manager.play('game_over')
                    print("GAME OVER! Enemy caught you!")
                    self.game_state = 'game_over'
                    return
            
            # EXACT COPY FROM BASE GAME - Check snake bullets hitting enemy
            for bullet in self.snake.bullets[:]:
                distance_to_enemy = ((bullet['x'] - enemy.x)**2 + (bullet['y'] - enemy.y)**2)**0.5
                if distance_to_enemy < 15:
                    self.snake.bullets.remove(bullet)
                    enemy.take_damage()
        
        # NORMAL MODE ADDITION: Handle special shooting
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.stun_shot_ready:
            # Stun all enemies
            for enemy in self.enemies:
                enemy.stunned = True
                enemy.stun_timer = current_time
                enemy.STUN_DURATION = 10000  # 10 seconds
            self.sound_manager.play('stun')
            self.stun_shot_ready = False
        
        # NORMAL MODE ADDITION: Update shield
        if self.shield_active and current_time - self.shield_start_time > 15000:
            self.shield_active = False
        
        # NORMAL MODE ADDITION: Spawn special fruits
        if not self.stun_fruit and random.randint(1, 1000) == 1:
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            if not self.maze.is_wall(x, y):
                self.stun_fruit = {'x': x, 'y': y}
        
        if not self.shield_fruit and random.randint(1, 800) == 1:
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            if not self.maze.is_wall(x, y):
                self.shield_fruit = {'x': x, 'y': y}
        
        # NORMAL MODE ADDITION: Check fruit collection
        if self.stun_fruit:
            distance = ((self.stun_fruit['x'] - self.snake.head_x)**2 + (self.stun_fruit['y'] - self.snake.head_y)**2)**0.5
            if distance < 20:
                self.stun_shot_ready = True
                self.stun_fruit = None
        
        if self.shield_fruit:
            distance = ((self.shield_fruit['x'] - self.snake.head_x)**2 + (self.shield_fruit['y'] - self.snake.head_y)**2)**0.5
            if distance < 20:
                self.shield_active = True
                self.shield_start_time = current_time
                self.sound_manager.play('shield')
                self.shield_fruit = None
        
        # NORMAL MODE ADDITION: Ping alert
        self.ping_alert = False
        for enemy in self.enemies:
            if not enemy.stunned:
                distance = ((enemy.x - self.snake.head_x)**2 + (enemy.y - self.snake.head_y)**2)**0.5
                if distance < 120:
                    self.ping_alert = True
                    break
        
        # EXACT COPY FROM BASE GAME - Win condition
        if self.maze.is_exit(self.snake.head_x, self.snake.head_y):
            self.sound_manager.play('victory')
            print("YOU WIN! Reached the exit!")
            self.game_state = 'victory'
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if self.game_state == 'playing':
            # EXACT COPY FROM BASE GAME - Draw game objects
            self.maze.draw(self.screen)
            self.snake.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            # NORMAL MODE ADDITION: Draw special fruits
            if self.stun_fruit:
                pygame.draw.circle(self.screen, (0, 0, 255), 
                                 (int(self.stun_fruit['x']), int(self.stun_fruit['y'])), 15)
            
            if self.shield_fruit:
                pygame.draw.circle(self.screen, (0, 255, 0), 
                                 (int(self.shield_fruit['x']), int(self.shield_fruit['y'])), 12)
            
            # NORMAL MODE ADDITION: Draw UI indicators
            font = pygame.font.Font(None, 32)
            if self.shield_active:
                shield_text = font.render("SHIELD ACTIVE", True, (0, 255, 0))
                self.screen.blit(shield_text, (10, 80))
            
            if self.stun_shot_ready:
                stun_text = font.render("STUN SHOT READY", True, (0, 0, 255))
                self.screen.blit(stun_text, (10, 110))
            
            if self.ping_alert and (pygame.time.get_ticks() // 250) % 2:
                alert_font = pygame.font.Font(None, 64)
                alert_text = alert_font.render("!", True, (255, 0, 0))
                alert_rect = alert_text.get_rect(center=(SCREEN_WIDTH//2, 50))
                self.screen.blit(alert_text, alert_rect)
            
            # EXACT COPY FROM BASE GAME - Show head start countdown
            current_time = pygame.time.get_ticks()
            if (self.enemies and 
                current_time - self.enemy_start_time < self.ENEMY_HEAD_START):
                remaining_time = (self.ENEMY_HEAD_START - (current_time - self.enemy_start_time)) // 1000 + 1
                countdown_font = pygame.font.Font(None, 48)
                countdown_text = countdown_font.render(f"Enemy starts in: {remaining_time}", True, (255, 255, 0))
                self.screen.blit(countdown_text, (SCREEN_WIDTH//2 - 150, 80))
            
            # EXACT COPY FROM BASE GAME - Draw timer
            if self.timer_enabled:
                elapsed_time = (current_time - self.start_time) / 1000
                remaining_time = max(0, self.timer_minutes * 60 - elapsed_time)
                minutes = int(remaining_time // 60)
                seconds = int(remaining_time % 60)
                timer_font = pygame.font.Font(None, 36)
                timer_text = timer_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, (255, 255, 255))
                self.screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))
            
            # Draw difficulty
            diff_text = timer_font.render(f"Difficulty: {self.difficulty.upper()}", True, (255, 255, 255))
            self.screen.blit(diff_text, (SCREEN_WIDTH - 200, 50))
        
        # EXACT COPY FROM BASE GAME - Game over screens
        elif self.game_state == 'time_up':
            font = pygame.font.Font(None, 96)
            time_up_text = font.render("TIME UP!", True, (255, 255, 0))
            text_rect = time_up_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            self.screen.blit(time_up_text, text_rect)
            
            subtitle_font = pygame.font.Font(None, 72)
            subtitle_text = subtitle_font.render("YOU LOSE", True, (255, 0, 0))
            subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(subtitle_text, subtitle_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press R to Restart or ESC to Menu", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            self.screen.blit(restart_text, restart_rect)
            
        elif self.game_state == 'game_over':
            font = pygame.font.Font(None, 96)
            game_over_text = font.render("YOU LOSE !!!", True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            self.screen.blit(game_over_text, text_rect)
            
            subtitle_font = pygame.font.Font(None, 72)
            subtitle_text = subtitle_font.render("GAME OVER", True, (255, 100, 100))
            subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(subtitle_text, subtitle_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press R to Restart or ESC to Menu", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            self.screen.blit(restart_text, restart_rect)
        
        elif self.game_state == 'victory':
            font = pygame.font.Font(None, 96)
            victory_text = font.render("YOU WIN !!!", True, (0, 255, 0))
            text_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 80))
            self.screen.blit(victory_text, text_rect)
            
            subtitle_font = pygame.font.Font(None, 72)
            subtitle_text = subtitle_font.render("VICTORY!", True, (100, 255, 100))
            subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            self.screen.blit(subtitle_text, subtitle_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render("Press R to Play Again or ESC to Menu", True, (255, 255, 255))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40))
            self.screen.blit(restart_text, restart_rect)
    
    def handle_events(self, event):
        # EXACT COPY FROM BASE GAME - Event handling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (self.game_state == 'game_over' or self.game_state == 'victory' or self.game_state == 'time_up'):
                return {'action': 'restart'}
            elif event.key == pygame.K_ESCAPE:
                return {'action': 'back_to_menu'}
        return None