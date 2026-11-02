"""
Combat Module

Description: Turn-based battles. Each round the player picks Attack, Ability, Item,
             Laugh, or Flee, then the enemy performs the move it telegraphed.
             Enemies are defined in data/enemies.json; relic abilities in data/items.json.
"""

import random
from goldenbat.audio import audio
from goldenbat.data import load_json
from goldenbat.state import MAX_HP, MAX_ENERGY
from goldenbat.text import scroll_text, pause, clear, GOLD, RED, RESET

ENEMIES = load_json("enemies.json")

STRIKE_DAMAGE = (6, 9)
FLEE_CHANCE = 0.6
LAUGH_FRIGHT_CHANCE = 0.4
# Only living things can be frightened by the laugh
FEARFUL_KINDS = ("human", "beast")


class Battle:
    """One fight between Golden Bat and a single enemy."""

    def __init__(self, state, enemy_id):
        self.state = state
        self.enemy = ENEMIES[enemy_id]
        self.name = self.enemy["name"]
        self.enemy_hp = self.enemy["hp"]
        self.turn = 0
        self.vanished = False
        self.enemy_skips = False
        self.log = []

    # ---- Helpers ----

    def next_move(self):
        """The enemy's upcoming move; moves cycle in the order listed."""
        moves = self.enemy["moves"]
        return moves[self.turn % len(moves)]

    def is_spirit(self):
        return self.enemy["kind"] == "spirit"

    def damage_enemy(self, amount, effect = None):
        """Deals damage (doubled if the enemy is weak to the effect) and logs it."""
        if effect in self.enemy.get("weak_to", []):
            amount *= 2
            self.log.append("It's a weak point!")
        self.enemy_hp = max(0, self.enemy_hp - amount)
        self.log.append(f"{amount} damage to {self.name}.")

    def abilities(self):
        """Abilities granted by relics in the inventory, in relic order."""
        return [self.state.items[name]["ability"] for name in self.state.relics()
                if name in self.state.inventory and "ability" in self.state.items[name]]

    def consumables(self):
        """Unique consumable item names in the inventory."""
        return [name for name in dict.fromkeys(self.state.inventory)
                if self.state.items[name].get("consumable")]

    # ---- Display ----

    def render(self):
        """Draws the battle panel, last round's log, the enemy's telegraph, and the menu."""
        clear()
        state = self.state
        print("=" * 60)
        print(f"  {GOLD}GOLDEN BAT{RESET}   HP {state.hp}/{MAX_HP}   ENERGY {state.energy}/{MAX_ENERGY}"
              f"{'   (VANISHED)' if self.vanished else ''}")
        print(f"  {RED}{self.name}{RESET}   HP {self.enemy_hp}/{self.enemy['hp']}")
        print("=" * 60)
        for line in self.log:
            print(f"  {line}")
        self.log = []
        print(f"\n  NEXT: {self.next_move()['telegraph']}")
        print("\n  [1] Attack   [2] Ability   [3] Item   [4] Laugh   [5] Flee")

    def choose(self, options):
        """Prompts for a numbered choice from a submenu. Returns the option or None to go back."""
        for number, (label, _) in enumerate(options, start = 1):
            print(f"    [{number}] {label}")
        print("    [0] Back")
        choice = input("  > ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1][1]
        return None

    # ---- Player actions (each returns True if it used the turn) ----

    def attack(self):
        if self.is_spirit():
            self.log.append("Your strike passes through the spirit like smoke!")
        else:
            self.log.append("Golden Bat strikes with a bony fist!")
            self.damage_enemy(random.randint(*STRIKE_DAMAGE))
        # Striking builds Energy for abilities
        self.state.energy = min(MAX_ENERGY, self.state.energy + 1)
        return True

    def use_ability(self):
        options = [(f"{a['name']} ({a['cost']} EN) - {a['summary']}", a) for a in self.abilities()]
        if not options:
            print("\n  You have no abilities yet. Relics grant them.")
            pause(1.5)
            return False
        ability = self.choose(options)
        if ability is None:
            return False
        if self.state.energy < ability["cost"]:
            print("\n  Not enough Energy. Attack to build it up.")
            pause(1.5)
            return False

        self.state.energy -= ability["cost"]
        self.log.append(ability["text"].format(enemy = self.name))
        effect = ability["effect"]

        if effect == "damage":
            if self.is_spirit() and not ability.get("hits_spirits"):
                self.log.append("It has no effect on the spirit!")
            else:
                self.damage_enemy(random.randint(*ability["damage"]), effect)
        elif effect == "push":
            if self.is_spirit():
                self.log.append("The wind passes straight through the spirit!")
            else:
                self.damage_enemy(random.randint(*ability["damage"]), effect)
                # Bosses can't be staggered, but a heavy attack can still be interrupted
                if not self.enemy.get("boss") or self.next_move().get("heavy"):
                    self.enemy_skips = True
                    self.log.append(f"{self.name} is knocked off balance!")
        elif effect == "vanish":
            self.vanished = True
        return True

    def use_item(self):
        options = [(f"{name} x{self.state.inventory.count(name)}", name) for name in self.consumables()]
        if not options:
            print("\n  You have no usable items.")
            pause(1.5)
            return False
        name = self.choose(options)
        if name is None:
            return False
        self.log.append(use_consumable(self.state, name))
        return True

    def laugh(self):
        audio.play_sfx("laugh")
        self.log.append(f"{GOLD}GOLDEN BAT: 'HA-HA-HA-HA-HAAA!'{RESET}")
        if self.enemy["kind"] in FEARFUL_KINDS and random.random() < LAUGH_FRIGHT_CHANCE:
            self.enemy_skips = True
            self.log.append(f"{self.name} freezes in terror!")
        elif self.enemy["kind"] in FEARFUL_KINDS:
            self.log.append(f"{self.name} trembles, but holds its ground.")
        else:
            self.log.append(f"{self.name} does not know fear.")
        return True

    # ---- Enemy turn ----

    def enemy_turn(self):
        move = self.next_move()
        self.turn += 1
        if self.enemy_skips:
            self.enemy_skips = False
            self.log.append(f"{self.name} loses its chance to attack!")
        elif self.vanished:
            self.vanished = False
            self.log.append(f"{move['name']}! It strikes only empty air.")
        else:
            damage = random.randint(*move["damage"])
            self.state.hp = max(0, self.state.hp - damage)
            self.log.append(f"{RED}{move['name']}! You take {damage} damage.{RESET}")

    # ---- Main loop ----

    def run(self):
        """Runs the battle. Returns "won", "fled", or "lost"."""
        clear()
        scroll_text(self.enemy["intro"])
        scroll_text(f"{GOLD}GOLDEN BAT: '{self.enemy['bat_line']}'{RESET}")
        pause()

        while True:
            self.render()
            choice = input("  > ").strip()

            if choice == '5':
                if self.enemy.get("boss"):
                    print("\n  There is no escape from this fight!")
                    pause(1.5)
                    continue
                if self.vanished or random.random() < FLEE_CHANCE:
                    return "fled"
                self.log.append("You try to flee, but the way is blocked!")
                used_turn = True
            else:
                actions = {'1': self.attack, '2': self.use_ability, '3': self.use_item, '4': self.laugh}
                action = actions.get(choice)
                used_turn = action() if action else False

            if not used_turn:
                continue
            if self.enemy_hp <= 0:
                return "won"
            self.enemy_turn()
            if self.state.hp <= 0:
                return "lost"

    def victory(self):
        """Shows the victory screen and hands out Energy and loot."""
        clear()
        scroll_text(self.enemy["defeat"])
        self.state.energy = min(MAX_ENERGY, self.state.energy + 1)
        for item in self.enemy.get("loot", []):
            self.state.inventory.append(item)
            audio.play_sfx("item")
            scroll_text(f"{self.name} dropped a {item}!")
        pause()
        clear()


def use_consumable(state, name):
    """Applies a consumable's effects, removes it from the inventory, and returns a message."""
    item = state.items[name]
    state.inventory.remove(name)
    gained = []
    if item.get("heal_hp"):
        before = state.hp
        state.hp = min(MAX_HP, state.hp + item["heal_hp"])
        gained.append(f"+{state.hp - before} HP")
    if item.get("restore_energy"):
        before = state.energy
        state.energy = min(MAX_ENERGY, state.energy + item["restore_energy"])
        gained.append(f"+{state.energy - before} Energy")
    return f"You use the {name}. ({', '.join(gained)})"

def fight(state, enemy_id):
    """Starts a battle. Returns "won", "fled", or "lost"."""
    battle = Battle(state, enemy_id)
    result = battle.run()
    if result == "won":
        battle.victory()
    return result
