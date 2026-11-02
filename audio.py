"""
Audio Controller Module

Description: Encapsulates Pygame Mixer BGM and SFX management, file path resolution,
             and automatic ambient sound playback per room location.

             Audio is optional: any missing file is skipped silently, and if no audio
             device is available the whole manager becomes a no-op.
"""

import time, os, sys, pygame

# Background music: key -> path relative to the assets folder
MUSIC_FILES = {
    "title": "Music/title_screen.mp3",
    "bgm": "Music/main_bgm.mp3",
    
    "true_credits": "Music/credits_true.mp3",
    "win_credits": "Music/credits_win.mp3",
    "lose_credits": "Music/credits_lose.mp3",
    "tomb": "Rooms/tomb.mp3",
    "tunnel": "Rooms/tunnel.mp3",
    "beach": "Rooms/beach.mp3",
    "cliffs": "Rooms/cliffs.mp3",
    "church": "Rooms/church.mp3",
    "cellar": "Rooms/cellar.mp3",
    "town": "Rooms/town.mp3",
    "armory": "Rooms/armory.mp3",
    "lab": "Rooms/lab.mp3",
    "observatory": "Rooms/observatory.mp3",
    "gallery": "Rooms/street.mp3",
}

# Sound effects: key -> path relative to the assets folder
SFX_FILES = {
    "laugh": "SFX/laugh.wav",
    "bats": "SFX/bats.wav",
    "scifi": "SFX/scifi.wav",
    "item": "SFX/item.wav",
    "quit": "SFX/quit.wav",
    "icarus": "SFX/icarus_impact.wav",
}

# Room name -> (music key, volume)
ROOM_MUSIC = {
    "Ancient Tomb": ("tomb", 0.8),
    "Secret Tunnel": ("tunnel", 0.4),
    "Shipwrecked Beach": ("beach", 0.4),
    "Ocean-Facing Cliffs": ("cliffs", 0.4),
    "Abandoned Church": ("church", 0.4),
    "Church Cellar": ("cellar", 0.4),
    "Abandoned Residential District": ("town", 0.8),
    "Rusted Armory": ("armory", 0.2),
    "Ancient Atlantean Lab": ("lab", 1.0),
    "Submerged Observation Deck": ("observatory", 0.6),
    "Echoing Gallery": ("gallery", 0.6),
}


def default_assets_dir():
    """Returns the assets folder, accounting for PyInstaller's temp extraction dir."""
    # PyInstaller creates a temporary folder and stores path in _MEIPASS
    if hasattr(sys, '_MEIPASS'):
        base_dir = sys._MEIPASS
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "assets")


class AudioManager:
    """Manages background music, sound effects, volume leveling, and fades."""

    def __init__(self, assets_dir=None):
        """Initializes the Pygame mixer and loads whichever audio files exist."""
        self.assets_dir = assets_dir or default_assets_dir()
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
        for key, filename in MUSIC_FILES.items():
            path = os.path.join(self.assets_dir, filename)
            if os.path.exists(path):
                self.music[key] = path

        # Sound effects are loaded up front; a missing or broken file is skipped
        for key, filename in SFX_FILES.items():
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

    def get_room_music(self, current_room):
        """Triggers room-specific ambient background music."""
        if current_room in ROOM_MUSIC:
            key, volume = ROOM_MUSIC[current_room]
            self.play_bgm(key, volume=volume)

# Shared global instance
audio = AudioManager()
