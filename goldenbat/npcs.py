"""
Characters Module

Description: Conversations with Marie (hints, rest, quests, radio), Professor Yamatone,
             and simpler characters like the Bronze Sentinel. All dialogue comes from
             data/dialogue.json.
"""

from goldenbat.data import load_json
from goldenbat.save import save_game
from goldenbat.text import scroll_text, play_beats, pause, clear

DIALOGUE = load_json("dialogue.json")

def find_npc(state, target):
    """Returns the id of the character in this room matching the target name, or None."""
    npcs = state.npcs()
    if not target and len(npcs) == 1:
        return npcs[0]
    for npc_id in npcs:
        if target.lower() in DIALOGUE[npc_id]["aliases"]:
            return npc_id
    return None

def npc_name(npc_id):
    """The short name players type to talk to a character, e.g. 'marie'."""
    return DIALOGUE[npc_id]["aliases"][0]

def first_match(state, entries):
    """Returns the first entry whose requirements are met, or None."""
    return next((entry for entry in entries if state.meets(entry.get("requires"))), None)

def talk(state, npc_id):
    """Starts a conversation with a character."""
    if npc_id == "marie":
        talk_marie(state)
    else:
        talk_simple(state, npc_id)

def give_reward(state, reward):
    """Applies a reward block and tells the player what they received."""
    if not reward:
        return
    state.apply_reward(reward)
    if reward.get("drops"):
        scroll_text("(Marie's canteen gains a drop of water.)")
    if reward.get("items"):
        scroll_text(f"(You received: {', '.join(reward['items'])})")

def talk_simple(state, npc_id):
    """Plays the first available line or scene for a character, applying its effects once."""
    entry = first_match(state, DIALOGUE[npc_id]["talks"])
    clear()
    if "beats" in entry:
        play_beats(entry["beats"])
    else:
        scroll_text(entry["text"])
    state.flags.update(entry.get("set_flags", []))
    give_reward(state, entry.get("reward"))
    pause()
    clear()

def quest_ready(state, quest):
    """True if a quest isn't done and its items and flags have all been collected."""
    return (quest["flag"] not in state.flags
            and all(item in state.inventory for item in quest.get("items", []))
            and all(flag in state.flags for flag in quest.get("flags_needed", [])))

def ready_quests(state):
    """Marie's quests that can be turned in right now."""
    return [quest for quest in DIALOGUE["marie"]["quests"] if quest_ready(state, quest)]

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
        if state.meets(DIALOGUE["radio"]["requires"]):
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
    """Marie offers a hint for the main story, plus one for any unfinished side quest."""
    marie = DIALOGUE["marie"]
    hint = first_match(state, marie["hints"])
    side_hint = first_match(state, marie["side_hints"])
    clear()
    scroll_text(f"MARIE: '{hint['text'] if hint else marie['default_hint']}'")
    if side_hint:
        scroll_text(f"MARIE: '{side_hint['text']}'")
    pause()

def rest(state):
    """Restores HP and Energy and saves the game."""
    clear()
    scroll_text(first_match(state, DIALOGUE["marie"]["rest"])["text"])
    state.restore()
    save_game(state)
    scroll_text("(HP and Energy restored. Game saved.)")
    pause()

def give_quest_items(state):
    """Hands Marie the items for every quest that's ready."""
    for quest in ready_quests(state):
        clear()
        for item in quest.get("items", []):
            state.inventory.remove(item)
        state.flags.add(quest["flag"])
        play_beats(quest["beats"])
        give_reward(state, quest.get("reward"))
        scroll_text(f"(Quest complete: {quest['name']})")
        pause()

def radio_yamatone(state):
    """Professor Yamatone gives advice over the radio."""
    radio = DIALOGUE["radio"]
    line = first_match(state, radio["lines"])
    clear()
    scroll_text("Marie hands you the crackling radio...")
    scroll_text(f"{radio['name']}: '{line['text'] if line else radio['default']}'")
    pause()

def quest_status(state):
    """Returns a list of lines describing Marie's quests for the status screen."""
    lines = []
    for quest in DIALOGUE["marie"]["quests"]:
        if not state.meets(quest.get("visible")):
            continue
        if quest["flag"] in state.flags:
            progress = "complete"
        else:
            needed = quest.get("items", []) + quest.get("flags_needed", [])
            found = (sum(item in state.inventory for item in quest.get("items", []))
                     + sum(flag in state.flags for flag in quest.get("flags_needed", [])))
            progress = f"{found}/{len(needed)} {quest['progress']}, then see Marie"
        lines.append(f"{quest['name']}: {progress}")
    return lines
