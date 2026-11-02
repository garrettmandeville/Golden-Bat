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
| **Marie Mire** | Base-camp ally: in the Ancient Tomb in Act I, then at Bell Landing beside the Super Car in Act II. Translates her late father's notes into hints, gives side quests, revives Golden Bat with drops of water, and saves the game. |
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
Yamatone's Super Car dives to the drowned city with Marie aboard and docks at Bell Landing,
which becomes the new camp. Nine rooms below the sea: the Sunken Stair, Bell Landing, the
Drowned Avenue, the Spirit Archive, the Coral Market, the Tide Temple and its Inner Sanctum,
the Hall of Champions, the Abyssal Stables, and the Drowned Harbor.

- **Act I relics open the way:** the Silver Baton shatters the archive's crystal seal, the
  Kinesis Stone clears the market rubble, and the Red Cape crosses the abyss to the stables.
- **Relics:** Swashbuckler Armor (Hall of Champions, lets you pass the temple's steam),
  Hydroflask (Inner Sanctum), Spectral Reins (Abyssal Stables, lets you ride to the harbor).
- **Boss:** Admiral Gorgo riding the Leviathan, an Atlantean war-machine he controls through
  cables. The Spectral Reins can turn its crushing attack back on it.
- **Side goal:** wake three sleeping spirits with the Hydroflask (the Archivist, the
  Merchant, and the Champion's ghost), then tell Marie (counts toward the True ending).
- **Story:** the empty lens cradle in the sanctum and the Archivist reveal that Gorgo's
  divers already sent the Eye of Atlantis to Nazō's fortress. Act II ends with Icarus
  visible in the sky.

### Act III — The Spectral Cannon
The Super Car resurfaces and overloads Nazō's barrier, and Marie and Yamatone make camp in
the Ancient Atlantean Lab. Behind it, the Hall of Ancient Tech is now the gate of Nazō's
fortress: the Assembly Bay, Orbital Control, the Generator Core, the Spectral Bridge, and the
Cannon Chamber. Icarus fills more of the sky with every scene.

- **Relic:** Icarus Data (Orbital Control). Its Analyze ability exposes a weak point.
- **Puzzle:** the Spectral Reins take command of the Atlantean generators to light the bridge.
- **Bosses:** Five Finger Mk II in the Assembly Bay, then Dr. Nazō in two phases. Halfway
  through, he merges with the Spectral Cannon (becoming a machine the Reins can seize), and
  the seven relics answer with a second wind for Golden Bat.
- **The door:** entering the Cannon Chamber asks for confirmation. There is no turning back,
  and no revives inside.

### Endings

| Ending | Condition |
|---|---|
| **Lose** | Defeated in the finale, or reaching it without all relics. |
| **Win** | Defeat Dr. Nazō with all seven relics. |
| **True** | Win, while carrying the Botan Rice Candy and having completed all three of Marie's quests: the Ship Radio, Father's Journal, and the Sleeping Spirits. |

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
When HP reaches 0, Marie revives Golden Bat at her camp with a drop of water, and he keeps his
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
  combat.py          Turn-based battles
  npcs.py            Marie, Yamatone's radio, other characters
  save.py            Save file
  data.py            JSON loading
  paths.py           File paths (works in PyInstaller builds)
data/                Content
  rooms.json         Map, exits, encounters, events, secrets, interactions
  items.json         Items, relics and their abilities, consumables
  enemies.json       Enemy stats, moves, and dialogue
  dialogue.json      Marie, Yamatone, and other characters; quests
  story.json         Cutscenes, endings, and ending conditions
  audio.json         Audio file names and keys
assets/              Audio files (not distributed)
```

Story text supports inline tags: `[slow]`, `[fast]`, `[norm]`, `[gold]`, `[reset]`,
`[wait:seconds]`, and any sound-effect key from `audio.json` (e.g. `[laugh]`).

## Build plan

Each phase is playable and committed on its own.

1. ✅ **Engine and data files.** The classic game rebuilt on the new engine, playing the same as `classic`.
2. ✅ **Act I.** HP, Energy, combat, relic abilities, Marie, saving, and the Act I content.
3. ✅ **Act II.** The Sunken City. Each act break restores HP and Energy and autosaves.
4. ✅ **Act III.** The fortress, the finale, the endings, and README updates.
