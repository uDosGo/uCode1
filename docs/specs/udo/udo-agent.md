# UDO Agent Specification — v1.0

> **Agent kind — AI and automation definitions.** Migrated from OBF v1.0 Agent kind.

## Overview

An **Agent** is an AI or automated process definition — a self-contained unit that can observe, decide, and act within the ecosystem.

## Schema

```yaml
udo: 1.0
kind: Agent
id: agent.code-reviewer
name: Code Reviewer
description: AI agent that reviews pull requests
model: deepseek-coder        # AI model identifier
provider: deepseek            # AI provider
system_prompt: |
  You are a senior code reviewer. Analyze pull requests for:
  - Code quality and style
  - Security vulnerabilities
  - Performance issues
  - Test coverage
capabilities:
  - review:pr
  - comment:issue
  - suggest:fix
triggers:
  - event: pull_request.opened
  - event: pull_request.synchronize
config:
  max_tokens: 4096
  temperature: 0.3
  review_depth: full          # full | diff | summary
tags: [ai, code-review, automation]
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `model` | string | Yes | AI model identifier |
| `provider` | string | Yes | AI provider (deepseek, openai, anthropic, etc.) |
| `system_prompt` | string | Yes | System prompt defining agent behavior |
| `capabilities` | string[] | No | List of capabilities the agent provides |
| `triggers` | Trigger[] | No | Events that activate the agent |
| `config` | AgentConfig | No | Model configuration parameters |
| `tools` | ToolDef[] | No | Tools the agent can use |
| `memory` | MemoryConfig | No | Memory and context configuration |

## Triggers

```yaml
triggers:
  - event: pull_request.opened
    filter: "{{repo}} == OkAgentDigital/DevStudio"
  - event: schedule.cron
    cron: "0 6 * * 1"         # Every Monday at 6 AM
  - event: webhook
    url: /api/agents/code-reviewer/trigger
```

## Tools

```yaml
tools:
  - name: search_code
    description: Search codebase for patterns
    skill: skill.search-code
  - name: run_tests
    description: Run test suite
    skill: skill.run-tests
```

## Memory

```yaml
memory:
  type: semantic              # semantic | episodic | procedural
  ttl: 30d                    # Time-to-live for memories
  vector_store: chroma
  embedding_model: deepseek-embed
```

## See Also

- [udo-core.md](udo-core.md) — Core format
- [udo-skill.md](udo-skill.md) — Skills that agents can invoke
- [udo-workflow.md](udo-workflow.md) — Workflows that trigger agents
