import pygame
import math
import heapq

class Enemy:
    def __init__(self, x, y, sound_manager=None):
        self.x = x
        self.y = y
        self.sound_manager = sound_manager
        self.SIZE = 12
        self.SPEED = 2.0
        self.RED_COLOR = (255, 0, 0)
        
        # Health system
        self.MAX_HEALTH = 3
        self.health = self.MAX_HEALTH
        self.stunned = False
        self.stun_timer = 0
        self.STUN_DURATION = 10000  # 10 seconds
        
        self.bullets = []
        self.shoot_timer = 0
        self.SHOOT_DELAY = 1500
        
        # A* pathfinding
        self.path = []
        self.path_timer = 0
        self.PATH_UPDATE_DELAY = 500  # Update path every 0.5 seconds
        
        # Movement
        self.move_timer = 0
        self.MOVE_DELAY = 80
        
    def update(self, snake_x=None, snake_y=None, maze=None):
        current_time = pygame.time.get_ticks()
        
        # Handle stun
        if self.stunned:
            if current_time - self.stun_timer > self.STUN_DURATION:
                self.stunned = False
                self.health = self.MAX_HEALTH  # Respawn with full health
            else:
                return  # Don't move or shoot while stunned
        
        # Update path using A*
        if snake_x and snake_y and maze and current_time - self.path_timer > self.PATH_UPDATE_DELAY:
            self.path = self.find_path_to_target(snake_x, snake_y, maze)
            self.path_timer = current_time
        
        # Move along path using A*
        if current_time - self.move_timer > self.MOVE_DELAY:
            if self.path:
                next_pos = self.path[0]
                target_x, target_y = next_pos[0] * maze.CELL_SIZE + maze.CELL_SIZE // 2, next_pos[1] * maze.CELL_SIZE + maze.CELL_SIZE // 2
                
                # Move towards next position
                dx = target_x - self.x
                dy = target_y - self.y
                
                if abs(dx) < 5 and abs(dy) < 5:  # Reached waypoint
                    self.path.pop(0)
                else:
                    # Move towards target
                    if abs(dx) > abs(dy):
                        self.x += 8 if dx > 0 else -8
                    else:
                        self.y += 8 if dy > 0 else -8
                        
            self.move_timer = current_time
                
        # Keep enemy in bounds
        self.x = max(self.SIZE, min(800 - self.SIZE, self.x))
        self.y = max(self.SIZE, min(600 - self.SIZE, self.y))
        
        # Shooting
        if not self.stunned and current_time - self.shoot_timer > self.SHOOT_DELAY:
            if snake_x and snake_y:
                self.shoot_at_target(snake_x, snake_y)
            self.shoot_timer = current_time
            
        # Update bullets
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            
            if (bullet['x'] < 0 or bullet['x'] > 800 or 
                bullet['y'] < 0 or bullet['y'] > 600 or
                (maze and maze.is_wall(bullet['x'], bullet['y']))):
                self.bullets.remove(bullet)
                
    def shoot_at_target(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            bullet = {
                'x': self.x,
                'y': self.y,
                'dx': (dx / distance) * 4,
                'dy': (dy / distance) * 4
            }
            self.bullets.append(bullet)
            
    def take_damage(self):
        if not self.stunned:
            self.health -= 1
            if self.sound_manager:
                self.sound_manager.play('hit')
            print(f"Enemy hit! Health: {self.health}/{self.MAX_HEALTH}")
            if self.health <= 0:
                self.stunned = True
                self.stun_timer = pygame.time.get_ticks()
                if self.sound_manager:
                    self.sound_manager.play('stun')
                print("Enemy stunned for 10 seconds!")
                return True
        return False
    
    def find_path_to_target(self, target_x, target_y, maze):
        # Convert positions to grid coordinates
        start_col = int(self.x) // maze.CELL_SIZE
        start_row = int(self.y) // maze.CELL_SIZE
        target_col = int(target_x) // maze.CELL_SIZE
        target_row = int(target_y) // maze.CELL_SIZE
        
        # A* pathfinding
        open_set = [(0, start_col, start_row)]
        came_from = {}
        g_score = {(start_col, start_row): 0}
        
        while open_set:
            current_f, current_col, current_row = heapq.heappop(open_set)
            
            if current_col == target_col and current_row == target_row:
                # Reconstruct path
                path = []
                while (current_col, current_row) in came_from:
                    path.append((current_col, current_row))
                    current_col, current_row = came_from[(current_col, current_row)]
                return path[::-1]  # Reverse path
            
            # Check neighbors
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                neighbor_col, neighbor_row = current_col + dx, current_row + dy
                
                if (0 <= neighbor_col < maze.cols and 0 <= neighbor_row < maze.rows and 
                    not maze.grid[neighbor_row][neighbor_col]):
                    
                    tentative_g = g_score[(current_col, current_row)] + 1
                    
                    if (neighbor_col, neighbor_row) not in g_score or tentative_g < g_score[(neighbor_col, neighbor_row)]:
                        came_from[(neighbor_col, neighbor_row)] = (current_col, current_row)
                        g_score[(neighbor_col, neighbor_row)] = tentative_g
                        
                        # Heuristic: Manhattan distance
                        h = abs(neighbor_col - target_col) + abs(neighbor_row - target_row)
                        f = tentative_g + h
                        
                        heapq.heappush(open_set, (f, neighbor_col, neighbor_row))
        
        return []  # No path found
    
    def draw(self, screen):
        if self.stunned:
            # Flash white when stunned
            flash_color = (255, 255, 255) if (pygame.time.get_ticks() // 200) % 2 else (100, 100, 100)
            pygame.draw.rect(screen, flash_color, 
                            (self.x - self.SIZE, self.y - self.SIZE, 
                             self.SIZE * 2, self.SIZE * 2))
        else:
            # Always red, darker when damaged
            health_ratio = self.health / self.MAX_HEALTH
            red_intensity = int(255 * (0.6 + 0.4 * health_ratio))
            enemy_color = (red_intensity, 0, 0)
            
            pygame.draw.rect(screen, enemy_color, 
                            (self.x - self.SIZE, self.y - self.SIZE, 
                             self.SIZE * 2, self.SIZE * 2))
        
        # Health bar
        if not self.stunned:
            bar_width = 30
            bar_height = 4
            bar_x = self.x - bar_width // 2
            bar_y = self.y - self.SIZE - 10
            
            health_ratio = self.health / self.MAX_HEALTH
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
            health_width = int(bar_width * health_ratio)
            pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, health_width, bar_height))
        
        # Bullets
        for bullet in self.bullets:
            pygame.draw.circle(screen, (255, 100, 100), 
                             (int(bullet['x']), int(bullet['y'])), 3)
    
    def update_bullets_only(self, maze):
        """Update only bullets during head start period"""
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            
            if (bullet['x'] < 0 or bullet['x'] > 800 or 
                bullet['y'] < 0 or bullet['y'] > 600 or
                (maze and maze.is_wall(bullet['x'], bullet['y']))):
                self.bullets.remove(bullet)