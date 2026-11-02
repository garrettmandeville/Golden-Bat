"""
Game State Module

Description: Holds the player's progress (location, stats, inventory, story flags) and a
             live copy of the world map, which changes as items are picked up.
"""

import copy
from dataclasses import dataclass, field

MAX_HP = 50
MAX_ENERGY = 5
STARTING_DROPS = 3


@dataclass
class GameState:
    """Everything that changes during a playthrough."""
    rooms: dict
    items: dict
    current_room: str
    # Rooms where Marie keeps camp, from data/rooms.json; the last one unlocked is used
    camps: list = field(default_factory = list)
    inventory: list = field(default_factory = list)
    flags: set = field(default_factory = set)
    visited: set = field(default_factory = set)
    hp: int = MAX_HP
    energy: int = MAX_ENERGY
    drops: int = STARTING_DROPS
    previous_room: str = None
    # True when the player has just arrived, so room events and encounters should run
    just_entered: bool = True

    @classmethod
    def new_game(cls, rooms_data, items):
        """Creates a fresh state from data/rooms.json and data/items.json."""
        return cls(rooms = copy.deepcopy(rooms_data["rooms"]), items = items,
                   current_room = rooms_data["start"], camps = rooms_data["camps"])

    @property
    def room(self):
        """The data dictionary for the current room."""
        return self.rooms[self.current_room]

    def meets(self, requires):
        """
        Checks a 'requires' block from the data files against the current state.

        Supported keys: flags, not_flags, items, not_items, all_relics.
        """
        requires = requires or {}
        if requires.get("all_relics") and not self.has_all_relics():
            return False
        return (all(flag in self.flags for flag in requires.get("flags", []))
                and not any(flag in self.flags for flag in requires.get("not_flags", []))
                and all(item in self.inventory for item in requires.get("items", []))
                and not any(item in self.inventory for item in requires.get("not_items", [])))

    def all_exits(self):
        """Returns every exit of the current room as {direction: exit dict}."""
        exits = {}
        for direction, value in self.room.get("exits", {}).items():
            # An exit is either a room name or a dict with requirements
            exits[direction] = {"to": value} if isinstance(value, str) else value
        return exits

    def exits(self):
        """Returns the exits the player can see (hidden ones only once unlocked)."""
        return {direction: exit for direction, exit in self.all_exits().items()
                if not exit.get("hidden") or self.meets(exit.get("requires"))}

    def visible_texts(self, key):
        """Returns the text of each entry in room[key] whose requirements are met."""
        return [entry["text"] for entry in self.room.get(key, []) if self.meets(entry.get("requires"))]

    def npcs(self):
        """Ids of the characters currently in this room (entries may have requirements)."""
        ids = []
        for entry in self.room.get("npcs", []):
            entry = {"id": entry} if isinstance(entry, str) else entry
            if self.meets(entry.get("requires")):
                ids.append(entry["id"])
        return ids

    def camp(self):
        """The room where Marie currently keeps camp (and revives Golden Bat)."""
        return [camp["room"] for camp in self.camps if self.meets(camp.get("requires"))][-1]

    def next_encounter(self):
        """Returns the first undefeated encounter in this room whose requirements are met."""
        for encounter in self.room.get("encounters", []):
            if encounter["flag"] not in self.flags and self.meets(encounter.get("requires")):
                return encounter
        return None

    def relics(self):
        """Names of all relics, in data/items.json order."""
        return [name for name, item in self.items.items() if item.get("relic")]

    def has_all_relics(self):
        """True if every relic listed in data/items.json is in the inventory."""
        return all(relic in self.inventory for relic in self.relics())

    def move_to(self, room_name):
        """Places the player in a room as if they had just arrived."""
        self.previous_room = None
        self.current_room = room_name
        self.just_entered = True

    def apply_reward(self, reward):
        """Applies a reward block: {"drops": n, "items": [...], "flags": [...]}."""
        reward = reward or {}
        self.drops += reward.get("drops", 0)
        self.inventory.extend(reward.get("items", []))
        self.flags.update(reward.get("flags", []))

    def restore(self):
        """Fully restores HP and Energy."""
        self.hp = MAX_HP
        self.energy = MAX_ENERGY

    def to_save(self):
        """Converts the state into a JSON-friendly dict."""
        return {
            "current_room": self.current_room,
            "inventory": self.inventory,
            "flags": sorted(self.flags),
            "visited": sorted(self.visited),
            "hp": self.hp,
            "energy": self.energy,
            "drops": self.drops,
            "room_items": {name: room.get("items", []) for name, room in self.rooms.items()},
        }

    @classmethod
    def from_save(cls, save, rooms_data, items):
        """Rebuilds a state from a dict made by to_save()."""
        state = cls.new_game(rooms_data, items)
        state.current_room = save["current_room"]
        state.inventory = save["inventory"]
        state.flags = set(save["flags"])
        state.visited = set(save["visited"])
        state.hp, state.energy, state.drops = save["hp"], save["energy"], save["drops"]
        for name, room_items in save["room_items"].items():
            if name in state.rooms:
                state.rooms[name]["items"] = room_items
        state.just_entered = False
        return state
