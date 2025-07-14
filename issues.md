# 🧪 SnakeMazeEscape – Bug & Challenge Report

This document outlines the technical challenges, bugs, resolutions, lessons, and risks encountered during the development of **SnakeMazeEscape** for the Amazon Q Build Games Challenge.

---

## 🐛 BUG TRACKER

### 🔴 Bug #1: Instant Game Over on Replay (Normal Mode)

* **Status:** ❌ Unresolved – Blocks gameplay
* **Priority:** HIGH
* **Affected Modes:** Normal, Advanced
* **Reproduction Rate:** 100% after first game

#### 🔬 Root Cause:

* Previous session’s `self.enemy` object not cleared.
* Game state stuck in `game_over`.
* Collision logic from base game running simultaneously with enhanced modes.


### 🔴 Bug #2: False Enemy Collision (Normal & Advanced)

* **Status:** ❌ Unresolved
* **Priority:** MEDIUM
* **Reproduction Rate:** High

#### 🧪 Debug Output:

```
DEBUG: Enemy at (650, 450), Snake at (150, 200), Distance: 500
DEBUG: COLLISION DETECTED! Distance: 500, Shield: False
```

#### 📌 Possible Causes:

* Incorrect pixel distance logic
* Collision detection across modes overlapping
* Bullets or ghost objects being misclassified

---

### ✅ Bug #3: Fullscreen Issues

* **Status:** ✅ Fixed
* **Problem:** F11 toggle minimized other windows
* **Fix:** Replaced F11 with menu/auto-toggle. Used custom scaling with centered alignment.

```python
pygame.display.set_mode((width, height), pygame.NOFRAME)  # Clean fullscreen
```

---

## 🧪 TESTING PROTOCOL

| Step | Action                    |
| ---- | ------------------------- |
| 1    | Start game in Normal Mode |
| 2    | Play until win/lose       |
| 3    | Press R to restart        |
| 4    | Expected: Clean reset     |
| 5    | Actual: Instant Game Over |

**Test System:**

* OS: Windows 11 Pro
* Python 3.13.5
* Pygame 2.6.1
* Resolution: 1920x1080

---

## ⚠️ DEVELOPMENT CHALLENGES

### ❌ Git Installation Failed

* **Cause:** `winget` timeout and blocked downloads
* **Workaround:** Uploaded repo via manual ZIP
* **Lesson Learned:** Always prep alternate deployment methods
* **Time Lost:** \~1 hour

---

### 🧠 Prompt Engineering Issues

* Complex prompts led to faulty logic (e.g., multiple enemies with different behaviors).
* Amazon Q struggled with:

  * Layered logic
  * Simultaneous mode handling

**What Worked Instead:**

*  I Broke prompts into smaller parts:

  1. "Add enemy spawn"
  2. "Add second enemy"
  3. "Add stun logic"

🧠 Example:
The reversal logic (snake flips tail and head in tight corners) was **my own solution** after observing stuck behavior.
Similarly, I relocated the bullet system from head-based to tail-based shooting after debugging Amazon Q’s implementation.

---

## 🧩 LOGIC & STRATEGY SOLUTIONS

| Problem                   | Strategy                                       |
| ------------------------- | ---------------------------------------------- |
| Snake stuck in corners    | Reversal logic: head and tail switch direction |
| Shooting from wrong point | Moved projectile source from head to tail      |
| Game resets losing state  | Added state management return guards           |
| Sound overlaps            | Added cooldowns and state-based triggers       |

---

## 📊 BUG IMPACT ASSESSMENT

| Bug                 | Severity | User Impact           | Risk    |
| ------------------- | -------- | --------------------- | ------- |
| Game Over on Replay | CRITICAL | Blocks enhanced modes | HIGH    |
| False Enemy Hits    | HIGH     | Confusing deaths      | MEDIUM  |
| Fullscreen          | LOW      | Visual UI issue       | FIXED ✅ |

---

## 🎓 KEY DEVELOPMENT INSIGHTS

### ✅ What Worked

* Modular architecture: Easy to debug and isolate features
* Checkpoint saves at key stages (e.g., Base Game, Base + Fullscreen)
* Amazon Q: Helpful for quick prototyping and menus

### ❌ What Didn’t

* Complex features in one Q prompt led to tangled logic
* Simultaneous development of base and advanced modes caused mode overlap
* Poor state separation between Easy, Normal, and Advanced

---

## 🤖 AMAZON Q: Strengths & Cautions

| Aspect            | Result                                         |
| ----------------- | ---------------------------------------------- |
| Menu UI           | Great – Clean and professional                 |
| Sound system      | Excellent with minor tuning                    |
| Game loop         | Good with tweaks                               |
| Multi-enemy logic | Risky – Needed manual fixes                    |
| Bullet systems    | Basic, required user refinement                |
| Maze AI           | Helpful, but solvability logic required tuning |

**Saved Checkpoints I Created:**

* `Half_Done`
* `Base_Game`
* `Base_Plus_Fullscreen`

These served as recovery points during bug testing and experiments.

---

## 🚀 COMPETITION STATUS

| Mode        | Readiness       | Notes                       |
| ----------- | --------------- | --------------------------- |
| Easy / Base | ✅ 100% Complete | Polished, bug-free          |
| Normal      | ⚠️ 60%          | Playable with collision bug |
| Advanced    | ⚠️ 40%          | Experimental, concept phase |

**Submission Strategy:**

* Submit Base Game as polished entry
* Document challenges transparently in Normal/Advanced modes
* Use AI collaboration (Amazon Q) as innovation point

---

## 🏁 FINAL THOUGHT

> **"Sometimes, AI just needs your brain to do the thinking first."**
> While Amazon Q was an essential partner, many breakthroughs came from brainstorming solutions (like reversal logic and tail-based shooting), debugging step-by-step, and carefully breaking prompts into modular ideas. The project is a mix of human design and AI execution — the best of both.


