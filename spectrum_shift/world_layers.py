"""World layer system for Spectrum Shift.

Manages the cyclic stack order of the three color layers (Red, Blue, Yellow).
Serves as the single source of truth for both physics collision checks and depth rendering.
"""

from typing import List, Tuple
try:
    from .settings import (
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        DEFAULT_CYCLE,
        ROTATION_ANIM_DURATION,
    )
except ImportError:
    from settings import (
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        DEFAULT_CYCLE,
        ROTATION_ANIM_DURATION,
    )


class WorldLayers:
    """Deterministic cyclic layer manager."""

    def __init__(self, initial_cycle: Tuple[str, ...] = DEFAULT_CYCLE):
        self._initial_cycle: Tuple[str, ...] = tuple(initial_cycle)
        self.stack: List[str] = list(self._initial_cycle)
        self.prev_stack: List[str] = list(self.stack)

        # Transition animation state
        self.transition_timer: float = 0.0
        self.transition_duration: float = ROTATION_ANIM_DURATION
        self.rotation_direction: int = 0  # +1 for forward, -1 for backward

        # Pulse effect triggered upon rotation
        self.pulse_timer: float = 0.0

    def reset(self, initial_cycle: Tuple[str, ...] = None) -> None:
        """Reset the world layer stack to initial configuration."""
        if initial_cycle is not None:
            self._initial_cycle = tuple(initial_cycle)
        self.stack = list(self._initial_cycle)
        self.prev_stack = list(self.stack)
        self.transition_timer = 0.0
        self.rotation_direction = 0
        self.pulse_timer = 0.0

    @property
    def foreground(self) -> str:
        """Currently active foreground layer (the only solid layer)."""
        return self.stack[0]

    @property
    def middle(self) -> str:
        """Middle depth layer (semi-transparent)."""
        return self.stack[1]

    @property
    def background(self) -> str:
        """Deepest background layer (faint)."""
        return self.stack[2]

    @property
    def next_layer(self) -> str:
        """Layer that will become foreground upon forward rotation (E)."""
        return self.stack[1]

    @property
    def prev_layer(self) -> str:
        """Layer that will become foreground upon backward rotation (Q)."""
        return self.stack[2]

    def is_solid(self, layer_name: str) -> bool:
        """Determine whether a platform of the given layer is physically solid."""
        if layer_name == "all_solid":
            return True
        return layer_name == self.foreground

    def rotate_forward(self) -> bool:
        """Rotate cyclic sequence forward: (0, 1, 2) -> (1, 2, 0).
        
        Returns True if rotation occurred.
        """
        self.prev_stack = list(self.stack)
        # Shift first element to back: [Red, Blue, Yellow] -> [Blue, Yellow, Red]
        self.stack = self.stack[1:] + self.stack[:1]
        self.transition_timer = self.transition_duration
        self.rotation_direction = 1
        self.pulse_timer = 0.25
        return True

    def rotate_backward(self) -> bool:
        """Rotate cyclic sequence backward: (0, 1, 2) -> (2, 0, 1).
        
        Returns True if rotation occurred.
        """
        self.prev_stack = list(self.stack)
        # Shift last element to front: [Red, Blue, Yellow] -> [Yellow, Red, Blue]
        self.stack = self.stack[-1:] + self.stack[:-1]
        self.transition_timer = self.transition_duration
        self.rotation_direction = -1
        self.pulse_timer = 0.25
        return True

    def update(self, dt: float) -> None:
        """Update visual transition timers."""
        if self.transition_timer > 0.0:
            self.transition_timer = max(0.0, self.transition_timer - dt)
        if self.pulse_timer > 0.0:
            self.pulse_timer = max(0.0, self.pulse_timer - dt)

    def get_visual_depth(self, layer_name: str) -> float:
        """Get the continuous depth position for rendering (0.0=foreground, 1.0=mid, 2.0=back).
        
        Interpolates smoothly during transitions to animate depth changing.
        """
        target_depth = float(self.stack.index(layer_name))
        if self.transition_timer <= 0.0:
            return target_depth

        # Calculate previous depth before rotation
        prev_depth = float(self.prev_stack.index(layer_name))

        # Progress from 0.0 (start of transition) to 1.0 (end)
        progress = 1.0 - (self.transition_timer / self.transition_duration)
        # Smooth ease-out cubic
        t = 1.0 - (1.0 - progress) ** 3

        # Cyclic wrap interpolation for depth transitions
        # When shifting forward: 0->2 wrapped, 1->0, 2->1
        # When shifting backward: 0->1, 1->2, 2->0 wrapped
        diff = target_depth - prev_depth
        if diff > 1.5:
            # e.g. from 0 to 2: smoothly wrap around or step
            prev_depth += 3.0
        elif diff < -1.5:
            # e.g. from 2 to 0: smoothly wrap
            prev_depth -= 3.0

        current_val = prev_depth + (target_depth - prev_depth) * t
        return max(0.0, min(2.0, current_val))

    def get_render_order(self) -> List[str]:
        """Return layer names ordered from back to front (for correct alpha blending)."""
        # Render back layer first, then middle, then foreground
        return [self.stack[2], self.stack[1], self.stack[0]]
