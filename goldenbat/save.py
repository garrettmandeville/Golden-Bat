"""
Save Game Module

Description: Writes and reads the single save slot. Saves live in the user's data folder
             (%APPDATA%\\GoldenBat on Windows, ~/.local/share/GoldenBat elsewhere).
"""

import json, os
from goldenbat.state import GameState

SAVE_VERSION = 1

def save_path():
    """Returns the full path of the save file."""
    if os.name == 'nt':
        base_dir = os.environ.get("APPDATA", os.path.expanduser("~"))
    else:
        base_dir = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    return os.path.join(base_dir, "GoldenBat", "save.json")

def save_exists():
    """True if a save file is present."""
    return os.path.exists(save_path())

def save_game(state):
    """Writes the current state to the save file."""
    path = save_path()
    os.makedirs(os.path.dirname(path), exist_ok = True)
    with open(path, "w", encoding = "utf-8") as file:
        json.dump({"version": SAVE_VERSION, "state": state.to_save()}, file, ensure_ascii = False, indent = 2)

def load_game(rooms_data, items):
    """Reads the save file and returns a GameState, or None if it's missing or unreadable."""
    try:
        with open(save_path(), encoding = "utf-8") as file:
            save = json.load(file)
        return GameState.from_save(save["state"], rooms_data, items)
    except (OSError, ValueError, KeyError):
        return None
