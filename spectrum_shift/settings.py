"""Settings, constants, physics parameters, and color palettes for Spectrum Shift."""

from typing import Tuple, Dict

# Display configuration
SCREEN_WIDTH: int = 960
SCREEN_HEIGHT: int = 540
FPS: int = 60
TITLE: str = "SPECTRUM SHIFT"

# Color Layer Identifiers
LAYER_RED: str = "red"
LAYER_BLUE: str = "blue"
LAYER_YELLOW: str = "yellow"

LAYER_NAMES = {
    LAYER_RED: "CRIMSON RED",
    LAYER_BLUE: "ELECTRIC BLUE",
    LAYER_YELLOW: "GOLDEN YELLOW",
}

LAYER_SYMBOLS = {
    LAYER_RED: "▲",      # Triangle for Red
    LAYER_BLUE: "■",     # Square for Blue
    LAYER_YELLOW: "●",    # Circle for Yellow
}

# Color Palettes (RGB)
COLOR_BG: Tuple[int, int, int] = (11, 14, 23)           # Deep charcoal / dark navy
COLOR_BG_ALT: Tuple[int, int, int] = (18, 23, 36)       # Lighter navy for cards
COLOR_GRID: Tuple[int, int, int] = (25, 33, 49)         # Subtle grid lines
COLOR_BORDER: Tuple[int, int, int] = (45, 55, 75)       # Card borders

# Layer Base Colors
COLOR_RED: Tuple[int, int, int] = (255, 45, 85)         # Neon crimson red
COLOR_BLUE: Tuple[int, int, int] = (0, 210, 255)        # Electric cyan blue
COLOR_YELLOW: Tuple[int, int, int] = (255, 210, 30)     # Golden yellow

# Layer Color Definitions: Primary, Dark/Fill, Glow, Accent
LAYER_COLORS: Dict[str, Dict[str, Tuple[int, int, int]]] = {
    LAYER_RED: {
        "bright": (255, 60, 100),
        "core": (255, 45, 85),
        "dark": (140, 18, 45),
        "glow": (255, 80, 120),
        "pattern": (255, 140, 165),
    },
    LAYER_BLUE: {
        "bright": (30, 230, 255),
        "core": (0, 210, 255),
        "dark": (10, 100, 150),
        "glow": (70, 225, 255),
        "pattern": (150, 240, 255),
    },
    LAYER_YELLOW: {
        "bright": (255, 235, 70),
        "core": (255, 210, 30),
        "dark": (150, 120, 10),
        "glow": (255, 225, 80),
        "pattern": (255, 245, 160),
    },
}

# Depth Layer Opacity (Alpha values 0-255)
DEPTH_ALPHA = {
    0: 255,  # Foreground: Solid, fully opaque, glowing
    1: 125,  # Middle layer: Semi-transparent, visible outline
    2: 55,   # Background layer: Faint, deep transparency
}

# Depth Layer Visual Offset (Y displacement to give 3D depth perception)
DEPTH_Y_OFFSET = {
    0: 0,
    1: 4,
    2: 8,
}

# Depth Layer Scale Factor
DEPTH_SCALE = {
    0: 1.0,
    1: 0.96,
    2: 0.92,
}

# Player Appearance
COLOR_PLAYER: Tuple[int, int, int] = (255, 255, 255)
COLOR_PLAYER_CORE: Tuple[int, int, int] = (245, 248, 255)
COLOR_PLAYER_EYE: Tuple[int, int, int] = (0, 210, 255)
COLOR_PLAYER_GLOW: Tuple[int, int, int] = (190, 230, 255)
PLAYER_WIDTH: int = 24
PLAYER_HEIGHT: int = 34

# Exit Portal
COLOR_EXIT_CORE: Tuple[int, int, int] = (100, 255, 218)
COLOR_EXIT_RING: Tuple[int, int, int] = (180, 130, 255)
COLOR_EXIT_GLOW: Tuple[int, int, int] = (80, 240, 200)
PORTAL_RADIUS: int = 22

# UI & Text Colors (High Contrast)
COLOR_TEXT_WHITE: Tuple[int, int, int] = (255, 255, 255)
COLOR_TEXT_MUTED: Tuple[int, int, int] = (210, 225, 245)      # Crisp bright silver-cyan
COLOR_TEXT_DIM: Tuple[int, int, int] = (165, 182, 208)        # Clean readable subtitle text
COLOR_TEXT_ACCENT: Tuple[int, int, int] = (0, 235, 255)       # High-vis electric cyan
COLOR_BUTTON_BG: Tuple[int, int, int] = (28, 36, 54)
COLOR_BUTTON_HOVER: Tuple[int, int, int] = (45, 60, 90)
COLOR_BUTTON_BORDER: Tuple[int, int, int] = (85, 110, 155)

# Physics Parameters
GRAVITY: float = 0.58
MAX_FALL_SPEED: float = 12.0
ACCELERATION: float = 0.85
MAX_SPEED: float = 5.2
FRICTION_GROUND: float = 0.78
FRICTION_AIR: float = 0.92
JUMP_VELOCITY: float = -11.8
JUMP_CUT_MULTIPLIER: float = 0.5
COYOTE_FRAMES: int = 6
JUMP_BUFFER_FRAMES: int = 6
DEATH_Y: int = 570

# Unique Feature: Chroma Phase Dash
DASH_SPEED: float = 9.6
DASH_DURATION: float = 0.16
DASH_COOLDOWN: float = 0.35

# Key & Lock System Parameters
KEY_SIZE: int = 22
LOCK_WIDTH: int = 18
LOCK_HEIGHT: int = 70

# World Rotation System
DEFAULT_CYCLE = (LAYER_RED, LAYER_BLUE, LAYER_YELLOW)
ROTATION_ANIM_DURATION: float = 0.22  # Seconds for depth transition visual animation

# Game States
STATE_MENU: str = "menu"
STATE_HOW_TO_PLAY: str = "how_to_play"
STATE_LEVEL_SELECT: str = "level_select"
STATE_PLAYING: str = "playing"
STATE_PAUSED: str = "paused"
STATE_DYING: str = "dying"
STATE_VICTORY: str = "victory"
STATE_CAMPAIGN_WIN: str = "campaign_win"
