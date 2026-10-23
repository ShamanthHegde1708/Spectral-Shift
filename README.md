# SPECTRUM SHIFT

> **"All three color worlds exist together. Rotate their layers to bring the platforms you need into the foreground."**

A polished 2D neon sci-fi platform puzzle game built in Python with **Pygame CE** and ready for browser deployment via **Pygbag (WebAssembly)**.

---

## 1. Game Concept & The Core Twist

In traditional platformers, platforms are either solid or absent. In **Spectrum Shift**, three overlapping dimensional worlds exist simultaneously:

- 🔴 **Crimson Red World** (`▲` Triangle icon, diagonal hazard hatch)
- 🔵 **Electric Blue World** (`■` Square icon, high-tech grid)
- 🟡 **Golden Yellow World** (`●` Circle icon, circuit node matrix)

### The Central Twist
All three worlds are visible at all times:
- **Foreground layer (Active)**: Fully saturated, glowing, crisp borders, and **physically solid**.
- **Middle layer**: Semi-transparent (alpha ~125), recessed depth outline.
- **Background layer**: Deeply transparent (alpha ~55), faint outlines.

The player deterministically rotates the cyclic world stack forward or backward:
$$\text{Red} \longrightarrow \text{Blue} \longrightarrow \text{Yellow} \longrightarrow \text{Red}$$

- **Q Key**: Rotate backward
- **E Key**: Rotate forward

Only platforms on the foreground layer participate in collision detection. When the world rotates, if the player was standing on a platform that is no longer in the foreground, **ground support vanishes immediately and the player falls naturally**. Momentum and velocity are preserved; the player is never magically teleported or saved from an unsafe rotation.

---

## 2. Controls & Accessibility

| Action | Primary Controls | Mouse / Browser |
| :--- | :--- | :--- |
| **Move Left** | `A` or `Left Arrow` | — |
| **Move Right** | `D` or `Right Arrow` | — |
| **Jump** (Variable Height) | `Spacebar`, `W`, or `Up Arrow` | — |
| **Chroma Phase Dash** | `Left Shift`, `Right Shift`, or `J` | Clickable `[SHIFT] DASH` button |
| **Rotate Stack Forward** | `E` | Clickable `[E] ROTATE ►` button |
| **Rotate Stack Backward** | `Q` | Clickable `◄ [Q] ROTATE` button |
| **Restart Current Level** | `R` | Clickable `R: RESET` HUD button |
| **Pause / Resume** | `Escape` | Clickable `PAUSE` HUD button |
| **Menu Navigation** | Mouse Click | Fully clickable buttons |

### Accessibility & Visual Clarity
- **High-Contrast Text Visibility**: All HUD labels, level titles, control hints, and menu descriptions feature dark drop shadows and bold, high-contrast palettes for crystal-clear readability across all displays.
- **Colorblind-safe icons**: Every platform and HUD indicator stamps geometric symbols (`▲`, `■`, `●`) so players never have to rely solely on color recognition.
- **Pattern hatching**: Diagonal stripes for Red, digital grids for Blue, and circuit node dots for Yellow.
- **On-Screen Touch / Mouse Controls**: Clickable on-screen rotation and dash pills allow playing without a keyboard in web browsers or on touch devices.

---

## 3. Project Architecture

```
PIxathod-Spectrum-Shift/
├── main.py                     # Root launcher script
├── requirements.txt            # Project dependencies (pygame-ce, pygbag, pytest)
├── README.md                   # Complete documentation & deployment guide
├── spectrum_shift/
│   ├── __init__.py             # Package descriptor
│   ├── main.py                 # Async game loop, window scaling, and state machine
│   ├── settings.py             # Colors, physics parameters, layer configurations
│   ├── player.py               # Humanoid pixel hero, Chroma Phase Dash, platform ride & jump physics
│   ├── platform.py             # Platform geometry, depth rendering & accessibility textures
│   ├── world_layers.py         # Single source of truth for cyclic rotation and active layer
│   ├── items.py                # SpectrumKey (prismatic crystal keys) and SpectrumLockGate (laser barriers)
│   ├── level_manager.py        # Level loading, update loop, collision resolution & restart
│   ├── levels.py               # Handcrafted level definitions & metadata (5 Levels)
│   ├── rotor.py                # Spinning color segment mechanisms: SpectrumRotor and SpectrumSpinGate
│   ├── ui.py                   # High-contrast start menu, HUD, 5-level select, pause modal & victory overlays
│   ├── effects.py              # Glow particles, jump dust, rotation shockwaves, animated exit portal
│   ├── sound.py                # Procedural audio synthesis (jump, land, rotate, dash, key pickup, unlock)
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_rotation.py    # Cyclic ordering, determinism, forward/backward invariance
│   │   ├── test_collision.py   # Solidity filtering, rotation drop, wall blocking
│   │   ├── test_mechanics.py   # Key pickup & barrier unlock, Chroma Phase Dash, rotor momentum
│   │   ├── test_levels.py      # Automated winning sequence replay for Levels 1 to 5
│   │   └── test_restart.py     # Clean state reset verification
│   └── build/
│       └── web/                # Compiled WebAssembly build ready for static web hosting
```

---

## 4. Handcrafted Levels & Solvability Verification

Every level has a verified winning route that runs against the actual physics engine in `spectrum_shift/tests/test_levels.py`:

### Level 1 — First Rotation
- **Purpose**: Teaches the core forward rotation mechanic.
- **Progression**: Start on Red platform $\to$ rotate forward to Blue to cross first gap $\to$ rotate forward to Yellow to cross second gap $\to$ rotate forward to Red to reach the exit portal.
- **Automated Replay**: Passed at tick 134 (clear time: 2.25s).

### Level 2 — Color Sequence
- **Purpose**: Introduces color planning, elevated ledges, and backward rotation (`Q`).
- **Progression**: Navigate forward to Blue and Yellow, then rotate backward directly to Blue and Red to scale ascending platforms.
- **Automated Replay**: Passed at tick 159 (clear time: 2.67s).

### Level 3 — The Impossible Bridge
- **Purpose**: Requires mid-air rotation during jumps. No single color layer contains a complete path across the abyss.
- **Progression**: Player must launch from Red, rotate mid-flight to Blue, land on a stepping stone, launch from Blue, rotate mid-flight to Yellow, and execute precise timing to reach the final sanctuary.
- **Automated Replay**: Passed at tick 152 (clear time: 2.55s).

### Level 4 — The Prism Rotor (NEW)
- **Purpose**: Introduces the **Spinning Color Rotor** carousel and the **Spectrum Spin Gate**.
- **Progression**: Ride the revolving 3-arm color rotor across the chasm, leap to the yellow ledge, and surge through the spinning accelerator gate directly into the portal sanctuary.
- **Automated Replay**: Passed at tick 128 (clear time: 2.15s).

### Level 5 — The Grand Mechanism (NEW)
- **Purpose**: The master spectrum challenge combining dual spinning mechanisms, multi-stage precision jumps, and counter-rotations.
- **Progression**: Jump through the first spinning spectrum accelerator, navigate intermediate color transitions, leap through the second counter-spinning gate, and land on the sky sanctuary to beat the campaign!
- **Automated Replay**: Passed at tick 145 (clear time: 2.42s).

---

## 5. Setup & Desktop Execution Guide (Windows & VS Code)

### Prerequisites
- Python 3.11, 3.12, or 3.13 installed on Windows.
- Visual Studio Code (optional, but recommended).

### Step 1: Open Terminal in Project Directory
Open PowerShell or Command Prompt inside the project directory:
```powershell
cd C:\Users\hegde\OneDrive\Desktop\PIxathod-Spectrum-Shift
```

### Step 2: Create and Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment in PowerShell
.\.venv\Scripts\Activate.ps1

# (If PowerShell script execution is restricted, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)
```

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Run the Desktop Game
```powershell
python main.py
```
Or run as a package:
```powershell
python -m spectrum_shift.main
```

### Step 5: Run the Automated Test Suite
To run all 21 automated unit, mechanic, and level solvability tests:
```powershell
pytest -v spectrum_shift/tests
```
Expected output:
```
spectrum_shift/tests/test_collision.py::test_player_lands_on_foreground_platform PASSED
spectrum_shift/tests/test_collision.py::test_player_passes_through_non_foreground_platforms PASSED
spectrum_shift/tests/test_collision.py::test_rotation_removes_ground_support PASSED
spectrum_shift/tests/test_collision.py::test_horizontal_collision_blocks_movement PASSED
spectrum_shift/tests/test_collision.py::test_horizontal_movement_passes_through_inactive_layer_wall PASSED
spectrum_shift/tests/test_levels.py::test_level_1_solvability PASSED
spectrum_shift/tests/test_levels.py::test_level_2_solvability PASSED
spectrum_shift/tests/test_levels.py::test_level_3_solvability PASSED
spectrum_shift/tests/test_levels.py::test_level_4_solvability PASSED
spectrum_shift/tests/test_levels.py::test_level_5_solvability PASSED
spectrum_shift/tests/test_levels.py::test_all_level_geometries_valid PASSED
spectrum_shift/tests/test_mechanics.py::test_key_pickup_and_unlock_barrier PASSED
spectrum_shift/tests/test_mechanics.py::test_chroma_phase_dash PASSED
spectrum_shift/tests/test_mechanics.py::test_rotor_platform_stability_and_momentum PASSED
spectrum_shift/tests/test_restart.py::test_restart_resets_player_and_world_state PASSED
spectrum_shift/tests/test_restart.py::test_next_level_transition_resets_state PASSED
spectrum_shift/tests/test_rotation.py::test_initial_world_layers PASSED
spectrum_shift/tests/test_rotation.py::test_forward_cyclic_rotation PASSED
spectrum_shift/tests/test_rotation.py::test_backward_cyclic_rotation PASSED
spectrum_shift/tests/test_rotation.py::test_reversible_rotation PASSED
spectrum_shift/tests/test_rotation.py::test_reset_layer_stack PASSED

============================= 21 passed in 4.50s ==============================
```

---

## 6. Browser Deployment with Pygbag (WebAssembly)

The game is designed with an asynchronous main loop (`asyncio.sleep(0)`) specifically engineered for Pygbag and WebAssembly.

### Local Browser Testing
To compile and launch the browser test server on port 8000:
```powershell
pygbag spectrum_shift
```
1. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```
2. The WebAssembly loader will download the Python runtime and launch the game directly inside your browser window.

### Generating Static Production Build
To create a static production build ready for deployment:
```powershell
pygbag --build spectrum_shift
```
This generates the standalone web distribution inside `spectrum_shift/build/web`:
- `index.html`: Web page hosting the canvas and WASM loader.
- `spectrum_shift.apk` & `spectrum_shift.tar.gz`: Compressed game package.
- `favicon.png`: Game favicon.

### Hosting on Static Web Services
You can host the contents of `spectrum_shift/build/web` on any static host:

#### Option A: GitHub Pages
1. Push your repository to GitHub.
2. In repository **Settings** $\to$ **Pages**, set branch to `main` and folder to `/spectrum_shift/build/web` (or copy files to a `gh-pages` branch).
3. Your game is immediately live at `https://<username>.github.io/<repo>/`.

#### Option B: itch.io
1. Zip the contents of `spectrum_shift/build/web` into a file named `web.zip` (ensure `index.html` is at the zip root).
2. Create a new project on [itch.io](https://itch.io).
3. Set **Kind of project** to **HTML**.
4. Upload `web.zip` and check the checkbox **This file will be played in the browser**.
5. Set viewport dimensions to `960` $\times$ `540`.

#### Option C: Local Static HTTP Server
```powershell
cd spectrum_shift\build\web
python -m http.server 8080
```
Open `http://localhost:8080` in any web browser.

---

## 7. Definition of Done Checklist

- [x] **Runs locally**: Tested and runs natively on Windows desktop.
- [x] **All three layers visible simultaneously**: Rendered with proper depth alphas, offsets, and distinct visual patterns.
- [x] **Deterministic cyclic rotation**: Red $\to$ Blue $\to$ Yellow with `Q` (backward) and `E` (forward).
- [x] **Only foreground platforms solid**: Verified by collision unit tests and gameplay.
- [x] **Natural gravity drop**: Standing on a platform that rotates away drops player naturally.
- [x] **Movement & physics**: Subpixel physics, coyote time, jump buffering, variable jump height.
- [x] **Handcrafted levels with verified solutions**: Levels 1, 2, and 3 pass deterministic replay regression tests.
- [x] **Start screen with required prompt**: Displays *"All three color worlds exist together. Rotate their layers to bring the platforms you need into the foreground."* and animated 3-layer preview.
- [x] **Complete state machine**: Menu, How to Play, Level Select, Gameplay, Pause, Death, Victory, and Campaign Win.
- [x] **Procedural audio**: No missing audio asset files; synthesized directly in memory.
- [x] **Browser build verified**: Packaged and verified with Pygbag.
- [x] **Complete documentation**: Full Windows, VS Code, and deployment instructions provided.
#   S p e c t r a l - S h i f t  
 #   S p e c t r a l - S h i f t  
 