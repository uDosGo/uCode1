# USX Style Specification — v1.0

> **Style tokens, themes, and font system.** Merged from OBF style guide, VA1 style guide, and Monaspace font system.

## Overview

USX Style defines named themes and style tokens using ` ```usx-style ` fenced code blocks. Styles are wireframe-first: black background, green ink, monospace typography.

## Wireframe Theme

```usx-style name="udos-wireframe" version="1.0.0"

COLORS:
  ink: "#00FF00"        # Teletext green
  paper: "#000000"      # Black background
  grid: "#1a1a1a"       # Grid lines
  accent: "#00FF00"     # Highlights
  error: "#FF0000"      # Errors
  warning: "#FFCC00"    # Warnings

TYPOGRAPHY:
  family: "Monaspace Krypton, JetBrains Mono, Monaco, monospace"
  size: "14px"
  line-height: "1.5"

SPACING:
  cell: "8px"
  tile: "16px"
  gap: "4px"

BORDERS:
  style: "solid"
  width: "1px"
  color: "var(--grid)"

SHADOWS: none
ANIMATIONS: none (wireframe)

GRID:
  visible: true
  cell_size: "2×6"
  color: "var(--grid)"

COMPONENTS:
  button: "px-4 py-2 bg-teletext text-black rounded"
  card: "border border-teletext rounded-lg p-4"
  input: "bg-gray-800 border border-gray-700 rounded px-3 py-2"
```

## Colour Palette

| Role | Hex | CSS Variable | Use |
|------|-----|-------------|-----|
| Ink | `#00FF00` | `--usx-ink` | Primary text |
| Paper | `#000000` | `--usx-paper` | Background |
| Grid | `#1A1A1A` | `--usx-grid` | Grid lines |
| Accent | `#00FF00` | `--usx-accent` | Highlights |
| Error | `#FF0000` | `--usx-error` | Errors |
| Warning | `#FFCC00` | `--usx-warning` | Warnings |

## Font System

### Monaspace Family

| Variant | Role |
|---------|------|
| **Monaspace Argon** | Structural, wide — headers / display |
| **Monaspace Krypton** | Monospace — grids, Teletext, code |
| **Monaspace Neon** | Clean sans — prose |
| **Monaspace Radon** | Cursive — quotes / emphasis |
| **Monaspace Xenon** | Serif — publishing |

**Why Monaspace:** variable font (single file, multiple axes), built for code and prose, open source, works with **24px** cell metrics.

### Variable-Width Healing

Proportional glyphs are **not** forced to one advance width: text "heals" into natural reading rhythm while **cell size (24px)** bounds the layout box. Renderers may still snap to grid lines for Teletext overlays.

### Font Sources

| Source | Behaviour |
|--------|-----------|
| **system** | Installed OS fonts |
| **google** | Google Fonts (via CDN where allowed) |
| **local** | `~/.local/share/udos/fonts/` |
| **cdn** | `https://cdn.udo.space/fonts/` |

### User Config

```yaml
# ~/.config/udos/fonts.yaml
defaults:
  mono: "Monaspace Krypton"
  sans: "Monaspace Neon"
  serif: "Monaspace Xenon"
  display: "Monaspace Argon"
  cursive: "Monaspace Radon"

sources:
  google:
    - "JetBrains Mono"
    - "IBM Plex Mono"
  local:
    - "~/.local/share/udos/fonts/C64_Pro_Mono.ttf"
  cdn:
    - "https://cdn.udo.space/fonts/Teletext50.woff2"

grid:
  cell_width: 24
  cell_height: 24
  fallback: "Courier New"
```

### USX-Style Font Block

```usx-style
FONT_SYSTEM:
  family: "Monaspace"
  sources:
    - type: "system"
      name: "Monaspace Krypton"
      weight: "400"
    - type: "google"
      name: "JetBrains Mono"
      fallback: true
    - type: "local"
      path: "~/.local/share/udos/fonts/retro.ttf"
    - type: "cdn"
      url: "https://cdn.udo.space/fonts/teletext.woff2"

  grid_cell:
    width: 24
    height: 24
    unit: "pixels"

  variable_width: true
  ligatures: true
```

### CLI Commands

```text
udo font install retro
udo font list
udo font activate Teletext50
```

## Layout Blocks

```usx-ui
BLOCK two-column
  STYLE: "display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;"

BLOCK three-column
  STYLE: "display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;"

BLOCK card-grid
  STYLE: "display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem;"
```

## Display Profiles

### Text-Terminal Profiles

| Profile | Width | Height | Grid (cells) | Cell size |
|---------|-------|--------|-------------|-----------|
| **terminal** | 80 columns | 24 rows | 12×12 | 2×6 chars |
| **mobile** | 40 columns (scaled) | 12 rows (scaled) | 6×6 | 2×6 chars (scaled) |
| **desktop** | 120 columns | 36 rows | 18×18 | 2×6 chars |

### Default Fonts (Text Mode)

| Platform | Font |
|----------|------|
| macOS | Monaco |
| Linux / Windows | JetBrains Mono |
| Fallback | Courier New |

### Fallback Glyphs

- **Blocks:** `█ ░ ▒ ▓ ■ □`
- **Lines:** `┌ ┐ └ ┘ ├ ┤ ┬ ┴ ┼`
- **Arrows:** `← ↑ → ↓ ↔ ↕`

Renderers should substitute down gracefully when a font lacks Teletext glyphs.

## See Also

- [usx-core.md](usx-core.md) — Core format and fence types
- [usx-ui.md](usx-ui.md) — UI components and authoring blocks
- [usx-grid.md](usx-grid.md) — Grid system and cell maths
