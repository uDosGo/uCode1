---
title: "uCode1 CLI — User Guide"
status: draft
last_updated: 2026-05-10T19:12:56+10:00
category: readme
tags: [ucode1]
description: "Welcome to uCode1 — the **Text/ASCII/Teletext layer** of the uDos ecosystem. uCode1 provides a modern BBC BASIC-inspi..."
---
# uCode1 CLI — User Guide

## Introduction

Welcome to uCode1 — the **Text/ASCII/Teletext layer** of the uDos ecosystem. uCode1 provides a modern BBC BASIC-inspired scripting runtime with a spatial grid/cell system, teletext graphics, and feed operations.

**CLI Command:** `ucode` (runtime/educational)  
**System operations:** `udo` (see [Connect/udo](https://github.com/uDosGo/Connect))

### Layer Boundaries

| Layer | Component | Purpose | CLI |
|-------|-----------|---------|-----|
| **uCode1** | Text/ASCII/Teletext | BBC BASIC runtime, grid/cell system, teletext | `ucode` |
| **uCode2** | Sprite/BOB | AMOS runtime, sprites, BOBs, multimedia | `ucode` |
| **uCode3** | Vector/SVG | HomeNest server, home automation | `ucode` |
| **uCode4** | Spatial/3D | Virtual worlds, spatial computing | `ucode` |
| **System** | udo CLI | System operations (daemons, containers, security) | `udo` |

## Installation

### Prerequisites

- Python 3.9+
- pip

### Install from PyPI

```bash
pip install ucode1
```

### Install from source

```bash
git clone git@github.com:uDosGo/uCode1.git
cd uCode1
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Verification

```bash
ucode --help
```

## Getting Started

### Run a BASIC script

```bash
ucode run examples/hello.bas
```

### Interactive REPL

```bash
ucode
OK> PRINT "Hello, uDos!"
OK> RUN
```

### Create a cell

```basic
OK> cell create L100-AA10-0000-0
OK> cell edit L100-AA10-0000-0 --resource script.ucode
OK> cell neighbours L100-AA10-0000-0 --radius 5
```

## Command Reference

### Program Execution

| Command | Description | Example |
|---------|-------------|---------|
| `run <file>` | Execute BASIC file | `ucode run hello.bas` |
| `list` | List available programs | `ucode list` |
| `load <file>` | Load program into memory | `ucode load adventure.bas` |
| `save <file>` | Save current program | `ucode save mygame.bas` |
| `new` | Clear current program | `ucode new` |

### Cell Commands (Grid System)

| Command | Description | Example |
|---------|-------------|---------|
| `cell create <coord>` | Create a cell at coordinate | `ucode cell create L100-AA10-0000-0` |
| `cell show <coord>` | Show cell details | `ucode cell show L100-AA10-0317-2` |
| `cell edit <coord> --resource <file>` | Edit cell resource | `ucode cell edit L100-AA10-0000-0 --resource script.ucode` |
| `cell neighbours <coord> --radius <n>` | List neighbouring cells | `ucode cell neighbours L100-AA10-0000-0 --radius 5` |

### Cube Commands

| Command | Description | Example |
|---------|-------------|---------|
| `cube create <cube-coord>` | Create a 6-cell cube | `ucode cube create L100-AA10-0317` |
| `cube stack <cube-coord> --layers <list>` | Stack layers into cube | `ucode cube stack L100-AA10-0317 --layers 0,1,2,3,4,5` |
| `cube physical <cube-coord> --lego` | Generate Lego build instructions | `ucode cube physical L100-AA10-0317 --lego` |

### Grid Commands

| Command | Description | Example |
|---------|-------------|---------|
| `grid export --level <n> --format <fmt>` | Export grid data | `ucode grid export --level 100 --format json` |
| `grid import --file <path>` | Import grid data | `ucode grid import --file grid_data.json` |

### Map Commands

| Command | Description | Example |
|---------|-------------|---------|
| `map render --world <name>` | Render a world map | `ucode map render --world L100` |
| `map near <coord> --radius <n> --type <type>` | Find nearby features | `ucode map near L100-AA10-0000-0 --radius 10 --type waypoint` |
| `map path <from> <to>` | Find path between coordinates | `ucode map path L100-AA10-0000-0 L300-BD14-1522-0` |

### Movement

| Command | Description | Example |
|---------|-------------|---------|
| `locate <coord> X=<x> Y=<y>` | Position within grid | `ucode locate L100-AA10-0000-0 X=100 Y=50` |
| `move <coord> TO <x>,<y> STEP <n>` | Animate movement | `ucode move L100-AA10-0000-0 TO 200,100 STEP 10` |
| `collide <coord>` | Check collision | `ucode collide L100-AA10-0000-0` |

### Audio

| Command | Description | Example |
|---------|-------------|---------|
| `sound play <file>` | Play audio file | `ucode sound play alert.wav` |
| `sound stop` | Stop current audio | `ucode sound stop` |
| `sound loop <file> [count]` | Loop playback | `ucode sound loop bgm.mp3 3` |
| `sound volume <level>` | Set volume (0-100) | `ucode sound volume 75` |

*Note: Audio commands are handled by the Groovebox audio lane.*

### Program Flow

| Command | Description | Example |
|---------|-------------|---------|
| `wait <frames>` | Delay execution | `ucode wait 50` |
| `print "<message>"` | Output to console | `ucode print "Hello, World!"` |
| `input "<prompt>", <var>$` | Read user input | `ucode input "Your name? ", name$` |
| `goto <line>` | Jump to line | `ucode goto 100` |
| `gosub <line>` | Subroutine call | `ucode gosub 500` |
| `return` | Return from subroutine | `ucode return` |
| `if <cond> then <cmd>` | Conditional execution | `ucode if score > 100 then print "Winner!"` |

### Variables

| Command | Description | Example |
|---------|-------------|---------|
| `let <var> = <value>` | Variable assignment | `ucode let score = 100` |
| `dim <array>(<size>)` | Array declaration | `ucode dim grid(10, 10)` |
| `poke <addr>, <value>` | Write to cell memory | `ucode poke 53280, 0` |
| `peek <addr>` | Read from cell memory | `ucode peek 53280` |

### Feed

| Command | Description | Example |
|---------|-------------|---------|
| `feed recent --limit <n>` | Show recent feed entries | `ucode feed recent --limit 10` |
| `feed search <query>` | Search feed spool | `ucode feed search "game update"` |
| `feed post <message>` | Post to feed | `ucode feed post "Level completed!"` |

## Global Flags

| Flag | Description |
|------|-------------|
| `--line <n>` | Start at specific line number |
| `--quiet` | Suppress output (except PRINT) |
| `--trace` | Trace execution (for debugging) |
| `--profile` | Profile performance |

## Spatial Grid System

### Coordinate Format

```
L{level}-{gridX}{gridY}-{cellX}{cellY}-{layer}

Components:
- level:    signed int (world level)
- gridX:    2 letters (AA=0, AB=1, ... ZZ=675)
- gridY:    2 letters (AA=0, AB=1, ... ZZ=675)
- cellX:    2 digits (00-23, 24 cells per grid)
- cellY:    2 digits (00-23, 24 cells per grid)
- layer:    1 digit (0-5, Z-plane within cube)
```

### Layer Bands

| Band | Range | Name | Purpose |
|------|-------|------|---------|
| 000-099 | L000-L099 | System | Reserved for core |
| 100-199 | L100-L199 | Dungeons | Procedural learning |
| 200-299 | L200-L299 | Subterranean | Underground, caves |
| **300-399** | **L300-L399** | **Earth Surface** | **Real-world GPS** |
| 400-499 | L400-L499 | Dimensions | AR/VR, game worlds |
| 500-599 | L500-L599 | User Vaults | Private knowledge spaces |
| 600-699 | L600-L699 | Public Library | Shared knowledge |
| 700-799 | L700-L799 | Portals | Inter-map gateways |
| 800-899 | L800-L899 | Stellar | Solar system, galaxies |
| 900+ | L900+ | Reserved | Future expansion |

## Workflow Examples

### BASIC program with grid operations

```basic
10 REM === Grid Explorer ===
20 cell create L100-AA10-0000-0
30 cell edit L100-AA10-0000-0 --resource "exploration_log.txt"
40 FOR i = 1 TO 10
50   cell neighbours L100-AA10-0000-0 --radius i
60   wait 10
70 NEXT i
80 END
```

### Feed monitoring

```basic
10 REM Check recent feed
20 feed recent --limit 5
30 INPUT "Search term? ", term$
40 feed search term$
50 END
```

## See Also

- [System commands (`udo`)](https://github.com/uDosGo/Connect)
- [uCode2 — Sprite/BOB layer (AMOS runtime)](https://github.com/uDosGo/uCode2)
- [uCode3 — Vector/SVG layer (HomeNest)](https://github.com/uDosGo/uCode3)
- [uCode4 — Spatial/3D layer](https://github.com/uDosGo/uCode4)
- [CLI Command Reference](CLI_COMMANDS.md)
