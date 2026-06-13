---
title: "USX Surface Specification — v1.0"
status: draft
last_updated: 2026-05-17T22:11:35+10:00
category: specification
tags: [specification, surface, ucode1, usx]
description: "> **Surface definitions, ASCII blocks, and story format.** Merged from USXD spec, USXD ASCII blocks, USXD-GO, and USX..."
---
# USX Surface Specification — v1.0

> **Surface definitions, ASCII blocks, and story format.** Merged from USXD spec, USXD ASCII blocks, USXD-GO, and USXD story format.

## Overview

USX Surface defines interactive surfaces — text/ASCII blocks that can be rendered in terminal or exported through tooling. Surfaces use the ` ```usx-surface ` fence.

## Surface Definition

```usx-surface
SURFACE name="dashboard" version="1.0.0"

STYLE
  background: #000000
  ink: #00FF00
  typography: "ui-monospace, monospace"

REGIONS
  header: "uDos Dashboard"
  status: "Ready"
```

## Four-Layer IO Model (USX-GO)

USX surfaces align to a four-layer architecture:

| Layer | Purpose | Status |
|-------|---------|--------|
| **CHASIS** | Core layout/runtime and serialization | `v1.0` |
| **WIDGET** | Reusable UI components | `v1.0` |
| **SKIN** | Visual styling and tokens | `v1.0` |
| **LENS** | Future gameplay/filter overlays | Planned |

### Open Box Compatible USX JSON

USX blocks are self-describing, portable, and schema-addressable:

```json
{
  "open_box": {
    "id": "dashboard",
    "type": "application/vnd.usx.surface",
    "usx_version": "1.0.0"
  },
  "chassis": {
    "layout": "grid",
    "columns": 12,
    "rows": 12
  },
  "widgets": [
    { "type": "header", "content": "uDos Dashboard" },
    { "type": "status", "content": "Ready" }
  ]
}
```

## Story Format

Story is a **linear step-form surface** with presentation-slide styling:

- typeform-like progression and pacing
- keyboard-first controls (`Enter` as primary action)
- one focal decision per panel
- shared semantics across browser, ThinUI, and TUI adapters

### Core Principles

| Principle | Baseline rule |
|-----------|---------------|
| Linear navigation | Start -> Step 1 -> ... -> End |
| Enter to continue | Primary action is `Enter` on every step |
| Input density | Prefer one primary field per panel |
| Progress visibility | Show `Step X/Y` or progress bar |
| Surface separation | Core owns semantics; themes own presentation |

### Story Panel Anatomy

```text
┌─────────────────────────────────────────────────────────────┐
│ Story Title                                Step 2 / 7       │
│ Optional subtitle / helper text                             │
├─────────────────────────────────────────────────────────────┤
│ Presentation block / prompt / instructions                  │
│ Primary interaction area                                    │
├─────────────────────────────────────────────────────────────┤
│ [ Back ]                                      [ Continue ]  │
│ Hint: Enter = continue                                      │
└─────────────────────────────────────────────────────────────┘
```

### Panel Taxonomy

| Kind | Purpose |
|------|---------|
| `story-intro` | Opening frame before input |
| `story-input` | Single or grouped text input |
| `story-choice` | Single or multi-select |
| `story-scale` | Numeric scale (typically 1-5) |
| `story-rating-stars` | Star rating (typically 1-5) |
| `story-summary` | Review answers before submit |
| `story-confirm` | Explicit confirmation/submit |
| `story-slide` | Presentation-only step |
| `story-slide-input` | Hybrid presentation + input |
| `story-end` | Completion state |

### Step Types

| Type | Purpose | Control model |
|------|---------|---------------|
| `presentation` | Read-mostly framing content | Enter to continue |
| `input` | Text/textarea capture | One primary field |
| `single_choice` | One option | Radio semantics |
| `multi_choice` | Multiple options | Checkbox semantics (`Space` toggle) |
| `stars` | 1..N star rating | `Left/Right` then `Enter` |
| `scale` | Numeric range | `Left/Right` then `Enter` |

### Story JSON Contract

```json
{
  "open_box": {
    "id": "onboarding-story",
    "type": "application/vnd.usx.story",
    "usx_version": "1.0.0"
  },
  "story": {
    "title": "Welcome to uDos",
    "steps": [
      { "type": "presentation", "content": "# Welcome", "next_action": "enter" },
      { "type": "input", "label": "Workspace name", "field": "text", "required": true },
      { "type": "multi_choice", "label": "Select features", "options": [] },
      { "type": "stars", "label": "How familiar are you?", "max": 5, "value": 4 },
      { "type": "scale", "label": "Rate CLI experience", "min": 1, "max": 5, "value": 4 },
      { "type": "single_choice", "label": "Launch dashboard?", "options": [] }
    ],
    "navigation": {
      "back": true,
      "cancel": true,
      "progress": "visible",
      "enter_to_continue": true
    }
  }
}
```

### Progress Styles

- numeric: `Step 2 / 6` (default)
- bar: `[######------------] 2 / 6`
- labeled sequence: `Feedback · Rating · Comment · Confirm`

### Theme Abstraction

Story semantics remain fixed while adapters theme output:

- Typeform (minimal)
- Marp (presentation-forward)
- Teletext (retro terminal)
- ThinUI (low-resource web)

Themes change chrome/tokens only, not step meaning.

### Good Defaults

- one primary action per panel
- visible progress
- explicit back navigation where allowed
- inline validation
- explicit completion state

### Anti-Patterns

- giant multi-decision survey pages
- hidden progress
- ambiguous completion state
- heavy presentation content that hides the next action

## CLI Commands

| Command | Description |
|---------|-------------|
| `udo usx serve` | Serve surface as HTTP endpoint |
| `udo usx export` | Export surface to HTML |
| `udo usx validate <file>` | Validate surface syntax |
| `udo usx list` | List available surfaces |
| `udo usx apply <name>` | Apply a surface theme |

## See Also

- [usx-core.md](usx-core.md) — Core format and fence types
- [usx-ui.md](usx-ui.md) — UI components and authoring blocks
- [usx-style.md](usx-style.md) — Style tokens and themes
