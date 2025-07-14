# 🐍 SnakeMazeEscape – Developer Log

This is the full development breakdown for my submission to the **Build Games Challenge** using **Python**, **Pygame**, and **Amazon Q Developer CLI (inside VS Code)**.

> 📌 *Amazon Q Developer helped me brainstorm, generate code snippets, fix bugs, and improve logic through iterative prompting. Its AI-assisted coding was central to this project.*

---

## ✅ Step 1: Project Setup

- **Python**: v3.13  
- **Pygame**: v2.6.1  
- **OS**: Windows 11 Pro  
- **Editor**: Visual Studio Code  
- **Amazon Q CLI**: Authenticated via AWS Builder ID  
- **Repository**: Created manually (Git installation failed)

---

## ✅ Step 2: Project Structure

Initial folder layout:

📁 SnakeMazeEscape/
├── main.py
├── maze.py
├── snake.py
├── enemy.py
├── sound_manager.py
├── assets/
│ ├── sounds/
│ └── images/

bash
Copy
Edit

Created using command line:

```bash
mkdir SnakeMazeEscape
cd SnakeMazeEscape
echo. > main.py
echo. > maze.py
echo. > snake.py
echo. > enemy.py
mkdir assets
✅ Step 3: Game Window and Maze Skeleton
Prompt to Q:
"Create a Pygame window with a game loop and a randomly generated maze."

Generated Output:

Functional 800x600 window at 60 FPS

Placeholder maze

Static snake and enemy

python
Copy
Edit
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
✅ Step 4: Maze + Snake Mechanics
Replaced grid blocks with a recursive backtracking maze. Snake now moves automatically with proper wall detection and reversal behavior.

python
Copy
Edit
def generate_maze():
    grid = [[1 for _ in range(cols)] for _ in range(rows)]
    def carve(x, y):
        grid[y][x] = 0
        dirs = [(0,2), (2,0), (-2,0), (0,-2)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 < nx < cols-1 and 0 < ny < rows-1 and grid[ny][nx] == 1:
                grid[y + dy//2][x + dx//2] = 0
                carve(nx, ny)
✅ Step 5: Combat System + Ammo
Food = Ammo

Shooting uses ammo (Spacebar)

Bullet launches from tail

Enemy health + stun logic

python
Copy
Edit
def shoot(self):
    if self.ammo > 0:
        self.bullets.append({'x': self.head_x, 'y': self.head_y, 'dir': self.direction})
        self.ammo -= 1
        self.sound_manager.play('shoot')
python
Copy
Edit
def check_hit(self, bullets):
    for bullet in bullets:
        if self.rect.colliderect(bullet['rect']):
            self.health -= 1
            self.stunned = True
            self.stun_timer = pygame.time.get_ticks()
✅ Step 6: Sound System
Full audio mapping:

BGM + SFX (shoot.wav, eat.wav, win.mp3, etc.)

Background music looped from assets/sounds/BGM.mp3

python
Copy
Edit
class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {
            'shoot': 'assets/sounds/shoot.wav',
            ...
        }
        pygame.mixer.music.load('assets/sounds/BGM.mp3')
        pygame.mixer.music.play(-1)
✅ Step 7: Fullscreen Integration
Fullscreen toggle added via menu (not F11)

Proper scaling, screen-centering, and aspect ratio

Does not interfere with window switching

python
Copy
Edit
def toggle_fullscreen(self):
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    self.screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
✅ Step 8: Menu System Implementation
Prompt to Q:
"Create a professional game menu with difficulty selection, timer, and sound settings."

Menu Features:

Difficulty: Easy / Normal / Advanced

Timer: Custom duration (or none)

Sound toggles: Music & SFX

“How to Play” screen

Fullscreen toggle

Exit Game option

python
Copy
Edit
class MainMenu:
    def __init__(self, screen, sound_manager):
        self.menu_options = ["Start Game", "Select Difficulty", "Set Timer", 
                             "How to Play", "Music", "SFX", "Exit Game"]
✅ Step 9: Game State Management
Game States:

Main Menu

Playing

Victory

Game Over

Time-Up

python
Copy
Edit
def update_game_state(self):
    if self.maze.is_exit(self.snake.head_x, self.snake.head_y):
        self.sound_manager.play('victory')
        self.game_state = 'victory'
    elif enemy_collision:
        self.sound_manager.play('game_over')
        self.game_state = 'game_over'
🧱 SnakeyMaze Base Version
📁 Folder: SnakeMazeEscape_Base_Version

Feature	Status	Notes
Maze generation	✅ Complete	Recursive, randomized
Entrance/Exit doors	✅ Complete	Green = Start, Purple = Exit
Snake movement	✅ Complete	Auto + reversible tail switch
Wall collision	✅ Complete	Snake stops at barriers
Shooting	✅ Complete	Directional bullets use ammo
Food & Ammo	✅ Complete	Food = +1 ammo
Enemy AI	✅ Complete	Pathfinding + health + stun system
Sound system	✅ Complete	SFX + BGM fully integrated
Menu system	✅ Complete	Functional with difficulty and sound toggles
Fullscreen mode	✅ Complete	Manual toggle from menu
Victory/Defeat states	✅ Complete	Proper transitions with sound

🧪 Final Bug Fixes
✅ Fixed:
Snake stalling at wall corners

Food and ammo sync

Fullscreen scaling

Static enemy logic replaced with chase AI

⚠️ Known Issues (Normal/Advanced Modes):
Instant "Game Over" on replay

Game ends even when enemy hasn’t touched snake

Timer and enemy spawn overlap in replay loops

🧠 Development Philosophy
I wanted a unique game that combined retro roots with modern mechanics. Instead of recreating an old Snake clone, I built a system that:

Challenges player reflex and memory

Explores AI-assisted development with Amazon Q

Fuses shooting, evasion, and procedural logic

“A game should feel alive — even in early builds.”

This project evolved naturally through prompt brainstorming, debug feedback, and clean architectural design. I’m proud of what it became — and I hope you have as much fun playing it as I did making it.

🏆 Competition Highlights
🔥 Unique Features
Snake with tail-switch reversal mechanic

Stun-based combat + enemy tracking

Procedural maze with guaranteed path

Full menu UI, sound control, and custom timer

Visual and auditory design polish

⚙️ Technical Excellence
Smooth 60 FPS

Clean modular code (main, snake, maze, enemy)

Robust collision logic

Fully keyboard-accessible

🤖 Amazon Q Integration
~800+ lines generated

70% of systems AI-assisted

50+ prompts used

12 major bugs resolved

8 new features suggested through Q brainstorming

📊 Development Stats
Time Logged: ~15 hours total

Codebase: ~1,200 lines

Modules: 8 Python files

Classes: 6

Functions: 45+

Issues Fixed: 12 major

📸 Visual Showcase
(Will be added to the GitHub repo)

Menu System UI

Maze Layout Screens

Snake & Enemy Combat

Game Over / Victory Screens

Fullscreen layout

🚀 Why This Deserves to Win
Innovation: Merges retro and modern genres (maze + shooting + survival)
Execution: Clean mechanics, menu polish, responsive controls
Learning & Growth: Explored AI-coding collaboration from prompt to polish
Replayability: Maze is always different, combat varies, multiple difficulties
AI Synergy: Amazon Q was more than a tool — it was a co-pilot.

