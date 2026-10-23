"""Automated deterministic regression tests for Level 1, Level 2, and Level 3 solvability.

Each test feeds an exact winning input sequence into the real game update loop,
verifying that every jump, rotation, and landing succeeds and that the exit portal is reached.
"""

import pytest
import pygame
from spectrum_shift.settings import (
    STATE_VICTORY,
    STATE_DYING,
    STATE_PLAYING,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
)
from spectrum_shift.level_manager import LevelManager, InputAction
from spectrum_shift.levels import load_level, ALL_LEVEL_GETTERS


@pytest.fixture(autouse=True)
def init_pygame():
    """Ensure headless pygame initialization for testing."""
    pygame.init()
    yield
    pygame.quit()


def _replay_schedule(level_num: int, event_schedule: list, max_ticks: int = 250) -> bool:
    """Helper that replays deterministic inputs against actual movement and collision logic."""
    mgr = LevelManager()
    mgr.load_level(level_num)

    # Convert event list into tick lookup dictionary
    event_dict = {event["tick"]: event for event in event_schedule}

    for tick in range(max_ticks):
        ev = event_dict.get(tick, {})
        action = InputAction(
            right=True,
            left=False,
            jump_pressed=ev.get("jump_pressed", False),
            jump_held=True,
            rotate_fwd=ev.get("rot_fwd", False),
            rotate_bwd=ev.get("rot_bwd", False),
        )

        mgr.update(action)

        if mgr.state == STATE_VICTORY:
            return True
        elif mgr.state == STATE_DYING or mgr.player.is_dead:
            return False

    return False


def test_level_1_solvability():
    """Level 1 — First Rotation:
    Verifies that forward cyclic rotations bring Blue, Yellow, and Red into foreground,
    allowing the player to cross all gaps and reach the exit portal.
    """
    schedule_l1 = [
        {"tick": 20, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 26, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
        {"tick": 63, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 69, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
        {"tick": 105, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 111, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
    ]

    won = _replay_schedule(1, schedule_l1, max_ticks=180)
    assert won is True, "Level 1 winning sequence failed to reach victory portal!"


def test_level_2_solvability():
    """Level 2 — Color Sequence:
    Verifies forward rotations followed by backward rotations (Q) to bring
    Blue and Red into foreground before landing on elevated platforms.
    """
    schedule_l2 = [
        {"tick": 18, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 24, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
        {"tick": 57, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 63, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
        {"tick": 95, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 101, "jump_pressed": False, "rot_fwd": False, "rot_bwd": True},
        {"tick": 133, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 139, "jump_pressed": False, "rot_fwd": False, "rot_bwd": True},
    ]

    won = _replay_schedule(2, schedule_l2, max_ticks=200)
    assert won is True, "Level 2 winning sequence failed to reach victory portal!"


def test_level_3_solvability():
    """Level 3 — The Impossible Bridge:
    Verifies that the mid-air bridge across the abyss can be crossed
    by rotating layers in mid-air during jumps.
    """
    schedule_l3 = [
        {"tick": 14, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 20, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
        {"tick": 51, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 57, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
        {"tick": 88, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 94, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
        {"tick": 125, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 131, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
    ]

    won = _replay_schedule(3, schedule_l3, max_ticks=200)
    assert won is True, "Level 3 winning sequence failed to reach victory portal!"


def test_level_4_solvability():
    """Level 4 — The Prism Rotor:
    Verifies that the spinning color segment gate and revolving rotor
    allow the player to surge across the dimensional abyss to the portal.
    """
    schedule_l4 = [
        {"tick": 18, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 24, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
        {"tick": 57, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 63, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
        {"tick": 95, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 101, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
    ]

    won = _replay_schedule(4, schedule_l4, max_ticks=200)
    assert won is True, "Level 4 winning sequence failed to reach victory portal!"


def test_level_5_solvability():
    """Level 5 — The Grand Mechanism:
    Verifies that the double spinning spectrum gates and complex rotations
    can be conquered to reach the final sanctuary portal.
    """
    schedule_l5 = [
        {"tick": 18, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 24, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
        {"tick": 57, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 63, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
        {"tick": 118, "jump_pressed": True, "rot_fwd": False, "rot_bwd": False},
        {"tick": 124, "jump_pressed": False, "rot_fwd": True, "rot_bwd": False},
    ]

    won = _replay_schedule(5, schedule_l5, max_ticks=200)
    assert won is True, "Level 5 winning sequence failed to reach victory portal!"


def test_all_level_geometries_valid():
    """Ensure all handcrafted levels have valid spawns, portals, and platforms."""
    for idx in range(1, len(ALL_LEVEL_GETTERS) + 1):
        lvl = load_level(idx)
        assert lvl.level_id == idx
        assert len(lvl.platforms) >= 3
        # Spawn within screen
        assert 0 <= lvl.spawn_pos[0] < SCREEN_WIDTH
        assert 0 <= lvl.spawn_pos[1] < SCREEN_HEIGHT
        # Portal within screen
        assert 0 <= lvl.portal_pos[0] < SCREEN_WIDTH
        assert 0 <= lvl.portal_pos[1] < SCREEN_HEIGHT
