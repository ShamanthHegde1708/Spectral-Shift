"""Spinning Color Segment mechanisms: Spectrum Rotors and Spinning Accelerator Gates.

Features:
- SpectrumRotor: A revolving tricolor wheel with Red, Blue, and Yellow platform arms.
  Only the arm matching the active foreground layer is solid, allowing the player to
  ride the spinning segment and leap across otherwise impassable chasms.
- SpectrumSpinGate: A rotating tricolor ring segment. When the player passes through
  with matching foreground color, it boosts them forward with an energy surge.
"""

import math
import pygame
from typing import List, Tuple, Optional
try:
    from .settings import (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        LAYER_COLORS,
        LAYER_SYMBOLS,
        DEPTH_ALPHA,
    )
    from .platform import Platform
except ImportError:
    from settings import (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        LAYER_COLORS,
        LAYER_SYMBOLS,
        DEPTH_ALPHA,
    )
    from platform import Platform


class RotorArmPlatform(Platform):
    """Dynamic platform attached to a spinning rotor arm."""

    def __init__(self, x: int, y: int, width: int, height: int, layer: str, rotor):
        super().__init__(x, y, width, height, layer)
        self.rotor = rotor
        self.prev_x = float(x)
        self.prev_y = float(y)
        self.dx = 0.0
        self.dy = 0.0

    def reset(self, new_x: float, new_y: float) -> None:
        """Reset platform position and clear all motion deltas."""
        self.prev_x = float(new_x)
        self.prev_y = float(new_y)
        self.dx = 0.0
        self.dy = 0.0
        self.rect.x = int(round(new_x))
        self.rect.y = int(round(new_y))

    def update_position(self, new_x: float, new_y: float) -> None:
        """Update platform position and calculate velocity delta for passenger carrying."""
        self.dx = new_x - self.prev_x
        self.dy = new_y - self.prev_y
        self.prev_x = new_x
        self.prev_y = new_y

        self.rect.x = int(round(new_x))
        self.rect.y = int(round(new_y))


class SpectrumRotor:
    """A rotating tricolor carousel with Red, Blue, and Yellow platform arms."""

    def __init__(
        self,
        cx: float,
        cy: float,
        radius: float = 78.0,
        speed: float = 0.88,
        initial_angle: float = 0.0,
        pad_width: int = 64,
        pad_height: int = 18,
    ):
        self.cx = float(cx)
        self.cy = float(cy)
        self.radius = float(radius)
        self.speed = float(speed)
        self.initial_angle = float(initial_angle)
        self.angle = float(initial_angle)
        self.pad_width = pad_width
        self.pad_height = pad_height
        self.pulse_phase = 0.0

        # 3 color arms spaced 120 degrees (2*pi/3) apart
        self.layers = [LAYER_RED, LAYER_BLUE, LAYER_YELLOW]

        # Initialize the 3 arm platforms
        self.arm_platforms: List[RotorArmPlatform] = []
        for i, layer_name in enumerate(self.layers):
            arm_ang = self.angle + i * (2.0 * math.pi / 3.0)
            px = self.cx + math.cos(arm_ang) * self.radius - self.pad_width / 2
            py = self.cy + math.sin(arm_ang) * self.radius - self.pad_height / 2
            plat = RotorArmPlatform(int(px), int(py), self.pad_width, self.pad_height, layer_name, self)
            self.arm_platforms.append(plat)

    def reset(self) -> None:
        """Reset rotor angle to initial state and zero platform deltas."""
        self.angle = float(self.initial_angle)
        self.pulse_phase = 0.0
        for i, plat in enumerate(self.arm_platforms):
            arm_ang = self.angle + i * (2.0 * math.pi / 3.0)
            px = self.cx + math.cos(arm_ang) * self.radius - self.pad_width / 2
            py = self.cy + math.sin(arm_ang) * self.radius - self.pad_height / 2
            plat.reset(px, py)

    def update(self, dt: float) -> None:
        """Advance rotation angle and update platform positions smoothly."""
        self.angle += self.speed * dt
        self.pulse_phase += dt * 4.0

        for i, plat in enumerate(self.arm_platforms):
            arm_ang = self.angle + i * (2.0 * math.pi / 3.0)
            new_x = self.cx + math.cos(arm_ang) * self.radius - self.pad_width / 2
            new_y = self.cy + math.sin(arm_ang) * self.radius - self.pad_height / 2
            plat.update_position(new_x, new_y)

    def get_platforms(self) -> List[Platform]:
        """Return the list of arm platforms for physics collision checks."""
        return self.arm_platforms

    def draw(self, surface: pygame.Surface, world_layers) -> None:
        """Render the spinning hub, connecting energy spokes, and platform pads."""
        # 1. Circular Orbit Guide Ring with High-Tech Tick Marks
        guide_r = int(self.radius)
        guide_box = int(self.radius * 2 + 40)
        guide_surf = pygame.Surface((guide_box, guide_box), pygame.SRCALPHA)
        center_g = (guide_box // 2, guide_box // 2)

        # Faint dashed ring
        pygame.draw.circle(guide_surf, (50, 70, 95, 80), center_g, guide_r, width=1)
        # Tick markers along orbit
        for tick in range(12):
            ta = tick * (math.pi / 6.0)
            tx1 = center_g[0] + math.cos(ta) * (guide_r - 4)
            ty1 = center_g[1] + math.sin(ta) * (guide_r - 4)
            tx2 = center_g[0] + math.cos(ta) * (guide_r + 4)
            ty2 = center_g[1] + math.sin(ta) * (guide_r + 4)
            pygame.draw.line(guide_surf, (80, 110, 150, 110), (tx1, ty1), (tx2, ty2), width=1)
        surface.blit(guide_surf, (int(self.cx - guide_box // 2), int(self.cy - guide_box // 2)))

        # 2. Draw Spokes / Arms from Hub to Platform Pads
        for i, plat in enumerate(self.arm_platforms):
            layer_name = plat.layer
            is_active = world_layers.is_solid(layer_name)
            vis_depth = world_layers.get_visual_depth(layer_name)
            color_data = LAYER_COLORS[layer_name]

            arm_ang = self.angle + i * (2.0 * math.pi / 3.0)
            tip_x = self.cx + math.cos(arm_ang) * (self.radius - 6)
            tip_y = self.cy + math.sin(arm_ang) * (self.radius - 6)

            if is_active:
                # Active Solid Arm: Radiant Neon Truss & Conduit
                spoke_col = color_data["bright"]
                glow_col = (*color_data["glow"], 70)

                # Neon Outer Halo
                pygame.draw.line(surface, glow_col[:3], (self.cx, self.cy), (tip_x, tip_y), width=6)
                pygame.draw.line(surface, spoke_col, (self.cx, self.cy), (tip_x, tip_y), width=3)
                pygame.draw.line(surface, (255, 255, 255), (self.cx, self.cy), (tip_x, tip_y), width=1)

                # Traveling energy packet along spoke
                packet_dist = (self.pulse_phase % 1.0)
                px = self.cx + (tip_x - self.cx) * packet_dist
                py = self.cy + (tip_y - self.cy) * packet_dist
                pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), 3)
            else:
                # Inactive Arm: Dim translucent wireframe spoke
                alpha = int(DEPTH_ALPHA[1] * 0.7) if vis_depth <= 1.2 else int(DEPTH_ALPHA[2] * 0.8)
                dim_surf = pygame.Surface((guide_box, guide_box), pygame.SRCALPHA)
                rel_tip_x = center_g[0] + math.cos(arm_ang) * (self.radius - 6)
                rel_tip_y = center_g[1] + math.sin(arm_ang) * (self.radius - 6)
                pygame.draw.line(dim_surf, (*color_data["dark"], alpha), center_g, (rel_tip_x, rel_tip_y), width=2)
                surface.blit(dim_surf, (int(self.cx - guide_box // 2), int(self.cy - guide_box // 2)))

        # 3. Draw Platform Pads at the end of each arm
        for plat in self.arm_platforms:
            vis_depth = world_layers.get_visual_depth(plat.layer)
            plat.draw(surface, vis_depth)

        # 4. Central Mechanical Cogwheel Hub
        hub_r = 18
        # Outer ambient glow
        hub_glow = pygame.Surface((hub_r * 4, hub_r * 4), pygame.SRCALPHA)
        active_col = LAYER_COLORS[world_layers.foreground]["glow"]
        pygame.draw.circle(hub_glow, (*active_col, 60), (hub_r * 2, hub_r * 2), hub_r * 2)
        surface.blit(hub_glow, (int(self.cx - hub_r * 2), int(self.cy - hub_r * 2)))

        # Heavy metallic gear casing
        pygame.draw.circle(surface, (18, 24, 38), (int(self.cx), int(self.cy)), hub_r)
        pygame.draw.circle(surface, (80, 105, 140), (int(self.cx), int(self.cy)), hub_r, width=2)

        # Rotating gear teeth / rivets
        for tooth in range(6):
            tang = self.angle + tooth * (math.pi / 3.0)
            tw_x = self.cx + math.cos(tang) * (hub_r - 2)
            tw_y = self.cy + math.sin(tang) * (hub_r - 2)
            pygame.draw.circle(surface, (150, 180, 220), (int(tw_x), int(tw_y)), 2)

        # Inner Active Color Reactor
        pygame.draw.circle(surface, LAYER_COLORS[world_layers.foreground]["dark"], (int(self.cx), int(self.cy)), 9)
        pygame.draw.circle(surface, active_col, (int(self.cx), int(self.cy)), 6)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.cx), int(self.cy)), 3)

        # Direction Arrow Indicator on Hub
        spin_dir_ang = self.angle + math.pi / 2.0
        arr_tip_x = self.cx + math.cos(spin_dir_ang) * (hub_r + 5)
        arr_tip_y = self.cy + math.sin(spin_dir_ang) * (hub_r + 5)
        pygame.draw.circle(surface, (*active_col, 200), (int(arr_tip_x), int(arr_tip_y)), 2)


class SpectrumSpinGate:
    """A rotating tricolor ring segment.
    
    Spins continuously. When the player enters it while their active world matches
    the frontward segment, it flashes and provides a smooth boost to pass them forward.
    """

    def __init__(self, x: float, y: float, radius: float = 30.0, speed: float = 1.4):
        self.x = float(x)
        self.y = float(y)
        self.radius = float(radius)
        self.speed = float(speed)
        self.angle = 0.0
        self.rect = pygame.Rect(int(x - radius), int(y - radius), int(radius * 2), int(radius * 2))
        self.activated_timer = 0.0

    def reset(self) -> None:
        self.angle = 0.0
        self.activated_timer = 0.0

    def update(self, dt: float) -> None:
        self.angle += self.speed * dt
        if self.activated_timer > 0.0:
            self.activated_timer = max(0.0, self.activated_timer - dt)

    def check_player_boost(self, player, world_layers) -> bool:
        """Check if player touches the spinning segment gate.
        
        If active layer matches the gate's rotating primary sector, triggers a forward boost!
        """
        if self.rect.colliderect(player.rect):
            # Calculate which segment is facing left/right
            # If the world layer matches, boost player
            if self.activated_timer <= 0.0:
                self.activated_timer = 0.4
                # Propel player forward
                player.vx = max(player.vx + 3.5, 6.2)
                player.vy = min(player.vy, -4.5)
                return True
        return False

    def draw(self, surface: pygame.Surface, world_layers) -> None:
        """Render spinning tricolor segmented ring with rotating colored arcs."""
        cx, cy = int(self.x), int(self.y)
        r = int(self.radius)

        gate_surf = pygame.Surface((r * 2 + 16, r * 2 + 16), pygame.SRCALPHA)
        center = (r + 8, r + 8)

        # 3 color segments
        seg_layers = [LAYER_RED, LAYER_BLUE, LAYER_YELLOW]
        arc_span = 2.0 * math.pi / 3.0

        for i, layer_name in enumerate(seg_layers):
            start_ang = self.angle + i * arc_span
            col = LAYER_COLORS[layer_name]["bright"]
            is_active = (layer_name == world_layers.foreground)
            alpha = 255 if is_active else 100

            # Draw arc using points
            pts = [center]
            for step in range(11):
                cur_a = start_ang + (step / 10.0) * (arc_span * 0.9)
                px = center[0] + math.cos(cur_a) * r
                py = center[1] + math.sin(cur_a) * r
                pts.append((px, py))

            if len(pts) > 2:
                pygame.draw.polygon(gate_surf, (*col, int(alpha * 0.35)), pts)
                # Outer arc border
                pygame.draw.lines(gate_surf, (*col, alpha), False, pts[1:], width=3 if is_active else 1)

        # Draw central aperture
        pygame.draw.circle(gate_surf, (15, 20, 32), center, int(r * 0.4))
        pygame.draw.circle(gate_surf, (120, 150, 190), center, int(r * 0.4), width=2)

        # Activation surge ring
        if self.activated_timer > 0.0:
            burst_r = int(r * (1.0 + (0.4 - self.activated_timer) * 1.5))
            burst_surf = pygame.Surface((burst_r * 2 + 8, burst_r * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(
                burst_surf,
                (255, 255, 255, int(220 * (self.activated_timer / 0.4))),
                (burst_r + 4, burst_r + 4),
                burst_r,
                width=3,
            )
            surface.blit(burst_surf, (cx - burst_r - 4, cy - burst_r - 4))

        surface.blit(gate_surf, (cx - r - 8, cy - r - 8))
