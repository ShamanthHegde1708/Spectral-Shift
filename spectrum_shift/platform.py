"""Platform geometry, collision bounds, and neon sci-fi rendering."""

import pygame
from typing import Tuple
try:
    from .settings import (
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        LAYER_COLORS,
        LAYER_SYMBOLS,
        DEPTH_ALPHA,
        DEPTH_Y_OFFSET,
        DEPTH_SCALE,
    )
except ImportError:
    from settings import (
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        LAYER_COLORS,
        LAYER_SYMBOLS,
        DEPTH_ALPHA,
        DEPTH_Y_OFFSET,
        DEPTH_SCALE,
    )


class Platform:
    """A geometric platform belonging to one of the three color worlds."""

    def __init__(self, x: int, y: int, width: int, height: int, layer: str):
        self.rect = pygame.Rect(x, y, width, height)
        self.layer = layer
        self.color_data = LAYER_COLORS.get(layer, LAYER_COLORS[LAYER_RED])
        self.symbol = LAYER_SYMBOLS.get(layer, "•")

        # Pre-calculated accessibility pattern spacing
        self.stripe_spacing = 16

    @property
    def x(self) -> int:
        return self.rect.x

    @property
    def y(self) -> int:
        return self.rect.y

    @property
    def width(self) -> int:
        return self.rect.width

    @property
    def height(self) -> int:
        return self.rect.height

    def draw(self, surface: pygame.Surface, visual_depth: float) -> None:
        """Render platform with visual depth effects, transparency, and accessibility patterns.
        
        visual_depth ranges from 0.0 (solid foreground) to 2.0 (faint background).
        Physical collision bounds are completely unaffected by this visual rendering.
        """
        # Interpolate alpha based on continuous depth
        # Depth 0.0 -> alpha ~255
        # Depth 1.0 -> alpha ~125
        # Depth 2.0 -> alpha ~55
        if visual_depth <= 1.0:
            alpha = int(DEPTH_ALPHA[0] - visual_depth * (DEPTH_ALPHA[0] - DEPTH_ALPHA[1]))
            y_offset = visual_depth * DEPTH_Y_OFFSET[1]
        else:
            t = visual_depth - 1.0
            alpha = int(DEPTH_ALPHA[1] - t * (DEPTH_ALPHA[1] - DEPTH_ALPHA[2]))
            y_offset = DEPTH_Y_OFFSET[1] + t * (DEPTH_Y_OFFSET[2] - DEPTH_Y_OFFSET[1])

        alpha = max(35, min(255, alpha))

        # Visual bounding box with depth displacement
        draw_rect = pygame.Rect(
            self.rect.x,
            int(self.rect.y + y_offset),
            self.rect.width,
            self.rect.height,
        )

        is_foreground = (visual_depth < 0.25)
        is_middle = (0.25 <= visual_depth < 1.4)

        if is_foreground:
            # Full solid render with glow and crisp details
            # 1. Subtle Outer Glow
            glow_surf = pygame.Surface((draw_rect.width + 12, draw_rect.height + 12), pygame.SRCALPHA)
            glow_color = (*self.color_data["glow"], 45)
            pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=6)
            surface.blit(glow_surf, (draw_rect.x - 6, draw_rect.y - 6))

            # 2. Main Platform Body
            pygame.draw.rect(surface, self.color_data["dark"], draw_rect, border_radius=4)

            # 3. Accessibility Pattern
            self._draw_pattern(surface, draw_rect, self.color_data["pattern"], alpha=140)

            # 4. Neon Outer Border
            pygame.draw.rect(surface, self.color_data["core"], draw_rect, width=2, border_radius=4)

            # 5. Bright Top Highlight (Ledge indicator with animated pulse)
            pygame.draw.line(
                surface,
                self.color_data["bright"],
                (draw_rect.left + 2, draw_rect.top),
                (draw_rect.right - 2, draw_rect.top),
                width=3,
            )
            # Energy flow pulse along ledge
            if draw_rect.width > 30:
                pulse_offset = int((pygame.time.get_ticks() * 0.08) % (draw_rect.width - 15))
                pygame.draw.line(
                    surface,
                    (255, 255, 255),
                    (draw_rect.left + pulse_offset, draw_rect.top),
                    (draw_rect.left + pulse_offset + 12, draw_rect.top),
                    width=3,
                )

            # 6. High-tech Corner Brackets
            c_len = min(6, draw_rect.height // 2)
            pygame.draw.line(surface, (255, 255, 255), (draw_rect.left, draw_rect.top), (draw_rect.left + c_len, draw_rect.top), width=2)
            pygame.draw.line(surface, (255, 255, 255), (draw_rect.left, draw_rect.top), (draw_rect.left, draw_rect.top + c_len), width=2)
            pygame.draw.line(surface, (255, 255, 255), (draw_rect.right - c_len, draw_rect.top), (draw_rect.right, draw_rect.top), width=2)
            pygame.draw.line(surface, (255, 255, 255), (draw_rect.right, draw_rect.top), (draw_rect.right, draw_rect.top + c_len), width=2)

            # 7. Accessibility Symbol Stamp
            self._draw_symbol(surface, draw_rect, self.color_data["bright"], alpha=220)

        else:
            # Middle or Background Layer (Translucent ghost platform)
            plat_surf = pygame.Surface((draw_rect.width, draw_rect.height), pygame.SRCALPHA)
            
            # Fill
            fill_color = (*self.color_data["dark"], int(alpha * 0.45))
            plat_surf.fill(fill_color)

            # Pattern on transparent surface
            self._draw_pattern(plat_surf, plat_surf.get_rect(), self.color_data["pattern"], alpha=int(alpha * 0.5))

            # Border
            border_color = (*self.color_data["core"], alpha)
            pygame.draw.rect(plat_surf, border_color, plat_surf.get_rect(), width=1 if visual_depth >= 1.4 else 2, border_radius=4)

            # Accessibility symbol on ghost platform
            self._draw_symbol(plat_surf, plat_surf.get_rect(), self.color_data["bright"], alpha=int(alpha * 0.75))

            surface.blit(plat_surf, (draw_rect.x, draw_rect.y))

    def _draw_pattern(self, surface: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int], alpha: int = 120) -> None:
        """Draw unique accessibility texture per layer:
        - Red: Diagonal hazard stripes
        - Blue: Tech grid & horizontal slots
        - Yellow: Circuit dots / circles
        """
        line_color = (*color, alpha) if len(color) == 3 else color
        # Red: Diagonal stripes
        if self.layer == LAYER_RED:
            for x_offset in range(-rect.height, rect.width, 14):
                p1 = (rect.x + max(0, x_offset), rect.y + max(0, -x_offset))
                p2 = (rect.x + min(rect.width, x_offset + rect.height), rect.y + min(rect.height, rect.height + x_offset))
                if p1[0] < rect.right and p2[0] > rect.left:
                    # Clip to rect
                    pygame.draw.line(surface, line_color, p1, p2, width=1)

        # Blue: Horizontal tech grid
        elif self.layer == LAYER_BLUE:
            # Horizontal lines
            for y_off in range(4, rect.height - 2, 8):
                pygame.draw.line(surface, line_color, (rect.x + 4, rect.y + y_off), (rect.right - 4, rect.y + y_off), width=1)
            # Vertical tic marks
            for x_off in range(16, rect.width - 8, 20):
                pygame.draw.line(surface, line_color, (rect.x + x_off, rect.y + 4), (rect.x + x_off, rect.y + 8), width=1)

        # Yellow: Circuit dots
        elif self.layer == LAYER_YELLOW:
            for x_off in range(10, rect.width - 6, 16):
                for y_off in range(8, rect.height - 4, 12):
                    pygame.draw.circle(surface, line_color, (rect.x + x_off, rect.y + y_off), 2)

    def _draw_symbol(self, surface: pygame.Surface, rect: pygame.Rect, color: Tuple[int, int, int], alpha: int = 200) -> None:
        """Draw geometric symbol icon in center or left of platform for instant identification."""
        if rect.width < 24 or rect.height < 14:
            return

        cx = rect.x + 14
        cy = rect.y + rect.height // 2
        sym_color = (*color[:3], alpha) if len(color) == 3 else color

        if self.layer == LAYER_RED:
            # Triangle ▲
            pts = [(cx, cy - 4), (cx - 4, cy + 4), (cx + 4, cy + 4)]
            pygame.draw.polygon(surface, sym_color, pts)
        elif self.layer == LAYER_BLUE:
            # Square ■
            sq_rect = pygame.Rect(cx - 4, cy - 4, 8, 8)
            pygame.draw.rect(surface, sym_color, sq_rect)
        elif self.layer == LAYER_YELLOW:
            # Circle ●
            pygame.draw.circle(surface, sym_color, (cx, cy), 4)
