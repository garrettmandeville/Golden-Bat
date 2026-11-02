"""
Audio Controller Module

Description: Encapsulates Pygame Mixer BGM and SFX management and per-room ambient
             music. File names and keys are configured in data/audio.json.

             Audio is optional: any missing file is skipped silently, and if no audio
             device is available the whole manager becomes a no-op.
"""

import time, os, pygame
from goldenbat.data import load_json
from goldenbat.paths import resource_path


class AudioManager:
    """Manages background music, sound effects, volume leveling, and fades."""

    def __init__(self, assets_dir=None):
        """Initializes the Pygame mixer and loads whichever audio files exist."""
        config = load_json("audio.json")
        self.assets_dir = assets_dir or resource_path("assets")
        self.fallback_room_music = config["fallback_room_music"]
        # Known SFX keys, loaded or not, so story text can use them as inline tags
        self.sfx_keys = set(config["sfx"])
        self.current_track = None
        self.master_sfx_volume = 0.4
        self.music = {}
        self.sfx = {}

        try:
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            # No audio device (headless machine, CI, etc.) - run silently
            self.enabled = False
            return

        # Music is streamed when played, so only the path is stored
        for key, filename in config["music"].items():
            path = os.path.join(self.assets_dir, filename)
            if os.path.exists(path):
                self.music[key] = path

        # Sound effects are loaded up front; a missing or broken file is skipped
        for key, filename in config["sfx"].items():
            path = os.path.join(self.assets_dir, filename)
            if not os.path.exists(path):
                continue
            try:
                self.sfx[key] = pygame.mixer.Sound(path)
            except pygame.error as e:
                print(f"Audio Loading Error ({filename}): {e}")

        self.set_all_sfx_volume(self.master_sfx_volume)

    def set_all_sfx_volume(self, volume):
        """Sets master volume across all loaded sound effects."""
        self.master_sfx_volume = volume
        for sound in self.sfx.values():
            sound.set_volume(volume)

    def play_bgm(self, key, volume = 0.2, fade = 500):
        """Loads and loops background music track if not already playing."""
        if not self.enabled or key not in self.music:
            return
        if pygame.mixer.music.get_busy() and key == self.current_track:
            return
        try:
            pygame.mixer.music.load(self.music[key])
        except pygame.error as e:
            print(f"Audio Loading Error ({key}): {e}")
            return
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1, fade_ms = fade)
        self.current_track = key

    def play_sfx(self, effect):
        """Plays a sound effect by key, if it was loaded."""
        sound = self.sfx.get(effect)
        if sound:
            sound.play()

    def stop(self):
        """Stops all active BGM and SFX channels."""
        if self.enabled:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
        self.current_track = None

    def fade(self, duration = 5000):
        """Fades out audio tracks over specified duration in milliseconds."""
        if self.enabled:
            pygame.mixer.music.fadeout(duration)
            pygame.mixer.fadeout(duration)
        self.current_track = None
        # Long fades double as dramatic pauses, so keep the timing even without audio
        if duration >= 5000:
            time.sleep(duration / 1000)

    def play_room_music(self, room_music):
        """
        Plays a room's ambient track, falling back to the overworld track.

        Args:
            room_music (list | None): [music key, volume] from data/rooms.json.
        """
        key, volume = room_music or self.fallback_room_music
        if key not in self.music:
            key, volume = self.fallback_room_music
        self.play_bgm(key, volume = volume)

# Shared global instance
audio = AudioManager()
