"""
Characters Module

Description: Conversations with Marie (hints, rest, quests, radio), Professor Yamatone
             (over the radio), and simple characters like the Bronze Sentinel. All
             dialogue comes from data/dialogue.json.
"""

from goldenbat.data import load_json
from goldenbat.save import save_game
from goldenbat.text import scroll_text, play_beats, pause, clear

DIALOGUE = load_json("dialogue.json")

def find_npc(state, target):
    """Returns the id of the character in this room matching the target name, or None."""
    npcs = state.room.get("npcs", [])
    if not target and len(npcs) == 1:
        return npcs[0]
    for npc_id in npcs:
        if target.lower() in DIALOGUE[npc_id]["aliases"]:
            return npc_id
    return None

def first_match(state, entries):
    """Returns the first entry whose requirements are met, or None."""
    return next((entry for entry in entries if state.meets(entry.get("requires"))), None)

def talk(state, npc_id):
    """Starts a conversation with a character."""
    if npc_id == "marie":
        talk_marie(state)
    else:
        talk_simple(state, npc_id)

def talk_simple(state, npc_id):
    """Plays the first available line or scene for a character, applying its effects once."""
    entry = first_match(state, DIALOGUE[npc_id]["talks"])
    clear()
    if "beats" in entry:
        play_beats(entry["beats"])
    else:
        scroll_text(entry["text"])
    state.flags.update(entry.get("set_flags", []))
    if entry.get("reward"):
        state.apply_reward(entry["reward"])
        if entry["reward"].get("drops"):
            scroll_text("(Marie's canteen gains a drop of water.)")
    pause()
    clear()

def ready_quests(state):
    """Marie's quests whose items the player is carrying and that aren't done yet."""
    return [quest for quest in DIALOGUE["marie"]["quests"]
            if quest["flag"] not in state.flags and all(item in state.inventory for item in quest["items"])]

def talk_marie(state):
    """Marie's conversation menu."""
    marie = DIALOGUE["marie"]
    clear()
    if "met_marie" not in state.flags:
        state.flags.add("met_marie")
        play_beats(marie["first_meeting"])
        pause()

    while True:
        clear()
        print(f"\n  {marie['name']}")
        options = [("Talk", talk_hint), ("Rest and save", rest)]
        if ready_quests(state):
            options.append(("Give", give_quest_items))
        if "radio_fixed" in state.flags:
            options.append(("Radio Professor Yamatone", radio_yamatone))
        options.append(("Leave", None))

        for number, (label, _) in enumerate(options, start = 1):
            print(f"    [{number}] {label}")
        choice = input("  > ").strip()
        if not (choice.isdigit() and 1 <= int(choice) <= len(options)):
            continue
        action = options[int(choice) - 1][1]
        if action is None:
            clear()
            return
        action(state)

def talk_hint(state):
    """Marie offers a hint based on story progress."""
    marie = DIALOGUE["marie"]
    hint = first_match(state, marie["hints"])
    clear()
    scroll_text(f"MARIE: '{hint['text'] if hint else marie['default_hint']}'")
    pause()

def rest(state):
    """Restores HP and Energy and saves the game."""
    clear()
    scroll_text(DIALOGUE["marie"]["rest"])
    state.restore()
    save_game(state)
    scroll_text("(HP and Energy restored. Game saved.)")
    pause()

def give_quest_items(state):
    """Hands Marie the items for every quest that's ready."""
    for quest in ready_quests(state):
        clear()
        for item in quest["items"]:
            state.inventory.remove(item)
        state.flags.add(quest["flag"])
        play_beats(quest["beats"])
        if quest.get("reward"):
            state.apply_reward(quest["reward"])
        scroll_text(f"(Quest complete: {quest['name']})")
        pause()

def radio_yamatone(state):
    """Professor Yamatone gives advice over the radio."""
    yamatone = DIALOGUE["yamatone"]
    line = first_match(state, yamatone["lines"])
    clear()
    scroll_text("Marie hands you the crackling radio...")
    scroll_text(f"{yamatone['name']}: '{line['text'] if line else yamatone['default']}'")
    pause()

def quest_status(state):
    """Returns a list of lines describing Marie's quests for the status screen."""
    lines = []
    for quest in DIALOGUE["marie"]["quests"]:
        if quest["flag"] in state.flags:
            progress = "complete"
        else:
            found = sum(item in state.inventory for item in quest["items"])
            progress = f"{found}/{len(quest['items'])} found, bring to Marie"
        lines.append(f"{quest['name']}: {progress}")
    return lines
