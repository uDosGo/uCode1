# UDO Publish Specification — v1.0

> **Publish kind — release pipelines and distribution channels.** Migrated from OBF v1.0 Publish kind.

## Overview

A **Publish** document defines a release pipeline — how artifacts are built, signed, versioned, and distributed to registries, repositories, and end users.

## Schema

```yaml
udo: 1.0
kind: Publish
id: publish.pypi
name: PyPI Package Publisher
description: Build and publish Python packages to PyPI
version: 1.0.0
source:
  repo: OkAgentDigital/uCode1
  branch: main
  tag_pattern: "v*"
build:
  tool: python-build
  command: python -m build
  artifacts: ./dist/*
sign:
  enabled: true
  key: var.gpg-signing-key
registries:
  - name: pypi
    type: pypi
    url: https://upload.pypi.org/legacy/
    token: var.pypi-token
  - name: test-pypi
    type: pypi
    url: https://test.pypi.org/legacy/
    token: var.test-pypi-token
channels:
  - name: stable
    registry: pypi
    auto_publish: true
  - name: beta
    registry: test-pypi
    auto_publish: true
notify:
  - channel: slack
    message: "📦 Published {{package.name}} v{{package.version}} to {{registry.name}}"
tags: [publish, python, pypi]
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | SourceDef | Yes | Source repository configuration |
| `build` | BuildDef | Yes | Build tool and command configuration |
| `sign` | SignDef | No | Artifact signing configuration |
| `registries` | Registry[] | Yes | Target distribution registries |
| `channels` | Channel[] | No | Release channels with auto-publish rules |
| `notify` | Notification[] | No | Post-publish notifications |

## Registry Types

| Type | Description |
|------|-------------|
| `pypi` | Python Package Index |
| `npm` | npm registry |
| `crates.io` | Rust crate registry |
| `docker` | Docker container registry |
| `github-release` | GitHub Releases |
| `apt` | Debian/APT repository |
| `homebrew` | Homebrew tap |

## Channel Configuration

```yaml
channels:
  - name: stable
    registry: pypi
    auto_publish: true
    required_checks:
      - workflow.ci-passed
      - workflow.security-scan
  - name: beta
    registry: test-pypi
    auto_publish: true
    pre_release: true
  - name: nightly
    registry: test-pypi
    auto_publish: true
    schedule: "0 2 * * *"
```

## Version Strategy

```yaml
version:
  strategy: semver            # semver | calendar | custom
  bump: patch                 # major | minor | patch | auto
  pre_release: false
  metadata:
    - "{{commit.sha}}"
    - "{{build.timestamp}}"
```

## See Also

- [udo-core.md](udo-core.md) — Core format
- [udo-workflow.md](udo-workflow.md) — Workflows that trigger publishing
