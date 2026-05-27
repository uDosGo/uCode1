# uCode1 — Grid/Cell Foundation Layer

**Ownership:** uDosGo  
**Core Language:** Python  
**CLI Command:** `ucode` (runtime/educational)  
**Status:** 🟢 Active  
**Size:** ~8M / 25K lines

---

## Overview

uCode1 is the **foundation layer** of the uDos ecosystem. It provides the spatial grid/cell coordinate system and a BBC BASIC-inspired scripting runtime. Higher layers (uCode2-4) may import from uCode1, but uCode1 never imports from them.

### What uCode1 Owns

- **BBC BASIC interpreter** — Run `.bas` scripts with modern extensions
- **Grid/Cell coordinate system** — Spatial addressing format (`L100-AA10-0317-2`)
- **Teletext/MODE 7 graphics** — Character-based rendering
- **Cell storage** — SQLite-backed cell database

### What Belongs to Other Layers

| Feature | Layer | Why |
|---------|-------|-----|
| Vault Bridge (filesystem ops) | uCode2 | I/O services layer |
| Feed Spool (event management) | uCode2 | I/O services layer |
| MCP Gateway (IPC) | uCode2 | I/O services layer |
| Sprites & BOBs (visual rendering) | uCode2 | Consumes uCode1 grid format |
| Spatial primitives | uCode2 | Consumes uCode1 grid format |
| Home media, automation | uCode3 | Application layer |
| 3D worlds, portals | uCode4 | Application layer |

### Dependency Rule

```
uCode1 ──► uCode2 ──► uCode3 ──► uCode4
  (none)    (uses 1)   (uses 2)   (uses 2,1)
```

Each layer may only depend on layers below it. uCode1 has zero dependencies.

---

## CLI: `ucode` (Runtime/Educational)

```
ucode <command> [arguments] [flags]
```

| Command | Purpose | Example |
|---------|---------|---------|
| `run` | Execute BASIC file | `ucode run hello.bas` |
| `list` | List available programs | `ucode list` |
| `load` | Load program into memory | `ucode load adventure.bas` |
| `save` | Save current program | `ucode save mygame.bas` |
| `new` | Clear current program | `ucode new` |
| `cell` | Cell operations | `ucode cell show L100-AA10-0317-2` |
| `cube` | Cube operations | `ucode cube create L100-AA10-0317` |
| `grid` | Grid-level operations | `ucode grid export --level 100 --format json` |
| `map` | Map-level operations | `ucode map render --world L100` |
| `locate` | Position within grid | `ucode locate L100-AA10-0000-0 X=100 Y=50` |
| `move` | Animate movement | `ucode move L100-AA10-0000-0 TO 200,100 STEP 10` |
| `collide` | Check collision | `ucode collide L100-AA10-0000-0` |
| `sound` | Audio playback | `ucode play sound alert.wav` |
| `print` | Output to console | `ucode print "Hello, uDos!"` |
| `input` | Read user input | `ucode input "Your name? " name$` |
| `let` | Variable assignment | `ucode let score = 100` |
| `wait` | Delay execution | `ucode wait 50` |

---

## Architecture

```
uCode1 (Python)
├── Interpreter       — BBC BASIC parser & runtime
├── Grid Engine       — Spatial coordinate system (24×24 cells)
├── Cell Storage      — SQLite-backed cell database
├── Teletext Renderer — MODE 7 character graphics
├── Ceefax Bridge     — Teletext grid rendering + CEETEX RSS reader
├── Snack System      — Pluggable app runner (textual-based)
├── LENS/SKIN/MCP     — State capture, theme hot-reload, remote control (⚠️ "MCP" here = Mini Control Protocol, an internal uCode1 IPC mechanism — NOT the Model Context Protocol used by uCode2's MCP Gateway)
├── UDO Runtime       — Agentic workflow engine (skills, tasks, agents)
└── CLI               — Command-line interface
```

### Spatial Hierarchy

```
Pixel (24×24 px) ──┐
QR Code (5KB) ─────┼──► Cell (24×24 px, 45KB storage, 36 bricks)
Physical Brick ────┘
FCELL (flexible width, 24px height) ──► Cell (for prose/teletext)
Cell × 6 (stacked) = Cube (display, storage, physical)
Rows × Columns of Cells → Grid
Single Z-plane (0-5) → Layer
Named world, multiple Layers → Map
```

### Coordinate Format

```
L{level}-{gridX}{gridY}-{cellX}{cellY}-{layer}

Example: L100-AA10-0317-2
  level=100, grid=AA10, cell=0317, layer=2
```

---

## Development

### Setup
```bash
git clone git@github.com:uDosGo/uCode1.git
cd uCode1
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Testing
```bash
pytest tests/
```

---

## License

MIT

---

*Part of the uDos ecosystem. See [uCode2](https://github.com/uDosGo/uCode2) for services layer.*
