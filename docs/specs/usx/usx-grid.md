# USX Grid Specification — v1.0

> **Grid system, teletext cells, pixel/QR maths, and display sizes.** Merged from grid-spec.md, grid-cell-cube-maths.md, and display-sizes.md.

## Overview

USX defines two complementary grid models:

1. **Text / Teletext cell** — **2×6 characters** per cell for terminal rendering
2. **Pixel / QR storage cell** — **24×24 px** default for display and data storage

## Text Grid (Teletext)

| Property | Value |
|----------|-------|
| **Name** | Teletext Grid |
| **Cell size** | **2×6** characters (width × height) |
| **Default display** | **12×12** cells |
| **Total cells (default)** | **144** per screen |
| **Character set** | ASCII + block glyphs (e.g. `█ ░ ▒ ▓ ■ □`) |

### Coordinates

- Cells addressed **(0,0)** through **(11,11)** for a 12×12 grid
- **uTile** = one **2×6** cell region (e.g. for QR or storage layout)
- Logical model: `grid[x][y]` with origin top-left unless a renderer specifies otherwise

### Display Modes

| Mode | Description |
|------|-------------|
| **mono** | Black background, green text (`#00FF00`) |
| **teletext** | Black background, coloured blocks (Teletext palette) |
| **wireframe** | White background, black text |

### Example

```usx-grid size="12x12" mode="teletext"
[0,0]█ [0,1]█ [0,2]█ [0,3]█ [0,4]█ [0,5]█
[1,0]█ [1,1]░ [1,2]░ [1,3]░ [1,4]░ [1,5]█
[2,0]█ [2,1]░ [2,2]▒ [2,3]▒ [2,4]░ [2,5]█
[3,0]█ [3,1]░ [3,2]▒ [3,3]▒ [3,4]░ [3,5]█
[4,0]█ [4,1]░ [4,2]░ [4,3]░ [4,4]░ [4,5]█
[5,0]█ [5,1]█ [5,2]█ [5,3]█ [5,4]█ [5,5]█
```

## Pixel/QR Grid

### Standard 24 (Default Cell)

| Quantity | Value |
|----------|-------|
| **Cell size** | **24×24 pixels** |
| **QR module** | **8×8 pixels** |
| **QR grid per cell** | **3×3** QR (nine positions) |
| **QR per cell** | **9** |
| **Storage per cell** | 9 × 5,000 = **45,000 characters (45KB)** |

Layout: **3 QR across × 3 QR down** inside one 24×24 pixel cell.

### Cube (Logical Stack)

| Quantity | Value |
|----------|-------|
| **Cells stacked (depth)** | **6** |
| **Total QR** | 6 × 9 = **54** |
| **Storage per cube** | 54 × 5,000 = **270,000 characters (270KB)** |

### Physical Cube (Bricks)

| Quantity | Value |
|----------|-------|
| **Brick lattice** | **6×6×6** |
| **Total bricks** | **216** |
| **Bricks per QR** | 216 ÷ 54 = **4** |
| **Cluster** | **2×2** bricks per QR |
| **Storage per brick** | 5,000 ÷ 4 = **1,250 characters** |

### Grid Size Variants

| Name | Cell (px) | QR grid | QR / cell | Storage / cell | Typical use |
|------|-----------|---------|-----------|----------------|-------------|
| **Retro 16** | 16×16 | 2×2 | 4 | **20KB** | Tiny displays, watches |
| **Standard 24** | 24×24 | 3×3 | 9 | **45KB** | Default, phones |
| **Console 32** | 32×32 | 4×4 | 16 | **80KB** | Tablets, terminals |
| **HD 64** | 64×64 | 8×8 | 64 | **320KB** | Desktop, monitors |
| **HDD 128** | 128×128 | 16×16 | 256 | **1.28MB** | Large displays, kiosks |

**Default:** **Standard 24** — balance of **45KB/cell** clarity and density.

### Visual Reference (Standard 24)

```
Standard cell (24×24 px, 3×3 QR grid):

┌────────────────────────┐
│  ┌────┬────┬────┐      │   each small box = one 8×8 QR module
│  │ QR │ QR │ QR │      │   QR indices 00–08
│  ├────┼────┼────┤      │
│  │ QR │ QR │ QR │      │
│  ├────┼────┼────┤      │
│  │ QR │ QR │ QR │      │
│  └────┴────┴────┘      │
│  9 QR  |  45KB/cell    │
└────────────────────────┘

Physical cube (6×6×6 = 216 bricks):

     ┌─────┐  Layer 5  (36 bricks)
     ├─────┤  Layer 4
     ├─────┤  Layer 3
     ├─────┤  Layer 2
     ├─────┤  Layer 1
     └─────┘  Layer 0

1 brick  ≈ 1,250 chars  
4 bricks (2×2) ≈ 1 QR (5,000 chars)  
9 QR ≈ 1 cell (45KB)  
6 cells ≈ 1 logical cube (270KB)
```

## Spatial Hierarchy

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

## Coordinate Format

```
L{level}-{gridX}{gridY}-{cellX}{cellY}-{layer}

Example: L100-AA10-0317-2
  level=100, grid=AA10, cell=0317, layer=2
```

## Display Profiles

### Text-Terminal Profiles

| Profile | Width | Height | Grid (cells) | Cell size |
|---------|-------|--------|-------------|-----------|
| **terminal** | 80 columns | 24 rows | 12×12 | 2×6 chars |
| **mobile** | 40 columns (scaled) | 12 rows (scaled) | 6×6 | 2×6 chars (scaled) |
| **desktop** | 120 columns | 36 rows | 18×18 | 2×6 chars |

### Pixel/QR Cell Variants

| Name | Cell (px) | Storage/cell | Notes |
|------|-----------|-------------|-------|
| **Retro 16** | 16×16 | 20KB | Tiny / watch |
| **Standard 24** | 24×24 | **45KB** (default) | Phones |
| **Console 32** | 32×32 | 80KB | Tablets |
| **HD 64** | 64×64 | 320KB | Desktop |
| **HDD 128** | 128×128 | 1.28MB | Kiosks |

## Conventions

- **Character capacity** is stated in **decimal** (e.g. 45,000 characters ≈ **45KB** when 1 "KB" = 1,000 characters for human-readable storage labels)
- **QR module** size on the pixel grid: **8×8 pixels** per small QR "tile"
- **Storage per QR:** **5,000 characters** (locked constant for uDos QR payload planning)

## See Also

- [usx-core.md](usx-core.md) — Core format and fence types
- [usx-ui.md](usx-ui.md) — UI components and authoring blocks
- [usx-style.md](usx-style.md) — Style tokens and themes
