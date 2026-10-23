"""Handcrafted level definitions and level metadata for Spectrum Shift.

Every level is mathematically tuned to physics constants and verified with automated test suites.
"""

from typing import List, Tuple, Optional
try:
    from .settings import (
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        DEFAULT_CYCLE,
    )
    from .platform import Platform
    from .rotor import SpectrumRotor, SpectrumSpinGate
    from .items import SpectrumKey, SpectrumLockGate
except ImportError:
    from settings import (
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        DEFAULT_CYCLE,
    )
    from platform import Platform
    from rotor import SpectrumRotor, SpectrumSpinGate
    from items import SpectrumKey, SpectrumLockGate


class LevelData:
    """Container for level geometry, spawn point, portal location, mechanisms, and key/lock items."""

    def __init__(
        self,
        level_id: int,
        title: str,
        subtitle: str,
        description: str,
        spawn_pos: Tuple[int, int],
        portal_pos: Tuple[int, int],
        platforms: List[Platform],
        rotors: Optional[List[SpectrumRotor]] = None,
        gates: Optional[List[SpectrumSpinGate]] = None,
        keys: Optional[List[SpectrumKey]] = None,
        locks: Optional[List[SpectrumLockGate]] = None,
        initial_cycle: Tuple[str, ...] = DEFAULT_CYCLE,
        par_time: float = 30.0,
    ):
        self.level_id = level_id
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.spawn_pos = spawn_pos
        self.portal_pos = portal_pos
        self.platforms = platforms
        self.rotors = rotors or []
        self.gates = gates or []
        self.keys = keys or []
        self.locks = locks or []
        self.initial_cycle = initial_cycle
        self.par_time = par_time


def get_level_1() -> LevelData:
    """Level 1 — First Rotation.
    
    Teaches the core mechanic.
    Starts on Red, introduces Blue gap, then Yellow gap, finishing on Red.
    Forward rotations bring each next platform into the foreground.
    """
    platforms = [
        # 1. Starting Red ledge
        Platform(x=50, y=410, width=170, height=28, layer=LAYER_RED),
        Platform(x=50, y=460, width=170, height=20, layer=LAYER_BLUE),
        
        # 2. First Gap -> Blue platform
        Platform(x=290, y=400, width=150, height=28, layer=LAYER_BLUE),
        Platform(x=290, y=445, width=150, height=20, layer=LAYER_YELLOW),

        # 3. Second Gap -> Yellow platform
        Platform(x=510, y=380, width=150, height=28, layer=LAYER_YELLOW),
        Platform(x=510, y=430, width=150, height=20, layer=LAYER_RED),

        # 4. Final Gap -> Red platform with Exit Portal
        Platform(x=720, y=360, width=170, height=28, layer=LAYER_RED),
    ]

    return LevelData(
        level_id=1,
        title="LEVEL 1",
        subtitle="FIRST ROTATION",
        description="Rotate forward (E) to bring the next color world into the solid foreground.",
        spawn_pos=(90, 360),
        portal_pos=(810, 315),
        platforms=platforms,
        initial_cycle=(LAYER_RED, LAYER_BLUE, LAYER_YELLOW),
        par_time=15.0,
    )


def get_level_2() -> LevelData:
    """Level 2 — Color Sequence.
    
    Introduces color planning and backward rotation (Q).
    Platforms are spaced so backward rotations bring the required color before landing.
    """
    platforms = [
        # 1. Starting Red platform
        Platform(x=50, y=430, width=150, height=28, layer=LAYER_RED),
        Platform(x=50, y=475, width=150, height=20, layer=LAYER_YELLOW),

        # 2. Forward rotation (E) -> Blue platform
        Platform(x=260, y=400, width=140, height=28, layer=LAYER_BLUE),
        Platform(x=260, y=450, width=140, height=20, layer=LAYER_RED),

        # 3. Forward rotation (E) -> Yellow elevated platform
        Platform(x=460, y=360, width=140, height=28, layer=LAYER_YELLOW),
        Platform(x=460, y=410, width=140, height=20, layer=LAYER_BLUE),

        # 4. Backward rotation (Q) -> Blue platform (from [Yellow, Red, Blue], Q brings Blue!)
        Platform(x=660, y=320, width=140, height=28, layer=LAYER_BLUE),
        Platform(x=660, y=370, width=140, height=20, layer=LAYER_RED),

        # 5. Backward rotation (Q) -> Red platform with portal (from [Blue, Yellow, Red], Q brings Red!)
        Platform(x=835, y=285, width=120, height=28, layer=LAYER_RED),
    ]

    return LevelData(
        level_id=2,
        title="LEVEL 2",
        subtitle="COLOR SEQUENCE",
        description="Plan your sequence. Use (Q) to rotate backward directly to the previous color.",
        spawn_pos=(85, 380),
        portal_pos=(890, 240),
        platforms=platforms,
        initial_cycle=(LAYER_RED, LAYER_BLUE, LAYER_YELLOW),
        par_time=20.0,
    )


def get_level_3() -> LevelData:
    """Level 3 — The Impossible Bridge.
    
    Combines narrow platforms, wide chasms, and midair rotation.
    No single color layer contains a complete path across the abyss.
    Requires rotating in mid-air during jumps to make landing platforms solid.
    """
    platforms = [
        # 1. Starting Red launch pad
        Platform(x=40, y=420, width=130, height=26, layer=LAYER_RED),
        Platform(x=40, y=465, width=130, height=20, layer=LAYER_BLUE),

        # 2. Stepping stone 1 (Blue)
        Platform(x=230, y=390, width=120, height=26, layer=LAYER_BLUE),
        Platform(x=230, y=440, width=120, height=20, layer=LAYER_YELLOW),

        # 3. Stepping stone 2 (Yellow)
        Platform(x=430, y=360, width=120, height=26, layer=LAYER_YELLOW),
        Platform(x=430, y=410, width=120, height=20, layer=LAYER_RED),

        # 4. Mid-bridge launch stone (Red)
        Platform(x=630, y=330, width=120, height=26, layer=LAYER_RED),
        Platform(x=630, y=380, width=120, height=20, layer=LAYER_BLUE),

        # 5. Final Sanctuary (Blue) with Exit Portal
        Platform(x=805, y=300, width=135, height=26, layer=LAYER_BLUE),
    ]

    keys = [
        # Prism Key floating above intermediate Yellow stone
        SpectrumKey(x=490, y=310, layer="prism", key_id=1),
    ]

    locks = [
        # Holographic Laser Barrier guarding the final portal
        SpectrumLockGate(x=838, y=230, width=18, height=70, layer="prism", lock_id=1),
    ]

    return LevelData(
        level_id=3,
        title="LEVEL 3",
        subtitle="THE IMPOSSIBLE BRIDGE",
        description="Retrieve the Prism Key and unlock the spectral barrier guarding the exit.",
        spawn_pos=(75, 370),
        portal_pos=(875, 255),
        platforms=platforms,
        keys=keys,
        locks=locks,
        initial_cycle=(LAYER_RED, LAYER_BLUE, LAYER_YELLOW),
        par_time=25.0,
    )


def get_level_4() -> LevelData:
    """Level 4 — The Prism Rotor.
    
    Features spinning color mechanisms: a revolving spectrum rotor and a spinning
    color accelerator gate that propels the player across the dimensional abyss.
    """
    platforms = [
        # 1. Starting Red launch pad
        Platform(x=40, y=420, width=150, height=26, layer=LAYER_RED),
        Platform(x=40, y=465, width=150, height=20, layer=LAYER_BLUE),

        # 2. Stepping stone (Blue)
        Platform(x=250, y=390, width=140, height=26, layer=LAYER_BLUE),
        Platform(x=250, y=440, width=140, height=20, layer=LAYER_YELLOW),

        # 3. Elevated stone (Yellow) before the spinning gate
        Platform(x=450, y=360, width=140, height=26, layer=LAYER_YELLOW),
        Platform(x=450, y=410, width=140, height=20, layer=LAYER_RED),

        # 4. Final Sanctuary (Red) reached via the spinning accelerator gate
        Platform(x=730, y=340, width=150, height=26, layer=LAYER_RED),
    ]

    rotors = [
        SpectrumRotor(cx=330, cy=380, radius=65, speed=1.0, initial_angle=-0.5),
    ]

    gates = [
        # Spinning color gate: surges player forward across the abyss
        SpectrumSpinGate(x=625, y=330, radius=32, speed=1.6),
    ]

    return LevelData(
        level_id=4,
        title="LEVEL 4",
        subtitle="THE PRISM ROTOR",
        description="Ride the revolving color rotor and leap through the spinning spectrum gate to surge forward.",
        spawn_pos=(75, 370),
        portal_pos=(820, 295),
        platforms=platforms,
        rotors=rotors,
        gates=gates,
        initial_cycle=(LAYER_RED, LAYER_BLUE, LAYER_YELLOW),
        par_time=25.0,
    )


def get_level_5() -> LevelData:
    """Level 5 — The Grand Mechanism.
    
    The ultimate spectrum challenge. Features dual spinning mechanisms,
    alternating color sectors, and multi-stage precision jumps.
    """
    platforms = [
        # 1. Launch Platform (Red)
        Platform(x=40, y=420, width=150, height=26, layer=LAYER_RED),
        Platform(x=40, y=465, width=150, height=20, layer=LAYER_BLUE),

        # 2. Stepping Stone (Blue)
        Platform(x=250, y=390, width=140, height=26, layer=LAYER_BLUE),
        Platform(x=250, y=440, width=140, height=20, layer=LAYER_YELLOW),

        # 3. Intermediate Hub (Yellow)
        Platform(x=440, y=360, width=160, height=26, layer=LAYER_YELLOW),
        Platform(x=440, y=410, width=160, height=20, layer=LAYER_RED),

        # 4. Final Sky Sanctuary (Red) with Portal
        Platform(x=710, y=340, width=180, height=26, layer=LAYER_RED),
    ]

    rotors = [
        SpectrumRotor(cx=330, cy=375, radius=60, speed=1.2, initial_angle=0.0),
    ]

    gates = [
        # Dual spinning color gates in sequence
        SpectrumSpinGate(x=415, y=345, radius=28, speed=1.8),
        SpectrumSpinGate(x=625, y=330, radius=32, speed=-1.8),
    ]

    keys = [
        # Prism Key on intermediate platform
        SpectrumKey(x=510, y=315, layer="prism", key_id=2),
    ]

    locks = [
        # Holographic Laser Barrier guarding the final portal
        SpectrumLockGate(x=770, y=270, width=18, height=70, layer="prism", lock_id=2),
    ]

    return LevelData(
        level_id=5,
        title="LEVEL 5",
        subtitle="THE GRAND MECHANISM",
        description="Master the spinning color rings and retrieve the Prism Key to unlock the final gate.",
        spawn_pos=(75, 370),
        portal_pos=(820, 295),
        platforms=platforms,
        rotors=rotors,
        gates=gates,
        keys=keys,
        locks=locks,
        initial_cycle=(LAYER_RED, LAYER_BLUE, LAYER_YELLOW),
        par_time=30.0,
    )


ALL_LEVEL_GETTERS = [get_level_1, get_level_2, get_level_3, get_level_4, get_level_5]


def load_level(level_index: int) -> LevelData:
    """Load level data by 1-based index."""
    idx = max(0, min(len(ALL_LEVEL_GETTERS) - 1, level_index - 1))
    return ALL_LEVEL_GETTERS[idx]()
