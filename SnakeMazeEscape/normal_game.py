import pygame
import sys
import random
from maze import Maze
from snake import Snake
from enemy import Enemy
from sounds import SoundManager

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BLACK = (0, 0, 0)

class NormalGame:
    def __init__(self, screen, sound_manager, timer_minutes):
        self.screen = screen
        self.sound_manager = sound_manager
        self.clock = pygame.time.Clock()
        self.timer_minutes = timer_minutes
        self.reset_game_state()
    
    def reset_game_state(self):
        """Complete reset of all game state for fresh start"""
        self.running = True
        self.game_state = 'playing'
        
        # Timer settings
        self.session_timer = self.timer_minutes * 60 * 1000 if self.timer_minutes > 0 else 0
        self.timer_start_delay = 2 * 60 * 1000  # 2 minutes delay
        self.game_start_time = pygame.time.get_ticks()
        self.timer_started = False
        self.timer_enabled = self.timer_minutes > 0
        
        # Fresh game objects
        self.maze = Maze(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.maze.complexity = 0.9  # Increased complexity for Normal mode
        
        # Fresh snake at entrance
        entrance_x = 1 * 20 + 10
        entrance_y = 1 * 20 + 10
        self.snake = Snake(entrance_x, entrance_y, self.sound_manager)
        
        # Reset enemy system
        self.enemies = []
        self.enemy_spawn_delay = 10000  # 10 seconds
        self.enemies_spawned = False
        self.enemy_spawn_time = 0
        
        # Reset power-ups
        self.stun_fruit = None
        self.shield_fruit = None
        self.shield_active = False
        self.shield_timer = 0
        self.super_stun_available = False
        
        # Reset ping alert
        self.ping_alert = False
        self.ping_blink_timer = 0
        
    def spawn_enemies(self):
        # Enemy 1: Far from snake spawn (entrance is at 30, 30)
        enemy1_x = SCREEN_WIDTH - 100  # Right side
        enemy1_y = 100
        enemy1 = Enemy(enemy1_x, enemy1_y, self.sound_manager)
        enemy1.SHOOT_DELAY = 1000  # More frequent shooting
        
        # Enemy 2: Bottom area, far from entrance
        enemy2_x = SCREEN_WIDTH // 2
        enemy2_y = SCREEN_HEIGHT - 100
        enemy2 = Enemy(enemy2_x, enemy2_y, self.sound_manager)
        enemy2.SHOOT_DELAY = 1000  # More frequent shooting
        
        self.enemies = [enemy1, enemy2]
        
    def spawn_power_ups(self):
        current_time = pygame.time.get_ticks()
        
        # Spawn stun fruit (rare) - larger blue fruit
        if not self.stun_fruit and random.randint(1, 500) == 1:
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            if not self.maze.is_wall(x, y):
                self.stun_fruit = {'x': x, 'y': y, 'spawn_time': current_time}
        
        # Spawn shield fruit (rare) - green fruit
        if not self.shield_fruit and random.randint(1, 400) == 1:
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 100)
            if not self.maze.is_wall(x, y):
                self.shield_fruit = {'x': x, 'y': y, 'spawn_time': current_time}
    
    def check_ping_alert(self):
        self.ping_alert = False
        for enemy in self.enemies:
            if enemy.stunned:
                continue
                
            # Manhattan distance check
            distance = abs(enemy.x - self.snake.head_x) + abs(enemy.y - self.snake.head_y)
            if distance < 150:  # Threshold
                # Simple line-of-sight check (basic pathfinding toward player)
                dx = self.snake.head_x - enemy.x
                dy = self.snake.head_y - enemy.y
                if abs(dx) > abs(dy):
                    # Enemy moving horizontally toward player
                    if (dx > 0 and enemy.x < self.snake.head_x) or (dx < 0 and enemy.x > self.snake.head_x):
                        self.ping_alert = True
                        break
                else:
                    # Enemy moving vertically toward player
                    if (dy > 0 and enemy.y < self.snake.head_y) or (dy < 0 and enemy.y > self.snake.head_y):
                        self.ping_alert = True
                        break
    
    def update(self):
        if self.game_state != 'playing':
            return
            
        current_time = pygame.time.get_ticks()
        
        # Enemy spawn logic
        elapsed_time = current_time - self.game_start_time
        if not self.enemies_spawned and elapsed_time >= self.enemy_spawn_delay:
            self.spawn_enemies()
            self.enemies_spawned = True
            self.enemy_spawn_time = current_time
            print("Enemies spawned in Normal mode")
        
        # Timer logic (only if enabled)
        if self.timer_enabled:
            if elapsed_time >= self.timer_start_delay and not self.timer_started:
                self.timer_started = True
                self.timer_start_time = current_time
            
            if self.timer_started:
                timer_elapsed = current_time - self.timer_start_time
                if timer_elapsed >= self.session_timer:
                    self.sound_manager.play('game_over')
                    self.game_state = 'time_up'
                    return
        
        # Update snake
        self.snake.update(self.maze)
        
        # Handle super stun
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.super_stun_available:
            # Super stun all enemies
            for enemy in self.enemies:
                enemy.stunned = True
                enemy.stun_timer = current_time
                enemy.STUN_DURATION = 10000  # 10 seconds
            self.sound_manager.play('stun')
            self.super_stun_available = False
        
        # Update enemies only if spawned and game is playing
        if self.enemies_spawned and self.game_state == 'playing':
            for enemy in self.enemies:
                if enemy and hasattr(enemy, 'x') and hasattr(enemy, 'y'):
                    enemy.update(self.snake.head_x, self.snake.head_y, self.maze)
                    
                    # Check enemy bullets hitting snake using proper collision
                    snake_rect = pygame.Rect(self.snake.head_x - 8, self.snake.head_y - 8, 16, 16)
                    for bullet in enemy.bullets[:]:
                        if bullet and 'x' in bullet and 'y' in bullet:
                            bullet_rect = pygame.Rect(bullet['x'] - 4, bullet['y'] - 4, 8, 8)
                            if snake_rect.colliderect(bullet_rect):
                                enemy.bullets.remove(bullet)
                                if not self.shield_active and self.snake.ammo > 0:
                                    self.snake.ammo -= 1
                    
                    # Check physical collision with snake using proper rect collision
                    if (not enemy.stunned and not self.shield_active):
                        enemy_rect = pygame.Rect(enemy.x - 10, enemy.y - 10, 20, 20)
                        if snake_rect.colliderect(enemy_rect):
                            self.sound_manager.play('game_over')
                            self.game_state = 'game_over'
                            return
                    
                    # Check snake bullets hitting enemies using proper collision
                    enemy_rect = pygame.Rect(enemy.x - 10, enemy.y - 10, 20, 20)
                    for bullet in self.snake.bullets[:]:
                        if bullet and 'x' in bullet and 'y' in bullet:
                            bullet_rect = pygame.Rect(bullet['x'] - 4, bullet['y'] - 4, 8, 8)
                            if enemy_rect.colliderect(bullet_rect):
                                self.snake.bullets.remove(bullet)
                                enemy.take_damage()
        
        # Update shield
        if self.shield_active:
            if current_time - self.shield_timer > 15000:  # 15 seconds
                self.shield_active = False
        
        # Spawn power-ups
        self.spawn_power_ups()
        
        # Check power-up collection
        if self.stun_fruit:
            distance = ((self.stun_fruit['x'] - self.snake.head_x)**2 + (self.stun_fruit['y'] - self.snake.head_y)**2)**0.5
            if distance < 20:
                self.super_stun_available = True
                self.stun_fruit = None
        
        if self.shield_fruit:
            distance = ((self.shield_fruit['x'] - self.snake.head_x)**2 + (self.shield_fruit['y'] - self.snake.head_y)**2)**0.5
            if distance < 20:
                self.shield_active = True
                self.shield_timer = current_time
                self.sound_manager.play('shield')
                self.shield_fruit = None
        
        # Check ping alert only if enemies spawned
        if self.enemies_spawned:
            self.check_ping_alert()
        
        # Win condition
        if self.maze.is_exit(self.snake.head_x, self.snake.head_y):
            self.sound_manager.play('victory')
            self.game_state = 'victory'
    
    def draw(self):
        self.screen.fill(BLACK)
        
        if self.game_state == 'playing':
            # Draw maze and game objects
            self.maze.draw(self.screen)
            self.snake.draw(self.screen)
            
            # Draw enemies only if spawned
            if self.enemies_spawned:
                for enemy in self.enemies:
                    enemy.draw(self.screen)
            
            # Draw power-ups
            if self.stun_fruit:
                # Large blue stun fruit
                pygame.draw.circle(self.screen, (0, 0, 255), 
                                 (int(self.stun_fruit['x']), int(self.stun_fruit['y'])), 15)
                pygame.draw.circle(self.screen, (100, 100, 255), 
                                 (int(self.stun_fruit['x']), int(self.stun_fruit['y'])), 12)
            
            if self.shield_fruit:
                # Green shield fruit
                pygame.draw.circle(self.screen, (0, 255, 0), 
                                 (int(self.shield_fruit['x']), int(self.shield_fruit['y'])), 12)
                pygame.draw.circle(self.screen, (100, 255, 100), 
                                 (int(self.shield_fruit['x']), int(self.shield_fruit['y'])), 9)
            
            # Draw timer (if enabled and started)
            if self.timer_enabled and self.timer_started:
                current_time = pygame.time.get_ticks()
                remaining_time = max(0, self.session_timer - (current_time - self.timer_start_time))
                minutes = int(remaining_time // 60000)
                seconds = int((remaining_time % 60000) // 1000)
                timer_font = pygame.font.Font(None, 36)
                timer_text = timer_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, (255, 255, 255))
                self.screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))
            
            # Draw enemy spawn countdown
            if not self.enemies_spawned:
                current_time = pygame.time.get_ticks()
                elapsed_time = current_time - self.game_start_time
                remaining_spawn = max(0, self.enemy_spawn_delay - elapsed_time)
                spawn_seconds = int(remaining_spawn // 1000) + 1
                spawn_font = pygame.font.Font(None, 48)
                spawn_text = spawn_font.render(f"Enemies spawn in: {spawn_seconds}", True, (255, 255, 0))
                self.screen.blit(spawn_text, (SCREEN_WIDTH//2 - 150, 80))
            
            # Draw shield indicator
            if self.shield_active:
                shield_font = pygame.font.Font(None, 32)
                shield_text = shield_font.render("SHIELD ACTIVE", True, (0, 255, 0))
                self.screen.blit(shield_text, (10, 80))
            
            # Draw super stun indicator
            if self.super_stun_available:
                stun_font = pygame.font.Font(None, 32)
                stun_text = stun_font.render("SUPER STUN READY", True, (0, 0, 255))
                self.screen.blit(stun_text, (10, 110))
            
            # Draw ping alert
            if self.ping_alert:
                current_time = pygame.time.get_ticks()
                if (current_time // 250) % 2:  # Blink every 250ms
                    alert_font = pygame.font.Font(None, 64)
                    alert_text = alert_font.render("!", True, (255, 0, 0))
                    alert_rect = alert_text.get_rect(center=(SCREEN_WIDTH//2, 50))
                    self.screen.blit(alert_text, alert_rect)
        
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and (self.game_state == 'game_over' or self.game_state == 'victory' or self.game_state == 'time_up'):
                self.reset_game_state()  # Reset instead of returning restart action
                return None
            elif event.key == pygame.K_ESCAPE:
                return {'action': 'back_to_menu'}
        return None