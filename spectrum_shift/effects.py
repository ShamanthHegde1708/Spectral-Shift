"""Visual effects: neon particles, portal vortex, screen pulses, and ambient sci-fi grid."""

import math
import random
import pygame
from typing import List, Tuple
try:
    from .settings import (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        COLOR_BG,
        COLOR_GRID,
        COLOR_EXIT_CORE,
        COLOR_EXIT_RING,
        COLOR_EXIT_GLOW,
        PORTAL_RADIUS,
        LAYER_COLORS,
    )
except ImportError:
    from settings import (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        COLOR_BG,
        COLOR_GRID,
        COLOR_EXIT_CORE,
        COLOR_EXIT_RING,
        COLOR_EXIT_GLOW,
        PORTAL_RADIUS,
        LAYER_COLORS,
    )


class Particle:
    """Individual geometric particle for trails, jumps, and rotation bursts."""

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: Tuple[int, int, int],
        lifetime: float,
        size: float = 3.0,
        shape: str = "rect",
    ):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.max_life = lifetime
        self.size = size
        self.shape = shape

    def update(self, dt: float) -> bool:
        """Update particle physics. Returns False when particle is dead."""
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        return True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw fading neon particle."""
        progress = max(0.0, self.lifetime / self.max_life)
        alpha = int(255 * progress)
        curr_size = max(1.0, self.size * progress)

        p_surf = pygame.Surface((int(curr_size * 2 + 4), int(curr_size * 2 + 4)), pygame.SRCALPHA)
        draw_color = (*self.color, alpha)

        if self.shape == "rect":
            rect = pygame.Rect(2, 2, int(curr_size), int(curr_size))
            pygame.draw.rect(p_surf, draw_color, rect)
        else:
            pygame.draw.circle(p_surf, draw_color, (int(curr_size + 2), int(curr_size + 2)), int(curr_size / 2))

        surface.blit(p_surf, (int(self.x - curr_size), int(self.y - curr_size)))


class RotationPulse:
    """Expanding neon shockwave ring when the world stack is rotated."""

    def __init__(self, color: Tuple[int, int, int], max_radius: float = 300.0, duration: float = 0.35):
        self.color = color
        self.max_radius = max_radius
        self.duration = duration
        self.timer = duration

    def update(self, dt: float) -> bool:
        self.timer -= dt
        return self.timer > 0

    def draw(self, surface: pygame.Surface, center: Tuple[int, int]) -> None:
        progress = 1.0 - (self.timer / self.duration)
        radius = int(progress * self.max_radius)
        alpha = int(180 * (1.0 - progress))
        if radius > 0 and alpha > 0:
            pulse_surf = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(
                pulse_surf,
                (*self.color, alpha),
                (radius + 4, radius + 4),
                radius,
                width=max(1, int(4 * (1.0 - progress))),
            )
            surface.blit(pulse_surf, (center[0] - radius - 4, center[1] - radius - 4))


class ExitPortal:
    """Glowing, animated sci-fi exit portal."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x - PORTAL_RADIUS, y - PORTAL_RADIUS, PORTAL_RADIUS * 2, PORTAL_RADIUS * 2)
        self.angle = 0.0
        self.pulse = 0.0

    def update(self, dt: float) -> None:
        self.angle += dt * 3.5
        self.pulse = math.sin(self.angle * 1.5) * 4.0

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = self.x, self.y
        base_r = PORTAL_RADIUS + self.pulse

        # 1. Outer ambient glow
        glow_size = int(base_r * 2.8)
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surf,
            (*COLOR_EXIT_GLOW, 50),
            (glow_size // 2, glow_size // 2),
            int(base_r * 1.3),
        )
        surface.blit(glow_surf, (cx - glow_size // 2, cy - glow_size // 2))

        # 2. Outer Rotating Ring with notches
        ring_r = int(base_r)
        ring_surf = pygame.Surface((ring_r * 2 + 10, ring_r * 2 + 10), pygame.SRCALPHA)
        pygame.draw.circle(
            ring_surf,
            COLOR_EXIT_RING,
            (ring_r + 5, ring_r + 5),
            ring_r,
            width=2,
        )
        # Notches
        for i in range(4):
            not_ang = self.angle + i * (math.pi / 2)
            nx = (ring_r + 5) + math.cos(not_ang) * ring_r
            ny = (ring_r + 5) + math.sin(not_ang) * ring_r
            pygame.draw.circle(ring_surf, COLOR_EXIT_CORE, (int(nx), int(ny)), 3)
        surface.blit(ring_surf, (cx - ring_r - 5, cy - ring_r - 5))

        # 3. Inner Counter-Rotating Diamond
        inner_r = int(base_r * 0.6)
        diamond_pts = []
        for i in range(4):
            d_ang = -self.angle * 1.8 + i * (math.pi / 2)
            dx = cx + math.cos(d_ang) * inner_r
            dy = cy + math.sin(d_ang) * inner_r
            diamond_pts.append((dx, dy))
        pygame.draw.polygon(surface, COLOR_EXIT_CORE, diamond_pts, width=2)

        # 4. Radiant Gravitational Light Rays
        for i in range(6):
            r_ang = self.angle * 0.8 + i * (math.pi / 3.0)
            ray_len = base_r * 1.5 + math.sin(self.angle * 2.0 + i) * 5.0
            rx = cx + math.cos(r_ang) * ray_len
            ry = cy + math.sin(r_ang) * ray_len
            pygame.draw.line(surface, (*COLOR_EXIT_CORE, 80), (cx, cy), (rx, ry), width=1)

        # 5. Core Beacon
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 6)
        pygame.draw.circle(surface, COLOR_EXIT_CORE, (cx, cy), 3)


class EffectManager:
    """Central manager for ambient grid, particles, pulses, and screen feedback."""

    def __init__(self):
        self.particles: List[Particle] = []
        self.pulses: List[RotationPulse] = []
        self.screen_shake_time = 0.0
        self.screen_shake_intensity = 0.0

        # Ambient floating sci-fi stars
        self.stars = [
            (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.uniform(0.5, 1.8), random.uniform(0.2, 0.8))
            for _ in range(35)
        ]

    def reset(self) -> None:
        self.particles.clear()
        self.pulses.clear()
        self.screen_shake_time = 0.0
        self.screen_shake_intensity = 0.0

    def trigger_shake(self, intensity: float = 6.0, duration: float = 0.25) -> None:
        self.screen_shake_intensity = intensity
        self.screen_shake_time = duration

    def trigger_rotation_pulse(self, foreground_layer: str, center: Tuple[int, int]) -> None:
        color = LAYER_COLORS.get(foreground_layer, {}).get("bright", (255, 255, 255))
        self.pulses.append(RotationPulse(color=color, max_radius=320.0, duration=0.3))

    def spawn_jump_dust(self, x: float, y: float) -> None:
        for _ in range(8):
            vx = random.uniform(-2.2, 2.2)
            vy = random.uniform(-0.5, -2.5)
            self.particles.append(
                Particle(x, y, vx, vy, color=(200, 240, 255), lifetime=0.25, size=random.uniform(2.0, 4.0))
            )

    def spawn_land_dust(self, x: float, y: float) -> None:
        for _ in range(10):
            vx = random.uniform(-3.0, 3.0)
            vy = random.uniform(-0.2, -1.2)
            self.particles.append(
                Particle(x, y, vx, vy, color=(200, 240, 255), lifetime=0.22, size=random.uniform(2.5, 4.5))
            )

    def spawn_death_burst(self, x: float, y: float) -> None:
        for _ in range(25):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.0, 6.5)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            color = random.choice([(255, 50, 90), (0, 210, 255), (255, 210, 30), (255, 255, 255)])
            self.particles.append(
                Particle(x, y, vx, vy, color=color, lifetime=random.uniform(0.35, 0.6), size=random.uniform(3.0, 6.0))
            )

    def spawn_player_trail(self, x: float, y: float) -> None:
        if random.random() < 0.4:
            self.particles.append(
                Particle(
                    x + random.uniform(-4, 4),
                    y + random.uniform(-4, 4),
                    vx=random.uniform(-0.2, 0.2),
                    vy=random.uniform(-0.2, 0.2),
                    color=(180, 220, 255),
                    lifetime=0.2,
                    size=2.5,
                )
            )

    def spawn_portal_motes(self, portal_x: int, portal_y: int) -> None:
        if random.random() < 0.35:
            ang = random.uniform(0, math.pi * 2)
            dist = random.uniform(25, 45)
            px = portal_x + math.cos(ang) * dist
            py = portal_y + math.sin(ang) * dist
            # Float inwards toward portal center
            vx = -math.cos(ang) * 1.2
            vy = -math.sin(ang) * 1.2
            self.particles.append(
                Particle(px, py, vx, vy, color=COLOR_EXIT_CORE, lifetime=0.5, size=2.0)
            )

    def update(self, dt: float) -> None:
        # Screen shake
        if self.screen_shake_time > 0:
            self.screen_shake_time = max(0.0, self.screen_shake_time - dt)

        # Particles
        self.particles = [p for p in self.particles if p.update(dt)]

        # Pulses
        self.pulses = [pulse for pulse in self.pulses if pulse.update(dt)]

    def get_shake_offset(self) -> Tuple[int, int]:
        if self.screen_shake_time > 0:
            prog = self.screen_shake_time
            cur_i = self.screen_shake_intensity * prog
            return (
                int(random.uniform(-cur_i, cur_i)),
                int(random.uniform(-cur_i, cur_i)),
            )
        return (0, 0)

    def draw_background(self, surface: pygame.Surface) -> None:
        """Render rich dark sci-fi background with geometric grid, star dust, and cyber vignette."""
        surface.fill(COLOR_BG)

        # Subtle background grid
        grid_size = 40
        for x in range(0, SCREEN_WIDTH, grid_size):
            # Intermittent brightness for high-tech aesthetic
            col = (35, 45, 68) if (x // grid_size) % 4 == 0 else COLOR_GRID
            pygame.draw.line(surface, col, (x, 0), (x, SCREEN_HEIGHT), width=1)
        for y in range(0, SCREEN_HEIGHT, grid_size):
            col = (35, 45, 68) if (y // grid_size) % 4 == 0 else COLOR_GRID
            pygame.draw.line(surface, col, (0, y), (SCREEN_WIDTH, y), width=1)

        # Ambient sci-fi dust/stars
        for sx, sy, size, speed in self.stars:
            star_alpha = int(70 + 40 * math.sin(pygame.time.get_ticks() * 0.002 * speed))
            s_surf = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s_surf, (150, 180, 220, star_alpha), (2, 2), int(size))
            surface.blit(s_surf, (sx, sy))

        # Vignette / subtle top-bottom darkness
        vig = pygame.Surface((SCREEN_WIDTH, 40), pygame.SRCALPHA)
        vig.fill((0, 0, 0, 50))
        surface.blit(vig, (0, 0))
        surface.blit(vig, (0, SCREEN_HEIGHT - 40))

    def draw_effects(self, surface: pygame.Surface, pulse_center: Tuple[int, int]) -> None:
        for pulse in self.pulses:
            pulse.draw(surface, pulse_center)
        for p in self.particles:
            p.draw(surface)
