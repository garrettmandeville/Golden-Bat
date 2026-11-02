"""
Text Display Module

Description: Controls the typewriter-style text scroller, its inline tags (colors,
             audio triggers, delays), and terminal screen clears.
"""

import sys, time, os
from goldenbat.audio import audio

# ANSI Terminal Colors
GOLD = '\033[33m'
RESET = '\033[0m'

def pause(seconds = 2.0):
    """Execution delay helper."""
    time.sleep(seconds)

def clear():
    """Cross-platform terminal screen clear."""
    os.system('cls' if os.name == 'nt' else 'clear')

def scroll_text(text, delay = 0.03, color = None):
    """
    Prints text character-by-character while parsing inline bracket tags.

    Supports:
        Audio tags: any SFX key from data/audio.json, e.g. [laugh], [marie1]
        Speed tags: [slow], [fast], [norm]
        Color tags: [gold], [reset]
        Wait tags:  [wait:seconds]
    """
    if color:
        sys.stdout.write(color)

    i = 0
    current_delay = delay
    while i < len(text):
        char = text[i]

        if char == "[":
            end_tag = text.find("]", i)
            if end_tag != -1:
                tag = text[i + 1:end_tag]

                # Audio triggers
                if tag in audio.sfx_keys:
                    audio.play_sfx(tag)
                # Speed triggers
                elif tag == "slow":
                    current_delay = 0.1
                elif tag == "fast":
                    current_delay = 0.01
                elif tag == "norm":
                    current_delay = 0.03
                # Color triggers
                elif tag == "gold":
                    sys.stdout.write(GOLD)
                elif tag == "reset":
                    sys.stdout.write(RESET)
                # Pause delays
                elif tag.startswith("wait"):
                    try:
                        seconds = float(tag.split(":")[1])
                        time.sleep(seconds)
                    except (ValueError, IndexError):
                        pass

                i = end_tag + 1
                continue

        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(current_delay)
        i += 1

    sys.stdout.write(RESET)
    print("\n")
