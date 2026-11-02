"""
Game Loop Module

Description: Loads game content, runs the title and prologue, and drives the main
             exploration loop until an ending or the player quits.
"""

from goldenbat.audio import audio
from goldenbat.data import load_json
from goldenbat.state import GameState
from goldenbat.commands import handle_command
from goldenbat.cinematics import display_title, intro_sequence, play_ending

def get_user_input(state):
    """
    Displays the current player location and inventory state, then prompts for command input.

    Returns:
        list: Tokenized user command split into [action, target].
    """
    print(f"\nLocation: {state.current_room}\nInventory: {state.inventory}")
    user_input = input(
        "Action (laugh / room / path / search / go [direction] / get [item] / quit): "
    ).lower().split(maxsplit = 1)

    if not user_input:
        return ['none']
    return user_input

def run():
    """Main execution loop."""
    story = load_json("story.json")
    state = GameState.new_game(load_json("rooms.json"), load_json("items.json"))

    # Launch sequence
    display_title()
    intro_sequence(story)

    # Main gameplay loop
    while True:
        audio.play_room_music(state.room.get("music"))

        # Entering the villain's room ends the game
        if 'villain' in state.room:
            play_ending(state, story)
            break

        if not handle_command(state, get_user_input(state)):
            break
