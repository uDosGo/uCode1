# v2 Workflow, Automation, and Runtime Split

## Purpose

Lock the product-level runtime split across Wizard, uHOME, app surfaces, and
gameplay before deeper implementation expands.

## Ownership

- `uDOS-host` hosts the always-on command-centre runtime
- `uDOS-wizard` owns provider adapters, assist, MCP, and remote publishing workflows
- `uHOME-server` owns the `uHOME` service stream and household/local-console fulfillment
- app surfaces own selective user-touch advance or approve interactions
- `uDOS-gameplay` owns interpretation, progression, `LENS`, and `SKIN`-aware
  feedback
- `uDOS-core` owns only the minimal shared contract layer between them

## Product Model

`uDOS-host` is the durable command-centre environment.

Use `uDOS-host` for:

- base browser command centre
- TUI shell
- schedules
- queued execution
- local watchers
- retries and background continuity
- vault, sync, and networking state

Wizard is the adapter and assist surface.

Use Wizard for:

- online assist
- provider-backed flows
- remote publishing
- MCP
- optional approval and policy workflows above the base runtime

## Shared Core Contracts

The shared minimum is:

- `workflow-state`
- `workflow-action`
- `automation-job`
- `automation-result`
- `artifact-ref`
- `capability-registry`
- `event-log`

These contracts should stay small enough that multiple repos can consume them
without inheriting each other's policy.

Machine-readable source of truth:

- `uDOS-core/contracts/workflow-state-contract.json`
- `uDOS-core/contracts/workflow-action-contract.json`
- `uDOS-core/contracts/automation-job-contract.json`
- `uDOS-core/contracts/automation-result-contract.json`

## Design Rule

Wizard does not need to be open for routine fulfillment to continue.

Wizard may still be required for:

- online API assist
- conscious mission advancement
- explicit approval gates
- re-planning or policy changes

This is the intended v2 behavior.

## GUI Rule

- primary browser operator GUI belongs to `uDOS-host`
- Thin GUI belongs to `uDOS-thinui` and selected local service consumers
- shared render and theme contracts stay in `uDOS-core` and `uDOS-themes`

No UI shim is required yet. The boundary is the priority.
