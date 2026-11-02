"""
Cinematics Module

Description: Title card, prologue, objective screen, and scripted endings. All story
             text comes from data/story.json.
"""

import os, time, textwrap
from goldenbat.audio import audio
from goldenbat.text import scroll_text, pause, clear, GOLD, RESET

def display_title():
    """Displays ASCII title card and plays title BGM."""
    clear()
    audio.play_bgm("title")
    audio.play_sfx("bats")
    if 'TERM' not in os.environ:
        os.environ['TERM'] = 'xterm'

    title = r"""

    ______________________________________________________________________
        ______ ____   __     ____   ______ _   __     ____   ___   ______
       / ____// __ \ / /    / __ \ / ____// | / /    / __ ) /   | /_  __/
      / / __ / / / // /    / / / // __/  /  |/ /    / __  |/ /| |  / /
     / / / // /_/ // /___ / /_/ // /___ / /|  /    / /_/ // ___ | / /
     \____/ \____//_____//_____//_____//_/ |_/    /_____//_/  |_|/_/
    _____________________________________________________________________

    """

    print(GOLD + title + RESET)
    input(f"{GOLD}                           [ PRESS ENTER TO AWAKEN ]{RESET}")
    clear()

def play_beats(beats):
    """Scrolls a list of story beats ({text, pause, clear}) from data/story.json."""
    for beat in beats:
        wrapped = textwrap.fill(beat["text"], width = 70)
        scroll_text(wrapped)
        time.sleep(beat["pause"])
        if beat["clear"]:
            clear()

def intro_sequence(story):
    """Prompts player to read or skip the prologue, then shows the objective screen."""
    while True:
        skip = input("\n\nWould you like to read the prologue? (y/n): ").lower()
        if skip == 'y':
            clear()
            audio.play_bgm("intro")
            play_beats(story["prologue"])
            audio.play_sfx("laugh")
            scroll_text(story["prologue_laugh"], delay = 0.1)
            break
        elif skip == 'n':
            break
        else:
            print("\nInvalid input. Please try again and enter 'y' or 'n'.\n")
            pause(3.0)
            clear()

    game_start_message(story)

def game_start_message(story):
    """Displays opening objective header prior to entering world map loop."""
    clear()
    audio.stop()
    audio.play_sfx("scifi")
    scroll_text(story["game_start"])
    pause(3.0)
    clear()

def requirements_met(state, requires):
    """Checks an ending's 'requires' block from data/story.json against the game state."""
    if requires.get("all_relics") and not state.has_all_relics():
        return False
    return all(item in state.inventory for item in requires.get("items", []))

def play_ending(state, story):
    """Plays the first ending in data/story.json whose requirements are met."""
    ending = next(e for e in story["endings"] if requirements_met(state, e["requires"]))

    audio.stop()
    audio.play_bgm("boss")
    clear()
    play_beats(ending["beats"])

    # Render final banner
    audio.play_bgm(ending["credits"])
    print("\n" + "*" * 30)
    scroll_text(ending["banner"], delay = 0.1, color = GOLD)
    scroll_text(ending["message"], delay = 0.1)
    print("*" * 30)

    if "sfx_after_banner" in ending:
        audio.play_sfx(ending["sfx_after_banner"])

    audio.fade(10000)
