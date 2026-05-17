# USX UI Specification — v1.0

> **UI components, authoring blocks, and grid layouts.** Merged from OBF components, UI blocks, and grid spec.

## Overview

USX UI defines markdown-first, text-authored components for static rendering and terminal-preview workflows. All UI is defined inside ` ```usx-ui ` fenced code blocks.

## Component Definitions

### Button

```usx-ui
COMPONENT button
  STYLE: "px-4 py-2 bg-teletext text-black rounded hover:bg-green-400"
  VARIANTS:
    primary: "bg-teletext text-black"
    secondary: "bg-gray-700 text-white"
    danger: "bg-red-600 text-white"
  SIZE:
    sm: "px-2 py-1 text-sm"
    md: "px-4 py-2 text-base"
    lg: "px-6 py-3 text-lg"
```

### Card

```usx-ui
COMPONENT card
  STYLE: "border border-teletext rounded-lg p-4 bg-gray-900"
  PARTS:
    header: "border-b border-gray-800 pb-2 mb-2 font-bold"
    body: "text-gray-300"
    footer: "border-t border-gray-800 pt-2 mt-2 text-xs text-gray-500"
```

### Form

```usx-ui
COMPONENT form
  STYLE: "space-y-4"
  FIELD:
    label: "block text-sm font-medium mb-1"
    input: "w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 focus:outline-none focus:border-teletext"
    error: "text-red-400 text-xs mt-1"
```

## Authoring Blocks

USX UI supports these authoring block patterns for markdown-first layout:

### COLUMNS

```usx-ui
COLUMNS
  COLUMN
    Content for left column.
  COLUMN
    Content for right column.
```

### CARD

```usx-ui
CARD title="Getting Started"
  BODY
    This is a card component.
  FOOTER
    Button: [Learn More](#)
```

### TABS

```usx-ui
TABS
  TAB "Overview"
    Intro copy.
  TAB "Details"
    More detail copy.
```

### ACCORDION

```usx-ui
ACCORDION
  ITEM "What is uDos?"
    Universal Device Operating Surface.
  ITEM "Is this local-first?"
    Yes. A1 is local-first and wireframe.
```

### GRID (UI Layout)

```usx-ui
GRID
  ROWS
    ████████
    █░░░░░░█
    ████████
```

## Grid Fence Syntax

For detailed grid layouts with cell addressing, use the ` ```usx-grid ` fence:

````markdown
```usx-grid [options]
…cell data…
```
````

### Options

| Option | Values | Default |
|--------|--------|---------|
| `size` | `WxH` cells | `12x12` (coordinate mode) or inferred (compact) |
| `mode` | `teletext` \| `mono` \| `wireframe` | `teletext` |
| `cell_size` | e.g. `2x6` chars | documentation only in VA1 parser |
| `show_coords` | `true` \| `false` | `false` |
| `editable` | `true` \| `false` | `true` |
| `compact` | flag or `compact=true` | off |

### Coordinate Format

Each token: `[x,y]<char>` with zero-based indices.

```usx-grid size="12x12" mode="teletext" show_coords="true"
[0,0]█ [0,1]█ [0,2]█
```

### Compact Format

Add `compact` to the header. One character per column; one row per line:

```usx-grid size="12x6" mode="teletext" compact
████████████
█░░░░░░░░░░█
█░░▒▒░░░░░░█
```

### Character Set

| Char | Notes |
|------|-------|
| `█` `▓` `▒` `░` | Blocks / shades |
| `□` `■` | Boxes |
| space | Empty (render may show `·` in terminal) |

## CLI Commands

| Command | Description |
|---------|-------------|
| `udo usx render <file> [--mode]` | Terminal ANSI rendering |
| `udo usx render <file> --format html` | HTML snippet output |
| `udo usx export <file> --format ascii\|usx` | Plain text or fenced USX |
| `udo usx validate <file>` | Dimension and syntax check |
| `udo usx edit <file>` | Opens `$EDITOR`; creates minimal grid if missing |

## File Conventions

- Embed in any `.md` file, or use a dedicated `.usx.md` / `.usx` file
- Publish/build-safe behavior: ` ```usx-ui` authoring blocks are source artifacts, not transformed during `udo publish build`

## See Also

- [usx-core.md](usx-core.md) — Core format and fence types
- [usx-style.md](usx-style.md) — Style tokens and themes
- [usx-grid.md](usx-grid.md) — Grid system and cell maths
