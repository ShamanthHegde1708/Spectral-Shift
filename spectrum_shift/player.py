"""Player character entity, movement physics, jump mechanics, and collision detection.

Features:
- The Spectrum Nomad: A detailed humanoid cyber-hero with articulated helmet, visor glints,
  segmented torso armor, glowing arc reactor, utility belt, magnet boots, and flowing scarf.
- Chroma Phase Dash: High-speed burst with RGB chromatic ghost trail.
- Rock-Solid Moving Platform Ride: Seamless momentum transfer when jumping off rotors.
"""

import math
import pygame
from typing import List, Optional, Tuple, Dict
try:
    from .settings import (
        COLOR_PLAYER,
        COLOR_PLAYER_CORE,
        COLOR_PLAYER_EYE,
        COLOR_PLAYER_GLOW,
        LAYER_COLORS,
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        PLAYER_WIDTH,
        PLAYER_HEIGHT,
        GRAVITY,
        MAX_FALL_SPEED,
        ACCELERATION,
        MAX_SPEED,
        FRICTION_GROUND,
        FRICTION_AIR,
        JUMP_VELOCITY,
        JUMP_CUT_MULTIPLIER,
        COYOTE_FRAMES,
        JUMP_BUFFER_FRAMES,
        DEATH_Y,
        DASH_SPEED,
        DASH_DURATION,
        DASH_COOLDOWN,
    )
    from .platform import Platform
    from .world_layers import WorldLayers
except ImportError:
    from settings import (
        COLOR_PLAYER,
        COLOR_PLAYER_CORE,
        COLOR_PLAYER_EYE,
        COLOR_PLAYER_GLOW,
        LAYER_COLORS,
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        PLAYER_WIDTH,
        PLAYER_HEIGHT,
        GRAVITY,
        MAX_FALL_SPEED,
        ACCELERATION,
        MAX_SPEED,
        FRICTION_GROUND,
        FRICTION_AIR,
        JUMP_VELOCITY,
        JUMP_CUT_MULTIPLIER,
        COYOTE_FRAMES,
        JUMP_BUFFER_FRAMES,
        DEATH_Y,
        DASH_SPEED,
        DASH_DURATION,
        DASH_COOLDOWN,
    )
    from platform import Platform
    from world_layers import WorldLayers


# 12x17 Handcrafted High-Detail Humanoid Pixel Art Sprite Matrices
# Letters:
#   . = Transparent
#   K = Dark cyber outline (14, 18, 28)
#   H = Highlight specular white (255, 255, 255)
#   W = White cyber chassis armor (240, 245, 255)
#   S = Shaded armor plating (165, 182, 210)
#   P = Articulated leg plates (195, 210, 230)
#   A = Arm / Gauntlet plating (215, 228, 245)
#   B = Utility belt with holsters (85, 102, 128)
#   D = Dark flexible joint mesh (38, 48, 68)
#   V = Cyan visor glass (0, 230, 255)
#   E = Visor eye glint aperture (255, 255, 255)
#   C = Energy scarf (color matches active world)
#   R = Torso Arc Reactor (color matches active world)
#   T = Jet thruster flare (110, 245, 255)
#   M = Magnetized boot sole (105, 125, 155)

PIXEL_SPRITES: Dict[str, List[str]] = {
    "idle": [
        "..KHHHHHK...",
        ".KWWWWWWK...",
        ".KWEVVVVEK..",
        ".KWWWWWWK...",
        ".KCCWWCCK.C.",
        "KAWWWWAK.CC.",
        "KAWRRWAK..C.",
        ".AWWWWA.....",
        ".KBBBBK.....",
        "..KDDDK.....",
        ".KPP.PPK....",
        ".KPP.PPK....",
        ".KDD.DDK....",
        ".KDD.DDK....",
        "KKDD.DDKK...",
        "KMMK.KMMK...",
        "............",
    ],
    "run_0": [
        "..KHHHHHK...",
        ".KWWWWWWK...",
        ".KWEVVVVEK..",
        ".KWWWWWWK...",
        ".KCCWWCCK.C.",
        "KAWWWWAK.CC.",
        "KAWRRWAK.CC.",
        ".AWWWWA..C..",
        ".KBBBBK.....",
        "..KDDDK.....",
        ".KPP...PK...",
        ".KPP....PK..",
        "KKD......DKK",
        "KDD......DDK",
        "KMMK....KMMK",
        "............",
        "............",
    ],
    "run_1": [
        "..KHHHHHK...",
        ".KWWWWWWK...",
        ".KWEVVVVEK..",
        ".KWWWWWWK...",
        ".KCCWWCCK...",
        "KAWWWWAK.CCC",
        "KAWRRWAK..C.",
        ".AWWWWA.....",
        ".KBBBBK.....",
        "..KDDDK.....",
        "..KDDDK.....",
        ".KPP.PPK....",
        ".KDD.DDK....",
        ".KDD.DDK....",
        "KKDD.DDKK...",
        "KMMK.KMMK...",
        "............",
    ],
    "run_2": [
        "..KHHHHHK...",
        ".KWWWWWWK...",
        ".KWEVVVVEK..",
        ".KWWWWWWK...",
        ".KCCWWCCK.C.",
        "KAWWWWAK.CC.",
        "KAWRRWAK.CC.",
        ".AWWWWA..C..",
        ".KBBBBK.....",
        "..KDDDK.....",
        "..KP...PPK..",
        ".KP.....PPK.",
        "KKD......DKK",
        "KDD......DDK",
        "KMMK....KMMK",
        "............",
        "............",
    ],
    "run_3": [
        "..KHHHHHK...",
        ".KWWWWWWK...",
        ".KWEVVVVEK..",
        ".KWWWWWWK...",
        ".KCCWWCCK...",
        "KAWWWWAK.CCC",
        "KAWRRWAK..C.",
        ".AWWWWA.....",
        ".KBBBBK.....",
        "..KDDDK.....",
        "..KDDDK.....",
        ".KPP.PPK....",
        ".KDD.DDK....",
        ".KDD.DDK....",
        "KKDD.DDKK...",
        "KMMK.KMMK...",
        "............",
    ],
    "jump": [
        "..KHHHHHK...",
        ".KWWWWWWK...",
        ".KWEVVVVEK..",
        ".KWWWWWWK...",
        ".KCCWWCCK...",
        "KAWWWWAK.C..",
        "KAWRRWAK.CC.",
        ".AWWWWA..C..",
        ".KBBBBK.....",
        "..KDDDK.....",
        ".KPP.PPK....",
        ".KKDDDKK....",
        "..KDDDK.....",
        "..KTTTK.....",
        "..KTTTK.....",
        "..TT.TT.....",
        "............",
    ],
    "fall": [
        "..KHHHHHK...",
        ".KWWWWWWK...",
        ".KWEVVVVEK..",
        ".KWWWWWWK...",
        ".KCCWWCCK...",
        "KAWWWWAK..C.",
        "KAWRRWAK.CC.",
        ".AWWWWA.CCC.",
        ".KBBBBK.....",
        "..KDDDK.....",
        ".KPP.PPK....",
        ".KPP.PPK....",
        ".KDD.DDK....",
        "KKDD.DDKK...",
        "KMMK.KMMK...",
        "............",
        "............",
    ],
    "dash": [
        "....KHHHHHK.",
        "...KWWWWWWK.",
        "...KWEVVVVEK",
        "...KWWWWWWK.",
        ".KCCWWCCK...",
        "KAWWWWAKCCCC",
        "KAWRRWAK.CCC",
        ".AWWWWA.....",
        ".KBBBBK.....",
        "..KDDDK.....",
        ".KPPPPPK....",
        "KKDD.DDKK...",
        "KTTK.KTTK...",
        "TTT...TTT...",
        "............",
        "............",
        "............",
    ],
}


class PixelHeroRenderer:
    """Renders and caches humanoid pixel art sprites with dynamic color tints."""

    def __init__(self):
        self.cache: Dict[Tuple[str, int, Tuple[int, int, int], Tuple[int, int, int]], pygame.Surface] = {}

    def get_sprite(
        self,
        frame_name: str,
        facing_dir: int,
        active_color: Tuple[int, int, int],
        visor_color: Tuple[int, int, int] = (0, 230, 255),
    ) -> pygame.Surface:
        key = (frame_name, facing_dir, active_color, visor_color)
        if key in self.cache:
            return self.cache[key]

        raw_lines = PIXEL_SPRITES.get(frame_name, PIXEL_SPRITES["idle"])
        h = len(raw_lines)
        w = len(raw_lines[0])

        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        palette = {
            ".": (0, 0, 0, 0),
            "K": (14, 18, 28, 255),        # Cyber outline
            "H": (255, 255, 255, 255),     # Specular white
            "W": (240, 245, 255, 255),     # White cyber armor
            "S": (165, 182, 210, 255),     # Shaded armor
            "P": (195, 210, 230, 255),     # Articulated leg plates
            "A": (215, 228, 245, 255),     # Arms / Gauntlets
            "B": (85, 102, 128, 255),      # Utility belt
            "D": (38, 48, 68, 255),        # Flexible under-suit
            "V": (*visor_color, 255),      # Visor glass
            "E": (255, 255, 255, 255),     # Visor eye aperture glint
            "C": (*active_color, 255),     # Energy Scarf (color matches active world)
            "R": (*active_color, 255),     # Torso Arc Reactor Core
            "T": (110, 245, 255, 255),     # Jet thruster
            "M": (105, 125, 155, 255),     # Magnet boot soles
        }

        for y, line in enumerate(raw_lines):
            for x, char in enumerate(line):
                color = palette.get(char, (0, 0, 0, 0))
                if color[3] > 0:
                    surf.set_at((x, y), color)

        # Scale 2x with nearest neighbor for crisp pixel art (12x17 -> 24x34)
        scaled_surf = pygame.transform.scale(surf, (w * 2, h * 2))

        if facing_dir < 0:
            scaled_surf = pygame.transform.flip(scaled_surf, True, False)

        self.cache[key] = scaled_surf
        return scaled_surf


# Global pixel art renderer instance
pixel_renderer = PixelHeroRenderer()


class Player:
    """The Spectrum Nomad: A custom humanoid cyber-hero with deterministic physics and Chroma Phase Dash."""

    def __init__(self, spawn_x: float, spawn_y: float):
        self.spawn_x = float(spawn_x)
        self.spawn_y = float(spawn_y)

        # Precise position and velocity
        self.x = float(spawn_x)
        self.y = float(spawn_y)
        self.vx = 0.0
        self.vy = 0.0

        # Physical collision bounding box (24x34)
        self.rect = pygame.Rect(int(self.x), int(self.y), PLAYER_WIDTH, PLAYER_HEIGHT)

        # State flags
        self.is_grounded = False
        self.current_ground_platform = None
        self.facing_dir = 1  # 1 for right, -1 for left
        self.is_dead = False

        # Input buffering & coyote time
        self.coyote_timer = 0
        self.jump_buffer_timer = 0

        # Unique Feature: Chroma Phase Dash
        self.is_dashing = False
        self.dash_timer = 0.0
        self.dash_cooldown = 0.0
        self.has_dash = True
        self.dash_ghosts: List[Dict[str, float]] = []

        # Visual animation parameters
        self.squash_stretch_x = 1.0
        self.squash_stretch_y = 1.0
        self.run_anim_phase = 0.0

        # Callbacks
        self.on_jump = None
        self.on_land = None
        self.on_dash = None

    def reset(self, x: Optional[float] = None, y: Optional[float] = None) -> None:
        """Reset player state and teleport back to spawn coordinates."""
        if x is not None:
            self.spawn_x = float(x)
        if y is not None:
            self.spawn_y = float(y)

        self.x = self.spawn_x
        self.y = self.spawn_y
        self.vx = 0.0
        self.vy = 0.0
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.is_grounded = False
        self.current_ground_platform = None
        self.facing_dir = 1
        self.is_dead = False
        self.coyote_timer = 0
        self.jump_buffer_timer = 0
        self.is_dashing = False
        self.dash_timer = 0.0
        self.dash_cooldown = 0.0
        self.has_dash = True
        self.dash_ghosts.clear()
        self.squash_stretch_x = 1.0
        self.squash_stretch_y = 1.0
        self.run_anim_phase = 0.0

    def execute_dash(self) -> bool:
        """Trigger Chroma Phase Dash surge."""
        if self.is_dashing or not self.has_dash or self.dash_cooldown > 0.0:
            return False

        self.is_dashing = True
        self.dash_timer = DASH_DURATION
        self.dash_cooldown = DASH_COOLDOWN
        self.has_dash = False
        self.vx = float(self.facing_dir) * DASH_SPEED
        self.vy = 0.0  # Zero vertical gravity during dash
        self.squash_stretch_x = 1.4
        self.squash_stretch_y = 0.7
        if self.on_dash:
            self.on_dash()
        return True

    def handle_input(
        self,
        move_left: bool,
        move_right: bool,
        jump_pressed: bool,
        jump_held: bool,
        dash_pressed: bool = False,
    ) -> None:
        """Process movement, jump, and dash intents."""
        # Check Dash Trigger
        if dash_pressed:
            self.execute_dash()

        if self.is_dashing:
            # During dash, momentum is locked forward
            return

        # Horizontal acceleration
        if move_left and not move_right:
            self.vx -= ACCELERATION
            if self.vx < -MAX_SPEED:
                self.vx = -MAX_SPEED
            self.facing_dir = -1
        elif move_right and not move_left:
            self.vx += ACCELERATION
            if self.vx > MAX_SPEED:
                self.vx = MAX_SPEED
            self.facing_dir = 1
        else:
            # Friction when not actively pressing directional keys
            friction = FRICTION_GROUND if self.is_grounded else FRICTION_AIR
            self.vx *= friction
            if abs(self.vx) < 0.15:
                self.vx = 0.0

        # Jump buffering
        if jump_pressed:
            self.jump_buffer_timer = JUMP_BUFFER_FRAMES

        # Variable jump height cut
        if not jump_held and self.vy < -2.0:
            self.vy *= JUMP_CUT_MULTIPLIER

    def update(self, platforms: List[Platform], world_layers: WorldLayers) -> None:
        """Perform one deterministic physics step."""
        if self.is_dead:
            return

        # Cooldown & Dash timers
        if self.dash_cooldown > 0.0:
            self.dash_cooldown = max(0.0, self.dash_cooldown - 0.016)

        if self.is_dashing:
            self.dash_timer -= 0.016
            # Record ghost trail during dash
            self.dash_ghosts.append({
                "x": float(self.rect.x),
                "y": float(self.rect.y),
                "facing": self.facing_dir,
                "alpha": 1.0,
            })
            if self.dash_timer <= 0.0:
                self.is_dashing = False
                self.vx *= 0.6  # Smooth exit deceleration

        # Update and fade chromatic ghosts
        for g in self.dash_ghosts:
            g["alpha"] -= 0.08
        self.dash_ghosts = [g for g in self.dash_ghosts if g["alpha"] > 0.05]

        # Moving platform carry: smoothly follow platform motion
        if self.is_grounded and self.current_ground_platform:
            p = self.current_ground_platform
            if hasattr(p, "dx") and hasattr(p, "dy"):
                self.x += p.dx
                self.y += p.dy
                self.rect.x = int(round(self.x))
                self.rect.y = int(round(self.y))

        # Re-arm dash when touching solid ground
        if self.is_grounded:
            self.has_dash = True
            self.coyote_timer = COYOTE_FRAMES
        else:
            if self.coyote_timer > 0:
                self.coyote_timer -= 1

        # Check if buffered jump can execute
        if self.jump_buffer_timer > 0:
            if self.is_grounded or self.coyote_timer > 0:
                self._execute_jump()
                self.jump_buffer_timer = 0
            else:
                self.jump_buffer_timer -= 1

        # Apply gravity if not grounded and not dashing
        if not self.is_grounded and not self.is_dashing:
            self.vy += GRAVITY
            if self.vy > MAX_FALL_SPEED:
                self.vy = MAX_FALL_SPEED

        # Filter platforms to ONLY foreground (solid) layer or all_solid
        solid_platforms = [p for p in platforms if world_layers.is_solid(p.layer)]

        # --- Horizontal Move & Resolve ---
        self.x += self.vx
        self.rect.x = int(round(self.x))

        for p in solid_platforms:
            # Ignore the ground platform player is currently standing on
            if p == self.current_ground_platform:
                continue
            # Ignore horizontal collision if player feet are near top of platform
            if self.rect.bottom <= p.rect.top + 5:
                continue

            if self.rect.colliderect(p.rect):
                if self.vx > 0:
                    self.rect.right = p.rect.left
                    self.vx = 0.0
                    self.x = float(self.rect.x)
                elif self.vx < 0:
                    self.rect.left = p.rect.right
                    self.vx = 0.0
                    self.x = float(self.rect.x)

        # --- Vertical Move & Resolve ---
        was_grounded = self.is_grounded
        self.y += self.vy
        self.rect.y = int(round(self.y))
        self.is_grounded = False

        for p in solid_platforms:
            if self.rect.colliderect(p.rect):
                if self.vy > 0 or (self.current_ground_platform == p and self.vy >= 0):
                    # Landing on platform top
                    self.rect.bottom = p.rect.top
                    self.vy = 0.0
                    self.y = float(self.rect.y)
                    self.is_grounded = True
                    self.current_ground_platform = p
                    if not was_grounded:
                        self.squash_stretch_x = 1.25
                        self.squash_stretch_y = 0.75
                        if self.on_land:
                            self.on_land()
                elif self.vy < 0:
                    # Hitting bottom of platform with head
                    self.rect.top = p.rect.bottom
                    self.vy = 0.0
                    self.y = float(self.rect.y)

        # --- Ground Support Verification ---
        feet_probe = pygame.Rect(self.rect.x + 2, self.rect.bottom, self.rect.width - 4, 3)
        matched_p = None
        for p in solid_platforms:
            if feet_probe.colliderect(p.rect):
                matched_p = p
                break

        if matched_p is not None and self.vy >= 0:
            self.is_grounded = True
            self.current_ground_platform = matched_p
            self.rect.bottom = matched_p.rect.top
            self.y = float(self.rect.y)
            self.vy = 0.0
            self.has_dash = True  # Re-arm dash when firmly grounded
            if not was_grounded:
                self.squash_stretch_x = 1.25
                self.squash_stretch_y = 0.75
                if self.on_land:
                    self.on_land()
        else:
            self.is_grounded = False
            self.current_ground_platform = None

        # --- Fall / Death Detection ---
        if self.rect.top > DEATH_Y:
            self.is_dead = True

        # Running animation phase
        if self.is_grounded and abs(self.vx) > 0.5:
            self.run_anim_phase += 0.28
        else:
            self.run_anim_phase = 0.0

        # Decay squash/stretch back to 1.0
        self.squash_stretch_x += (1.0 - self.squash_stretch_x) * 0.2
        self.squash_stretch_y += (1.0 - self.squash_stretch_y) * 0.2

    def check_ground_after_rotation(self, platforms: List[Platform], world_layers: WorldLayers) -> None:
        """Called immediately after layer rotation to verify ground support."""
        solid_platforms = [p for p in platforms if world_layers.is_solid(p.layer)]
        feet_probe = pygame.Rect(self.rect.x + 2, self.rect.bottom, self.rect.width - 4, 3)
        has_support = any(feet_probe.colliderect(p.rect) for p in solid_platforms)
        if not has_support:
            self.is_grounded = False
            self.current_ground_platform = None
            self.coyote_timer = 0

    def _execute_jump(self) -> None:
        """Trigger jump impulse and preserve moving platform tangential velocity."""
        self.vy = JUMP_VELOCITY
        if self.current_ground_platform:
            p = self.current_ground_platform
            if hasattr(p, "dx"):
                self.vx += p.dx * 0.75
            if hasattr(p, "dy") and p.dy < 0:
                self.vy += p.dy * 0.5  # Boost jump if platform moves up!
        self.is_grounded = False
        self.current_ground_platform = None
        self.coyote_timer = 0
        self.squash_stretch_x = 0.8
        self.squash_stretch_y = 1.3
        if self.on_jump:
            self.on_jump()

    def draw(self, surface: pygame.Surface, world_layers: Optional[WorldLayers] = None) -> None:
        """Render the custom humanoid hero with chromatic dash trails and color-reactive armor."""
        # Active layer energy color
        if world_layers:
            fg = world_layers.foreground
            active_color = LAYER_COLORS.get(fg, {}).get("bright", (0, 220, 255))
            glow_color = LAYER_COLORS.get(fg, {}).get("glow", (0, 220, 255))
        else:
            active_color = (0, 220, 255)
            glow_color = (0, 220, 255)

        # 1. Render Chromatic Phase Dash Ghost Trails (RGB Split)
        for g in self.dash_ghosts:
            alpha = int(g["alpha"] * 160)
            ghost_spr = pixel_renderer.get_sprite("dash", int(g["facing"]), active_color)
            ghost_surf = pygame.Surface(ghost_spr.get_size(), pygame.SRCALPHA)
            ghost_surf.blit(ghost_spr, (0, 0))
            ghost_surf.set_alpha(alpha)
            # RGB chromatic shift: Red offset left, Blue center, Yellow offset right
            surface.blit(ghost_surf, (int(g["x"] - 3), int(g["y"])))
            surface.blit(ghost_surf, (int(g["x"] + 3), int(g["y"])))

        # 2. Determine animation frame
        if self.is_dashing:
            frame_name = "dash"
        elif not self.is_grounded:
            if self.vy < -1.5:
                frame_name = "jump"
            else:
                frame_name = "fall"
        elif abs(self.vx) > 0.5:
            step_idx = int(self.run_anim_phase) % 4
            frame_name = f"run_{step_idx}"
        else:
            frame_name = "idle"

        # 3. Outer Pixel Glow Aura
        glow_surf = pygame.Surface((PLAYER_WIDTH + 14, PLAYER_HEIGHT + 14), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*glow_color, 50), glow_surf.get_rect(), border_radius=4)
        surface.blit(glow_surf, (self.rect.x - 7, self.rect.y - 7))

        # 4. Render Handcrafted Humanoid Pixel Art Sprite
        sprite = pixel_renderer.get_sprite(
            frame_name=frame_name,
            facing_dir=self.facing_dir,
            active_color=active_color,
            visor_color=(0, 240, 255),
        )

        surface.blit(sprite, (self.rect.x, self.rect.y))
