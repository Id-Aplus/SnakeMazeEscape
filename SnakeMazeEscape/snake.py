import pygame

class Snake:
    def __init__(self, x, y, sound_manager=None):
        self.head_x = x
        self.head_y = y
        self.sound_manager = sound_manager
        self.size = 8
        self.head_color = (0, 255, 0)
        self.body_color = (0, 200, 0)
        
        # Snake body (list of segments) - adjusted for smaller steps
        self.body = [(x, y), (x-20, y), (x-40, y)]  # 3 segments with proper grid spacing
        
        self.direction = 'RIGHT'
        self.direction_queue = []  # Queue for smooth corner navigation
        self.move_timer = 0
        self.MOVE_DELAY = 150  # Level 7 speed (was 100 = Level 10)
        self.MAX_QUEUE_SIZE = 2  # Allow 2 buffered direction changes
        
        self.ammo = 0
        self.bullets = []
        self.last_shot = 0

    def update(self, maze):
        current_time = pygame.time.get_ticks()
        
        # Handle direction changes - detect ALL inputs first
        keys = pygame.key.get_pressed()
        new_direction = None
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            new_direction = 'LEFT'
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            new_direction = 'RIGHT'
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            new_direction = 'UP'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            new_direction = 'DOWN'
        
        # Check for smooth reversal when opposite direction is pressed
        if new_direction:
            is_opposite = ((self.direction == 'LEFT' and new_direction == 'RIGHT') or
                         (self.direction == 'RIGHT' and new_direction == 'LEFT') or
                         (self.direction == 'UP' and new_direction == 'DOWN') or
                         (self.direction == 'DOWN' and new_direction == 'UP'))
            
            if is_opposite:
                # Execute smooth reversal - head and tail switch
                self.body.reverse()
                self.direction = new_direction
                self.head_x, self.head_y = self.body[0]
                self.direction_queue.clear()
                print(f"Snake reversed! New direction: {new_direction}")
                return  # Skip normal queueing
            
            # Block invalid directions (non-opposite, non-perpendicular)
            if ((self.direction == 'LEFT' and new_direction == 'RIGHT') or
                (self.direction == 'RIGHT' and new_direction == 'LEFT') or
                (self.direction == 'UP' and new_direction == 'DOWN') or
                (self.direction == 'DOWN' and new_direction == 'UP')):
                pass  # Already handled above
            elif ((self.direction == 'LEFT' and new_direction == 'RIGHT') or
                  (self.direction == 'RIGHT' and new_direction == 'LEFT') or
                  (self.direction == 'UP' and new_direction == 'DOWN') or
                  (self.direction == 'DOWN' and new_direction == 'UP')):
                new_direction = None  # Block true reverse into body
        
        # Add to queue if valid and not already queued
        if (new_direction and len(self.direction_queue) < self.MAX_QUEUE_SIZE and 
            (not self.direction_queue or self.direction_queue[-1] != new_direction)):
            self.direction_queue.append(new_direction)
                
        if keys[pygame.K_SPACE] and current_time - self.last_shot > 300 and self.ammo > 0:
            self.shoot()
            self.last_shot = current_time
        
        if current_time - self.move_timer > self.MOVE_DELAY:
            MOVE_STEP = 20  # Grid-aligned movement
            
            # Process direction queue for smooth corner navigation
            if self.direction_queue:
                potential_direction = self.direction_queue[0]
                
                # Test if the queued direction is now valid
                test_x, test_y = self.body[0]
                
                if potential_direction == 'LEFT':
                    test_x -= MOVE_STEP
                elif potential_direction == 'RIGHT':
                    test_x += MOVE_STEP
                elif potential_direction == 'UP':
                    test_y -= MOVE_STEP
                elif potential_direction == 'DOWN':
                    test_y += MOVE_STEP
                
                # If the queued direction is valid, use it
                if not maze.is_wall(test_x, test_y):
                    self.direction = self.direction_queue.pop(0)
                else:
                    # Remove invalid direction from queue (no auto-bounce)
                    self.direction_queue.pop(0)
            
            # Calculate new head position (grid-based movement)
            new_head_x, new_head_y = self.body[0]
            
            if self.direction == 'LEFT':
                new_head_x -= MOVE_STEP
            elif self.direction == 'RIGHT':
                new_head_x += MOVE_STEP
            elif self.direction == 'UP':
                new_head_y -= MOVE_STEP
            elif self.direction == 'DOWN':
                new_head_y += MOVE_STEP
                
            # Check if new position is valid (not a wall)
            if not maze.is_wall(new_head_x, new_head_y):
                # Move snake: add new head, remove tail
                self.body.insert(0, (new_head_x, new_head_y))
                self.body.pop()  # Remove tail
                
                # Update head position for other functions
                self.head_x, self.head_y = new_head_x, new_head_y
                
                # Play movement sound
                if self.sound_manager:
                    self.sound_manager.play('move')
                
                # Check food collision
                if maze.check_food_collision(new_head_x, new_head_y, self.size):
                    self.ammo += 1
                    if self.sound_manager:
                        self.sound_manager.play('food')
                    print(f"Food eaten! Ammo: {self.ammo}")  # Debug
            # Otherwise: snake simply stops (no bounce)
                    
            self.move_timer = current_time
        
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['dx']
            bullet['y'] += bullet['dy']
            
            if (maze.is_wall(bullet['x'], bullet['y']) or
                bullet['x'] < 0 or bullet['x'] > 800 or 
                bullet['y'] < 0 or bullet['y'] > 600):
                self.bullets.remove(bullet)

    def shoot(self):
        if self.ammo > 0 and len(self.body) > 0:  # Only shoot if we have ammo and body exists
            # Get tail position (last segment)
            tail_x, tail_y = self.body[-1]
            
            # Shoot in the opposite direction of movement (from tail backwards)
            dx, dy = 0, 0
            if self.direction == 'LEFT':
                dx = 6  # Shoot right from tail when moving left
            elif self.direction == 'RIGHT':
                dx = -6  # Shoot left from tail when moving right
            elif self.direction == 'UP':
                dy = 6  # Shoot down from tail when moving up
            elif self.direction == 'DOWN':
                dy = -6  # Shoot up from tail when moving down
                
            bullet = {'x': tail_x, 'y': tail_y, 'dx': dx, 'dy': dy}
            self.bullets.append(bullet)
            self.ammo -= 1  # Decrease ammo after shooting
            
            # Play shooting sound
            if self.sound_manager:
                self.sound_manager.play('shoot')
            
            print(f"Shot fired from tail! Ammo remaining: {self.ammo}")  # Debug

    def draw(self, screen):
        # Draw snake body
        for i, (x, y) in enumerate(self.body):
            if i == 0:  # Head
                pygame.draw.rect(screen, self.head_color, 
                                (x - self.size, y - self.size, 
                                 self.size * 2, self.size * 2))
                # Draw eyes on head
                pygame.draw.circle(screen, (255, 255, 255), (x-3, y-3), 2)
                pygame.draw.circle(screen, (255, 255, 255), (x+3, y-3), 2)
                pygame.draw.circle(screen, (0, 0, 0), (x-3, y-3), 1)
                pygame.draw.circle(screen, (0, 0, 0), (x+3, y-3), 1)
            else:  # Body
                pygame.draw.rect(screen, self.body_color, 
                                (x - self.size, y - self.size, 
                                 self.size * 2, self.size * 2))
        
        for bullet in self.bullets:
            pygame.draw.circle(screen, (255, 255, 0), 
                             (int(bullet['x']), int(bullet['y'])), 4)
                             
        font = pygame.font.Font(None, 36)
        ammo_text = font.render(f"Ammo: {self.ammo}", True, (255, 255, 255))
        screen.blit(ammo_text, (10, 10))
        
        controls_font = pygame.font.Font(None, 24)
        controls_text = controls_font.render("WASD/Arrows: Move | SPACE: Shoot", True, (200, 200, 200))
        screen.blit(controls_text, (10, 50))