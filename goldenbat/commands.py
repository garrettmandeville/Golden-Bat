"""
Commands Module

Description: Handles exploration commands (go, get, use, talk, search, path, room,
             status, laugh, help, quit) and updates the game state.
"""

import time
from goldenbat.audio import audio
from goldenbat.combat import use_consumable
from goldenbat.npcs import find_npc, npc_name, talk, quest_status
from goldenbat.state import MAX_HP, MAX_ENERGY
from goldenbat.text import scroll_text, play_beats, pause, clear, GOLD, RESET

HELP_TEXT = """
  go [direction]   Move to an adjacent room (e.g. go north)
  get [item]       Pick up an item
  use [item]       Use an item or relic (e.g. use coral salve)
  talk [name]      Talk to someone in the room
  search           Look for items and secrets
  path             List visible exits
  room             Re-read the room's description
  status           Show health, relics, abilities, and quests
  laugh            Unleash the laugh of Golden Bat
  quit             Abandon the mission
"""

def describe_room(state):
    """Prints the room description plus any extra lines whose conditions are met."""
    lines = [state.room['description']] + state.visible_texts("extra")
    scroll_text("\n" + "\n".join(lines))

def find_in(names, target):
    """Case-insensitive lookup of target in a list of item names."""
    return next((name for name in names if name.lower() == target.lower()), None)

def cmd_laugh(state, target):
    """Character SFX command."""
    scroll_text(f"\nManiacal laughter reverberates throughout the {state.current_room}...")
    audio.play_sfx("laugh")
    scroll_text(f"{GOLD}GOLDEN BAT: 'HA-HA-HA-HAAAA..!!!'{RESET}", delay = 0.1)
    pause()
    clear()

def cmd_room(state, target):
    """Re-reads the current room's description."""
    describe_room(state)
    pause()
    clear()

def cmd_search(state, target):
    """Reveals items in the room and any secrets whose conditions are met."""
    items = state.room.get("items", [])
    lines = state.visible_texts("secrets")
    if items:
        lines.insert(0, f"You see: {', '.join(items)}.")
    if not lines:
        lines = [f"You scour the {state.current_room}, and find nothing of use..."]
    scroll_text("\n" + "\n".join(lines))
    pause()
    clear()

def cmd_path(state, target):
    """Lists visible exits."""
    scroll_text(f"\nVisible pathways: {', '.join(state.exits())}")
    pause()
    clear()

def cmd_go(state, target):
    """Moves to an adjacent room, if its requirements are met."""
    direction = target.title()
    exit = state.exits().get(direction)
    if exit is None:
        scroll_text("\nYou cannot go that way.")
    elif not state.meets(exit.get("requires")):
        scroll_text(f"\n{exit['blocked_text']}")
    else:
        if "pass_text" in exit:
            scroll_text(f"\n{exit['pass_text']}")
        state.previous_room = state.current_room
        state.current_room = exit["to"]
        state.just_entered = True
        audio.play_sfx("walk")
        scroll_text(f"\nYou move {direction} to the {state.current_room}...")
        pause()
        audio.fade(500)
        clear()
        return
    pause()
    clear()

def cmd_get(state, target):
    """Picks up an item from the room and applies any pickup effect."""
    room_items = state.room.get("items", [])
    name = find_in(room_items, target) if target else None
    if name:
        room_items.remove(name)
        state.inventory.append(name)
        item = state.items[name]
        audio.play_sfx("item")
        scroll_text(f"\nYou picked up the {name}!")
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

def cmd_use(state, target):
    """Uses a consumable, or a relic on something in the room."""
    name = find_in(state.inventory, target) if target else None
    if not name:
        scroll_text("\nYou aren't carrying that.")
    elif state.items[name].get("consumable"):
        scroll_text("\n" + use_consumable(state, name))
    else:
        interaction = next((i for i in state.room.get("interactions", [])
                            if i["item"] == name and i["flag"] not in state.flags
                            and state.meets(i.get("requires"))), None)
        if interaction:
            state.flags.add(interaction["flag"])
            state.room.setdefault("items", []).extend(interaction.get("add_items", []))
            if "beats" in interaction:
                clear()
                play_beats(interaction["beats"])
            else:
                scroll_text(f"\n{interaction['text']}")
        else:
            scroll_text(f"\nYou hold up the {name}. Nothing happens here.")
    pause()
    clear()

def cmd_talk(state, target):
    """Talks to a character in the room."""
    npc_id = find_npc(state, target)
    if npc_id:
        talk(state, npc_id)
        return
    if target:
        scroll_text("\nThere's no one here by that name.")
    elif state.npcs():
        scroll_text(f"\nTalk to whom? ({', '.join(npc_name(npc) for npc in state.npcs())})")
    else:
        scroll_text("\nThere's no one here to talk to.")
        pause()
        clear()

def cmd_status(state, target):
    """Shows health, relics, abilities, and quest progress."""
    clear()
    print(f"\n  {GOLD}GOLDEN BAT{RESET}")
    print(f"  HP {state.hp}/{MAX_HP}   ENERGY {state.energy}/{MAX_ENERGY}   DROPS OF WATER {state.drops}")
    print("\n  RELICS")
    for relic in state.relics():
        if relic in state.inventory:
            ability = state.items[relic].get("ability")
            passive = " (passive)" if ability and ability.get("passive") else ""
            print(f"    {relic}" + (f"  ->  {ability['name']}{passive}: {ability['summary']}" if ability else ""))
    print("\n  QUESTS")
    for line in quest_status(state):
        print(f"    {line}")
    input("\n  [ PRESS ENTER ]")
    clear()

def cmd_help(state, target):
    """Lists commands."""
    print(HELP_TEXT)
    input("  [ PRESS ENTER ]")
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
    scroll_text("\nInvalid action. Type 'help' for a list of commands.")
    pause()
    clear()

COMMANDS = {
    'laugh': cmd_laugh,
    'room': cmd_room,
    'search': cmd_search,
    'path': cmd_path,
    'go': cmd_go,
    'get': cmd_get,
    'use': cmd_use,
    'talk': cmd_talk,
    'status': cmd_status,
    'help': cmd_help,
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
