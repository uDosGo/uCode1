# USX Core Specification — v1.0

> **The style/design/surface format for the uDos ecosystem.** Merged from OBF (Open Box Format) and USXD (Universal Surface Definition).

## Core Principle

**Everything is text in a fenced code block.** No proprietary canvas, no binary source, no lock-in.

If it is not in a text code block, it is not USX.

## Document Structure

Every USX document is a self-describing block with a defined kind, identity, and structure.

### Fence Syntax

````markdown
```usx [kind] [options]
# USX document content
```
````

### Required Fields

```yaml
usx: 1.0                    # USX version (required)
kind: Style                  # Document kind (required)
id: style.udos-wireframe     # Unique identifier (required)
name: uDos Wireframe         # Human-readable name (optional)
description: ...             # Description (optional)
version: 1.0.0               # Semantic version (optional)
tags: [wireframe]            # Discovery tags (optional)
```

### Common Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `usx` | string | Yes | USX format version |
| `kind` | string | Yes | Document kind |
| `id` | string | Yes | Unique identifier (dot-separated) |
| `name` | string | No | Human-readable name |
| `description` | string | No | Description |
| `version` | string | No | Semantic version |
| `tags` | string[] | No | Discovery tags |
| `metadata` | object | No | Arbitrary key-value metadata |

## Kinds

USX defines these surface/design kinds:

| Kind | Spec | Description |
|------|------|-------------|
| `UI` | [usx-ui.md](usx-ui.md) | UI component definitions |
| `Style` | [usx-style.md](usx-style.md) | Named theme/style tokens |
| `Grid` | [usx-grid.md](usx-grid.md) | Cell grid layouts |
| `Surface` | [usx-surface.md](usx-surface.md) | Surface definitions |
| `Story` | [usx-surface.md](usx-surface.md) | Story/narrative surfaces |

For system-layer kinds (Skill, Task, Variable, Agent, Workflow, Publish, Meta), see the [UDO specification](../udo/).

## Fence Types

| Fence | Kind | Purpose |
|-------|------|---------|
| ` ```usx ` | Any | USX document (any surface kind) |
| ` ```usx-ui ` | UI | Component definitions: `COMPONENT`, `STYLE`, `VARIANTS` |
| ` ```usx-style ` | Style | Named theme: colours, typography, spacing |
| ` ```usx-grid ` | Grid | Cell grid: attributes `size`, `mode`, cell addresses |
| ` ```usx-surface ` | Surface | Surface definition |
| ` ```usx-story ` | Story | Narrative surface with step progression |
| ` ```usx-template ` | — | Markdown-first boilerplate |

## ID Convention

IDs use dot-separated namespacing:

```
<domain>.<group>.<name>
```

Examples:
- `ui.dashboard-card`
- `style.udos-wireframe`
- `grid.main-layout`
- `surface.teletext-display`
- `story.onboarding`

## Validation Rules

1. `usx` field must be a valid semver string
2. `kind` must be one of the defined surface kinds
3. `id` must be unique within its scope
4. All required fields must be present

## Legacy Compatibility

USX v1.0 is backward-compatible with:
- **OBF v1.0** — `obf` field accepted as alias for `usx`; ` ```obf ` fences accepted as alias for ` ```usx-ui `
- **USXD A1.0.0** — ` ```usxd ` fences accepted as alias for ` ```usx-surface `

## See Also

- [usx-ui.md](usx-ui.md) — UI components and authoring blocks
- [usx-style.md](usx-style.md) — Style tokens and themes
- [usx-surface.md](usx-surface.md) — Surface definitions and story format
- [usx-grid.md](usx-grid.md) — Grid system and cell maths
- [UDO specification](../udo/) — System-layer kinds (Skill, Task, Workflow, etc.)
