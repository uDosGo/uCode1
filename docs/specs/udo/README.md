---
title: "UDO — Unified Document Object Format"
status: draft
last_updated: 2026-05-17T22:11:35+10:00
category: specification
tags: [cli, specification, ucode1, udo]
description: "**UDO** is the system-layer document format for the uDos ecosystem. It defines structured document kinds for skills, ..."
---
# UDO — Unified Document Object Format

**UDO** is the system-layer document format for the uDos ecosystem. It defines structured document kinds for skills, tasks, variables, agents, workflows, and publishing — the "what it does" layer.

**UDO is for how things work.** For style/design/surface definitions (UI, themes, grids, surfaces), see the [USX spec](../usx/).

## What UDO Covers

| Spec | What It Defines | Merged From |
|------|----------------|-------------|
| [udo-core.md](udo-core.md) | Core format: kinds, document structure, ID convention | `obf-core.md` (general structure) |
| [udo-skill.md](udo-skill.md) | Skill kind — invocable capabilities | `obf-core.md` (Skill section) |
| [udo-task.md](udo-task.md) | Task kind — work items with state | `obf-core.md` (Task section) |
| [udo-variable.md](udo-variable.md) | Variable kind — configuration/secrets | `obf-core.md` (Variable section) |
| [udo-agent.md](udo-agent.md) | Agent kind — AI/automation definitions | `obf-agents.md` |
| [udo-workflow.md](udo-workflow.md) | Workflow kind — multi-step processes | `obf-workflows.md` |
| [udo-publish.md](udo-publish.md) | Publish kind — release pipelines | `obf-publish.md` |
| [udo-meta.md](udo-meta.md) | Meta kind — schema definitions, type system | `obf-meta.md` |

## Core Principle

> **Everything is a self-describing document.** No hidden state, no implicit configuration.

## Version

Current: **UDO v1.0** (migrated from OBF v1.0 system kinds)

## Location

- **Canonical specs:** `uCode1/docs/specs/udo/`
- **Implementation:** `uCode1/core_py/snack/` (skill engine), `uCode1/core_py/binder/` (document processing)
- **Legacy redirects:** `uCode1/docs/specs/usxd/` (stub files pointing here)
