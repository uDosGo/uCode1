# uCode1 Fonts

Font assets for uCode1 terminal and teletext rendering modes.

## Structure

```
fonts/
├── CREDITS.md           # Full attribution for all fonts
├── LICENSE              # Combined license information
├── font-manifest.json   # Machine-readable font registry
├── README.md            # This file
└── mods/                # uDos-modified font variants (live in repo)
    ├── PressStart2P-udos.ttf
    ├── PetMe128-udos.ttf
    ├── Teletext50-udos.otf
    └── Teletext50-udos-condensed.otf
```

## Font Sources

Original font files are **not** stored in this repo. They live in
`~/Code/Vendor/fonts/retro/` and are referenced by path at build time.
This keeps Vendor pristine and avoids forking upstream repos.

| Font | Style | Source | License |
|------|-------|--------|---------|
| PressStart2P | NES-style pixel | `~/Code/Vendor/fonts/retro/PressStart2P-Regular.ttf` | SIL OFL 1.1 |
| PetMe128 | C64-style | `~/Code/Vendor/fonts/retro/PetMe128.ttf` | MIT |
| PetMe128 2Y | C64-style variant | `~/Code/Vendor/fonts/retro/PetMe1282Y.ttf` | MIT |
| Teletext50 | Teletext Mode 7 | `~/Code/Vendor/fonts/retro/Teletext50.otf` | MIT |
| Teletext50 Condensed | Teletext Mode 7 condensed | `~/Code/Vendor/fonts/retro/Teletext50-condensed.otf` | MIT |

## Font Usage Rules

| Mode | Font |
|------|------|
| **Terminal** | PressStart2P (NES) or PetMe128 (C64) |
| **Ceefax/Teletext** | Teletext50 (standard or condensed) |

No other fonts are used in uCode1 grid modes.

## Modified Variants (mods/)

The `mods/` directory contains uDos-modified font variants with:
- uDos logo glyph at a dedicated codepoint
- Extended teletext characters for Mode 7 compatibility
- Additional glyphs for grid/cell system symbols

These are derived works distributed under the same license as their originals.
