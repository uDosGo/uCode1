# UDO Variable Specification — v1.0

> **Variable kind — configuration and secrets.** Migrated from OBF v1.0 Variable kind.

## Overview

A **Variable** is a configuration value, secret, or environment state — the data layer of the ecosystem.

## Schema

```yaml
udo: 1.0
kind: Variable
id: var.github-token
name: GitHub Personal Access Token
description: Token for GitHub API access
type: secret                 # string | secret | number | boolean | json
scope: user                  # user | project | global
encrypted: true
tags: [github, auth]
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | enum | Yes | Data type: `string`, `secret`, `number`, `boolean`, `json` |
| `scope` | enum | Yes | Visibility scope: `user`, `project`, `global` |
| `encrypted` | boolean | No | Whether value is encrypted |
| `default` | any | No | Default value |
| `validation` | string | No | Regex or schema for validation |

## See Also

- [udo-core.md](udo-core.md) — Core format
