# UDO Core Specification — v1.0

> **Core format for system-layer documents in the uDos ecosystem.** Migrated from OBF v1.0 system kinds.

## Document Structure

Every UDO document is a self-describing document with a defined kind, identity, and structure.

### Required Fields

```yaml
udo: 1.0                    # UDO version (required)
kind: Skill                  # Document kind (required)
id: skill.build-package      # Unique identifier (required)
name: Build Package          # Human-readable name (optional)
description: ...             # Description (optional)
version: 1.0.0               # Semantic version (optional)
tags: [build]                # Discovery tags (optional)
extends: base.skill          # Parent schema (optional)
```

### Common Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `udo` | string | Yes | UDO format version |
| `kind` | string | Yes | Document kind |
| `id` | string | Yes | Unique identifier (dot-separated) |
| `name` | string | No | Human-readable name |
| `description` | string | No | Description |
| `version` | string | No | Semantic version |
| `tags` | string[] | No | Discovery tags |
| `extends` | string | No | Parent schema ID |
| `metadata` | object | No | Arbitrary key-value metadata |

## Kinds

| Kind | Spec | Description |
|------|------|-------------|
| `Skill` | [udo-skill.md](udo-skill.md) | Invocable capability |
| `Task` | [udo-task.md](udo-task.md) | Work item with state |
| `Variable` | [udo-variable.md](udo-variable.md) | Configuration/secrets |
| `Agent` | [udo-agent.md](udo-agent.md) | AI/automation definition |
| `Workflow` | [udo-workflow.md](udo-workflow.md) | Multi-step process |
| `Publish` | [udo-publish.md](udo-publish.md) | Release pipeline |
| `Meta` | [udo-meta.md](udo-meta.md) | Schema/type definitions |

## ID Convention

IDs use dot-separated namespacing:

```
<domain>.<group>.<name>
```

Examples:
- `skill.build-package`
- `task.release-v1.0`
- `var.github-token`
- `agent.code-reviewer`
- `workflow.deploy-prod`
- `publish.pypi`
- `meta.skill-v2`

## Validation Rules

1. `udo` field must be a valid semver string
2. `kind` must be one of the defined kinds
3. `id` must be unique within its scope
4. All required fields must be present
5. Template expressions `{{...}}` must reference valid inputs/variables

## Legacy Compatibility

UDO v1.0 is backward-compatible with OBF v1.0 system kinds — `obf` field accepted as alias for `udo`.

## See Also

- [udo-skill.md](udo-skill.md) — Skill kind
- [udo-task.md](udo-task.md) — Task kind
- [udo-variable.md](udo-variable.md) — Variable kind
- [udo-agent.md](udo-agent.md) — Agent kind
- [udo-workflow.md](udo-workflow.md) — Workflow kind
- [udo-publish.md](udo-publish.md) — Publish kind
- [udo-meta.md](udo-meta.md) — Meta kind
- [USX specification](../usx/) — Style/design/surface layer
