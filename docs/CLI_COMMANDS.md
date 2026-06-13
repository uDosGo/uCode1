---
title: "uCode1 CLI Command Reference"
status: draft
last_updated: 2026-05-10T19:12:56+10:00
category: reference
tags: [ucode1]
description: "The `ucode` command is the **runtime and educational interface** for the uDos ecosystem. It provides BBC BASIC script..."
---
# uCode1 CLI Command Reference

## Overview

The `ucode` command is the **runtime and educational interface** for the uDos ecosystem. It provides BBC BASIC scripting, grid/cell management, teletext rendering, and feed operations.

**Layer:** uCode1 — Text/ASCII/Teletext layer  
**System operations:** Use `udo` (see [Connect/udo](https://github.com/uDosGo/Connect))  
**Sprites/BOBs:** Use uCode2 (AMOS runtime)  
**Vector/SVG:** Use uCode3 (HomeNest)  
**Spatial/3D:** Use uCode4

## Usage

```bash
ucode <command> [arguments] [flags]
```

## Core Commands

### Program Execution

| Command | Description | Example |
|---------|-------------|---------|
| `run <file>` | Execute BASIC file | `ucode run hello.bas` |
| `list` | List available programs | `ucode list` |
| `load <file>` | Load program into memory | `ucode load adventure.bas` |
| `save <file>` | Save current program | `ucode save mygame.bas` |
| `new` | Clear current program | `ucode new` |

### Cell Commands (Grid System)

Cells are 24×24 pixel addressable units with 45KB storage each.

| Command | Description | Example |
|---------|-------------|---------|
| `cell create <coord>` | Create a cell at coordinate | `ucode cell create L100-AA10-0000-0` |
| `cell show <coord>` | Show cell details | `ucode cell show L100-AA10-0317-2` |
| `cell edit <coord> --resource <file>` | Edit cell resource | `ucode cell edit L100-AA10-0000-0 --resource script.ucode` |
| `cell neighbours <coord> --radius <n>` | List neighbouring cells | `ucode cell neighbours L100-AA10-0000-0 --radius 5` |

### Cube Commands

A Cube is 6 stacked Cells (layers 0-5) at the same grid/cell coordinate.

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

### Movement Commands

| Command | Description | Example |
|---------|-------------|---------|
| `locate <coord> X=<x> Y=<y>` | Position within grid | `ucode locate L100-AA10-0000-0 X=100 Y=50` |
| `move <coord> TO <x>,<y> STEP <n>` | Animate movement | `ucode move L100-AA10-0000-0 TO 200,100 STEP 10` |
| `collide <coord>` | Check collision | `ucode collide L100-AA10-0000-0` |

### Audio Commands

| Command | Description | Example |
|---------|-------------|---------|
| `sound play <file>` | Play audio file | `ucode sound play alert.wav` |
| `sound stop` | Stop current audio | `ucode sound stop` |
| `sound loop <file> [count]` | Loop playback | `ucode sound loop bgm.mp3 3` |
| `sound volume <level>` | Set volume (0-100) | `ucode sound volume 75` |

*Note: Audio is handled by the Groovebox audio lane.*

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

### Feed Commands

| Command | Description | Example |
|---------|-------------|---------|
| `feed recent --limit <n>` | Show recent feed entries | `ucode feed recent --limit 10` |
| `feed search <query>` | Search feed spool | `ucode feed search "game update"` |
| `feed post <message>` | Post to feed | `ucode feed post "Level completed!"` |

### Sync

| Command | Description | Example |
|---------|-------------|---------|
| `sync` | Wait for vertical blank | `ucode sync` |

## Global Flags

| Flag | Description |
|------|-------------|
| `--line <n>` | Start at specific line number |
| `--quiet` | Suppress output (except PRINT) |
| `--trace` | Trace execution (for debugging) |
| `--profile` | Profile performance |

## Examples

### Create and explore a cell
```basic
OK> cell create L100-AA10-0000-0
OK> cell edit L100-AA10-0000-0 --resource "notes.txt"
OK> cell neighbours L100-AA10-0000-0 --radius 3
```

### BASIC program
```basic
10 PRINT "Welcome to uDos!"
20 INPUT "What's your name? ", name$
30 PRINT "Hello, "; name$;
40 FOR i = 1 TO 10
50   PRINT i;
60 NEXT i
70 END
```

### Grid export
```bash
ucode grid export --level 300 --format json
```

## See Also

- [System commands (`udo`)](https://github.com/uDosGo/Connect)
- [uCode2 — Sprite/BOB layer (AMOS runtime)](https://github.com/uDosGo/uCode2)
- [uCode3 — Vector/SVG layer (HomeNest)](https://github.com/uDosGo/uCode3)
- [uCode4 — Spatial/3D layer](https://github.com/uDosGo/uCode4)
