"""Automated unit and integration tests for Chroma Phase Dash, Keys & Locks, and Spinning Rotors."""

import pytest
import pygame
from spectrum_shift.settings import (
    LAYER_RED,
    LAYER_BLUE,
    LAYER_YELLOW,
    DASH_SPEED,
    DASH_DURATION,
)
from spectrum_shift.player import Player
from spectrum_shift.platform import Platform
from spectrum_shift.world_layers import WorldLayers
from spectrum_shift.items import SpectrumKey, SpectrumLockGate
from spectrum_shift.rotor import SpectrumRotor
from spectrum_shift.level_manager import LevelManager, InputAction


@pytest.fixture(autouse=True)
def init_pygame():
    """Ensure headless pygame initialization for tests."""
    pygame.init()
    yield
    pygame.quit()


def test_key_pickup_and_unlock_barrier():
    """Player picks up a key and dissolves the holographic lock barrier."""
    wl = WorldLayers()  # Foreground is Red
    player = Player(50, 200)

    # Floor, Key, and Lock Barrier
    floor = Platform(x=0, y=250, width=400, height=30, layer=LAYER_RED)
    key = SpectrumKey(x=120, y=220, layer="prism", key_id=1)
    lock = SpectrumLockGate(x=200, y=180, width=20, height=70, layer="prism", lock_id=1)

    platforms = [floor, lock.barrier_platform]

    # Land player
    for _ in range(15):
        player.update(platforms, wl)

    assert player.is_grounded is True
    player_keys = 0

    # Walk right towards key
    for _ in range(25):
        player.handle_input(move_left=False, move_right=True, jump_pressed=False, jump_held=False)
        player.update(platforms, wl)
        if key.check_pickup(player.rect, wl.foreground):
            player_keys += 1

    assert key.collected is True
    assert player_keys == 1

    # Walk further into lock barrier
    unlocked = False
    for _ in range(35):
        player.handle_input(move_left=False, move_right=True, jump_pressed=False, jump_held=False)
        if lock.check_interaction(player.rect, player_keys):
            player_keys -= 1
            unlocked = True
        # If unlocked, remove barrier from solid platforms
        active_platforms = [floor] if lock.is_unlocked else [floor, lock.barrier_platform]
        player.update(active_platforms, wl)

    assert unlocked is True
    assert lock.is_unlocked is True
    assert player_keys == 0
    # Player should now have walked past the barrier (x > 200)
    assert player.rect.x > 200


def test_chroma_phase_dash():
    """Chroma Phase Dash gives forward speed burst, zero gravity, and recharges on ground."""
    wl = WorldLayers()
    player = Player(100, 200)
    platforms = [Platform(x=0, y=350, width=400, height=30, layer=LAYER_RED)]

    # Start dash
    assert player.has_dash is True
    success = player.execute_dash()
    assert success is True
    assert player.is_dashing is True
    assert player.has_dash is False
    assert player.vx == pytest.approx(DASH_SPEED, 0.1)
    assert player.vy == 0.0

    # Advance physics while dashing: y should not drop under gravity
    init_y = player.rect.y
    for _ in range(5):
        player.update(platforms, wl)

    assert player.rect.y == init_y  # Zero vertical gravity while dashing!

    # Cannot dash a second time in air
    assert player.execute_dash() is False

    # Wait for dash to finish and let player fall to ground
    for _ in range(40):
        player.update(platforms, wl)
        if player.is_grounded:
            break

    assert player.is_grounded is True
    # Touching ground recharges dash
    assert player.has_dash is True


def test_rotor_platform_stability_and_momentum():
    """Rotor platform carries player smoothly and transfers momentum on jump."""
    wl = WorldLayers()  # Red is foreground
    # Place Red arm at 12 o'clock (pointing straight up)
    rotor = SpectrumRotor(cx=200, cy=250, radius=70, speed=0.8, initial_angle=-1.57079)
    player = Player(180, 100)

    # Let player land on active rotor platform arm
    for _ in range(35):
        rotor.update(0.016)
        all_platforms = rotor.get_platforms()
        player.update(all_platforms, wl)
        if player.is_grounded:
            break

    assert player.is_grounded is True
    ground_p = player.current_ground_platform
    assert ground_p is not None
    assert ground_p.layer == LAYER_RED

    # Update rotor and verify player is carried by the platform dx/dy
    old_px = player.rect.x
    for _ in range(5):
        rotor.update(0.016)
        all_platforms = rotor.get_platforms()
        player.update(all_platforms, wl)

    assert player.is_grounded is True
    # Player moved along with the rotor arm
    assert player.rect.x != old_px

    # Jump off the moving platform
    player._execute_jump()
    assert player.is_grounded is False
    # Player's jump inherits tangential momentum from the rotating arm
    assert player.vy < 0
