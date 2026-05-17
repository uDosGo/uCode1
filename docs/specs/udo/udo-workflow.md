# UDO Workflow Specification — v1.0

> **Workflow kind — multi-step process definitions.** Migrated from OBF v1.0 Workflow kind.

## Overview

A **Workflow** is a multi-step process that orchestrates skills, tasks, agents, and publishing into a cohesive pipeline. Workflows can branch, loop, wait for conditions, and manage state across steps.

## Schema

```yaml
udo: 1.0
kind: Workflow
id: workflow.deploy-prod
name: Deploy to Production
description: Full production deployment pipeline
version: 1.0.0
triggers:
  - event: workflow.completed
    source: workflow.ci-passed
  - event: manual
    role: deployer
steps:
  - id: build
    name: Build Artifacts
    skill: skill.build-package
    inputs:
      source_dir: ./src
      output_dir: ./dist
  - id: test
    name: Run Tests
    skill: skill.run-tests
    depends_on: [build]
  - id: security-scan
    name: Security Scan
    skill: skill.security-scan
    depends_on: [build]
  - id: approve
    name: Approval Gate
    type: manual
    depends_on: [test, security-scan]
    assignee: team-lead
  - id: deploy
    name: Deploy to Production
    skill: skill.deploy
    inputs:
      environment: production
      artifacts: "{{steps.build.outputs.artifacts}}"
    depends_on: [approve]
  - id: verify
    name: Verify Deployment
    skill: skill.health-check
    inputs:
      endpoint: https://app.example.com/health
    depends_on: [deploy]
    timeout: 5m
    retry:
      attempts: 3
      delay: 10s
on_success:
  - notify:
      channel: slack
      message: "✅ Deployment {{workflow.id}} completed successfully"
on_failure:
  - notify:
      channel: slack
      message: "❌ Deployment {{workflow.id}} failed at step {{failed_step.id}}"
  - rollback:
      skill: skill.rollback
      inputs:
        deployment_id: "{{steps.deploy.outputs.deployment_id}}"
tags: [deploy, production, critical]
```

## Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `triggers` | Trigger[] | No | Events that start the workflow |
| `steps` | WorkflowStep[] | Yes | Ordered execution steps |
| `on_success` | Action[] | No | Actions on successful completion |
| `on_failure` | Action[] | No | Actions on failure |
| `timeout` | duration | No | Maximum workflow execution time |
| `concurrency` | int | No | Max concurrent step executions |

## Step Types

| Step Type | Description |
|-----------|-------------|
| `skill` | Execute a UDO Skill |
| `manual` | Wait for human approval/input |
| `subworkflow` | Execute another workflow |
| `parallel` | Run steps in parallel |
| `foreach` | Iterate over a list |
| `switch` | Conditional branching |
| `wait` | Pause for duration or condition |

## Parallel Execution

```yaml
- id: parallel-checks
  type: parallel
  steps:
    - id: lint
      skill: skill.lint
    - id: test
      skill: skill.test
    - id: security
      skill: skill.security-scan
```

## Conditional Branching

```yaml
- id: deploy-env
  type: switch
  condition: "{{workflow.inputs.environment}}"
  cases:
    production:
      skill: skill.deploy-prod
    staging:
      skill: skill.deploy-staging
    development:
      skill: skill.deploy-dev
  default:
    skill: skill.deploy-dev
```

## State Management

Workflows maintain state across steps:

```yaml
- id: save-state
  skill: skill.save-artifact
  inputs:
    data: "{{steps.build.outputs}}"
    key: "build-{{workflow.id}}"
```

Available context variables:
- `{{workflow.id}}` — Workflow instance ID
- `{{workflow.inputs.*}}` — Workflow input parameters
- `{{steps.<id>.outputs.*}}` — Step output values
- `{{steps.<id>.status}}` — Step completion status
- `{{failed_step.id}}` — ID of the failed step (in on_failure)

## See Also

- [udo-core.md](udo-core.md) — Core format
- [udo-skill.md](udo-skill.md) — Skills invoked by workflow steps
- [udo-agent.md](udo-agent.md) — Agents triggered by workflows
- [udo-publish.md](udo-publish.md) — Publishing pipelines as workflows
