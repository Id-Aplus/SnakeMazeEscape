NAME = SnakeMazeEscape

A retro-style inspired maze survival game  built with Python + Pygame, developed using Amazon Q Developer CLI inside VS Code for the Build Games Challenge.
You must outsmart enemies, collect food for ammo, and find the maze exit before you're caught!

For full details, check out  → [See devlog.md](./devlog.md)
For issues and how I found a way around some, check out →  [See issues.md](./issues.md)
For screenshots on the process and game screen, check out  → ### 🟩 Main Menu Screen  
![Main Menu](./MEDIA/MAIN%20MENU.png)

### 🌀 Gameplay in Action  
![In-Game Screenshot](./MEDIA/snakey%20maze%202.png)

### 🔧 Backend Command Line (CLI) Interface  
![CLI Output](./MEDIA/snakey%20maze%20CLI.png)




 Overview

SnakeMazeEscape blends old-school snake gameplay with:

* Procedurally generated maze layouts which has a new pattern on every replay
* Auto-moving snake + tail-based shooting
* Enemy AI that hunts you down
* Food = ammo mechanics
* Real sound effects and full-screen visuals

> Built and debugged in collaboration with **Amazon Q Developer CLI** (VS Code integration).



 Game Modes

| Mode               | Description                                                             |
| ------------------ | ----------------------------------------------------------------------- |
|  **Easy (Base)** | Classic Snake-Maze escape. 1 enemy, ammo = food, basic AI. ✅            |
|  **Normal**      | Adds: 2 enemies, 3-min timer, stun fruit, shield, radar ping. ⚠️ Bugged |
|  **Advanced**    | Adds: 4 enemies, purple boss enemy, more complex maze. ❌ Not completed  |

🛑 *Note: Normal and Advanced modes are in-progress and have issues with replay and early game over.*



 Tech Stack (what I installed and used)

1. Python 3.13
2. Pygame 2.6.1
3. Amazon Q Developer CLI (via Visual Studio Code)
4. Windows 11 Pro

NOTE : Git was **not used** due to installation issues. Repository created via manual `.zip` upload.



## 🧱 Features (Base Version)

 ✅ Procedural maze with entrance/exit
 ✅ Auto-movement and smooth turning
 ✅ Reversal mechanic (snake can swap head/tail)
 ✅ Ammo system: food → bullets
 ✅ Shooting from tail using Space bar
 ✅ A\* pathfinding enemy AI
 ✅ Stun mechanic (enemy can be frozen)
 ✅ Sound effects: food, shoot, enemy hit, win/lose
 ✅ Working fullscreen display mode 



 🕹 Controls

| Action     | Key                                 |
| ---------- | ----------------------------------- |
| Move       | Arrow keys / WASD                   |
| Shoot Ammo | Space bar                           |
| Fullscreen | Enabled through settings screen     |
| Quit Game  | ESC                                 |



📸 Screenshots

📷 Screenshots will be added to this repository after submission.



## 🧠 Dev Resources

 **Full Devlog** → [devlog.md](#)
 **Bug & Challenge Notes** → [issues.md](#)

These include:

a. Project timeline
b. Prompt design used with Amazon Q
c. Implementation details
d. Sound integration
e. Debugging & gameplay tuning
f. Lessons learned & roadblocks



 🧪 Known Issues

- **Normal mode**: Game ends prematurely on replay
- **Enemy bug**: Sometimes triggers Game Over before enemy reaches player
- **Advanced mode**: Not yet implemented



## 🏁 Setup Instructions

```bash
# Make sure pygame is installed
python -m pip install pygame

# Run the game
python main.py
```



## 🏆 Challenge Status

✅ **Base Game**: Complete and tested
⚠️ **Normal Mode**: Implemented, but contains replay and collision bugs
⛔ **Advanced Mode**: Planned, not yet implemented


