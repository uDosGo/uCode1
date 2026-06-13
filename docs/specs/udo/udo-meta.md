---
title: "UDO Meta Specification — v1.0"
status: draft
last_updated: 2026-05-17T22:11:35+10:00
category: specification
tags: [cli, specification, ucode1, udo]
description: "> **Meta kind — schema definitions and type system.** Migrated from OBF v1.0 Meta kind."
---
# UDO Meta Specification — v1.0

> **Meta kind — schema definitions and type system.** Migrated from OBF v1.0 Meta kind.

## Overview

A **Meta** document defines schemas, types, and validation rules for other UDO documents. Meta kinds enable type-safe document authoring and validation across the ecosystem.

## Schema

```yaml
udo: 1.0
kind: Meta
id: meta.skill-v2
name: Skill Schema v2
description: Schema definition for Skill documents
version: 2.0.0
extends: meta.base-document
defines: Skill
schema:
  fields:
    inputs:
      type: array
      items:
        type: object
        properties:
          name:
            type: string
            required: true
          type:
            type: enum
            values: [string, number, boolean, path, file, secret]
            required: true
          required:
            type: boolean
            default: false
          default:
            type: any
          description:
            type: string
    steps:
      type: array
      items:
        type: object
        properties:
          run:
            type: string
          say:
            type: string
          check:
            type: string
          call:
            type: string
          prompt:
            type: string
          foreach:
            type: string
          if:
            type: string
    outputs:
      type: array
      items:
        type: object
        properties:
          name:
            type: string
            required: true
          type:
            type: string
            required: true
          description:
            type: string
    timeout:
      type: duration
    retry:
      type: object
      properties:
        attempts:
          type: integer
          default: 1
        delay:
          type: duration
          default: 1s
  validators:
    - rule: "steps must have at least one entry"
      check: "len(steps) > 0"
    - rule: "step must have exactly one action type"
      check: "sum(1 for f in ['run','say','check','call','prompt','foreach','if'] if f in step) == 1"
tags: [meta, schema, skill]
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `defines` | string | Yes | The kind this schema defines |
| `extends` | string | No | Parent schema ID |
| `schema` | SchemaDef | Yes | Field definitions and types |
| `validators` | Validator[] | No | Validation rules |

## Type System

| Type | Description |
|------|-------------|
| `string` | Text value |
| `number` | Numeric value |
| `boolean` | True/false |
| `enum` | One of defined values |
| `array` | Ordered list |
| `object` | Key-value structure |
| `duration` | Time duration (e.g. `30s`, `5m`, `1h`) |
| `date` | ISO 8601 date |
| `path` | File system path |
| `secret` | Encrypted/redacted value |

## See Also

- [udo-core.md](udo-core.md) — Core format
- [udo-skill.md](udo-skill.md) — Skill kind (defined by meta.skill-v2)
