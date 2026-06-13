---
title: "UDO Task Specification — v1.0"
status: draft
last_updated: 2026-05-17T22:11:35+10:00
category: specification
tags: [cli, specification, ucode1, udo]
description: "> **Task kind — work items with state.** Migrated from OBF v1.0 Task kind."
---
# UDO Task Specification — v1.0

> **Task kind — work items with state.** Migrated from OBF v1.0 Task kind.

## Overview

A **Task** is a work item with state, priority, and dependencies — representing something that needs to be done.

## Schema

```yaml
udo: 1.0
kind: Task
id: task.release-v1.0
name: Release v1.0.0
description: Coordinate the v1.0.0 release
status: active              # active | completed | archived | blocked
priority: high              # critical | high | medium | low
assignee: team-lead
due: 2026-06-01
depends_on:
  - task.build-complete
  - task.tests-pass
tags: [release, v1.0]
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `status` | enum | Yes | Current state: `active`, `completed`, `archived`, `blocked` |
| `priority` | enum | No | Importance level: `critical`, `high`, `medium`, `low` |
| `assignee` | string | No | Responsible party |
| `due` | date | No | Due date |
| `depends_on` | string[] | No | Task dependencies |
| `labels` | string[] | No | Categorization labels |
| `estimate` | duration | No | Time estimate |

## See Also

- [udo-core.md](udo-core.md) — Core format
- [udo-workflow.md](udo-workflow.md) — Orchestrating tasks in workflows
