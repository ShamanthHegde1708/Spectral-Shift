"""Level management, deterministic game update loop, transitions, and state progression."""

import pygame
from typing import Optional, Dict, Any, Tuple, List
try:
    from .settings import (
        STATE_PLAYING,
        STATE_PAUSED,
        STATE_DYING,
        STATE_VICTORY,
        STATE_CAMPAIGN_WIN,
        PORTAL_RADIUS,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
    )
    from .player import Player
    from .platform import Platform
    from .world_layers import WorldLayers
    from .levels import load_level, LevelData, ALL_LEVEL_GETTERS
    from .effects import EffectManager, ExitPortal
    from .sound import SoundManager
    from .items import SpectrumKey, SpectrumLockGate
except ImportError:
    from settings import (
        STATE_PLAYING,
        STATE_PAUSED,
        STATE_DYING,
        STATE_VICTORY,
        STATE_CAMPAIGN_WIN,
        PORTAL_RADIUS,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
    )
    from player import Player
    from platform import Platform
    from world_layers import WorldLayers
    from levels import load_level, LevelData, ALL_LEVEL_GETTERS
    from effects import EffectManager, ExitPortal
    from sound import SoundManager
    from items import SpectrumKey, SpectrumLockGate


class InputAction:
    """Encapsulates deterministic input signals for player movement and layer rotation."""

    def __init__(
        self,
        left: bool = False,
        right: bool = False,
        jump_pressed: bool = False,
        jump_held: bool = False,
        rotate_fwd: bool = False,
        rotate_bwd: bool = False,
        dash: bool = False,
        restart: bool = False,
    ):
        self.left = left
        self.right = right
        self.jump_pressed = jump_pressed
        self.jump_held = jump_held
        self.rotate_fwd = rotate_fwd
        self.rotate_bwd = rotate_bwd
        self.dash = dash
        self.restart = restart


class LevelManager:
    """Orchestrates physics simulation, world rotations, and level progression."""

    def __init__(self, sound_manager: Optional[SoundManager] = None):
        self.sound = sound_manager or SoundManager()
        self.effects = EffectManager()
        self.world_layers = WorldLayers()
        self.player = Player(100, 300)
        self.portal: Optional[ExitPortal] = None
        self.level_data: Optional[LevelData] = None

        # Level state
        self.current_level_idx: int = 1
        self.state: str = STATE_PLAYING
        self.level_time: float = 0.0
        self.death_timer: float = 0.0
        self.rotations_used: int = 0

        # Best completion times record
        self.best_times: Dict[int, float] = {}

        # Connect player audio callbacks
        self.player.on_jump = lambda: self.sound.play("jump")
        self.player.on_land = lambda: self._on_player_land()
        self.player.on_dash = lambda: self.sound.play("dash")

        # Key and Lock Inventory
        self.keys: List[SpectrumKey] = []
        self.locks: List[SpectrumLockGate] = []
        self.player_keys: int = 0

        # Load level 1 initially
        self.load_level(1)

    def _on_player_land(self) -> None:
        self.sound.play("land")
        self.effects.spawn_land_dust(self.player.rect.centerx, self.player.rect.bottom)

    def load_level(self, level_num: int) -> None:
        """Load a level and reset all transient states."""
        self.current_level_idx = max(1, min(len(ALL_LEVEL_GETTERS), level_num))
        self.level_data = load_level(self.current_level_idx)

        # Reset world layers with the level's initial cycle
        self.world_layers.reset(self.level_data.initial_cycle)

        # Reset dynamic mechanisms (rotors and spinning gates)
        self.rotors = getattr(self.level_data, "rotors", [])
        for r in self.rotors:
            r.reset()

        self.gates = getattr(self.level_data, "gates", [])
        for g in self.gates:
            g.reset()

        # Reset Keys and Locks
        self.keys = getattr(self.level_data, "keys", [])
        for k in self.keys:
            k.reset()

        self.locks = getattr(self.level_data, "locks", [])
        for l in self.locks:
            l.reset()

        self.player_keys = 0

        # Reset player to spawn coordinates
        sx, sy = self.level_data.spawn_pos
        self.player.reset(sx, sy)

        # Setup exit portal
        px, py = self.level_data.portal_pos
        self.portal = ExitPortal(px, py)

        # Clear effects & timers
        self.effects.reset()
        self.state = STATE_PLAYING
        self.level_time = 0.0
        self.death_timer = 0.0
        self.rotations_used = 0

    def get_all_platforms(self) -> List[Platform]:
        """Aggregate static level platforms, dynamic rotor platforms, and solid lock barriers."""
        plat_list = list(self.level_data.platforms)
        for r in self.rotors:
            plat_list.extend(r.get_platforms())
        for lock in self.locks:
            if lock.is_solid():
                plat_list.append(lock.barrier_platform)
        return plat_list

    def restart_level(self) -> None:
        """Reset current level cleanly without carrying over velocity or state."""
        self.load_level(self.current_level_idx)

    def next_level(self) -> None:
        """Advance to the subsequent level or trigger campaign victory."""
        if self.current_level_idx < len(ALL_LEVEL_GETTERS):
            self.load_level(self.current_level_idx + 1)
        else:
            self.state = STATE_CAMPAIGN_WIN

    def rotate_forward(self) -> None:
        """Rotate cyclic layer stack forward (E)."""
        if self.state != STATE_PLAYING:
            return
        self.world_layers.rotate_forward()
        self.rotations_used += 1
        self.sound.play("rotate_fwd")
        self.effects.trigger_rotation_pulse(self.world_layers.foreground, (self.player.rect.centerx, self.player.rect.centery))
        # Immediate support verification: player falls if platform rotated away
        self.player.check_ground_after_rotation(self.get_all_platforms(), self.world_layers)

    def rotate_backward(self) -> None:
        """Rotate cyclic layer stack backward (Q)."""
        if self.state != STATE_PLAYING:
            return
        self.world_layers.rotate_backward()
        self.rotations_used += 1
        self.sound.play("rotate_bwd")
        self.effects.trigger_rotation_pulse(self.world_layers.foreground, (self.player.rect.centerx, self.player.rect.centery))
        # Immediate support verification: player falls if platform rotated away
        self.player.check_ground_after_rotation(self.get_all_platforms(), self.world_layers)

    def update(self, action: InputAction, dt: float = 1.0 / 60.0) -> None:
        """Single deterministic update step.
        
        Execution order:
        1. Restart check
        2. Layer rotation
        3. Input handling
        4. Physics & collision
        5. Goal verification
        6. Death check & respawn animation
        7. Ambient effects
        """
        if action.restart:
            self.restart_level()
            return

        # Handle Death State transition
        if self.state == STATE_DYING:
            self.death_timer -= dt
            self.effects.update(dt)
            if self.death_timer <= 0.0:
                self.restart_level()
            return

        # If victory or campaign win, only update portal / effects
        if self.state in (STATE_VICTORY, STATE_CAMPAIGN_WIN):
            if self.portal:
                self.portal.update(dt)
            self.effects.update(dt)
            return

        # Normal Gameplay Update
        self.level_time += dt

        # 1. Process World Rotations
        if action.rotate_fwd and not action.rotate_bwd:
            self.rotate_forward()
        elif action.rotate_bwd and not action.rotate_fwd:
            self.rotate_backward()

        # 2. Update Dynamic Mechanisms (Rotors and Spectrum Gates)
        for r in self.rotors:
            r.update(dt)

        for g in self.gates:
            g.update(dt)
            if g.check_player_boost(self.player, self.world_layers):
                self.sound.play("boost")
                self.effects.trigger_shake(intensity=5.0, duration=0.25)
                self.effects.trigger_rotation_pulse(
                    self.world_layers.foreground,
                    (int(self.player.rect.centerx), int(self.player.rect.centery)),
                )
                for _ in range(15):
                    self.effects.spawn_jump_dust(self.player.rect.centerx, self.player.rect.centery)

        # 3. Player Input (including Chroma Phase Dash)
        self.player.handle_input(
            move_left=action.left,
            move_right=action.right,
            jump_pressed=action.jump_pressed,
            jump_held=action.jump_held,
            dash_pressed=action.dash,
        )

        # 4. Update Keys & Collect
        for k in self.keys:
            k.update(dt)
            if k.check_pickup(self.player.rect, self.world_layers.foreground):
                self.player_keys += 1
                self.sound.play("key_pickup")
                self.effects.trigger_shake(intensity=3.0, duration=0.15)
                self.effects.trigger_rotation_pulse(
                    self.world_layers.foreground,
                    (int(k.x), int(k.y)),
                )
                for _ in range(16):
                    self.effects.spawn_jump_dust(k.x, k.y)

        # 5. Update Locks & Interacting
        for lock in self.locks:
            lock.update(dt)
            if lock.check_interaction(self.player.rect, self.player_keys):
                self.player_keys -= 1
                self.sound.play("unlock")
                self.effects.trigger_shake(intensity=6.0, duration=0.25)
                self.effects.trigger_rotation_pulse(
                    "blue",
                    (int(lock.x + lock.width / 2), int(lock.y + lock.height / 2)),
                )
                for _ in range(20):
                    self.effects.spawn_jump_dust(lock.x + lock.width / 2, lock.y + lock.height / 2)

        # 6. Particle trail for running or dashing player
        if abs(self.player.vx) > 2.0 and self.player.is_grounded:
            self.effects.spawn_player_trail(self.player.rect.centerx, self.player.rect.bottom - 4)

        # 7. Player Physics & Collision against Foreground Layer (including Rotors & Locks)
        all_platforms = self.get_all_platforms()
        self.player.update(all_platforms, self.world_layers)

        # 5. Check Death Condition (Falling below screen)
        if self.player.is_dead:
            self.state = STATE_DYING
            self.death_timer = 0.55
            self.sound.play("death")
            self.effects.trigger_shake(intensity=8.0, duration=0.3)
            self.effects.spawn_death_burst(self.player.rect.centerx, self.player.rect.centery)
            return

        # 6. Check Goal / Portal Collision
        if self.portal and self.player.rect.colliderect(self.portal.rect):
            self.state = STATE_VICTORY
            self.sound.play("victory")
            # Record best time
            cur_best = self.best_times.get(self.current_level_idx, 9999.0)
            if self.level_time < cur_best:
                self.best_times[self.current_level_idx] = self.level_time
            # Burst portal particles
            for _ in range(30):
                self.effects.spawn_portal_motes(self.portal.x, self.portal.y)
            return

        # 7. Update Portal & Layer animations
        if self.portal:
            self.portal.update(dt)
            self.effects.spawn_portal_motes(self.portal.x, self.portal.y)

        self.world_layers.update(dt)
        self.effects.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Render complete game scene with screen shake and depth ordering."""
        shake_x, shake_y = self.effects.get_shake_offset()

        # Dedicated game scene surface for shake effect
        scene_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.effects.draw_background(scene_surf)

        # Render Platforms in back-to-front layer order
        # WorldLayers.get_render_order() returns [back, middle, foreground]
        render_order = self.world_layers.get_render_order()
        for layer_name in render_order:
            vis_depth = self.world_layers.get_visual_depth(layer_name)
            for p in self.level_data.platforms:
                if p.layer == layer_name:
                    p.draw(scene_surf, vis_depth)

        # Render Dynamic Mechanisms (Rotors and Spinning Gates)
        for r in self.rotors:
            r.draw(scene_surf, self.world_layers)

        for g in self.gates:
            g.draw(scene_surf, self.world_layers)

        # Render Holographic Lock Barriers
        for lock in self.locks:
            lock.draw(scene_surf)

        # Render Floating Prismatic Keys
        for k in self.keys:
            k.draw(scene_surf, self.world_layers)

        # Render Exit Portal
        if self.portal:
            self.portal.draw(scene_surf)

        # Render Player (if not dead)
        if not self.player.is_dead:
            self.player.draw(scene_surf, self.world_layers)

        # Render Particles & Pulses
        self.effects.draw_effects(scene_surf, (self.player.rect.centerx, self.player.rect.centery))

        # Blit scene surface onto target surface with shake offset
        surface.blit(scene_surf, (shake_x, shake_y))
