"""
Game State Module

Description: Holds the player's progress (location, inventory, story flags) and a live
             copy of the world map, which changes as items are picked up.
"""

import copy
from dataclasses import dataclass, field


@dataclass
class GameState:
    """Everything that changes during a playthrough."""
    rooms: dict
    items: dict
    current_room: str
    inventory: list = field(default_factory = list)
    flags: set = field(default_factory = set)

    @classmethod
    def new_game(cls, rooms_data, items):
        """Creates a fresh state from data/rooms.json and data/items.json."""
        return cls(rooms = copy.deepcopy(rooms_data["rooms"]), items = items,
                   current_room = rooms_data["start"])

    @property
    def room(self):
        """The data dictionary for the current room."""
        return self.rooms[self.current_room]

    def exits(self):
        """Returns the current room's visible exits, including unlocked hidden ones."""
        exits = dict(self.room.get("exits", {}))
        for direction, hidden in self.room.get("hidden_exits", {}).items():
            if hidden["flag"] in self.flags:
                exits[direction] = hidden["to"]
        return exits

    def visible_secrets(self):
        """Returns secret text lines in the current room whose flag has been set."""
        return [secret["text"] for secret in self.room.get("secrets", [])
                if secret["flag"] in self.flags]

    def has_all_relics(self):
        """True if every relic listed in data/items.json is in the inventory."""
        relics = [name for name, item in self.items.items() if item.get("relic")]
        return all(relic in self.inventory for relic in relics)
