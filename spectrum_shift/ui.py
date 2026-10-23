"""User interface components, menus, in-game HUD, layer stack indicators, and overlay screens."""

import math
import pygame
from typing import List, Tuple, Optional, Callable, Dict
try:
    from .settings import (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        COLOR_BG,
        COLOR_BG_ALT,
        COLOR_BORDER,
        COLOR_TEXT_WHITE,
        COLOR_TEXT_MUTED,
        COLOR_TEXT_DIM,
        COLOR_TEXT_ACCENT,
        COLOR_BUTTON_BG,
        COLOR_BUTTON_HOVER,
        COLOR_BUTTON_BORDER,
        COLOR_RED,
        COLOR_BLUE,
        COLOR_YELLOW,
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        LAYER_NAMES,
        LAYER_SYMBOLS,
        LAYER_COLORS,
        STATE_MENU,
        STATE_HOW_TO_PLAY,
        STATE_LEVEL_SELECT,
        STATE_PLAYING,
        STATE_PAUSED,
        STATE_VICTORY,
        STATE_CAMPAIGN_WIN,
    )
    from .world_layers import WorldLayers
    from .levels import ALL_LEVEL_GETTERS
except ImportError:
    from settings import (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        COLOR_BG,
        COLOR_BG_ALT,
        COLOR_BORDER,
        COLOR_TEXT_WHITE,
        COLOR_TEXT_MUTED,
        COLOR_TEXT_DIM,
        COLOR_TEXT_ACCENT,
        COLOR_BUTTON_BG,
        COLOR_BUTTON_HOVER,
        COLOR_BUTTON_BORDER,
        COLOR_RED,
        COLOR_BLUE,
        COLOR_YELLOW,
        LAYER_RED,
        LAYER_BLUE,
        LAYER_YELLOW,
        LAYER_NAMES,
        LAYER_SYMBOLS,
        LAYER_COLORS,
        STATE_MENU,
        STATE_HOW_TO_PLAY,
        STATE_LEVEL_SELECT,
        STATE_PLAYING,
        STATE_PAUSED,
        STATE_VICTORY,
        STATE_CAMPAIGN_WIN,
    )
    from world_layers import WorldLayers
    from levels import ALL_LEVEL_GETTERS


def draw_text_with_shadow(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    pos: Tuple[int, int],
    color: Tuple[int, int, int] = COLOR_TEXT_WHITE,
    shadow_color: Tuple[int, int, int] = (0, 0, 0),
    offset: Tuple[int, int] = (2, 2),
) -> Tuple[int, int]:
    """Draw crisp text with a high-contrast drop shadow for maximum readability."""
    sh = font.render(text, True, shadow_color)
    surface.blit(sh, (pos[0] + offset[0], pos[1] + offset[1]))
    tx = font.render(text, True, color)
    surface.blit(tx, pos)
    return tx.get_size()


class Button:
    """Polished geometric UI button supporting hover states, icons, and click handling."""

    def __init__(
        self,
        rect: pygame.Rect,
        text: str,
        callback: Callable[[], None],
        color_accent: Optional[Tuple[int, int, int]] = None,
        font_size: int = 20,
    ):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.color_accent = color_accent or (0, 230, 255)
        self.font_size = font_size
        self.is_hovered = False

    def handle_event(self, event: pygame.event.Event, mouse_pos: Tuple[int, int]) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(mouse_pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(mouse_pos):
                self.callback()
                return True
        return False

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        bg_col = COLOR_BUTTON_HOVER if self.is_hovered else COLOR_BUTTON_BG
        border_col = self.color_accent if self.is_hovered else COLOR_BUTTON_BORDER

        # Button card
        pygame.draw.rect(surface, bg_col, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_col, self.rect, width=2 if self.is_hovered else 1, border_radius=6)

        # Glow line if hovered
        if self.is_hovered:
            glow_surf = pygame.Surface((self.rect.width + 6, self.rect.height + 6), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*self.color_accent, 50), glow_surf.get_rect(), border_radius=8)
            surface.blit(glow_surf, (self.rect.x - 3, self.rect.y - 3))

        # Text with shadow
        txt_col = COLOR_TEXT_WHITE if self.is_hovered else (225, 235, 250)
        txt_surf = font.render(self.text, True, txt_col)
        tx = self.rect.centerx - txt_surf.get_width() // 2
        ty = self.rect.centery - txt_surf.get_height() // 2
        draw_text_with_shadow(surface, font, self.text, (tx, ty), txt_col, offset=(1, 1))


class LayerPreviewWidget:
    """Animated mini-preview on the title screen demonstrating the 3-layer rotation twist."""

    def __init__(self, cx: int, cy: int):
        self.cx = cx
        self.cy = cy
        self.cycle = [LAYER_RED, LAYER_BLUE, LAYER_YELLOW]
        self.timer = 0.0
        self.cycle_interval = 1.4

    def update(self, dt: float) -> None:
        self.timer += dt
        if self.timer >= self.cycle_interval:
            self.timer = 0.0
            # Rotate preview cycle forward
            self.cycle = self.cycle[1:] + self.cycle[:1]

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        # Draw 3 miniature stacked platforms sliding in pseudo-3D
        preview_box = pygame.Rect(self.cx - 180, self.cy - 50, 360, 100)
        pygame.draw.rect(surface, (15, 20, 32), preview_box, border_radius=8)
        pygame.draw.rect(surface, (50, 70, 95), preview_box, width=1, border_radius=8)

        # Label with shadow
        lbl_text = "LAYER ROTATION STACK PREVIEW"
        lbl_sz = font.size(lbl_text)
        draw_text_with_shadow(
            surface,
            font,
            lbl_text,
            (self.cx - lbl_sz[0] // 2, self.cy - 44),
            COLOR_TEXT_MUTED,
            offset=(1, 1),
        )

        # Render 3 depth cards
        for depth_idx, layer_name in enumerate(reversed(self.cycle)):
            layer_info = LAYER_COLORS[layer_name]
            sym = LAYER_SYMBOLS[layer_name]
            name = LAYER_NAMES[layer_name]

            if depth_idx == 2:  # Foreground
                card_w, card_h = 130, 36
                px = self.cx - card_w // 2
                py = self.cy + 6
                # Glow
                glow_s = pygame.Surface((card_w + 10, card_h + 10), pygame.SRCALPHA)
                pygame.draw.rect(glow_s, (*layer_info["glow"], 60), glow_s.get_rect(), border_radius=6)
                surface.blit(glow_s, (px - 5, py - 5))

                pygame.draw.rect(surface, layer_info["dark"], (px, py, card_w, card_h), border_radius=5)
                pygame.draw.rect(surface, layer_info["bright"], (px, py, card_w, card_h), width=2, border_radius=5)

                txt_str = f"{sym} {name} (SOLID)"
                txt_sz = font.size(txt_str)
                draw_text_with_shadow(
                    surface,
                    font,
                    txt_str,
                    (px + card_w // 2 - txt_sz[0] // 2, py + card_h // 2 - txt_sz[1] // 2),
                    COLOR_TEXT_WHITE,
                    offset=(1, 1),
                )

            elif depth_idx == 1:  # Middle
                card_w, card_h = 105, 28
                px = self.cx - card_w // 2 - 95
                py = self.cy + 10
                c_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(c_surf, (*layer_info["dark"], 140), c_surf.get_rect(), border_radius=4)
                pygame.draw.rect(c_surf, (*layer_info["bright"], 180), c_surf.get_rect(), width=1, border_radius=4)
                surface.blit(c_surf, (px, py))
                txt_str = f"{sym} {layer_name.upper()}"
                txt_sz = font.size(txt_str)
                draw_text_with_shadow(
                    surface,
                    font,
                    txt_str,
                    (px + card_w // 2 - txt_sz[0] // 2, py + card_h // 2 - txt_sz[1] // 2),
                    (220, 230, 245),
                    offset=(1, 1),
                )

            else:  # Background
                card_w, card_h = 105, 28
                px = self.cx - card_w // 2 + 95
                py = self.cy + 10
                c_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
                pygame.draw.rect(c_surf, (*layer_info["dark"], 80), c_surf.get_rect(), border_radius=4)
                pygame.draw.rect(c_surf, (*layer_info["bright"], 100), c_surf.get_rect(), width=1, border_radius=4)
                surface.blit(c_surf, (px, py))
                txt_str = f"{sym} {layer_name.upper()}"
                txt_sz = font.size(txt_str)
                draw_text_with_shadow(
                    surface,
                    font,
                    txt_str,
                    (px + card_w // 2 - txt_sz[0] // 2, py + card_h // 2 - txt_sz[1] // 2),
                    (170, 185, 205),
                    offset=(1, 1),
                )


class UIManager:
    """Manages start menu, level select, HUD, pause screen, and victory overlays."""

    def __init__(self, sound_manager):
        self.sound = sound_manager
        self._init_fonts()

        self.preview_widget = LayerPreviewWidget(SCREEN_WIDTH // 2, 285)

        # On-screen HUD buttons for mouse/touch
        self.hud_btn_rotate_bwd = Button(
            pygame.Rect(20, SCREEN_HEIGHT - 60, 120, 44),
            "◄ [Q] ROTATE",
            lambda: None,
            color_accent=COLOR_BLUE,
            font_size=16,
        )
        self.hud_btn_dash = Button(
            pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 60, 150, 44),
            "[SHIFT] DASH",
            lambda: None,
            color_accent=(0, 235, 255),
            font_size=16,
        )
        self.hud_btn_rotate_fwd = Button(
            pygame.Rect(SCREEN_WIDTH - 140, SCREEN_HEIGHT - 60, 120, 44),
            "[E] ROTATE ►",
            lambda: None,
            color_accent=COLOR_BLUE,
            font_size=16,
        )
        self.hud_btn_restart = Button(
            pygame.Rect(SCREEN_WIDTH - 165, 14, 75, 32),
            "R: RESET",
            lambda: None,
            color_accent=(255, 90, 90),
            font_size=14,
        )
        self.hud_btn_pause = Button(
            pygame.Rect(SCREEN_WIDTH - 80, 14, 65, 32),
            "PAUSE",
            lambda: None,
            color_accent=COLOR_BLUE,
            font_size=14,
        )

    def _init_fonts(self) -> None:
        pygame.font.init()
        # Clean modern system fonts with fallbacks (larger for crisp visibility)
        self.font_title = pygame.font.SysFont(["consolas", "segoeui", "arial"], 46, bold=True)
        self.font_subtitle = pygame.font.SysFont(["consolas", "segoeui", "arial"], 19, bold=True)
        self.font_large = pygame.font.SysFont(["consolas", "segoeui", "arial"], 32, bold=True)
        self.font_hud = pygame.font.SysFont(["consolas", "segoeui", "arial"], 17, bold=True)
        self.font_body = pygame.font.SysFont(["consolas", "segoeui", "arial"], 16, bold=True)
        self.font_small = pygame.font.SysFont(["consolas", "segoeui", "arial"], 13, bold=True)

    def draw_hud(
        self,
        surface: pygame.Surface,
        world_layers: WorldLayers,
        level_id: int,
        level_title: str,
        level_time: float,
        rotations: int,
        mouse_pos: Tuple[int, int],
        player_keys: int = 0,
        has_dash: bool = True,
    ) -> None:
        """Render high-contrast in-game HUD with layer stack indicators, timers, key count, and controls."""
        # Top HUD bar background (rich dark contrast bar)
        bar_surf = pygame.Surface((SCREEN_WIDTH, 58), pygame.SRCALPHA)
        bar_surf.fill((8, 12, 20, 235))
        surface.blit(bar_surf, (0, 0))
        pygame.draw.line(surface, (0, 200, 240), (0, 58), (SCREEN_WIDTH, 58), width=2)

        # 1. Level Info (Top-Left) with Drop Shadow
        draw_text_with_shadow(
            surface,
            self.font_hud,
            f"LEVEL {level_id}: {level_title}",
            (20, 10),
            COLOR_TEXT_WHITE,
            offset=(2, 2),
        )
        draw_text_with_shadow(
            surface,
            self.font_small,
            "A/D: Move | SPACE: Jump | SHIFT: Dash | Q/E: Rotate",
            (20, 34),
            COLOR_TEXT_MUTED,
            offset=(1, 1),
        )

        # 2. Central Layer Stack Cyclic Display
        cx = SCREEN_WIDTH // 2
        fg_name = world_layers.foreground
        next_name = world_layers.next_layer
        prev_name = world_layers.prev_layer

        fg_col = LAYER_COLORS[fg_name]["bright"]
        next_col = LAYER_COLORS[next_name]["bright"]
        prev_col = LAYER_COLORS[prev_name]["bright"]

        fg_sym = LAYER_SYMBOLS[fg_name]
        next_sym = LAYER_SYMBOLS[next_name]
        prev_sym = LAYER_SYMBOLS[prev_name]

        # [Q] Prev Box
        prev_rect = pygame.Rect(cx - 215, 12, 95, 34)
        pygame.draw.rect(surface, (18, 24, 38), prev_rect, border_radius=5)
        pygame.draw.rect(surface, prev_col, prev_rect, width=1, border_radius=5)
        p_str = f"[Q] {prev_sym} {prev_name[:3].upper()}"
        p_sz = self.font_small.size(p_str)
        draw_text_with_shadow(
            surface,
            self.font_small,
            p_str,
            (prev_rect.centerx - p_sz[0] // 2, prev_rect.centery - p_sz[1] // 2),
            prev_col,
            offset=(1, 1),
        )

        # Arrow indicator
        draw_text_with_shadow(surface, self.font_hud, "◄", (cx - 114, 18), COLOR_TEXT_MUTED, offset=(1, 1))

        # Active Foreground Box (Prominent & Glowing)
        fg_rect = pygame.Rect(cx - 96, 7, 192, 44)
        fg_glow = pygame.Surface((202, 54), pygame.SRCALPHA)
        pygame.draw.rect(fg_glow, (*LAYER_COLORS[fg_name]["glow"], 70), fg_glow.get_rect(), border_radius=7)
        surface.blit(fg_glow, (cx - 101, 2))

        pygame.draw.rect(surface, LAYER_COLORS[fg_name]["dark"], fg_rect, border_radius=6)
        pygame.draw.rect(surface, fg_col, fg_rect, width=2, border_radius=6)
        f_str = f"SOLID: {fg_sym} {fg_name.upper()}"
        f_sz = self.font_hud.size(f_str)
        draw_text_with_shadow(
            surface,
            self.font_hud,
            f_str,
            (fg_rect.centerx - f_sz[0] // 2, fg_rect.centery - f_sz[1] // 2),
            (255, 255, 255),
            offset=(2, 2),
        )

        # Arrow indicator
        draw_text_with_shadow(surface, self.font_hud, "►", (cx + 102, 18), COLOR_TEXT_MUTED, offset=(1, 1))

        # [E] Next Box
        next_rect = pygame.Rect(cx + 120, 12, 95, 34)
        pygame.draw.rect(surface, (18, 24, 38), next_rect, border_radius=5)
        pygame.draw.rect(surface, next_col, next_rect, width=1, border_radius=5)
        n_str = f"[E] {next_sym} {next_name[:3].upper()}"
        n_sz = self.font_small.size(n_str)
        draw_text_with_shadow(
            surface,
            self.font_small,
            n_str,
            (next_rect.centerx - n_sz[0] // 2, next_rect.centery - n_sz[1] // 2),
            next_col,
            offset=(1, 1),
        )

        # 3. Keys & Dash Status Badges
        badge_x = cx + 225
        if player_keys > 0:
            key_pill = pygame.Rect(badge_x, 14, 90, 30)
            pygame.draw.rect(surface, (25, 35, 20), key_pill, border_radius=5)
            pygame.draw.rect(surface, (255, 220, 30), key_pill, width=2, border_radius=5)
            draw_text_with_shadow(surface, self.font_small, f"KEY: {player_keys}", (badge_x + 12, 20), (255, 235, 70))
            badge_x += 98

        dash_pill = pygame.Rect(badge_x, 14, 85, 30)
        dash_bg = (15, 32, 45) if has_dash else (20, 24, 30)
        dash_col = (0, 230, 255) if has_dash else (120, 130, 145)
        pygame.draw.rect(surface, dash_bg, dash_pill, border_radius=5)
        pygame.draw.rect(surface, dash_col, dash_pill, width=1, border_radius=5)
        d_lbl = "DASH: OK" if has_dash else "DASH: .."
        draw_text_with_shadow(surface, self.font_small, d_lbl, (badge_x + 8, 20), dash_col)

        # 4. Timer & Controls Buttons (Top-Right)
        time_str = f"{level_time:04.1f}s"
        draw_text_with_shadow(
            surface,
            self.font_hud,
            time_str,
            (SCREEN_WIDTH - 240, 20),
            (255, 255, 255),
            offset=(2, 2),
        )

        self.hud_btn_restart.draw(surface, self.font_small)
        self.hud_btn_pause.draw(surface, self.font_small)

        # On-screen touch/mouse rotation & dash pills at bottom
        self.hud_btn_rotate_bwd.draw(surface, self.font_body)
        self.hud_btn_dash.draw(surface, self.font_body)
        self.hud_btn_rotate_fwd.draw(surface, self.font_body)

    def draw_start_menu(
        self,
        surface: pygame.Surface,
        buttons: List[Button],
        mouse_pos: Tuple[int, int],
        dt: float,
    ) -> None:
        """Render Title Screen with required one-sentence explanation and animated preview."""
        surface.fill(COLOR_BG)
        cx = SCREEN_WIDTH // 2

        # Main Title Neon Text with Heavy Drop Shadow
        draw_text_with_shadow(
            surface,
            self.font_title,
            "SPECTRUM SHIFT",
            (cx - self.font_title.size("SPECTRUM SHIFT")[0] // 2, 38),
            (255, 255, 255),
            shadow_color=(0, 180, 240),
            offset=(3, 3),
        )

        # Subtitle
        sub_str = "CYCLIC MULTI-LAYER PLATFORM PUZZLE"
        draw_text_with_shadow(
            surface,
            self.font_subtitle,
            sub_str,
            (cx - self.font_subtitle.size(sub_str)[0] // 2, 92),
            (0, 225, 255),
            offset=(2, 2),
        )

        # High-Contrast Twist Explanation Box
        expl_rect = pygame.Rect(cx - 390, 125, 780, 72)
        pygame.draw.rect(surface, (12, 17, 28), expl_rect, border_radius=8)
        pygame.draw.rect(surface, (0, 200, 245), expl_rect, width=2, border_radius=8)

        line1 = '"All three color worlds exist together.'
        line2 = 'Rotate their layers to bring the platforms you need into the foreground."'
        sz1 = self.font_hud.size(line1)
        sz2 = self.font_hud.size(line2)

        draw_text_with_shadow(surface, self.font_hud, line1, (cx - sz1[0] // 2, 134), (255, 255, 255), offset=(2, 2))
        draw_text_with_shadow(surface, self.font_hud, line2, (cx - sz2[0] // 2, 160), (255, 220, 50), offset=(2, 2))

        # Animated 3-Layer Preview Widget
        self.preview_widget.update(dt)
        self.preview_widget.draw(surface, self.font_body)

        # Menu Buttons
        for btn in buttons:
            btn.draw(surface, self.font_hud)

    def draw_how_to_play(self, surface: pygame.Surface, btn_back: Button, mouse_pos: Tuple[int, int]) -> None:
        """Render How to Play and Controls guide with high visibility."""
        surface.fill(COLOR_BG)
        cx = SCREEN_WIDTH // 2

        # Header
        hdr_str = "HOW TO PLAY & CONTROLS"
        draw_text_with_shadow(
            surface,
            self.font_title,
            hdr_str,
            (cx - self.font_title.size(hdr_str)[0] // 2, 25),
            (255, 255, 255),
            shadow_color=(0, 160, 220),
            offset=(2, 2),
        )

        # Cards container
        c_rect = pygame.Rect(cx - 380, 85, 760, 385)
        pygame.draw.rect(surface, (14, 19, 32), c_rect, border_radius=8)
        pygame.draw.rect(surface, (60, 85, 125), c_rect, width=2, border_radius=8)

        lines = [
            ("THE CORE MECHANIC:", (0, 225, 255), True),
            ("• The Red, Blue, and Yellow worlds exist simultaneously in 3 layers.", (255, 255, 255), False),
            ("• ONLY the FOREGROUND layer is physically solid to walk and jump on.", (255, 220, 40), False),
            ("• Rotating shifts layers deterministically: Red -> Blue -> Yellow -> Red.", (255, 255, 255), False),
            ("• If you are standing on a platform that becomes inactive, you fall naturally!", (255, 90, 110), False),
            ("", (255, 255, 255), False),
            ("CONTROLS & UNIQUE ABILITIES:", (0, 225, 255), True),
            ("• A / D or ARROW KEYS: Move left and right", (255, 255, 255), False),
            ("• SPACEBAR: Jump (hold longer for maximum height)", (255, 255, 255), False),
            ("• SHIFT or J: CHROMA PHASE DASH (high-speed burst across gaps, recharges on ground)", (0, 235, 255), False),
            ("• E / Q: Rotate layer stack FORWARD (Next) or BACKWARD (Previous)", (255, 220, 40), False),
            ("• R: Restart level instantly  |  ESC: Pause game", (255, 255, 255), False),
            ("", (255, 255, 255), False),
            ("MECHANISMS & PUZZLES:", (0, 225, 255), True),
            ("• SPINNING WHEELS (Rotors): Ride active color arms to leap across huge chasms.", (255, 255, 255), False),
            ("• ACCELERATOR GATES: Match active color to boost through spinning rings.", (255, 255, 255), False),
            ("• KEYS & LOCKS: Retrieve floating Prism Keys to dissolve laser barriers blocking the exit.", (255, 215, 60), False),
        ]

        y_offset = 96
        for text, color, is_header in lines:
            if not text:
                y_offset += 4
                continue
            font_to_use = self.font_hud if is_header else self.font_small
            draw_text_with_shadow(surface, font_to_use, text, (cx - 355, y_offset), color, offset=(1, 1))
            y_offset += 20 if not is_header else 24

        btn_back.draw(surface, self.font_hud)

    def draw_level_select(
        self,
        surface: pygame.Surface,
        level_buttons: List[Button],
        btn_back: Button,
        best_times: Dict[int, float],
        mouse_pos: Tuple[int, int],
    ) -> None:
        """Render Level Selection Screen with high visibility cards for all 5 levels."""
        surface.fill(COLOR_BG)
        cx = SCREEN_WIDTH // 2

        hdr_str = "SELECT LEVEL"
        draw_text_with_shadow(
            surface,
            self.font_large,
            hdr_str,
            (cx - self.font_large.size(hdr_str)[0] // 2, 22),
            (255, 255, 255),
            shadow_color=(0, 160, 220),
            offset=(2, 2),
        )

        sub_str = "Choose a handcrafted puzzle challenge to test your rotation mastery:"
        draw_text_with_shadow(
            surface,
            self.font_small,
            sub_str,
            (cx - self.font_small.size(sub_str)[0] // 2, 64),
            COLOR_TEXT_MUTED,
            offset=(1, 1),
        )

        # Level cards info (5 Handcrafted Levels)
        descriptions = [
            ("LEVEL 1: FIRST ROTATION", "Learn the cyclic rotation mechanic. Red -> Blue -> Yellow.", (255, 45, 85), "TUTORIAL"),
            ("LEVEL 2: COLOR SEQUENCE", "Plan sequences and use backward rotation (Q) to reach high ledges.", (0, 210, 255), "SEQUENCE"),
            ("LEVEL 3: THE IMPOSSIBLE BRIDGE", "Cross the abyss & retrieve the Prism Key to unlock the laser barrier.", (255, 210, 30), "KEY & LOCK"),
            ("LEVEL 4: THE PRISM ROTOR", "Ride the revolving color carousel & surge through the spinning gate.", (0, 235, 215), "ROTORS"),
            ("LEVEL 5: THE GRAND MECHANISM", "Master spinning wheels, accelerator rings, and final lock barrier.", (255, 80, 140), "ULTIMATE"),
        ]

        for i, (title, desc, col, badge) in enumerate(descriptions, start=1):
            cy = 98 + (i - 1) * 68
            card = pygame.Rect(cx - 380, cy, 760, 60)
            pygame.draw.rect(surface, (16, 22, 35), card, border_radius=6)
            pygame.draw.rect(surface, (55, 75, 110), card, width=1, border_radius=6)

            # Left color bar
            pygame.draw.rect(surface, col, (cx - 380, cy, 8, 60), border_top_left_radius=6, border_bottom_left_radius=6)

            # Badge pill
            b_pill = pygame.Rect(cx - 362, cy + 8, 85, 20)
            pygame.draw.rect(surface, (*col, 40), b_pill, border_radius=4)
            pygame.draw.rect(surface, col, b_pill, width=1, border_radius=4)
            b_sz = self.font_small.size(badge)
            draw_text_with_shadow(surface, self.font_small, badge, (b_pill.centerx - b_sz[0] // 2, b_pill.centery - b_sz[1] // 2), col)

            draw_text_with_shadow(surface, self.font_hud, title, (cx - 265, cy + 9), (255, 255, 255), offset=(1, 1))
            draw_text_with_shadow(surface, self.font_small, desc, (cx - 362, cy + 34), COLOR_TEXT_MUTED, offset=(1, 1))

            best = best_times.get(i)
            b_txt = f"BEST: {best:.1f}s" if best is not None else "UNCOMPLETED"
            b_col = (0, 235, 170) if best is not None else (140, 155, 180)
            draw_text_with_shadow(surface, self.font_small, b_txt, (cx + 130, cy + 20), b_col, offset=(1, 1))

        for btn in level_buttons:
            btn.draw(surface, self.font_hud)

        btn_back.draw(surface, self.font_hud)

    def draw_pause_menu(self, surface: pygame.Surface, buttons: List[Button], mouse_pos: Tuple[int, int]) -> None:
        """Render high-contrast pause overlay modal."""
        dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((6, 9, 15, 225))
        surface.blit(dark_overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        modal_rect = pygame.Rect(cx - 190, cy - 165, 380, 330)
        pygame.draw.rect(surface, (16, 22, 36), modal_rect, border_radius=10)
        pygame.draw.rect(surface, (0, 200, 245), modal_rect, width=2, border_radius=10)

        title_str = "GAME PAUSED"
        sz = self.font_large.size(title_str)
        draw_text_with_shadow(
            surface,
            self.font_large,
            title_str,
            (cx - sz[0] // 2, cy - 135),
            (255, 255, 255),
            shadow_color=(0, 140, 200),
            offset=(2, 2),
        )

        for btn in buttons:
            btn.draw(surface, self.font_hud)

    def draw_victory_overlay(
        self,
        surface: pygame.Surface,
        level_num: int,
        level_title: str,
        time_taken: float,
        rotations: int,
        buttons: List[Button],
        mouse_pos: Tuple[int, int],
    ) -> None:
        """Render level completed victory modal with clear statistics."""
        dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((6, 10, 16, 225))
        surface.blit(dark_overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        modal = pygame.Rect(cx - 230, cy - 175, 460, 350)
        pygame.draw.rect(surface, (16, 22, 36), modal, border_radius=10)
        pygame.draw.rect(surface, (100, 255, 218), modal, width=2, border_radius=10)

        # Title
        vic_title = "PORTAL REACHED!"
        sz1 = self.font_large.size(vic_title)
        draw_text_with_shadow(
            surface,
            self.font_large,
            vic_title,
            (cx - sz1[0] // 2, cy - 145),
            (100, 255, 218),
            shadow_color=(0, 140, 100),
            offset=(2, 2),
        )

        sub_str = f"LEVEL {level_num}: {level_title} COMPLETE"
        sz2 = self.font_hud.size(sub_str)
        draw_text_with_shadow(surface, self.font_hud, sub_str, (cx - sz2[0] // 2, cy - 105), (255, 255, 255), offset=(2, 2))

        # Stats box
        stat_box = pygame.Rect(cx - 170, cy - 65, 340, 68)
        pygame.draw.rect(surface, (12, 16, 26), stat_box, border_radius=6)
        pygame.draw.rect(surface, (50, 70, 95), stat_box, width=1, border_radius=6)

        t_txt = f"Clear Time: {time_taken:.2f} seconds"
        t_sz = self.font_body.size(t_txt)
        draw_text_with_shadow(surface, self.font_body, t_txt, (stat_box.centerx - t_sz[0] // 2, stat_box.y + 12), (255, 255, 255), offset=(1, 1))

        r_txt = f"World Rotations: {rotations}"
        r_sz = self.font_body.size(r_txt)
        draw_text_with_shadow(surface, self.font_body, r_txt, (stat_box.centerx - r_sz[0] // 2, stat_box.y + 36), (0, 230, 255), offset=(1, 1))

        for btn in buttons:
            btn.draw(surface, self.font_hud)

    def draw_campaign_win_overlay(
        self,
        surface: pygame.Surface,
        buttons: List[Button],
        mouse_pos: Tuple[int, int],
    ) -> None:
        """Render final campaign victory celebration modal with high contrast."""
        dark_overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        dark_overlay.fill((5, 7, 12, 235))
        surface.blit(dark_overlay, (0, 0))

        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        modal = pygame.Rect(cx - 250, cy - 170, 500, 340)
        pygame.draw.rect(surface, (16, 22, 36), modal, border_radius=10)
        pygame.draw.rect(surface, (255, 215, 0), modal, width=2, border_radius=10)

        vic_title = "SPECTRUM CONQUERED!"
        sz1 = self.font_large.size(vic_title)
        draw_text_with_shadow(
            surface,
            self.font_large,
            vic_title,
            (cx - sz1[0] // 2, cy - 140),
            (255, 220, 50),
            shadow_color=(150, 110, 10),
            offset=(2, 2),
        )

        sub_str = "You have mastered all three color dimensions!"
        sz2 = self.font_hud.size(sub_str)
        draw_text_with_shadow(surface, self.font_hud, sub_str, (cx - sz2[0] // 2, cy - 95), (255, 255, 255), offset=(2, 2))

        desc_str = "Every impossible chasm, spinning rotor, and laser barrier solved."
        sz3 = self.font_small.size(desc_str)
        draw_text_with_shadow(surface, self.font_small, desc_str, (cx - sz3[0] // 2, cy - 55), COLOR_TEXT_MUTED, offset=(1, 1))

        for btn in buttons:
            btn.draw(surface, self.font_hud)
