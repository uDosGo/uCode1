---
title: "USX — Unified Surface eXchange Format"
status: draft
last_updated: 2026-05-17T22:11:35+10:00
category: specification
tags: [specification, surface, ucode1, usx]
description: "**USX** is the style/design/surface format for the uDos ecosystem, merging the former **OBF** (Open Box Format) and *..."
---
# USX — Unified Surface eXchange Format

**USX** is the style/design/surface format for the uDos ecosystem, merging the former **OBF** (Open Box Format) and **USXD** (Universal Surface Definition) into a single, coherent specification.

**USX is for how things look and feel.** For system-layer definitions (skills, tasks, workflows, agents), see the [UDO spec](../udo/).

## What USX Covers

| Spec | What It Defines | Merged From |
|------|----------------|-------------|
| [usx-core.md](usx-core.md) | Core format: fences, kinds, document structure | `open-box-format.md` |
| [usx-ui.md](usx-ui.md) | UI components, authoring blocks, grid layouts | `obf-components.md` + `obf-ui-blocks.md` + `obf-grid-spec.md` |
| [usx-style.md](usx-style.md) | Style tokens, themes, fonts, display profiles | `style-guide-obf.md` + `va1-style-guide.md` + `font-system-obf.md` + `display-sizes.md` |
| [usx-surface.md](usx-surface.md) | Surface definitions, ASCII blocks, story format | `usxd-spec.md` + `usxd-ascii-blocks.md` + `usxd-go.md` + `usxd-story-format.md` |
| [usx-grid.md](usx-grid.md) | Grid system, teletext cells, pixel/QR maths | `grid-spec.md` + `grid-cell-cube-maths.md` |

## Core Principle

> **Everything is text in a fenced code block.** No proprietary canvas, no binary source, no lock-in.

## Fence Types

| Fence | Purpose |
|-------|---------|
| ` ```usx ` | USX document (any surface kind) |
| ` ```usx-ui ` | UI component definitions |
| ` ```usx-style ` | Named theme/style tokens |
| ` ```usx-grid ` | Cell grid layouts |
| ` ```usx-surface ` | Surface definitions |
| ` ```usx-story ` | Story/narrative surfaces |
| ` ```usx-template ` | Markdown-first boilerplate |

## Version

Current: **USX v1.0** (unified from OBF v1.0 + USXD A1.0.0)

## Location

- **Canonical specs:** `uCode1/docs/specs/usx/`
- **Implementation:** `uCode1/core_py/usxd/` (Python), `uCode1/core_py/grid/` (grid engine)
- **Legacy redirects:** `Connect/docs/specs/` (stub files pointing here)
