# Golden Bat — Design Document

An unofficial fan game inspired by the 1967 anime *Golden Bat* (*Ōgon Bat*). This document
describes the expanded three-act version. The original 12-room game is preserved on the
`classic` branch (tag `v1.1.0`).

## Tone

Pulp and eerie, like a late-60s Saturday serial:

- An all-caps narrator, cliffhanger act breaks, and nods to the *kamishibai* paper-theatre
  roots of the character (the Echoing Gallery, the Botan Rice Candy).
- A lonely, ruined Atlantis: wind, waves, dead machines, and the ghosts of a lost people.
- **Golden Bat** is the world's first superhero, but he looks like something out of a
  nightmare: a golden skull, a black cape, and a laugh that shakes stone. He is looming and
  frightening, yet entirely righteous. He speaks in short, grave, heroic lines, and the laugh
  is his signature.

> GOLDEN BAT: "Ten thousand years I have slept. Ten thousand years evil has waited.
> Tremble, Nazō. Justice is awake."

## Characters

| Character | Role |
|---|---|
| **Golden Bat** | The player. Ancient god of justice awakened in the Ancient Tomb. |
| **Marie Mire** | Base-camp ally in the Ancient Tomb. Translates her late father's notes into hints, gives side quests, revives Golden Bat with drops of water, and saves the game. |
| **Professor Yamatone** | Inventor from the Pearl Research Institute. Reaches Marie by radio in Act I, arrives by Super Car in Act II, and helps aim the cannon in Act III. Rewards side quests with gadgets. |
| **Dr. Nazō** | Mad scientist who sent the rogue planet Icarus toward Earth. Final boss. |
| **Five Finger** | Nazō's giant mechanical robot. Act I boss; Act III rematch. |
| **Admiral Gorgo** *(original, placeholder name)* | Nazō's lieutenant, a cyborg naval officer who commands a sea beast with stolen Atlantean tech. Act II boss. |

## Story

### Act I — The Ruins of Atlantis
Golden Bat wakes in the tomb. Nazō's soldiers are excavating the ruins in search of the
special lens.

- **Map:** the original 12 rooms, fleshed out with enemies, characters, and secrets.
- **Relics:** Silver Baton, Red Cape, Kinesis Stone.
- **Boss:** Five Finger attacks the Shipwrecked Beach and is driven off, not destroyed.
- **Cliffhanger:** the Observation Deck floor cracks open onto a drowned city.

### Act II — The Sunken City
Roughly 8–10 new rooms below the sea: drowned avenues, a spirit archive, a tide temple.

- **Relics:** Swashbuckler Armor, Hydroflask, Spectral Reins.
- **Boss:** Admiral Gorgo and his sea beast.
- **Side goal:** free the trapped spirits of Atlantis (counts toward the True ending).

### Act III — The Spectral Cannon
The Hall of Ancient Tech becomes Nazō's fortress, about 6 rooms. Icarus grows larger in the
sky with every scene.

- **Relic:** Icarus Data.
- **Bosses:** Five Finger rematch, then a multi-phase battle with Dr. Nazō.

### Endings

| Ending | Condition |
|---|---|
| **Lose** | Defeated in the finale, or reaching it without all relics. |
| **Win** | All seven relics. |
| **True** | All relics, the Botan Rice Candy, Marie's side quests completed, and the spirits freed. |

## Systems

### Stats
- **HP** — damage taken in combat.
- **Energy** — spent on relic abilities; restored by resting with Marie or by items.

Golden Bat grows stronger only through relics and found items. There is no XP or levelling.

### Combat
Turn-based menu: **Attack / Ability / Item / Flee**. Enemies telegraph their next move, and
some have weaknesses or immunities (spirits can only be hurt by Silver Ray or Living Water).

### Relics

| Relic | Combat ability | In the world |
|---|---|---|
| Silver Baton | **Silver Ray** — heavy damage | Shatters crystal seals |
| Red Cape | **Vanish** — dodge the next attack; guaranteed flee | Flies across chasms |
| Kinesis Stone | **Gale Push** — stuns an enemy | Moves rubble; opens the tomb's secret passage |
| Swashbuckler Armor | **Iron Guard** — passive damage reduction | Walks through steam vents |
| Hydroflask | **Living Water** — heals; harms spirits | Wakes sleeping spirits |
| Spectral Reins | **Bind** — tame an enemy for one turn | Rides ancient machines |
| Icarus Data | **Analyze** — reveals an enemy's weakness | Required to aim the cannon |

### Enemies
- **Nazō's forces:** masked troopers, digging drones, sentry robots.
- **Atlantean guardians:** stone and crystal constructs that test intruders; some can be reasoned with.
- **Sea monsters:** creatures of the deep around the beach and the Sunken City.
- **Spirits of Atlantis:** ghosts of the lost people; only certain relics affect them.

### Defeat
When HP reaches 0, Marie revives Golden Bat in the tomb with a drop of water, and he keeps his
items. She has a limited number of drops (more can be found). When they run out, the game is
over and the player loads their last save.

### Saving
Talking to Marie saves the game, and an autosave happens at each act break. The title screen
offers **Continue** when a save exists.

## Architecture

```
main.py              Entry point
goldenbat/           Engine
  game.py            Main loop
  state.py           Player and world state
  commands.py        Exploration commands
  cinematics.py      Title, prologue, endings
  text.py            Typewriter text and inline tags
  audio.py           Optional music and sound effects
  data.py            JSON loading
  paths.py           File paths (works in PyInstaller builds)
data/                Content
  rooms.json         Map, descriptions, exits, secrets, room music
  items.json         Items, relics, pickup effects
  story.json         Prologue, endings, and ending conditions
  audio.json         Audio file names and keys
assets/              Audio files (not distributed)
```

Story text supports inline tags: `[slow]`, `[fast]`, `[norm]`, `[gold]`, `[reset]`,
`[wait:seconds]`, and any sound-effect key from `audio.json` (e.g. `[laugh]`).

## Build plan

Each phase is playable and committed on its own.

1. **Engine and data files.** The classic game rebuilt on the new engine, playing the same as `classic`.
2. **Act I.** HP, Energy, combat, relic abilities, Marie, saving, and the Act I content.
3. **Act II.** The Sunken City.
4. **Act III.** The fortress, the finale, the three endings, and README updates.
