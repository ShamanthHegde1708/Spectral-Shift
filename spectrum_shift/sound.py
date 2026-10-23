"""Procedural audio synthesizer for Spectrum Shift.

Generates 8-bit / 16-bit retro-modern sound effects entirely in memory using standard Python
math and the wave module. Requires no external audio files or internet connectivity.
Gracefully operates in headless/silent environments (e.g. unit tests).
"""

import io
import math
import struct
import wave
import pygame
from typing import Optional, Dict


class SoundManager:
    """Manages sound effects and procedural audio playback."""

    def __init__(self):
        self.enabled: bool = True
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.initialized: bool = False

        self._init_audio()

    def _init_audio(self) -> None:
        """Initialize pygame mixer and generate sound effects."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.initialized = True
            self._generate_sounds()
        except Exception:
            # Headless testing or missing audio device
            self.initialized = False

    def _generate_wav_bytes(self, samples: list, sample_rate: int = 44100) -> bytes:
        """Encode raw float audio samples [-1.0, 1.0] into WAV byte format."""
        byte_io = io.BytesIO()
        with wave.open(byte_io, "wb") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            # Pack samples as signed 16-bit integers
            packed = bytearray()
            for s in samples:
                val = max(-32767, min(32767, int(s * 32767.0)))
                packed.extend(struct.pack("<h", val))
            wav_file.writeframes(packed)
        return byte_io.getvalue()

    def _generate_sounds(self) -> None:
        """Synthesize all game sound effects."""
        sr = 44100

        # 1. Jump Sound (Upward chirp: 240Hz -> 620Hz over 0.12s)
        jump_samples = []
        duration = 0.12
        num_samples = int(sr * duration)
        for i in range(num_samples):
            t = i / sr
            progress = t / duration
            freq = 240.0 + progress * 380.0
            amp = (1.0 - progress) * 0.45
            # Square-sine hybrid
            sample = math.sin(2.0 * math.pi * freq * t) * amp
            jump_samples.append(sample)
        self.sounds["jump"] = pygame.mixer.Sound(io.BytesIO(self._generate_wav_bytes(jump_samples, sr)))

        # 2. Land Sound (Low thud: 140Hz decaying to 60Hz over 0.08s)
        land_samples = []
        duration = 0.08
        num_samples = int(sr * duration)
        for i in range(num_samples):
            t = i / sr
            progress = t / duration
            freq = 140.0 * (1.0 - progress * 0.5)
            amp = (1.0 - progress) ** 2 * 0.5
            sample = math.sin(2.0 * math.pi * freq * t) * amp
            land_samples.append(sample)
        self.sounds["land"] = pygame.mixer.Sound(io.BytesIO(self._generate_wav_bytes(land_samples, sr)))

        # 3. Rotate Forward Sound (Sci-fi high-tech chime: 520Hz & 880Hz over 0.15s)
        fwd_samples = []
        duration = 0.15
        num_samples = int(sr * duration)
        for i in range(num_samples):
            t = i / sr
            progress = t / duration
            freq = 480.0 + progress * 400.0
            amp = (1.0 - progress) * 0.4
            sample = (
                0.7 * math.sin(2.0 * math.pi * freq * t)
                + 0.3 * math.sin(2.0 * math.pi * (freq * 1.5) * t)
            ) * amp
            fwd_samples.append(sample)
        self.sounds["rotate_fwd"] = pygame.mixer.Sound(io.BytesIO(self._generate_wav_bytes(fwd_samples, sr)))

        # 4. Rotate Backward Sound (Sci-fi low-tech whoosh: 880Hz down to 480Hz over 0.15s)
        bwd_samples = []
        duration = 0.15
        num_samples = int(sr * duration)
        for i in range(num_samples):
            t = i / sr
            progress = t / duration
            freq = 880.0 - progress * 400.0
            amp = (1.0 - progress) * 0.4
            sample = (
                0.7 * math.sin(2.0 * math.pi * freq * t)
                + 0.3 * math.sin(2.0 * math.pi * (freq * 0.75) * t)
            ) * amp
            bwd_samples.append(sample)
        self.sounds["rotate_bwd"] = pygame.mixer.Sound(io.BytesIO(self._generate_wav_bytes(bwd_samples, sr)))

        # 5. Victory Sound (Majestic 3-note harmonic arpeggio: C5, E5, G5, C6)
        win_samples = []
        notes = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
        note_dur = 0.11
        for note_idx, freq in enumerate(notes):
            num_samples = int(sr * note_dur)
            for i in range(num_samples):
                t = i / sr
                prog = t / note_dur
                amp = (1.0 - prog * 0.7) * 0.4
                sample = (
                    0.6 * math.sin(2.0 * math.pi * freq * t)
                    + 0.4 * math.sin(2.0 * math.pi * (freq * 2) * t)
                ) * amp
                win_samples.append(sample)
        self.sounds["victory"] = pygame.mixer.Sound(io.BytesIO(self._generate_wav_bytes(win_samples, sr)))

        # 6. Death Sound (Glitch descend & noise: 400Hz down to 80Hz)
        death_samples = []
        duration = 0.28
        num_samples = int(sr * duration)
        for i in range(num_samples):
            t = i / sr
            progress = t / duration
            freq = 400.0 * (1.0 - progress * 0.8)
            amp = (1.0 - progress) * 0.5
            noise = ((math.sin(t * 12345.67) * 43758.5453) % 1.0) * 0.2
            sample = (math.sin(2.0 * math.pi * freq * t) * 0.8 + noise) * amp
            death_samples.append(sample)
        self.sounds["death"] = pygame.mixer.Sound(io.BytesIO(self._generate_wav_bytes(death_samples, sr)))

        # 7. Button Click Sound
        btn_samples = []
        duration = 0.04
        num_samples = int(sr * duration)
        for i in range(num_samples):
            t = i / sr
            progress = t / duration
            freq = 800.0 - progress * 300.0
            amp = (1.0 - progress) * 0.3
            sample = math.sin(2.0 * math.pi * freq * t) * amp
            btn_samples.append(sample)
        self.sounds["click"] = pygame.mixer.Sound(io.BytesIO(self._generate_wav_bytes(btn_samples, sr)))

        # 8. Spectrum Gate Boost Sound (Sci-fi energy surge)
        gate_samples = []
        duration = 0.22
        num_samples = int(sr * duration)
        for i in range(num_samples):
            t = i / sr
            progress = t / duration
            freq = 300.0 + progress * 700.0
            amp = (1.0 - progress) * 0.45
            sample = (
                0.7 * math.sin(2.0 * math.pi * freq * t)
                + 0.3 * math.sin(2.0 * math.pi * (freq * 1.5) * t)
            ) * amp
            gate_samples.append(sample)
        self.sounds["boost"] = pygame.mixer.Sound(io.BytesIO(self._generate_wav_bytes(gate_samples, sr)))

        # 9. Phase Dash Sound (High-speed chromatic warp whoosh)
        dash_samples = []
        duration = 0.14
        num_samples = int(sr * duration)
        for i in range(num_samples):
            t = i / sr
            progress = t / duration
            freq = 550.0 + 800.0 * math.sin(progress * math.pi)
            noise = ((math.sin(t * 8432.1) * 3123.4) % 1.0) * 0.25
            amp = (1.0 - progress) * 0.5
            sample = (math.sin(2.0 * math.pi * freq * t) * 0.75 + noise) * amp
            dash_samples.append(sample)
        self.sounds["dash"] = pygame.mixer.Sound(io.BytesIO(self._generate_wav_bytes(dash_samples, sr)))

        # 10. Key Pickup Sound (Prismatic crystalline arpeggio: E5, G#5, B5, E6)
        key_samples = []
        key_notes = [659.25, 830.61, 987.77, 1318.51]
        note_len = 0.06
        for note_idx, freq in enumerate(key_notes):
            n_samples = int(sr * note_len)
            for i in range(n_samples):
                t = i / sr
                prog = t / note_len
                amp = (1.0 - prog) * 0.35
                sample = (
                    0.7 * math.sin(2.0 * math.pi * freq * t)
                    + 0.3 * math.sin(2.0 * math.pi * (freq * 2.0) * t)
                ) * amp
                key_samples.append(sample)
        self.sounds["key_pickup"] = pygame.mixer.Sound(io.BytesIO(self._generate_wav_bytes(key_samples, sr)))

        # 11. Lock Dissolve Sound (Electromagnetic beam release)
        unlock_samples = []
        duration = 0.24
        num_samples = int(sr * duration)
        for i in range(num_samples):
            t = i / sr
            progress = t / duration
            freq = 380.0 + (progress ** 2) * 920.0
            amp = (1.0 - progress) * 0.45
            sample = (
                0.6 * math.sin(2.0 * math.pi * freq * t)
                + 0.4 * math.sin(2.0 * math.pi * (freq * 0.5) * t)
            ) * amp
            unlock_samples.append(sample)
        self.sounds["unlock"] = pygame.mixer.Sound(io.BytesIO(self._generate_wav_bytes(unlock_samples, sr)))

    def play(self, sound_name: str) -> None:
        """Play sound effect if audio is enabled and sound exists."""
        if not self.enabled or not self.initialized:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def toggle_mute(self) -> bool:
        """Toggle audio mute state. Returns new enabled status."""
        self.enabled = not self.enabled
        return self.enabled
