"""Key and Lock puzzle mechanics for Spectrum Shift.

Features:
- SpectrumKey: Floating crystalline keys with bobbing and spinning animations.
- SpectrumLockGate: High-tech laser barriers that block paths until unlocked with a key.
"""

import math
import pygame
from typing import Optional, Tuple, List
try:
    from .settings import (
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        LAYER_COLORS,
        DEPTH_ALPHA,
        COLOR_TEXT_WHITE,
    )
    from .platform import Platform
except ImportError:
    from settings import (
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        LAYER_COLORS,
        DEPTH_ALPHA,
        COLOR_TEXT_WHITE,
    )
    from platform import Platform


class SpectrumKey:
    """Floating prismatic key with animated bobbing, glowing halo, and sparkle particles."""

    def __init__(self, x: float, y: float, layer: str = "prism", key_id: int = 1):
        self.spawn_x = float(x)
        self.spawn_y = float(y)
        self.x = float(x)
        self.y = float(y)
        self.layer = layer  # "red", "blue", "yellow", or "prism" (universal)
        self.key_id = key_id
        self.collected = False
        self.anim_phase = 0.0
        self.radius = 14
        self.rect = pygame.Rect(int(x - self.radius), int(y - self.radius), self.radius * 2, self.radius * 2)

    def reset(self) -> None:
        self.collected = False
        self.anim_phase = 0.0
        self.x = self.spawn_x
        self.y = self.spawn_y

    def update(self, dt: float) -> None:
        if not self.collected:
            self.anim_phase += dt * 3.5
            # Gentle vertical float
            bob = math.sin(self.anim_phase) * 5.0
            self.y = self.spawn_y + bob
            self.rect.y = int(self.y - self.radius)

    def check_pickup(self, player_rect: pygame.Rect, active_layer: str) -> bool:
        """Check if player touches the key.
        
        Prism keys can be collected in any layer; color keys require their world layer.
        """
        if self.collected:
            return False
        if self.rect.colliderect(player_rect):
            if self.layer == "prism" or self.layer == active_layer:
                self.collected = True
                return True
        return False

    def draw(self, surface: pygame.Surface, world_layers, font: Optional[pygame.font.Font] = None) -> None:
        if self.collected:
            return

        cx = int(self.x)
        cy = int(self.y)

        # Determine color
        if self.layer == "prism":
            # Shifting prismatic color
            hue_phase = self.anim_phase * 0.8
            r = int(127 + 127 * math.sin(hue_phase))
            g = int(127 + 127 * math.sin(hue_phase + 2.09))
            b = int(127 + 127 * math.sin(hue_phase + 4.18))
            core_col = (r, g, b)
            glow_col = (r, g, b, 70)
        else:
            core_col = LAYER_COLORS[self.layer]["bright"]
            glow_col = (*LAYER_COLORS[self.layer]["glow"], 70)

        # 1. Outer Glow Aura
        glow_size = int(self.radius * 3)
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pulse = 1.0 + 0.15 * math.sin(self.anim_phase * 2.0)
        cur_r = int(self.radius * pulse * 1.2)
        pygame.draw.circle(glow_surf, glow_col, (glow_size // 2, glow_size // 2), cur_r)
        surface.blit(glow_surf, (cx - glow_size // 2, cy - glow_size // 2))

        # 2. Rotating Diamond / Key Crystal
        spin_w = math.cos(self.anim_phase * 1.8) * 12.0
        h = 16.0
        pts = [
            (cx, cy - h),
            (cx + spin_w, cy),
            (cx, cy + h),
            (cx - spin_w, cy),
        ]
        if abs(spin_w) > 1.0:
            pygame.draw.polygon(surface, core_col, pts)
            pygame.draw.polygon(surface, (255, 255, 255), pts, width=1)
        else:
            pygame.draw.line(surface, (255, 255, 255), (cx, cy - h), (cx, cy + h), width=2)

        # 3. Inner White Core Sparkle
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 3)

        # 4. Floating Key Label
        if font:
            lbl = font.render("KEY", True, (255, 255, 255))
            surface.blit(lbl, (cx - lbl.get_width() // 2, cy - int(h) - 15))


class SpectrumLockGate:
    """A high-tech laser barrier that blocks passage until unlocked with a key."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float = 18.0,
        height: float = 72.0,
        layer: str = "prism",
        lock_id: int = 1,
    ):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.layer = layer
        self.lock_id = lock_id
        self.is_unlocked = False
        self.unlock_progress = 0.0  # 0.0 to 1.0
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))
        self.anim_phase = 0.0

        # Create a physical solid platform barrier when locked
        self.barrier_platform = Platform(int(x), int(y), int(width), int(height), layer="all_solid")

    def reset(self) -> None:
        self.is_unlocked = False
        self.unlock_progress = 0.0
        self.anim_phase = 0.0

    def update(self, dt: float) -> None:
        self.anim_phase += dt * 4.0
        if self.is_unlocked and self.unlock_progress < 1.0:
            self.unlock_progress = min(1.0, self.unlock_progress + dt * 2.8)

    def unlock(self) -> None:
        """Trigger unlock sequence."""
        self.is_unlocked = True

    def check_interaction(self, player_rect: pygame.Rect, player_keys: int) -> bool:
        """Check if player with key collides with locked barrier to unlock it."""
        if self.is_unlocked:
            return False
        # Expand check rect slightly for interaction
        touch_rect = self.rect.inflate(8, 0)
        if touch_rect.colliderect(player_rect):
            if player_keys > 0:
                self.unlock()
                return True
        return False

    def is_solid(self) -> bool:
        """Lock barrier is only physically solid when not unlocked."""
        return not self.is_unlocked

    def draw(self, surface: pygame.Surface, font: Optional[pygame.font.Font] = None) -> None:
        if self.unlock_progress >= 1.0:
            return  # Completely dissolved

        alpha_factor = 1.0 - self.unlock_progress
        barrier_surf = pygame.Surface((int(self.width) + 32, int(self.height) + 16), pygame.SRCALPHA)
        ox = 16
        oy = 8

        # 1. Top and Bottom Emitter Terminals (Metal nodes)
        node_color = (65, 80, 110)
        glow_color = (0, 235, 255) if self.layer == "prism" else LAYER_COLORS.get(self.layer, {}).get("bright", (255, 210, 30))
        glow_alpha = int(220 * alpha_factor)

        # Top Emitter
        pygame.draw.rect(barrier_surf, node_color, (ox - 4, oy - 6, int(self.width) + 8, 8), border_radius=3)
        pygame.draw.circle(barrier_surf, (*glow_color, glow_alpha), (ox + int(self.width) // 2, oy - 2), 4)

        # Bottom Emitter
        pygame.draw.rect(barrier_surf, node_color, (ox - 4, oy + int(self.height) - 2, int(self.width) + 8, 8), border_radius=3)
        pygame.draw.circle(barrier_surf, (*glow_color, glow_alpha), (ox + int(self.width) // 2, oy + int(self.height) + 2), 4)

        # 2. Glowing Laser Barrier Field
        if not self.is_unlocked:
            laser_alpha = int((140 + 50 * math.sin(self.anim_phase)) * alpha_factor)
            pygame.draw.rect(
                barrier_surf,
                (*glow_color, laser_alpha),
                (ox, oy, int(self.width), int(self.height)),
                border_radius=4,
            )
            # Pulsing central beam
            pygame.draw.line(
                barrier_surf,
                (255, 255, 255, int(230 * alpha_factor)),
                (ox + int(self.width) // 2, oy),
                (ox + int(self.width) // 2, oy + int(self.height)),
                width=2,
            )

            # Horizontal energy scanline
            scan_y = oy + int(((self.anim_phase * 20.0) % self.height))
            pygame.draw.line(
                barrier_surf,
                (255, 255, 255, 200),
                (ox, scan_y),
                (ox + int(self.width), scan_y),
                width=2,
            )

            # Center Holographic Lock Icon
            mid_y = oy + int(self.height) // 2
            mid_x = ox + int(self.width) // 2
            lock_box = pygame.Rect(mid_x - 12, mid_y - 12, 24, 24)
            pygame.draw.rect(barrier_surf, (15, 20, 32, 240), lock_box, border_radius=4)
            pygame.draw.rect(barrier_surf, (*glow_color, 255), lock_box, width=2, border_radius=4)
            # Lock shackle
            pygame.draw.arc(barrier_surf, (*glow_color, 255), (mid_x - 7, mid_y - 10, 14, 12), math.pi, 2 * math.pi, width=2)
            # Keyhole
            pygame.draw.circle(barrier_surf, (255, 255, 255), (mid_x, mid_y), 2)
            pygame.draw.line(barrier_surf, (255, 255, 255), (mid_x, mid_y), (mid_x, mid_y + 4), width=2)

        else:
            # Dissolving expansion rings
            expand_w = int(self.width + self.unlock_progress * 40.0)
            expand_rect = pygame.Rect(ox - int((expand_w - self.width) / 2), oy, expand_w, int(self.height))
            pygame.draw.rect(
                barrier_surf,
                (*glow_color, int(180 * alpha_factor)),
                expand_rect,
                width=2,
                border_radius=4,
            )

        surface.blit(barrier_surf, (int(self.x) - ox, int(self.y) - oy))

        # Floating "LOCKED" hint
        if not self.is_unlocked and font:
            hint = font.render("LOCKED", True, (*glow_color, 220))
            surface.blit(hint, (int(self.x + self.width // 2 - hint.get_width() // 2), int(self.y - 18)))
