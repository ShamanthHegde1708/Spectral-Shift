"""Automated tests for platform collision detection, layer solidity, and rotation drop physics."""

import pytest
import pygame
from spectrum_shift.settings import (
    LAYER_RED,
    LAYER_BLUE,
    LAYER_YELLOW,
    PLAYER_WIDTH,
    PLAYER_HEIGHT,
)
from spectrum_shift.player import Player
from spectrum_shift.platform import Platform
from spectrum_shift.world_layers import WorldLayers


@pytest.fixture(autouse=True)
def init_pygame():
    """Ensure headless pygame initialization for tests."""
    pygame.init()
    yield
    pygame.quit()


def test_player_lands_on_foreground_platform():
    """Player falling onto an active foreground platform must land and become grounded."""
    wl = WorldLayers()  # Foreground is Red
    player = Player(100, 200)
    platforms = [Platform(x=50, y=250, width=150, height=30, layer=LAYER_RED)]

    # Run physics steps until player hits platform
    for _ in range(30):
        player.update(platforms, wl)
        if player.is_grounded:
            break

    assert player.is_grounded is True
    assert player.rect.bottom == 250
    assert player.vy == 0.0


def test_player_passes_through_non_foreground_platforms():
    """Player must NOT collide with middle or background platforms."""
    wl = WorldLayers()  # Foreground is Red
    player = Player(100, 200)
    # Platform is Blue (non-foreground)
    platforms = [Platform(x=50, y=250, width=150, height=30, layer=LAYER_BLUE)]

    for _ in range(30):
        player.update(platforms, wl)

    # Player should pass through y=250 without becoming grounded
    assert player.is_grounded is False
    assert player.rect.bottom > 250


def test_rotation_removes_ground_support():
    """Standing on a platform that rotates out of the foreground causes natural falling."""
    wl = WorldLayers()  # Foreground is Red
    player = Player(100, 200)
    platforms = [Platform(x=50, y=250, width=150, height=30, layer=LAYER_RED)]

    # 1. Land on Red platform
    for _ in range(30):
        player.update(platforms, wl)
        if player.is_grounded:
            break

    assert player.is_grounded is True
    assert player.rect.bottom == 250

    # 2. Rotate world to Blue foreground
    wl.rotate_forward()  # Foreground is now Blue
    assert wl.is_solid(LAYER_RED) is False

    # Check ground support immediately after rotation
    player.check_ground_after_rotation(platforms, wl)
    assert player.is_grounded is False

    # 3. Subsequent physics update must cause player to fall naturally
    old_y = player.rect.y
    player.update(platforms, wl)
    assert player.rect.y > old_y
    assert player.vy > 0.0


def test_horizontal_collision_blocks_movement():
    """Player moving horizontally into a solid platform must be blocked at its edge."""
    wl = WorldLayers()  # Foreground is Red
    # Place player at x=50, wall at x=80
    player = Player(50, 200)
    platforms = [
        Platform(x=20, y=250, width=150, height=30, layer=LAYER_RED),  # Floor
        Platform(x=80, y=180, width=30, height=70, layer=LAYER_RED),   # Solid Wall
    ]

    # Land first
    for _ in range(20):
        player.update(platforms, wl)

    # Try moving right into wall
    for _ in range(20):
        player.handle_input(move_left=False, move_right=True, jump_pressed=False, jump_held=False)
        player.update(platforms, wl)

    # Player's right edge must not penetrate the wall at x=80
    assert player.rect.right == 80
    assert player.vx == 0.0


def test_horizontal_movement_passes_through_inactive_layer_wall():
    """Player moving horizontally through an inactive layer wall must not be obstructed."""
    wl = WorldLayers()  # Foreground is Red
    player = Player(50, 200)
    platforms = [
        Platform(x=20, y=250, width=300, height=30, layer=LAYER_RED),   # Floor (Red)
        Platform(x=80, y=180, width=30, height=70, layer=LAYER_BLUE),   # Inactive Wall (Blue)
    ]

    # Land first
    for _ in range(20):
        player.update(platforms, wl)

    # Move right past x=80
    for _ in range(30):
        player.handle_input(move_left=False, move_right=True, jump_pressed=False, jump_held=False)
        player.update(platforms, wl)

    # Player should easily pass right through the blue wall
    assert player.rect.left > 80
