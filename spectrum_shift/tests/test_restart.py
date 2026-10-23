"""Automated tests for level restart and transition state reset."""

import pytest
import pygame
from spectrum_shift.settings import (
    STATE_PLAYING,
    STATE_VICTORY,
    LAYER_RED,
    LAYER_BLUE,
    LAYER_YELLOW,
)
from spectrum_shift.level_manager import LevelManager, InputAction


@pytest.fixture(autouse=True)
def init_pygame():
    pygame.init()
    yield
    pygame.quit()


def test_restart_resets_player_and_world_state():
    """Restarting must cleanly reset player position, velocity, timers, and layer stack."""
    mgr = LevelManager()
    mgr.load_level(1)

    initial_spawn = (mgr.level_data.spawn_pos[0], mgr.level_data.spawn_pos[1])
    initial_stack = list(mgr.world_layers.stack)

    # Simulate player moving and rotating world (e.g. 5 rotations so stack is shifted: 5 % 3 = 2)
    for _ in range(5):
        action = InputAction(right=True, jump_pressed=True, jump_held=True, rotate_fwd=True)
        mgr.update(action)

    assert mgr.player.rect.x != initial_spawn[0] or mgr.player.rect.y != initial_spawn[1]
    assert mgr.world_layers.stack != initial_stack
    assert mgr.level_time > 0.0
    assert mgr.rotations_used > 0

    # Execute restart
    mgr.restart_level()

    # Verify everything returned to initial baseline
    assert mgr.player.rect.x == initial_spawn[0]
    assert mgr.player.rect.y == initial_spawn[1]
    assert mgr.player.vx == 0.0
    assert mgr.player.vy == 0.0
    assert mgr.player.is_dead is False
    assert mgr.world_layers.stack == initial_stack
    assert mgr.level_time == 0.0
    assert mgr.rotations_used == 0
    assert mgr.state == STATE_PLAYING


def test_next_level_transition_resets_state():
    """Advancing to next level loads new geometry and cleans up all transient state."""
    mgr = LevelManager()
    mgr.load_level(1)

    # Move player and accumulate state
    for _ in range(10):
        mgr.update(InputAction(right=True, rotate_fwd=True))

    mgr.next_level()

    assert mgr.current_level_idx == 2
    assert mgr.level_data.level_id == 2
    assert mgr.player.rect.x == mgr.level_data.spawn_pos[0]
    assert mgr.player.rect.y == mgr.level_data.spawn_pos[1]
    assert mgr.player.vx == 0.0
    assert mgr.player.vy == 0.0
    assert mgr.level_time == 0.0
    assert mgr.state == STATE_PLAYING
