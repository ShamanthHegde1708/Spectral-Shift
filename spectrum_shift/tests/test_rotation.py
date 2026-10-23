"""Automated tests for WorldLayers cyclic rotation system."""

import pytest
from spectrum_shift.settings import (
    LAYER_RED,
    LAYER_BLUE,
    LAYER_YELLOW,
    DEFAULT_CYCLE,
)
from spectrum_shift.world_layers import WorldLayers


def test_initial_world_layers():
    """Verify default initial layer stack configuration."""
    wl = WorldLayers()
    assert wl.stack == [LAYER_RED, LAYER_BLUE, LAYER_YELLOW]
    assert wl.foreground == LAYER_RED
    assert wl.middle == LAYER_BLUE
    assert wl.background == LAYER_YELLOW
    assert wl.is_solid(LAYER_RED) is True
    assert wl.is_solid(LAYER_BLUE) is False
    assert wl.is_solid(LAYER_YELLOW) is False


def test_forward_cyclic_rotation():
    """Verify forward rotation cycle: Red -> Blue -> Yellow -> Red."""
    wl = WorldLayers()

    # Step 1: Forward -> Blue foreground
    wl.rotate_forward()
    assert wl.stack == [LAYER_BLUE, LAYER_YELLOW, LAYER_RED]
    assert wl.foreground == LAYER_BLUE
    assert wl.is_solid(LAYER_BLUE) is True
    assert wl.is_solid(LAYER_RED) is False
    assert wl.is_solid(LAYER_YELLOW) is False

    # Step 2: Forward -> Yellow foreground
    wl.rotate_forward()
    assert wl.stack == [LAYER_YELLOW, LAYER_RED, LAYER_BLUE]
    assert wl.foreground == LAYER_YELLOW
    assert wl.is_solid(LAYER_YELLOW) is True
    assert wl.is_solid(LAYER_BLUE) is False
    assert wl.is_solid(LAYER_RED) is False

    # Step 3: Forward -> Returns to Red foreground
    wl.rotate_forward()
    assert wl.stack == [LAYER_RED, LAYER_BLUE, LAYER_YELLOW]
    assert wl.foreground == LAYER_RED


def test_backward_cyclic_rotation():
    """Verify backward rotation cycle: Red -> Yellow -> Blue -> Red."""
    wl = WorldLayers()

    # Step 1: Backward -> Yellow foreground
    wl.rotate_backward()
    assert wl.stack == [LAYER_YELLOW, LAYER_RED, LAYER_BLUE]
    assert wl.foreground == LAYER_YELLOW
    assert wl.is_solid(LAYER_YELLOW) is True

    # Step 2: Backward -> Blue foreground
    wl.rotate_backward()
    assert wl.stack == [LAYER_BLUE, LAYER_YELLOW, LAYER_RED]
    assert wl.foreground == LAYER_BLUE

    # Step 3: Backward -> Returns to Red foreground
    wl.rotate_backward()
    assert wl.stack == [LAYER_RED, LAYER_BLUE, LAYER_YELLOW]
    assert wl.foreground == LAYER_RED


def test_reversible_rotation():
    """Forward followed by backward must return to exact same layer order."""
    wl = WorldLayers()
    initial_stack = list(wl.stack)

    wl.rotate_forward()
    wl.rotate_backward()
    assert wl.stack == initial_stack

    wl.rotate_backward()
    wl.rotate_forward()
    assert wl.stack == initial_stack


def test_reset_layer_stack():
    """Reset must restore original stack order and clear timers."""
    wl = WorldLayers()
    wl.rotate_forward()
    wl.rotate_forward()
    assert wl.foreground != LAYER_RED

    wl.reset()
    assert wl.stack == [LAYER_RED, LAYER_BLUE, LAYER_YELLOW]
    assert wl.foreground == LAYER_RED
    assert wl.transition_timer == 0.0
