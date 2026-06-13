---
title: "uCode1 Spatial-Character Mapping Reference"
status: draft
last_updated: 2026-04-25T16:27:54+10:00
category: reference
tags: [ucode1]
description: "L<level>-<gridX><gridY>-<cellX><cellY>-<layer>"
---
# uCode1 Spatial-Character Mapping Reference

## Quick Reference Guide

### Spatial Coordinate Format
```
L<level>-<gridX><gridY>-<cellX><cellY>-<layer>
Example: L100-AA10-0317-0
```

### C-Layer Character Format
```
CXXX#YYY
Example: C245#1 (:rocket:)
```

### Combined Format
```
[CXXX#YYY]@L<level>-<gridXY>-<cellXY>-<layer>
Example: :rocket: (C245#1)@L100-AA10-0317-0
```

## Common Spatial-Character Mappings

### Facility & Infrastructure

| Character | C-Layer Code | Spatial Use | Coordinate Example |
|-----------|--------------|-------------|---------------------|
| :door: | C123#1 | Main entrance | L100-AA10-0317-0 |
| :computer: | C187#1 | Server room | L100-AA10-0318-1 |
| :satellite: | C245#2 | Satellite dish | L100-AA10-0319-2 |
| :factory: | C301#1 | Factory | L100-AA10-0320-0 |
| :construction: | C301#2 | Construction site | L100-AA10-0321-1 |

### Status & Alerts

| Character | C-Layer Code | Spatial Use | Coordinate Example |
|-----------|--------------|-------------|---------------------|
| ✅ :check: | C211#1 | Operational | L100-AA10-0317-0 |
| ⚠️ :warning: | C345#1 | Warning | L100-AA10-0318-1 |
| ❌ :x: | C212#1 | Failure | L100-AA10-0319-2 |
| 🔒 :lock: | C312#1 | Secure area | L100-AA10-0320-0 |
| 🚨 :sos: | C345#2 | Emergency | L100-AA10-0321-1 |

### Network & IT

| Character | C-Layer Code | Spatial Use | Coordinate Example |
|-----------|--------------|-------------|---------------------|
| 🌐 :globe_with_meridians: | C187#2 | Network hub | L100-AA10-0317-0 |
| 📡 :signal_strength: | C187#3 | Antenna | L100-AA10-0318-1 |
| 🖥️ :desktop_computer: | C187#4 | Workstation | L100-AA10-0319-2 |
| 📶 :wireless: | C187#5 | WiFi access | L100-AA10-0320-0 |
| 🔌 :electric_plug: | C187#6 | Power source | L100-AA10-0321-1 |

### Transportation

| Character | C-Layer Code | Spatial Use | Coordinate Example |
|-----------|--------------|-------------|---------------------|
| 🚗 :car: | C245#3 | Parking | L100-AA10-0317-0 |
| 🚲 :bike: | C245#4 | Bike rack | L100-AA10-0318-1 |
| 🚇 :train: | C245#5 | Train station | L100-AA10-0319-2 |
| ✈️ :airplane: | C245#6 | Airport | L100-AA10-0320-0 |
| 🚢 :ship: | C245#7 | Port | L100-AA10-0321-1 |

### Utilities

| Character | C-Layer Code | Spatial Use | Coordinate Example |
|-----------|--------------|-------------|---------------------|
| 💧 :droplet: | C123#2 | Water source | L100-AA10-0317-0 |
| ⚡ :zap: | C123#3 | Electrical | L100-AA10-0318-1 |
| 🔥 :fire: | C123#4 | Heating | L100-AA10-0319-2 |
| 💨 :wind: | C123#5 | Ventilation | L100-AA10-0320-0 |
| ♻️ :recycle: | C123#6 | Recycling | L100-AA10-0321-1 |

## Teletext Spatial Elements

### UI Components

| Character | C-Layer Code | Spatial Use | Example |
|-----------|--------------|-------------|---------|
| [C400#1] | C400#1 | Solid wall | █ |
| [C404#1] | C404#1 | Path | ━━━━━ |
| [C405#1] | C405#1 | Vertical divider | ┃ |
| [C406#1] | C406#1 | Top-left corner | ┏ |
| [C407#1] | C407#1 | Top-right corner | ┓ |

### Facility Layout

```markdown
┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Data Center Layout   ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  [C400#1] Entrance     ┃
┃  [C400#1] Lobby        ┃
┃  [C400#1] Security     ┃
┃  [C400#1] Server Room  ┃
┃  [C400#1] Network Ops  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Spatial Character Patterns

### Status Dashboard

```markdown
# System Status @L100-AA10-0317-0

## Network
- ✅ Core Router :check: (C211#1)
- ✅ Switch A :check: (C211#1)
- ⚠️ Switch B :warning: (C345#1)

## Servers
- ✅ Web Server :check: (C211#1)
- ✅ DB Server :check: (C211#1)
- ❌ Backup Server :x: (C212#1)

## Power
- ✅ UPS A :check: (C211#1)
- ✅ UPS B :check: (C211#1)
```

### Facility Map

```markdown
# Facility Map @L100-AA10-0317-0

┌───────────────────────────────┐
│  Level 1: Data Center Floor    │
├───────────────────────────────┤
│  :door: Entrance (C123#1)     │
│  :computer: IT (C187#1)       │
│  :coffee: Break Room (C245#1)│
│  :warning: Fire Exit (C345#1) │
└───────────────────────────────┘
```

## Spatial Character Queries

### CLI Examples

```bash
# List all characters at a coordinate
ucode1 spatial-chars list L100-AA10-0317-0

# Find warning characters in a grid
ucode1 spatial-chars find C345#1 L100-AA10-0317-0 L100-AA10-0319-2

# Export spatial character map
ucode1 spatial-chars export L100-AA10-0317-0 3x3 markdown
```

### SQL Examples

```sql
-- Get all emoji characters at a location
SELECT * FROM spatial_characters
WHERE ucode = 'L100-AA10-0317-0' 
AND character_type = 'emoji';

-- Get all warning characters in a grid
SELECT * FROM spatial_characters
WHERE ucode LIKE 'L100-AA10-%'
AND character_code = 'C345#1';

-- Count characters by type in a layer
SELECT character_type, COUNT(*) as count
FROM spatial_characters
WHERE ucode LIKE 'L100-AA10-%'
GROUP BY character_type;
```

## Spatial Character Coordinate Examples

### Level 100 Examples

```markdown
# Office Building @L100-AA10-0317-0
- :door: Main Entrance (C123#1)
- :computer: IT Department (C187#1)
- :coffee: Break Room (C245#1)

# Server Room @L100-AA10-0318-1
- :computer: Rack A1 (C187#1)
- :computer: Rack A2 (C187#1)
- :warning: UPS Alert (C345#1)

# Network Closet @L100-AA10-0319-2
- 🌐 Core Switch (C187#2)
- 📡 WiFi Controller (C187#3)
- 🔌 Power Panel (C187#6)
```

### Level 0 Examples (Large Scale)

```markdown
# City Landmarks @L0-AA00-0000-0
- 🏙️ Downtown (C245#8)
- 🌉 Bridge (C245#9)
- 🏞️ Park (C245#10)

# Transportation Hub @L0-AA00-0001-0
- 🚇 Subway (C245#5)
- 🚗 Parking (C245#3)
- ✈️ Airport (C245#6)
```

## Spatial Character Best Practices

### Consistency Guidelines

1. **Standard Mappings**: Use consistent character types for similar features
2. **Coordinate Patterns**: Maintain uniform spatial organization
3. **Documentation**: Include C-layer references in all spatial maps
4. **Fallbacks**: Provide text alternatives for all spatial characters

### Performance Tips

1. **Density Limits**: Max 4-6 characters per cell
2. **Indexing**: Use spatial indexes for fast queries
3. **Caching**: Cache frequently accessed spatial character maps
4. **Rendering**: Optimize character rendering for viewport size

### Accessibility Recommendations

1. **Contrast**: Ensure sufficient visual contrast
2. **Alternatives**: Provide text descriptions
3. **Zoom Support**: Test at different zoom levels
4. **Color Blind**: Use distinguishable patterns

## Spatial Character Tools

### Character Placement

```bash
# Place character at coordinate
ucode1 spatial-place L100-AA10-0317-0 C245#1 "Main Entrance" 12 12

# Batch place characters
ucode1 spatial-batch place characters.csv

# Remove character
ucode1 spatial-remove L100-AA10-0317-0 C245#1
```

### Character Export

```bash
# Export to markdown
ucode1 spatial-export L100-AA10-0317-0 markdown

# Export to JSON
ucode1 spatial-export L100-AA10-0317-0 json

# Export range
ucode1 spatial-export L100-AA10-0317-0 L100-AA10-0319-2 markdown
```

## Spatial Character Reference Tables

### Common Character Types by Category

| Category | Characters | C-Layer Range |
|----------|------------|---------------|
| Entrances | :door:, :revolving_door: | C123#1-C123#5 |
| IT Equipment | :computer:, :server: | C187#1-C187#10 |
| Status | :check:, :warning:, :x: | C211#1-C345#2 |
| Network | :globe:, :signal: | C187#11-C187#20 |
| Transportation | :car:, :train: | C245#11-C245#20 |

### Teletext UI Elements

| Element | Character | C-Layer Code |
|---------|-----------|--------------|
| Wall | █ | C400#1 |
| Path | ━ | C404#1 |
| Corner | ┏┓┗┛ | C406#1-C409#1 |
| Junction | ┳┻┣┫╋ | C410#1-C414#1 |

## Spatial Character Integration Examples

### Facility Management

```markdown
# Data Center @L100-AA10-0317-0

## Floor Layout
┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Data Center Floor 1     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  :door: Entrance          ┃
┃  :computer: IT           ┃
┃  :coffee: Break Room     ┃
┃  :warning: Fire Exit     ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━┛

## Status Board
- ✅ Core Router :check: (C211#1)
- ✅ Switch A :check: (C211#1)
- ⚠️ Switch B :warning: (C345#1)
```

### Network Topology

```markdown
# Network Map @L100-AA10-0317-0

┌───────────────────────────────┐
│  Network Topology             │
├───────────────────────────────┤
│  🌐 Core Router (C187#2)       │
│  📡 Access Point (C187#3)      │
│  🖥️ Server Farm (C187#4)      │
│  🔌 Power UPS (C187#6)         │
└───────────────────────────────┘

## Connections
- 🌐 Core ↔ 📡 Access :check: (C211#1)
- 🌐 Core ↔ 🖥️ Servers :check: (C211#1)
- 📡 Access ↔ 🔌 UPS :warning: (C345#1)
```

## Spatial Character Quick Reference

### Common Patterns

```markdown
# Quick Reference

## Entrances
:door: Main (C123#1)
:revolving_door: Lobby (C123#2)
:door: Service (C123#3)

## Status
✅ OK (C211#1)
⚠️ Warning (C345#1)
❌ Error (C212#1)

## IT Equipment
:computer: Server (C187#1)
:desktop_computer: Workstation (C187#4)
:printer: Printer (C187#7)
```

### Teletext UI

```markdown
# UI Elements

## Borders
┏━━━━┓ Top (C404#1)
┃     ┃ Side (C405#1)
┗━━━━┛ Bottom (C404#1)

## Corners
┏ Top-left (C406#1)
┓ Top-right (C407#1)
┗ Bottom-left (C408#1)
┛ Bottom-right (C409#1)
```

---

© 2024 uCode1 Team
**Mapping Version**: 1.0
**Last Updated**: 2024-04-25
**Reference**: uCode1/docs/SPATIAL_CHARACTER_MAPPING.md