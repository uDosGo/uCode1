# Triage: Wizard and Core/Grid v2 Specs

- title: Wizard and Core/Grid v2 spec brief package
- date: 2026-03-16
- related binder: `#binder/dev-v2-0-4-wizard-core-grid-spec-routing`
- working tag: `@dev/wizard-core-grid-specs`
- related repos:
  - `uDOS-dev`
  - `uDOS-wizard`
  - `uDOS-core`
  - `uDOS-grid`
- status: `triaged`

## Summary

This intake package consolidates Wizard and Core/Grid spec briefs from
`@dev/inbox/briefs` and maps them to current canonical docs. Most Wizard v2
spec material is now promoted. Core/Grid promotion now includes named split
contract docs, and the Grid security/gameplay contract depth has been expanded.

## Brief Coverage

- `u_dos_v_2_OK Agent MCP Architecture.md`
  - promoted to `uDOS-wizard/docs/OK-AGENT-MCP-ARCHITECTURE.md`
- `u_dos_v_2_wizard_ok_targets.md`
  - promoted to `uDOS-wizard/docs/OK-AGENT-PROVIDERS.md`
  - promoted to `uDOS-wizard/docs/OK-PROVIDER-ROUTING-ENGINE.md`
- `u_dos_v_2_ok_agents_3_way_spec.md`
  - named split docs promoted across `uDOS-core`, `uDOS-wizard`, and `uDOS-dev`
- `u_dos_grid_spatial_brief_v_2.md`
  - partially promoted to `uDOS-grid/docs/spatial-runtime.md`
- `u_dos_grid_spatial_runtime_contract.md`
  - promoted baseline in `uDOS-grid/docs/spatial-runtime.md`
- `u_dos_grid_spatial_security_and_gameplay_link.md`
  - expanded in `uDOS-grid/docs/security-gameplay-link.md`

## Findings

- Wizard architecture docs for providers, routing, and MCP are already in
  canonical repo docs and aligned with Round A boundary ownership.
- Core has v2.0.4 OK contract coverage in
  `uDOS-core/docs/v2.0.4-ok-agent-core-contracts.md` and matching contract
  artifacts.
- Grid has published runtime/security/seed docs, but the security-gameplay
  contract depth is now aligned with permission, validation, and audit guidance.
- The named split docs requested by the 3-way spec are now present in canonical
  repo docs.
- Status language is normalized across Wizard OK docs as recommended
  architecture with initial implementation.

## Promotion Gaps

1. Round A owner acceptance is still pending for the updated submission package.
2. MCP editor integration implementation remains intentionally deferred until
  boundary lock acceptance, even though the design note is now published.

## Next Actions

- Route round-2 submission for Round A owner acceptance.
- Keep MCP editor integration at design-ready status until boundary lock
  acceptance gates implementation.
- Keep boundary ownership unchanged while promoting docs:
  Core contract owner, Wizard managed network owner, Grid spatial truth owner,
  Dev workflow owner.
