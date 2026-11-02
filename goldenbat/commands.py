"""
Commands Module

Description: Handles exploration commands ('laugh', 'room', 'path', 'search', 'go',
             'get', 'quit') and updates the game state.
"""

import time
from goldenbat.audio import audio
from goldenbat.text import scroll_text, pause, clear, GOLD, RESET


def cmd_laugh(state, target):
    """Character SFX command."""
    scroll_text(f"\nManiacal laughter reverberates throughout the {state.current_room}...")
    audio.play_sfx("laugh")
    scroll_text(f"{GOLD}GOLDEN BAT: 'HA-HA-HA-HAAAA..!!!'{RESET}", delay = 0.1)
    pause()
    clear()

def cmd_room(state, target):
    """Re-reads the current room's description."""
    scroll_text(f"\n{state.room['description']}")
    pause()
    clear()

def cmd_search(state, target):
    """Reveals an item in the room, or any secrets that have been unlocked."""
    secrets = state.visible_secrets()
    if 'item' in state.room:
        scroll_text(f"\nYou see the {state.room['item']} here.")
    elif secrets:
        scroll_text("\n" + "\n".join(secrets))
    else:
        scroll_text(f"\nYou scour the {state.current_room}, and find nothing of use...")
    pause()
    clear()

def cmd_path(state, target):
    """Lists visible exits."""
    scroll_text(f"\nVisible pathways: {', '.join(state.exits())}")
    pause()
    clear()

def cmd_go(state, target):
    """Moves to an adjacent room."""
    direction = target.title()
    exits = state.exits()
    if direction in exits:
        state.current_room = exits[direction]
        audio.play_sfx("walk")
        scroll_text(f"\nYou move {direction} to the {state.current_room}...")
        pause()
        audio.fade(500)
    else:
        scroll_text("\nYou cannot go that way.")
        pause()
    clear()

def cmd_get(state, target):
    """Picks up the room's item and applies any pickup effect."""
    item_in_room = state.room.get('item', '')
    if item_in_room and target.lower() == item_in_room.lower():
        state.inventory.append(state.room.pop('item'))
        item = state.items[item_in_room]
        audio.play_sfx("item")
        scroll_text(f"\nYou picked up the {item_in_room}!")
        pause()
        scroll_text(f">> {item['description']}")
        pause()

        # Pickup effects, e.g. the Kinesis Stone unlocking the secret path
        effect = item.get("on_pickup")
        if effect and effect["set_flag"] not in state.flags:
            state.flags.add(effect["set_flag"])
            scroll_text(effect["text"])
            pause()
    elif target:
        scroll_text(f"\nYou reach for the {target.title()}, but your hand only grasps thin air."
                    f"\nPerhaps it only exists in your mind...?")
        pause()
    else:
        scroll_text("\nNo item name entered.")
        pause()
    clear()

def cmd_quit(state, target):
    """Ends the game."""
    audio.stop()
    audio.play_sfx("quit")
    scroll_text("\nEarth's fate remains uncertain...")
    time.sleep(5.0)
    return False

def cmd_idle(state, target):
    """Empty input."""
    scroll_text("\nYou stand silently...")
    pause()
    clear()

def cmd_invalid(state, target):
    """Unknown command fallback."""
    scroll_text("\nInvalid action.")
    pause()
    clear()

COMMANDS = {
    'laugh': cmd_laugh,
    'room': cmd_room,
    'search': cmd_search,
    'path': cmd_path,
    'go': cmd_go,
    'get': cmd_get,
    'quit': cmd_quit,
    'none': cmd_idle,
}

def handle_command(state, user_input):
    """
    Runs one tokenized command.

    Args:
        state (GameState): Current game state, updated in place.
        user_input (list): Tokenized input [action, target].

    Returns:
        bool: False if the player quit; True if the game should continue.
    """
    action = user_input[0].lower()
    target = user_input[1] if len(user_input) > 1 else ""
    handler = COMMANDS.get(action, cmd_invalid)
    return handler(state, target) is not False
