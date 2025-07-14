import pygame
import random
from collections import deque

class Maze:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.CELL_SIZE = 20
        self.cols = width // self.CELL_SIZE
        self.rows = height // self.CELL_SIZE
        
        # Ensure odd dimensions for proper maze generation
        if self.cols % 2 == 0:
            self.cols -= 1
        if self.rows % 2 == 0:
            self.rows -= 1
            
        # Colors
        self.WALL_COLOR = (80, 80, 80)
        self.PATH_COLOR = (20, 20, 20)
        self.FOOD_COLOR = (255, 255, 0)
        self.ENTRANCE_COLOR = (0, 255, 0)
        self.EXIT_COLOR = (255, 0, 255)
        
        # Generate maze
        self.grid = self.generate_complex_maze()
        self.entrance_pos = (1, 1)
        self.exit_pos = (self.cols - 2, self.rows - 2)
        
        self.food_positions = self.place_food()
        
    def generate_complex_maze(self):
        # Initialize grid - all walls
        grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Recursive backtracking maze generation
        def carve_maze(x, y):
            grid[y][x] = 0  # Mark current cell as path
            
            # Get all possible directions (N, S, E, W)
            directions = [(0, -2), (0, 2), (2, 0), (-2, 0)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                
                # Check if the new position is valid and unvisited
                if (0 < nx < self.cols - 1 and 0 < ny < self.rows - 1 and 
                    grid[ny][nx] == 1):
                    # Carve the wall between current and next cell
                    grid[y + dy // 2][x + dx // 2] = 0
                    carve_maze(nx, ny)
        
        # Start from random odd position
        start_x = random.randrange(1, self.cols - 1, 2)
        start_y = random.randrange(1, self.rows - 1, 2)
        carve_maze(start_x, start_y)
        
        # Add some random loops to make it more interesting
        for _ in range(self.cols * self.rows // 20):
            x = random.randrange(1, self.cols - 1)
            y = random.randrange(1, self.rows - 1)
            if grid[y][x] == 1:  # If it's a wall
                # Check if removing this wall creates a loop
                neighbors = 0
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    if (0 <= x + dx < self.cols and 0 <= y + dy < self.rows and 
                        grid[y + dy][x + dx] == 0):
                        neighbors += 1
                if neighbors >= 2:  # Creates a loop
                    grid[y][x] = 0
        
        # Ensure entrance and exit are accessible with buffer zones
        # Entrance safe zone (3x3 area)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                entrance_x, entrance_y = 1 + dx, 1 + dy
                if 0 <= entrance_x < self.cols and 0 <= entrance_y < self.rows:
                    grid[entrance_y][entrance_x] = 0
        
        # Exit safe zone (3x3 area)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                exit_x, exit_y = self.cols - 2 + dx, self.rows - 2 + dy
                if 0 <= exit_x < self.cols and 0 <= exit_y < self.rows:
                    grid[exit_y][exit_x] = 0
        
        # Ensure path from entrance to main maze
        grid[1][2] = 0  # Right of entrance
        grid[2][1] = 0  # Below entrance
        grid[1][3] = 0  # Further right
        grid[3][1] = 0  # Further below
        
        return grid
        
    def place_food(self):
        food = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == 0 and random.random() < 0.08:
                    food.append((j * self.CELL_SIZE + self.CELL_SIZE//2, 
                               i * self.CELL_SIZE + self.CELL_SIZE//2))
        return food
        
    def draw(self, screen):
        # Draw maze grid
        for row in range(self.rows):
            for col in range(self.cols):
                x = col * self.CELL_SIZE
                y = row * self.CELL_SIZE
                
                if self.grid[row][col] == 1:  # Wall
                    pygame.draw.rect(screen, self.WALL_COLOR, (x, y, self.CELL_SIZE, self.CELL_SIZE))
                else:  # Path
                    pygame.draw.rect(screen, self.PATH_COLOR, (x, y, self.CELL_SIZE, self.CELL_SIZE))
        
        # Draw entrance (green)
        entrance_x = self.entrance_pos[0] * self.CELL_SIZE
        entrance_y = self.entrance_pos[1] * self.CELL_SIZE
        pygame.draw.rect(screen, self.ENTRANCE_COLOR, 
                        (entrance_x, entrance_y, self.CELL_SIZE, self.CELL_SIZE))
        pygame.draw.rect(screen, (255, 255, 255), 
                        (entrance_x, entrance_y, self.CELL_SIZE, self.CELL_SIZE), 2)
        
        # Draw exit (purple)
        exit_x = self.exit_pos[0] * self.CELL_SIZE
        exit_y = self.exit_pos[1] * self.CELL_SIZE
        pygame.draw.rect(screen, self.EXIT_COLOR, 
                        (exit_x, exit_y, self.CELL_SIZE, self.CELL_SIZE))
        pygame.draw.rect(screen, (255, 255, 255), 
                        (exit_x, exit_y, self.CELL_SIZE, self.CELL_SIZE), 2)
        
        # Draw labels
        font = pygame.font.Font(None, 16)
        start_text = font.render("START", True, (255, 255, 255))
        screen.blit(start_text, (entrance_x + 2, entrance_y + 2))
        
        exit_text = font.render("EXIT", True, (255, 255, 255))
        screen.blit(exit_text, (exit_x + 2, exit_y + 2))
        
        # Draw food
        for food_pos in self.food_positions:
            pygame.draw.circle(screen, self.FOOD_COLOR, 
                             (int(food_pos[0]), int(food_pos[1])), 6)
                             
    def is_wall(self, x, y):
        col = int(x) // self.CELL_SIZE
        row = int(y) // self.CELL_SIZE
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col] == 1
        return True
        
    def check_food_collision(self, x, y, radius):
        for i, food_pos in enumerate(self.food_positions):
            distance = ((int(x) - food_pos[0])**2 + (int(y) - food_pos[1])**2)**0.5
            if distance < radius + 6:
                self.food_positions.pop(i)
                return True
        return False
        
    def is_exit(self, x, y):
        exit_x = self.exit_pos[0] * self.CELL_SIZE
        exit_y = self.exit_pos[1] * self.CELL_SIZE
        return (exit_x <= int(x) <= exit_x + self.CELL_SIZE and 
                exit_y <= int(y) <= exit_y + self.CELL_SIZE)