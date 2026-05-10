# uCode1 — BBC BASIC Runtime + Grid/Cell System

**Ownership:** uDosGo  
**Core Language:** Python  
**CLI Command:** `ucode` (runtime/educational)  
**Status:** 🟢 Active

---

## Overview

uCode1 is the **Text/ASCII/Teletext layer** of the uDos ecosystem. It provides a modern BBC BASIC-inspired scripting runtime with a spatial grid/cell system.

### What uCode1 Owns

- **BBC BASIC interpreter** — Run `.bas` scripts with modern extensions
- **Grid/Cell system** — Spatial coordinate addressing, cell storage (SQLite)
- **Teletext/MODE 7 graphics** — Character-based rendering
- **Vault filesystem** — Secure document storage
- **Feed spool** — Time-ordered event management

### What Belongs to Other Layers

| Feature | Layer | CLI |
|---------|-------|-----|
| Sprites & BOBs (visual rendering) | uCode2 | `ucode` |
| Vector/SVG, HomeNest | uCode3 | `ucode` |
| Spatial/3D, virtual worlds | uCode4 | `ucode` |
| System operations (daemons, containers) | System | `udo` |

### CLI: `ucode` (Runtime/Educational)

All uCode layers use the `ucode` command. System operations use `udo` (see [Connect/udo](https://github.com/uDosGo/Connect)).

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
| `sound` | Audio playback | `ucode sound play alert.wav` |
| `print` | Output to console | `ucode print "Hello, uDos!"` |
| `input` | Read user input | `ucode input "Your name? " name$` |
| `let` | Variable assignment | `ucode let score = 100` |
| `feed` | Feed spool operations | `ucode feed recent --limit 10` |
| `wait` | Delay execution | `ucode wait 50` |

### Global Flags

| Flag | Description |
|------|-------------|
| `--line <n>` | Start at specific line number |
| `--quiet` | Suppress output (except PRINT) |
| `--trace` | Trace execution (debugging) |
| `--profile` | Profile performance |

---

## Quick Start

### Install
```bash
pip install ucode1
```

### Run a BASIC script
```bash
ucode run examples/hello.bas
```

### Interactive REPL
```bash
ucode
OK> PRINT "Hello, World!"
OK> RUN
```

### Create a cell
```basic
OK> cell create L100-AA10-0000-0
OK> cell edit L100-AA10-0000-0 --resource script.ucode
OK> cell neighbours L100-AA10-0000-0 --radius 5
```

---

## Architecture

```
uCode1 (Python)
├── Interpreter       — BBC BASIC parser & runtime
├── Grid Engine       — Spatial coordinate system (24×24 cells)
├── Cell Storage      — SQLite-backed cell database
├── Teletext Renderer — MODE 7 character graphics
├── Vault Bridge      — Secure document storage
├── Feed Spool        — Time-ordered event management
└── Cube Manager      — 6-cell stack (display, storage, physical)
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

### Build
```bash
python -m build
```

---

## License

MIT

---

*Part of the uDos ecosystem. See [uCode4](https://github.com/uDosGo/uCode4) for Spatial/3D documentation.*
