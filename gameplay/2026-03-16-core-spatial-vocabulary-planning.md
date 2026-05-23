# Core Spatial Vocabulary Planning Note

## Purpose

Define the minimum neutral spatial and file-location vocabulary that should be Core-supported in uDOS v2.0.5, ensuring boundaries remain clear between Core, Grid, and Gameplay.

## Canonical Place Identity

- Short form: `L{Layer}-{Cell}[-Z{z}]`
  - Example: `L300-AJ11`, `L300-AJ11-Z1`
- Portable PlaceRef: `ANCHOR:SPACE:LAYER-CELL[-Z]`
  - Example: `EARTH:SUR:L300-AJ11`, `GAME:VRT:L420-BB05-Z-2`

## Seed Layer and Domain Anchors

- Earth: `EARTH` (L300–L305 seed, L306+ overlays)
- Virtual: `GAME` (L420+)
- Planetary: `BODY:{planet}` (L610+)
- Orbital: `SKY` (L700+)
- Stellar/Galaxy: `GALAXY` (L800+)

## File and Artifact Location Fields

- `place_ref`: Canonical PlaceRef string (see above)
- `layer`: Layer identifier (e.g., `L300`)
- `cell`: Cell identifier (e.g., `AJ11`)
- `z`: Optional Z coordinate (integer, may be omitted)
- `anchor`: Domain anchor (e.g., `EARTH`, `GAME`)

## Minimum Core-Supported Spatial Conditions

- PlaceRef parsing and validation
- Layer/cell/anchor field extraction
- File/artifact attachment by PlaceRef
- Proximity and equality checks (e.g., same cell, same layer)
- No spatial dataset or registry ownership in Core

## Boundary Principles

- Core recognizes and validates PlaceRef, but does not own spatial datasets
- Grid remains the owner of place truth and spatial registries
- Gameplay remains the owner of interpretation and presentation
- Core only provides neutral, contract-level support for spatial references

## Tags

@dev/grid-core-support
@dev/core-place-ref
@dev/core-location-vocabulary
@dev/core-file-location
@dev/core-artifact-location
@dev/core-spatial-conditions
@dev/core-gameplay-hooks

---

This note identifies the Core-worthy spatial slice for v2.0.5 Round A. All further contract and implementation work should reference these boundaries and field definitions.