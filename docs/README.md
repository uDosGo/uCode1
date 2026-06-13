---
title: "uCode1 Documentation"
status: draft
last_updated: 2026-05-24T12:16:17+10:00
category: readme
tags: [ucode1]
description: "Welcome to the uCode1 documentation hub. uCode1 is the **Text/ASCII/Teletext layer** of the uDos ecosystem — a BBC BA..."
---
# uCode1 Documentation

Welcome to the uCode1 documentation hub. uCode1 is the **Text/ASCII/Teletext layer** of the uDos ecosystem — a BBC BASIC-inspired scripting runtime with a spatial grid/cell system.

**CLI Command:** `ucode` (runtime/educational)  
**System operations:** `udo` (see [Connect/udo](https://github.com/uDosGo/Connect))

## Layer Architecture

| Layer | Component | Purpose | CLI |
|-------|-----------|---------|-----|
| **uCode1** | Text/ASCII/Teletext | BBC BASIC runtime, grid/cell system, teletext | `ucode` |
| **uCode2** | Sprite/BOB | AMOS runtime, sprites, BOBs, multimedia | `ucode` |
| **uCode3** | Vector/SVG | HomeNest server, home automation | `ucode` |
| **uCode4** | Spatial/3D | Virtual worlds, spatial computing | `ucode` |
| **System** | udo CLI | System operations (daemons, containers, security) | `udo` |

## Getting Started

- [Quick Start Guide](QUICK_START.md) — Get up and running in minutes
- [CLI User Guide](CLI_README.md) — Complete user guide
- [CLI Command Reference](CLI_COMMANDS.md) — Detailed command reference

## Documentation Structure

```
docs/
├── README.md                # This file
├── QUICK_START.md           # Quick start guide
├── CLI_README.md            # Comprehensive user guide
├── CLI_COMMANDS.md          # Command reference
├── CHARACTER_SET_REFERENCE.md  # Teletext character set
├── C_LAYER_CHEAT_SHEET.md     # C layer reference
├── SPATIAL_CHARACTER_MAPPING.md  # Spatial character mapping
├── SPATIAL_CHARACTER_INTEGRATION.md  # Spatial integration
├── legacy/                  # Superseded docs (USYSTEM_*, usystem_schema.sql)
└── review/                  # Docs under review (currently empty)
```

## Core Concepts

### BBC BASIC Runtime
uCode1 provides a modern BBC BASIC interpreter with:
- Line-numbered programs (compatible with classic BASIC)
- Grid/cell system for spatial addressing
- Teletext/MODE 7 character graphics
- Feed spool for time-ordered events
- Vault filesystem for secure storage

### Spatial Grid System

```
Pixel (24×24 px) → Cell (24×24 px, 45KB) → Cube (6 cells, 270KB) → Grid → Layer → Map
```

**Coordinate format:** `L{level}-{gridXY}-{cellXY}-{layer}`

## CLI Reference

```bash
# Run a BASIC script
ucode run hello.bas

# Interactive REPL
ucode
OK> PRINT "Hello, World!"

# Create a cell
ucode cell create L100-AA10-0000-0

# Show cell neighbours
ucode cell neighbours L100-AA10-0000-0 --radius 5
```

## See Also

- [System commands (`udo`)](https://github.com/uDosGo/Connect)
- [uCode2 — Sprite/BOB layer (AMOS runtime)](https://github.com/uDosGo/uCode2)
- [uCode3 — Vector/SVG layer (HomeNest)](https://github.com/uDosGo/uCode3)
- [uCode4 — Spatial/3D layer](https://github.com/uDosGo/uCode4)
