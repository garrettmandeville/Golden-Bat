# GOLDEN BAT 🦇

**Golden Bat** is a text-based atmospheric adventure game written in Python. Explore the ruins of Atlantis, collect 7 legendary relics, and defeat the mysterious Dr. Nazō before the rogue planet Icarus crashes into Earth!

> **Unofficial fan game.** Inspired by the 1967 anime *Golden Bat* (*Ōgon Bat*). Not affiliated with or endorsed by the rights holders. See [Disclaimer](#%EF%B8%8F-disclaimer).

## 🌟 Features
- **Classic Text-Adventure Gameplay:** Navigate rooms, search for items, and uncover secrets using terminal commands.
- **Optional Audio:** Per-room music and sound effects via `pygame.mixer`. Audio files aren't included; the game runs silently without them, and picks up any you add (see [assets/README.md](assets/README.md)).
- **Multiple Endings:** Your inventory and exploration determine the fate of Earth. Can you unlock the True Ending?
- **Retro Terminal Aesthetic:** Dynamic scrolling text with inline delays, color formatting, and cinematic screen clears.

## 🎮 How to Play

### Playing the Executable (No Python Required)
1. Go to the **Releases** tab on the right side of this repository.
2. Download the `GoldenBat` executable for your operating system.
3. Double-click the file to launch the game! (A terminal window will open automatically).

### Running from Source
If you want to run or modify the raw Python code:
1. Ensure you have Python 3.x installed.
2. Clone this repository to your local machine.
3. Install the required dependencies:
   ```bash
   pip install pygame-ce
   ```
4. Run the main script:
   ```bash
   python main.py
   ```

### Building the Executable
```bash
pip install pyinstaller
python -m PyInstaller main.spec
```
The executable appears in `dist/`. The build bundles everything in `assets/`, so only build from a folder containing audio you have the rights to distribute.

## 🕹️ Commands
Type these actions when prompted to interact with the world:
- `go [direction]` - Move to an adjacent room (e.g., `go north`, `go east`).
- `get [item]` - Pick up a relic or item in the room (e.g., `get Red Cape`).
- `use [item]` - Use an item, or a relic on something in the room (e.g., `use coral salve`).
- `talk [name]` - Talk to someone nearby (e.g., `talk marie`).
- `search` - Inspect your current surroundings for hidden items or secrets.
- `path` - View all available exits from your current location.
- `room` - Re-read the narrative description of your current location.
- `status` - Check your health, relics, abilities, and quests.
- `laugh` - Unleash the signature Golden Bat laugh!
- `help` - List all commands.
- `quit` - Abandon the mission and exit the game.

### ⚔️ Combat
Enemies announce their next move before you act. Each turn, choose to **Attack** (builds Energy), use a relic **Ability** (costs Energy), use an **Item**, **Laugh** (may freeze living foes with terror), or **Flee**. If Golden Bat falls, Marie revives him in the tomb with a drop of water — but her canteen won't last forever. Talk to Marie to rest and save.

## 🗂️ Project Structure
```
main.py        Entry point
goldenbat/     Game engine (game loop, commands, cinematics, text, audio)
data/          Game content as JSON (rooms, items, story, audio config)
assets/        Audio files (not included)
docs/          Design document
```
Rooms, items, and story text live in `data/`, so new content can be written without touching the engine. The roadmap for the expanded three-act version is in [docs/DESIGN.md](docs/DESIGN.md). The original 12-room version is preserved on the `classic` branch.

## 🛠️ Built With
* **Python 3**
* **pygame-ce** - Utilized for the audio engine (BGM loops, SFX playback, and volume fading).

## ⚖️ Disclaimer
This is a non-commercial fan project. *Golden Bat* (*Ōgon Bat*) and its characters belong to their respective rights holders. All code and original story content in this repository are by the author.

## 👨‍💻 Author
**Garrett Mandeville**
