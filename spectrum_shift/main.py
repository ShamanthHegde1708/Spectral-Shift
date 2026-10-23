"""Main game loop, Pygbag asynchronous runner, resolution scaling, and state machine."""

import sys
import os
import asyncio
from pathlib import Path
from typing import Tuple, List, Optional
import pygame

# Ensure current package directory is in sys.path for both Pygbag and local launch
CURR_DIR = Path(__file__).resolve().parent
if str(CURR_DIR) not in sys.path:
    sys.path.insert(0, str(CURR_DIR))
ROOT_DIR = CURR_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from .settings import (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        FPS,
        TITLE,
        STATE_MENU,
        STATE_HOW_TO_PLAY,
        STATE_LEVEL_SELECT,
        STATE_PLAYING,
        STATE_PAUSED,
        STATE_VICTORY,
        STATE_CAMPAIGN_WIN,
        COLOR_BG,
        COLOR_BLUE,
        COLOR_RED,
        COLOR_YELLOW,
    )
    from .sound import SoundManager
    from .level_manager import LevelManager, InputAction
    from .ui import UIManager, Button
except ImportError:
    from settings import (
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        FPS,
        TITLE,
        STATE_MENU,
        STATE_HOW_TO_PLAY,
        STATE_LEVEL_SELECT,
        STATE_PLAYING,
        STATE_PAUSED,
        STATE_VICTORY,
        STATE_CAMPAIGN_WIN,
        COLOR_BG,
        COLOR_BLUE,
        COLOR_RED,
        COLOR_YELLOW,
    )
    from sound import SoundManager
    from level_manager import LevelManager, InputAction
    from ui import UIManager, Button


class Game:
    """Core game application with resolution scaling, state management, and input polling."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption(TITLE)

        # Logical rendering canvas (fixed 960x540)
        self.canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Real window display surface (resizable)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True

        # Scaled viewport tracking for letterboxing & mouse coordinate conversion
        self.viewport_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Core subsystems
        self.sound = SoundManager()
        self.level_mgr = LevelManager(self.sound)
        self.ui = UIManager(self.sound)

        # Application state
        self.app_state = STATE_MENU

        # One-shot input flags for the current frame
        self.rotate_fwd_pressed = False
        self.rotate_bwd_pressed = False
        self.jump_pressed = False
        self.dash_pressed = False
        self.restart_pressed = False

        self._build_ui_buttons()

    def _build_ui_buttons(self) -> None:
        """Construct interactive UI buttons for all menus."""
        cx = SCREEN_WIDTH // 2

        # 1. Main Menu Buttons
        btn_y = 390
        btn_w, btn_h = 160, 42
        self.menu_buttons = [
            Button(
                pygame.Rect(cx - 270, btn_y, btn_w, btn_h),
                "PLAY GAME",
                self._btn_play,
                color_accent=COLOR_BLUE,
            ),
            Button(
                pygame.Rect(cx - 90, btn_y, btn_w, btn_h),
                "LEVEL SELECT",
                self._btn_open_levels,
                color_accent=COLOR_YELLOW,
            ),
            Button(
                pygame.Rect(cx + 90, btn_y, btn_w, btn_h),
                "HOW TO PLAY",
                self._btn_open_how_to_play,
                color_accent=COLOR_RED,
            ),
            Button(
                pygame.Rect(cx - 90, btn_y + 54, btn_w, 36),
                "AUDIO: ON",
                self._btn_toggle_audio,
                color_accent=(140, 160, 190),
                font_size=15,
            ),
        ]

        # 2. Back buttons for sub-menus
        self.btn_back_to_menu = Button(
            pygame.Rect(cx - 75, SCREEN_HEIGHT - 60, 150, 38),
            "MAIN MENU",
            self._btn_to_main_menu,
            color_accent=COLOR_BLUE,
        )

        # 3. Level Select buttons (Levels 1 to 5)
        self.level_select_buttons = []
        level_colors = [COLOR_RED, COLOR_BLUE, COLOR_YELLOW, (0, 210, 255), (255, 60, 100)]
        for lvl_i in range(1, 6):
            cy = 105 + (lvl_i - 1) * 66
            btn = Button(
                pygame.Rect(cx + 255, cy + 12, 95, 36),
                f"PLAY L{lvl_i}",
                (lambda n=lvl_i: self._start_specific_level(n)),
                color_accent=level_colors[lvl_i - 1],
                font_size=14,
            )
            self.level_select_buttons.append(btn)

        # 4. Pause Menu buttons
        p_cy = SCREEN_HEIGHT // 2
        self.pause_buttons = [
            Button(
                pygame.Rect(cx - 130, p_cy - 70, 260, 40),
                "RESUME",
                self._btn_resume,
                color_accent=COLOR_BLUE,
            ),
            Button(
                pygame.Rect(cx - 130, p_cy - 20, 260, 40),
                "RESTART LEVEL",
                self._btn_restart_current,
                color_accent=COLOR_RED,
            ),
            Button(
                pygame.Rect(cx - 130, p_cy + 30, 260, 40),
                "LEVEL SELECT",
                self._btn_open_levels,
                color_accent=COLOR_YELLOW,
            ),
            Button(
                pygame.Rect(cx - 130, p_cy + 80, 260, 40),
                "MAIN MENU",
                self._btn_to_main_menu,
                color_accent=(150, 160, 180),
            ),
        ]

        # 5. Victory Screen buttons
        v_cy = SCREEN_HEIGHT // 2
        self.victory_buttons = [
            Button(
                pygame.Rect(cx - 180, v_cy + 25, 170, 44),
                "NEXT LEVEL ►",
                self._btn_next_level,
                color_accent=(100, 255, 218),
            ),
            Button(
                pygame.Rect(cx + 10, v_cy + 25, 170, 44),
                "REPLAY",
                self._btn_restart_current,
                color_accent=COLOR_BLUE,
            ),
            Button(
                pygame.Rect(cx - 85, v_cy + 85, 170, 36),
                "MAIN MENU",
                self._btn_to_main_menu,
                color_accent=COLOR_RED,
                font_size=15,
            ),
        ]

        # 6. Campaign Win buttons
        self.campaign_win_buttons = [
            Button(
                pygame.Rect(cx - 140, SCREEN_HEIGHT // 2 + 10, 280, 44),
                "PLAY AGAIN",
                lambda: self._start_specific_level(1),
                color_accent=(255, 215, 0),
            ),
            Button(
                pygame.Rect(cx - 140, SCREEN_HEIGHT // 2 + 65, 280, 40),
                "MAIN MENU",
                self._btn_to_main_menu,
                color_accent=COLOR_BLUE,
            ),
        ]

        # Hook in-game HUD button callbacks
        self.ui.hud_btn_rotate_bwd.callback = lambda: self._on_hud_rotate_bwd()
        self.ui.hud_btn_rotate_fwd.callback = lambda: self._on_hud_rotate_fwd()
        self.ui.hud_btn_dash.callback = lambda: self._on_hud_dash()
        self.ui.hud_btn_restart.callback = lambda: self._btn_restart_current()
        self.ui.hud_btn_pause.callback = lambda: self._btn_toggle_pause()

    def _on_hud_dash(self) -> None:
        self.dash_pressed = True

    def _on_hud_rotate_bwd(self) -> None:
        self.rotate_bwd_pressed = True

    def _on_hud_rotate_fwd(self) -> None:
        self.rotate_fwd_pressed = True

    def _btn_play(self) -> None:
        self.sound.play("click")
        self.level_mgr.load_level(1)
        self.app_state = STATE_PLAYING

    def _btn_open_levels(self) -> None:
        self.sound.play("click")
        self.app_state = STATE_LEVEL_SELECT

    def _btn_open_how_to_play(self) -> None:
        self.sound.play("click")
        self.app_state = STATE_HOW_TO_PLAY

    def _btn_to_main_menu(self) -> None:
        self.sound.play("click")
        self.app_state = STATE_MENU

    def _btn_toggle_audio(self) -> None:
        enabled = self.sound.toggle_mute()
        self.sound.play("click")
        self.menu_buttons[3].text = "AUDIO: ON" if enabled else "AUDIO: OFF"

    def _start_specific_level(self, level_num: int) -> None:
        self.sound.play("click")
        self.level_mgr.load_level(level_num)
        self.app_state = STATE_PLAYING

    def _btn_resume(self) -> None:
        self.sound.play("click")
        self.app_state = STATE_PLAYING

    def _btn_toggle_pause(self) -> None:
        self.sound.play("click")
        if self.app_state == STATE_PLAYING:
            self.app_state = STATE_PAUSED
        elif self.app_state == STATE_PAUSED:
            self.app_state = STATE_PLAYING

    def _btn_restart_current(self) -> None:
        self.sound.play("click")
        self.level_mgr.restart_level()
        self.app_state = STATE_PLAYING

    def _btn_next_level(self) -> None:
        self.sound.play("click")
        self.level_mgr.next_level()
        if self.level_mgr.state == STATE_CAMPAIGN_WIN:
            self.app_state = STATE_CAMPAIGN_WIN
        else:
            self.app_state = STATE_PLAYING

    def window_to_logical_coords(self, win_x: int, win_y: int) -> Tuple[int, int]:
        """Convert real window pixel coordinates to fixed 960x540 canvas space."""
        if self.viewport_rect.width == 0 or self.viewport_rect.height == 0:
            return (win_x, win_y)
        rel_x = (win_x - self.viewport_rect.x) / self.viewport_rect.width
        rel_y = (win_y - self.viewport_rect.y) / self.viewport_rect.height
        lx = int(rel_x * SCREEN_WIDTH)
        ly = int(rel_y * SCREEN_HEIGHT)
        return (max(0, min(SCREEN_WIDTH, lx)), max(0, min(SCREEN_HEIGHT, ly)))

    def handle_events(self) -> None:
        """Process keyboard, window resize, and mouse interactions."""
        # Reset frame one-shots
        self.rotate_fwd_pressed = False
        self.rotate_bwd_pressed = False
        self.jump_pressed = False
        self.dash_pressed = False
        self.restart_pressed = False

        raw_mouse_pos = pygame.mouse.get_pos()
        logical_mouse = self.window_to_logical_coords(*raw_mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            elif event.type == pygame.VIDEORESIZE:
                # Update display surface to new dimensions
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            # Keyboard triggers
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_e,):
                    self.rotate_fwd_pressed = True
                elif event.key in (pygame.K_q,):
                    self.rotate_bwd_pressed = True
                elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    self.jump_pressed = True
                elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_j):
                    self.dash_pressed = True
                elif event.key == pygame.K_r:
                    self.restart_pressed = True
                elif event.key == pygame.K_ESCAPE:
                    if self.app_state == STATE_PLAYING:
                        self.app_state = STATE_PAUSED
                    elif self.app_state == STATE_PAUSED:
                        self.app_state = STATE_PLAYING

            # Dispatch UI interactions based on app state
            if self.app_state == STATE_MENU:
                for btn in self.menu_buttons:
                    btn.handle_event(event, logical_mouse)

            elif self.app_state == STATE_HOW_TO_PLAY:
                self.btn_back_to_menu.handle_event(event, logical_mouse)

            elif self.app_state == STATE_LEVEL_SELECT:
                for btn in self.level_select_buttons:
                    btn.handle_event(event, logical_mouse)
                self.btn_back_to_menu.handle_event(event, logical_mouse)

            elif self.app_state == STATE_PAUSED:
                for btn in self.pause_buttons:
                    btn.handle_event(event, logical_mouse)

            elif self.app_state == STATE_VICTORY:
                for btn in self.victory_buttons:
                    btn.handle_event(event, logical_mouse)

            elif self.app_state == STATE_CAMPAIGN_WIN:
                for btn in self.campaign_win_buttons:
                    btn.handle_event(event, logical_mouse)

            elif self.app_state == STATE_PLAYING:
                # In-game HUD buttons
                self.ui.hud_btn_rotate_bwd.handle_event(event, logical_mouse)
                self.ui.hud_btn_dash.handle_event(event, logical_mouse)
                self.ui.hud_btn_rotate_fwd.handle_event(event, logical_mouse)
                self.ui.hud_btn_restart.handle_event(event, logical_mouse)
                self.ui.hud_btn_pause.handle_event(event, logical_mouse)

    def update(self, dt: float) -> None:
        """Update game simulation state."""
        if self.app_state == STATE_PLAYING:
            keys = pygame.key.get_pressed()
            move_left = keys[pygame.K_a] or keys[pygame.K_LEFT]
            move_right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
            jump_held = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

            action = InputAction(
                left=move_left,
                right=move_right,
                jump_pressed=self.jump_pressed,
                jump_held=jump_held,
                rotate_fwd=self.rotate_fwd_pressed,
                rotate_bwd=self.rotate_bwd_pressed,
                dash=self.dash_pressed,
                restart=self.restart_pressed,
            )

            self.level_mgr.update(action, dt)

            # Check if victory or campaign win was triggered
            if self.level_mgr.state == STATE_VICTORY:
                self.app_state = STATE_VICTORY
            elif self.level_mgr.state == STATE_CAMPAIGN_WIN:
                self.app_state = STATE_CAMPAIGN_WIN

    def render(self, dt: float) -> None:
        """Render scene onto logical canvas and scale to window with letterboxing."""
        raw_mouse_pos = pygame.mouse.get_pos()
        logical_mouse = self.window_to_logical_coords(*raw_mouse_pos)

        # 1. Render logical canvas
        if self.app_state == STATE_MENU:
            self.ui.draw_start_menu(self.canvas, self.menu_buttons, logical_mouse, dt)

        elif self.app_state == STATE_HOW_TO_PLAY:
            self.ui.draw_how_to_play(self.canvas, self.btn_back_to_menu, logical_mouse)

        elif self.app_state == STATE_LEVEL_SELECT:
            self.ui.draw_level_select(
                self.canvas,
                self.level_select_buttons,
                self.btn_back_to_menu,
                self.level_mgr.best_times,
                logical_mouse,
            )

        elif self.app_state == STATE_PLAYING:
            self.level_mgr.draw(self.canvas)
            self.ui.draw_hud(
                self.canvas,
                self.level_mgr.world_layers,
                self.level_mgr.current_level_idx,
                self.level_mgr.level_data.subtitle,
                self.level_mgr.level_time,
                self.level_mgr.rotations_used,
                logical_mouse,
                player_keys=self.level_mgr.player_keys,
                has_dash=self.level_mgr.player.has_dash,
            )

        elif self.app_state == STATE_PAUSED:
            self.level_mgr.draw(self.canvas)
            self.ui.draw_hud(
                self.canvas,
                self.level_mgr.world_layers,
                self.level_mgr.current_level_idx,
                self.level_mgr.level_data.subtitle,
                self.level_mgr.level_time,
                self.level_mgr.rotations_used,
                logical_mouse,
                player_keys=self.level_mgr.player_keys,
                has_dash=self.level_mgr.player.has_dash,
            )
            self.ui.draw_pause_menu(self.canvas, self.pause_buttons, logical_mouse)

        elif self.app_state == STATE_VICTORY:
            self.level_mgr.draw(self.canvas)
            self.ui.draw_victory_overlay(
                self.canvas,
                self.level_mgr.current_level_idx,
                self.level_mgr.level_data.subtitle,
                self.level_mgr.level_time,
                self.level_mgr.rotations_used,
                self.victory_buttons,
                logical_mouse,
            )

        elif self.app_state == STATE_CAMPAIGN_WIN:
            self.level_mgr.draw(self.canvas)
            self.ui.draw_campaign_win_overlay(self.canvas, self.campaign_win_buttons, logical_mouse)

        # 2. Scale logical canvas onto screen window with 16:9 letterboxing
        win_w, win_h = self.screen.get_size()
        scale = min(win_w / SCREEN_WIDTH, win_h / SCREEN_HEIGHT)
        scaled_w = int(SCREEN_WIDTH * scale)
        scaled_h = int(SCREEN_HEIGHT * scale)
        offset_x = (win_w - scaled_w) // 2
        offset_y = (win_h - scaled_h) // 2

        self.viewport_rect = pygame.Rect(offset_x, offset_y, scaled_w, scaled_h)

        self.screen.fill(COLOR_BG)
        scaled_surf = pygame.transform.smoothscale(self.canvas, (scaled_w, scaled_h))
        self.screen.blit(scaled_surf, (offset_x, offset_y))

        pygame.display.flip()

    async def run(self) -> None:
        """Asynchronous main loop compatible with desktop and Pygbag web execution."""
        dt = 1.0 / FPS
        while self.running:
            self.handle_events()
            self.update(dt)
            self.render(dt)
            self.clock.tick(FPS)
            # Essential for Pygbag / WebAssembly browser execution
            await asyncio.sleep(0)

        pygame.quit()


async def main() -> None:
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
