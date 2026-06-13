---
title: "UDO Skill Specification — v1.0"
status: draft
last_updated: 2026-05-17T22:11:35+10:00
category: specification
tags: [cli, specification, ucode1, udo]
description: "> **Skill kind — invocable capabilities.** Migrated from OBF v1.0 Skill kind."
---
# UDO Skill Specification — v1.0

> **Skill kind — invocable capabilities.** Migrated from OBF v1.0 Skill kind.

## Overview

A **Skill** is an invocable capability — a reusable unit of functionality that can be executed by agents, users, or workflows.

## Schema

```yaml
udo: 1.0
kind: Skill
id: skill.build-package
name: Build Python Package
description: Build a Python package using build
inputs:
  - name: source_dir
    type: path
    required: true
    description: Path to source directory
  - name: output_dir
    type: path
    default: ./dist
    description: Output directory for built artifacts
steps:
  - run: python -m build --outdir {{output_dir}} {{source_dir}}
  - check: "{{exit_code}} == 0"
    fail: Build failed
outputs:
  - name: artifacts
    type: path[]
    description: List of built artifacts
tags: [build, python, package]
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `inputs` | InputDef[] | No | Parameters the skill accepts |
| `steps` | Step[] | Yes | Ordered execution steps |
| `outputs` | OutputDef[] | No | Values the skill produces |
| `timeout` | duration | No | Maximum execution time |
| `retry` | RetryPolicy | No | Retry behavior on failure |

## Step Types

| Step Type | Description | Example |
|-----------|-------------|---------|
| `run` | Execute a shell command | `run: python build.py` |
| `say` | Log a message | `say: "Building..."` |
| `check` | Assert a condition | `check: "{{result}} == 0"` |
| `call` | Invoke another skill | `call: skill.validate` |
| `prompt` | Ask for user input | `prompt: "Enter version:"` |
| `foreach` | Iterate over items | `foreach: items` |
| `if` | Conditional branch | `if: "{{env}} == prod"` |

## See Also

- [udo-core.md](udo-core.md) — Core format
- [udo-workflow.md](udo-workflow.md) — Orchestrating multiple skills
- [udo-agent.md](udo-agent.md) — Agents that invoke skills
