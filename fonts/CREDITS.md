# uCode1 Font Credits & Attribution

## Font Sources

All original font files are preserved unmodified in `~/Code/Vendor/fonts/retro/`.
The uCode1 repo does **not** contain copies of vendor fonts — it references them
by path at build time. Only our modified variants (`mods/`) live in this repo.

---

### PressStart2P — NES-Style Pixel Font

| Field | Value |
|-------|-------|
| **Font** | Press Start 2P |
| **Author** | CodeMan38 (cody@zone38.net) |
| **Upstream** | https://github.com/CodeMan38/PressStart2P |
| **License** | SIL Open Font License 1.1 |
| **Vendor Path** | `~/Code/Vendor/fonts/retro/PressStart2P-Regular.ttf` |
| **Usage** | uCode1 Terminal mode — NES-style pixel rendering |
| **Mods** | `mods/PressStart2P-udos.ttf` — uDos glyph additions |

**License Text (SIL OFL 1.1):**
> This Font Software is licensed under the SIL Open Font License, Version 1.1.
> This license is available with a FAQ at: https://scripts.sil.org/OFL

---

### PetMe128 — C64-Style Font

| Field | Value |
|-------|-------|
| **Font** | Pet Me 128 / Pet Me 128 2Y |
| **Author** | Style-7 |
| **Upstream** | https://github.com/Style-7/PetMe128 |
| **License** | MIT License |
| **Vendor Path** | `~/Code/Vendor/fonts/retro/PetMe128.ttf`, `PetMe1282Y.ttf` |
| **Usage** | uCode1 Terminal mode — C64-style character rendering |
| **Mods** | `mods/PetMe128-udos.ttf` — uDos glyph additions |

**License Text (MIT):**
> Copyright (c) 2023 Style-7
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this font software and associated documentation files, to deal in the
> Software without restriction, including without limitation the rights to
> use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in
> all copies or substantial portions of the Software.

---

### Teletext50 — Teletext-Style Font

| Field | Value |
|-------|-------|
| **Font** | Teletext50 / Teletext50 Condensed |
| **Author** | Teletext Fonts Project |
| **Upstream** | https://github.com/teletext-fonts/Teletext50 |
| **License** | MIT License |
| **Vendor Path** | `~/Code/Vendor/fonts/retro/Teletext50.otf`, `Teletext50-condensed.otf` |
| **Usage** | uCode1 Ceefax/Teletext mode — Mode 7 character rendering |
| **Mods** | `mods/Teletext50-udos.otf`, `mods/Teletext50-udos-condensed.otf` — extended charset |

**License Text (MIT):**
> Copyright (c) 2024 Teletext Fonts Project
>
> Permission is hereby granted, free of charge, to any person obtaining a copy
> of this font software and associated documentation files, to deal in the
> Software without restriction, including without limitation the rights to
> use, copy, modify, merge, publish, distribute, sublicense, and/or sell
> copies of the Software, and to permit persons to whom the Software is
> furnished to do so, subject to the following conditions:
>
> The above copyright notice and this permission notice shall be included in
> all copies or substantial portions of the Software.

---

## Modified Fonts (mods/)

The files in `mods/` are derived works based on the original fonts listed above.
Each modified font retains the original license terms and adds the following
modifications:

- **uDos logo glyph** added at a dedicated codepoint
- **Extended teletext characters** for Mode 7 compatibility
- **Additional glyphs** for uCode1 grid/cell system symbols

Modified fonts are distributed under the same license as their originals
(MIT or SIL OFL 1.1 as applicable).

---

## Font Usage Rules

| Mode | Font | Source |
|------|------|--------|
| **Terminal** | PressStart2P (NES-style) | `~/Code/Vendor/fonts/retro/PressStart2P-Regular.ttf` |
| **Terminal** | PetMe128 (C64-style) | `~/Code/Vendor/fonts/retro/PetMe128.ttf` |
| **Ceefax/Teletext** | Teletext50 | `~/Code/Vendor/fonts/retro/Teletext50.otf` |
| **Ceefax/Teletext** | Teletext50 Condensed | `~/Code/Vendor/fonts/retro/Teletext50-condensed.otf` |

No other fonts are used in uCode1 grid modes.
