"""
Game Loop Module

Description: Loads game content, runs the title and prologue, and drives the main
             exploration loop: room events, encounters, defeat, and player commands.
"""

from goldenbat.audio import audio
from goldenbat.combat import fight
from goldenbat.data import load_json
from goldenbat.save import save_exists, save_game, load_game
from goldenbat.state import GameState, MAX_HP, MAX_ENERGY
from goldenbat.commands import handle_command, describe_room
from goldenbat.cinematics import display_title, intro_sequence, play_ending
from goldenbat.text import scroll_text, play_beats, pause, clear

# Marie keeps watch here and revives Golden Bat when he falls
REVIVE_ROOM = "Ancient Tomb"

def get_user_input(state):
    """
    Displays the current location, stats, and inventory, then prompts for command input.

    Returns:
        list: Tokenized user command split into [action, target].
    """
    print(f"\nLocation: {state.current_room}")
    print(f"HP {state.hp}/{MAX_HP} | ENERGY {state.energy}/{MAX_ENERGY} | DROPS OF WATER {state.drops}")
    counts = {name: state.inventory.count(name) for name in state.inventory}
    print("Inventory: " + (", ".join(name + (f" x{n}" if n > 1 else "") for name, n in counts.items()) or "empty"))
    user_input = input("Action (type 'help' for commands): ").lower().split(maxsplit = 1)

    if not user_input:
        return ['none']
    return user_input

def run_room_events(state, story):
    """Plays any one-time events in the room whose requirements are met."""
    for event in state.room.get("events", []):
        seen_flag = f"event_{event['id']}"
        if seen_flag not in state.flags and state.meets(event.get("requires")):
            state.flags.add(seen_flag)
            state.flags.update(event.get("set_flags", []))
            clear()
            play_beats(story[event["beats"]])
            pause()
            clear()

def handle_defeat(state, story):
    """
    Marie revives Golden Bat if she has water left.

    Returns:
        bool: True if revived; False if the game is over.
    """
    clear()
    if state.drops == 0:
        play_beats(story["game_over"])
        pause()
        return False
    state.drops -= 1
    play_beats(story["revive"])
    state.restore()
    state.current_room = REVIVE_ROOM
    state.just_entered = False
    scroll_text(f"(Drops of water remaining: {state.drops})")
    pause()
    clear()
    return True

def enter_room(state, story):
    """
    Runs everything that happens on arriving in a room.

    Returns:
        str: "continue", "act_end", or "game_over".
    """
    state.just_entered = False
    if state.current_room not in state.visited:
        state.visited.add(state.current_room)
        describe_room(state)
        pause()
    run_room_events(state, story)

    encounter = state.next_encounter()
    if not encounter:
        return "continue"

    result = fight(state, encounter["enemy"])
    if result == "fled":
        state.current_room, state.previous_room = state.previous_room or state.current_room, state.current_room
        clear()
        scroll_text(f"You retreat to the {state.current_room}...")
        pause()
        clear()
    elif result == "lost":
        if not handle_defeat(state, story):
            return "game_over"
    else:
        state.flags.add(encounter["flag"])
        victory = encounter.get("victory", {})
        state.flags.update(victory.get("set_flags", []))
        if "beats" in victory:
            play_beats(story[victory["beats"]])
        if victory.get("end_act"):
            save_game(state)
            return "act_end"
    return "continue"

def play(state, story):
    """
    Main gameplay loop.

    Returns:
        str: "quit", "ending", "act_end", or "game_over".
    """
    while True:
        audio.play_room_music(state.room.get("music"))

        # Entering the villain's room ends the game
        if 'villain' in state.room:
            play_ending(state, story)
            return "ending"

        if state.just_entered:
            result = enter_room(state, story)
            if result != "continue":
                return result
            # An event or fight may have moved the player, so start over
            continue

        if not handle_command(state, get_user_input(state)):
            return "quit"

def run():
    """Title screen, new game or continue, and game over handling."""
    story = load_json("story.json")
    rooms_data, items = load_json("rooms.json"), load_json("items.json")

    choice = display_title(has_save = save_exists())
    state = load_game(rooms_data, items) if choice == "continue" else None
    if state is None:
        state = GameState.new_game(rooms_data, items)
        intro_sequence(story)

    while True:
        if "act1_complete" in state.flags:
            clear()
            scroll_text(story["act_continue"])
            pause(3.0)
            return

        result = play(state, story)
        if result == "act_end":
            # Loops back to the act check above
            continue
        if result != "game_over":
            return

        # Out of water: offer to load the last save
        if save_exists() and input("\nLoad your last save? (y/n): ").lower().strip() == 'y':
            state = load_game(rooms_data, items) or GameState.new_game(rooms_data, items)
            clear()
            continue
        return
