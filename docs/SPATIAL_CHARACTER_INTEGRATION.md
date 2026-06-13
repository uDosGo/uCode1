---
title: "uCode1 Spatial Grid & Character System Integration"
status: draft
last_updated: 2026-04-25T16:27:54+10:00
category: documentation
tags: [ucode1]
description: "This document specifies how the **uCode1 Spatial Grid System** integrates with the **C-Layer Character System** to en..."
---
# uCode1 Spatial Grid & Character System Integration

## Overview

This document specifies how the **uCode1 Spatial Grid System** integrates with the **C-Layer Character System** to enable rich spatial documentation, mapping, and visualization.

## 1. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 uCode1 Integrated System                    │
├─────────────────────────────────────────────────────────────┤
│  Spatial Grid System          │  C-Layer Character System    │
│  (Coordinate-based)           │  (Visual representation)     │
├─────────────────────────────────────────────────────────────┤
│  L<level>-<gridXY>-<cellXY>  │  CXXX#YYY Character Format   │
│  Example: L100-AA10-0317-2   │  Example: C245#1 (:rocket:)   │
└─────────────────────────────────────────────────────────────┘
```

## 2. Integration Points

### 2.1 Spatial Character Anchoring

**Concept**: Characters can be anchored to specific spatial coordinates, enabling location-based documentation and visual mapping.

**Format**:
```markdown
[CXXX#YYY]@L<level>-<gridXY>-<cellXY>-<layer>
```

**Examples**:
```markdown
# Main Entrance :door: (C123#1)@L100-AA10-0317-0
# Server Room :computer: (C187#1)@L100-AA10-0318-1
# Emergency Exit :warning: (C345#1)@L100-AA10-0319-2
```

### 2.2 Character Grid Mapping

**Concept**: Create visual character maps that align with spatial grids.

**Format**:
```markdown
┏━━━━━━━━━━━━━━━━━━━━━━━━┓ [C404#1]@L100-AA10-0317-0
┃  Floor Plan: Level 1     ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  :door: Entrance (C123#1) ┃
┃  :computer: IT (C187#1)   ┃
┃  :coffee: Break (C245#1)  ┃

### 2.3 SPRITE Cell Type (Animated/Interactive)

**Concept**: SPRITE cells enable **animated characters and interactive personalities** using the base emoji map as Generation 1 sprites. SPRITEs are "alive" and can have behaviors, animations, and personalities.

**Format**:
```markdown
SPRITE@L<level>-<gridXY>-<cellXY>-<layer>[<interactive_properties>]
```

**Examples**:
```markdown
# Interactive Assistant :robot: (C245#1)@L100-AA10-0317-0[hover="Help",click="assistant"]
# Fantasy Character :fairy: (C245#50)@L100-AA10-0318-1[hover="Magic",click="spell",animation="float"]
# Animated Decoration :sparkles: (C245#10)@L100-AA10-0319-2[animation="pulse",speed="slow"]
```

**SPRITE Characteristics**:
- **Alive/Animated**: Have movement, animations, personalities
- **Interactive**: Respond to user actions (hover, click)
- **Behaviors**: Can have AI-driven behaviors
- **Personality**: Custom traits and characteristics

### 2.4 OBJECT Cell Type (Inanimate/Interactive)

**Concept**: OBJECT cells represent **inanimate interactive items** that users can manipulate. Unlike SPRITEs, OBJECTs are not "alive" but can still be interactive.

**Format**:
```markdown
OBJECT@L<level>-<gridXY>-<cellXY>-<layer>[<object_properties>]
```

**Examples**:
```markdown
# Tool Object :pick: (C301#10)@L100-AA10-0317-0[hover="Shovel",click="dig",action="equip"]
# Container Object :purse: (C245#20)@L100-AA10-0318-1[hover="Bag",click="open",capacity=10]
# Utility Object :wrench: (C301#5)@L100-AA10-0319-2[hover="Tool",click="use",action="repair"]
```

**OBJECT Characteristics**:
- **Inanimate**: No animation or personality
- **Functional**: Serve practical purposes (tools, containers)
- **Interactive**: Can be picked up, used, or manipulated
- **Static**: No AI behaviors or movement

### 2.5 SPRITE vs OBJECT Comparison

| Feature | SPRITE | OBJECT |
|---------|--------|--------|
| **Animation** | ✅ Yes (pulse, float, etc.) | ❌ No (static) |
| **Personality** | ✅ Yes (traits, behaviors) | ❌ No |
| **AI Behavior** | ✅ Yes (can move, react) | ❌ No |
| **Interactivity** | ✅ Yes (hover, click) | ✅ Yes (use, equip) |
| **Examples** | :robot:, :fairy:, :goblin: | :pick:, :purse:, :wrench: |
| **Use Case** | Characters, assistants, NPCs | Tools, items, containers |

**SPRITE Features**:
- **Size**: 24×24 pixels (matches CELL size)
- **Storage**: Uses CELL's 45KB QR data for sprite frames and metadata
- **Interactivity**: Supports hover text, click actions, animations
- **Animation**: Multiple frames stored in CELL data
- **Personality**: Custom behaviors and traits
┗━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### 2.3 Spatial Character References

**Concept**: Reference characters with their spatial context.

**Format**:
```markdown
**Status Board** @L100-AA10-0317-0
- ✅ Server A :check: (C211#1)
- ⚠️ Server B :warning: (C345#1)
- ❌ Server C :x: (C212#1)
```

## 3. Spatial-Character Data Structures

### 3.1 SQLite Schema Extension

```sql
-- Spatial Character Mapping Table
CREATE TABLE spatial_characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ucode TEXT NOT NULL,           -- Spatial coordinate (L100-AA10-0317-0)
    character_code TEXT NOT NULL,  -- Character code (C245#1)
    character_type TEXT NOT NULL,  -- 'emoji', 'teletext', 'c64', 'acorn', 'sprite', 'object'
    description TEXT,              -- Optional description
    entity_type TEXT,              -- 'character', 'object', 'decoration' (for sprites/objects)
    interactive_properties TEXT,   -- JSON: {"hover":"Help","click":"assistant","animation":"pulse"}
    animation_frames INTEGER,      -- Number of animation frames (for sprites)
    personality_traits TEXT,      -- JSON: {"friendly":true,"helpful":true} (for character sprites)
    object_properties TEXT,       -- JSON: {"capacity":10,"action":"equip"} (for objects)
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (ucode) REFERENCES cells(ucode)
);

-- Character Anchoring Index
CREATE INDEX idx_spatial_characters_ucode ON spatial_characters(ucode);
CREATE INDEX idx_spatial_characters_type ON spatial_characters(character_type);
```

### 3.2 Rust Struct Extension

```rust
#[derive(Debug, Clone)]
pub struct SpatialCharacter {
    pub ucode: String,           // Spatial coordinate
    pub character_code: String,  // C-layer character code
    pub character_type: String,  // emoji/teletext/c64/acorn/sprite/object
    pub description: Option<String>,
    pub x_offset: i32,           // Pixel offset within cell (0-23)
    pub y_offset: i32,           // Pixel offset within cell (0-23)
    pub entity_type: Option<String>, // character/object/decoration
    pub interactive_properties: Option<serde_json::Value>, // hover, click, animation
    pub animation_frames: Option<u8>, // Number of animation frames (sprites only)
    pub personality_traits: Option<serde_json::Value>, // For character sprites
    pub object_properties: Option<serde_json::Value>, // For objects (capacity, action, etc.)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpriteProperties {
    pub hover_text: Option<String>,
    pub click_action: Option<String>,
    pub animation: Option<String>, // "pulse", "spin", "bounce", etc.
    pub animation_speed: Option<String>, // "slow", "medium", "fast"
    pub personality: Option<SpritePersonality>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpritePersonality {
    pub friendly: bool,
    pub helpful: bool,
    pub humorous: bool,
    pub technical: bool,
    pub traits: Vec<String>, // Custom personality traits
}
```

## 4. Spatial Character Operations

### 4.1 Character Placement

```rust
// Place character at spatial coordinate
usystem.place_spatial_character(
    "L100-AA10-0317-0",  // Spatial coordinate
    "C245#1",           // Character code (:rocket:)
    "emoji",            // Character type
    "Main Entrance",    // Description
    12,                 // X offset (pixels)
    12                 // Y offset (pixels)
);
```

### 4.2 Character Retrieval

```rust
// Get all characters at a spatial coordinate
let characters = usystem.get_spatial_characters("L100-AA10-0317-0");

// Get characters in a spatial range
let range_characters = usystem.get_spatial_characters_in_range(
    "L100-AA10-0317-0",  // Start coordinate
    "L100-AA10-0319-2"   // End coordinate
);
```

### 4.3 Character Rendering

```rust
// Render spatial character map
usystem.render_spatial_characters(
    "L100-AA10-0317-0",  // Center coordinate
    5,                   // Radius (cells)
    "markdown"           // Output format
);

// Create interactive SPRITE
let sprite = SpatialCharacter {
    ucode: "L100-AA10-0317-0".to_string(),
    character_code: "C245#1".to_string(),
    character_type: "sprite".to_string(),
    description: Some("Assistant Bot".to_string()),
    x_offset: 12,
    y_offset: 12,
    sprite_type: Some("character".to_string()),
    interactive_properties: Some(serde_json::json!({
        "hover": "Click for help",
        "click": "assistant",
        "animation": "pulse"
    })),
    animation_frames: Some(3),
    personality_traits: Some(serde_json::json!({
        "friendly": true,
        "helpful": true,
        "humorous": false,
        "technical": true
    }))
};

usystem.place_spatial_character(sprite);

// Get interactive SPRITE
let assistant = usystem.get_spatial_character("L100-AA10-0317-0", "C245#1");
if let Some(character) = assistant {
    if character.character_type == "sprite" {
        println!("Found interactive sprite: {:?}", character);
    }
}

// Create interactive OBJECT
let tool = SpatialCharacter {
    ucode: "L100-AA10-0320-0".to_string(),
    character_code: "C301#10".to_string(),
    character_type: "object".to_string(),
    description: Some("Shovel".to_string()),
    x_offset: 8,
    y_offset: 8,
    entity_type: Some("tool".to_string()),
    interactive_properties: Some(serde_json::json!({
        "hover": "Digging tool",
        "click": "equip",
        "action": "dig"
    })),
    animation_frames: None,
    personality_traits: None,
    object_properties: Some(serde_json::json!({
        "durability": 100,
        "material": "steel"
    }))
};

usystem.place_spatial_character(tool);

// Get interactive OBJECT
let shovel = usystem.get_spatial_character("L100-AA10-0320-0", "C301#10");
if let Some(character) = shovel {
    if character.character_type == "object" {
        println!("Found tool object: {:?}", character);
        if let Some(props) = character.object_properties {
            println!("Durability: {}", props["durability"]);
        }
    }
}
```

## 5. Spatial-Character Mapping Examples

### 5.1 Facility Map

```markdown
# Data Center Layout @L100-AA10-0317-0

┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Data Center Floor 1  ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  [C400#1] Entrance     ┃
┃  [C400#1] Lobby        ┃
┃  [C400#1] Security     ┃
┃  [C400#1] Server Room  ┃
┃  [C400#1] Network Ops  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━┛

**Legend**:
- :door: Entrance (C123#1)@L100-AA10-0317-0
- :computer: Servers (C187#1)@L100-AA10-0318-1
- :warning: Fire Ext (C345#1)@L100-AA10-0319-2
```

### 5.2 Status Dashboard

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

### 5.3 Interactive SPRITE Examples

```markdown
# Interactive Control Panel @L100-AA10-0317-0

## Assistant SPRITE
:robot: Assistant (C245#1)@L100-AA10-0317-0[
  hover="Click for help",
  click="assistant",
  animation="pulse",
  personality={"friendly":true,"helpful":true}
]

## Control SPRITE
:control_knobs: Settings (C301#3)@L100-AA10-0318-1[
  hover="System Configuration",
  click="config",
  animation="spin"
]

## Animated Decoration
:sparkles: Effects (C245#10)@L100-AA10-0319-2[
  animation="bounce",
  speed="slow"
]
```

### 5.4 Interactive OBJECT Examples

```markdown
# Tool Inventory @L100-AA10-0320-0

## Tool OBJECT
:pick: Shovel (C301#10)@L100-AA10-0320-0[
  hover="Digging tool",
  click="equip",
  action="dig",
  durability=100
]

## Container OBJECT
:purse: Bag (C245#20)@L100-AA10-0321-1[
  hover="Storage bag",
  click="open",
  capacity=10,
  items=["key", "coin"]
]

## Utility OBJECT
:wrench: Tool (C301#5)@L100-AA10-0322-2[
  hover="Repair tool",
  click="use",
  action="repair",
  uses=50
]
```

## 6. Spatial Character Queries

### 6.1 SQL Queries

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

### 6.2 CLI Queries

```bash
# List spatial characters at coordinate
ucode1 spatial-chars list L100-AA10-0317-0

# Search for specific character in spatial range
ucode1 spatial-chars find C345#1 L100-AA10-0317-0 L100-AA10-0319-2

# Export spatial character map
ucode1 spatial-chars export L100-AA10-0317-0 5x5 markdown
```

## 7. Spatial Character Rendering

### 7.1 Markdown Output

```markdown
# Spatial Character Map: L100-AA10-0317-0

## Coordinate: L100-AA10-0317-0 (Level 100, Grid AA10, Cell 0317, Layer 0)

### Characters at this location:
- :rocket: Launch Point (C245#1)
- :computer: Server Room (C187#1)
- :door: Main Entrance (C123#1)

### Nearby Characters (1-cell radius):
- :warning: Fire Exit (C345#1) @L100-AA10-0318-0
- :check: Status Board (C211#1) @L100-AA10-0316-0
```

### 7.2 JSON Output

```json
{
  "coordinate": "L100-AA10-0317-0",
  "characters": [
    {
      "code": "C245#1",
      "type": "emoji",
      "description": "Launch Point",
      "x_offset": 12,
      "y_offset": 12
    },
    {
      "code": "C187#1",
      "type": "emoji",
      "description": "Server Room",
      "x_offset": 8,
      "y_offset": 8
    }
  ],
  "nearby": [
    {
      "coordinate": "L100-AA10-0318-0",
      "code": "C345#1",
      "type": "emoji",
      "description": "Fire Exit"
    }
  ]
}
```

## 8. Spatial Character Best Practices

### 8.1 Consistency
- Use consistent character types for similar spatial features
- Maintain uniform offset patterns
- Document character meanings in spatial context

### 8.2 Performance
- Limit spatial character density (max 4-6 per cell)
- Use indexing for fast spatial queries
- Cache frequently accessed spatial character maps

### 8.3 Accessibility
- Provide text alternatives for spatial characters
- Ensure sufficient contrast in rendering
- Support zoom levels for different character sizes

## 9. Integration with Spatial Grid System

### 9.1 Coordinate Resolution

```yaml
# Character placement at different spatial resolutions
L0:   # 10km grid, ~7.7m per cell
  - Use large Teletext blocks [C400#1] for major landmarks
  - Limit to 1-2 characters per cell

L1:   # 100m grid, ~7.7cm per cell  
  - Use emoji for building features
  - 2-4 characters per cell maximum

L2:   # 1m grid, ~0.77mm per cell
  - Use small C64/Acorn characters for details
  - Up to 6 characters per cell
```

### 9.2 Viewport Integration

```yaml
# Character rendering at different viewport sizes
watch (20×20 cells):
  - Show only critical spatial characters
  - Use larger character sizes

phone (24×32 cells):
  - Show primary spatial characters
  - Standard character sizes

tablet (48×36 cells):
  - Show all spatial characters
  - Include detailed descriptions
```

## 10. Spatial Character Tools

### 10.1 Character Map Editor

```bash
# Interactive spatial character placement
ucode1 spatial-edit L100-AA10-0317-0

# Batch import spatial characters
ucode1 spatial-import characters.json

# Validate spatial character placement
ucode1 spatial-validate
```

### 10.2 Character Query Tools

```bash
# Find spatial characters by type
ucode1 spatial-find emoji L100-AA10-0317-0

# Export spatial character map
ucode1 spatial-export L100-AA10-0317-0 3x3

# Generate spatial character report
ucode1 spatial-report L100-AA10-0317-0
```

## 11. Spatial Character Reference

### Common Spatial Character Mappings

| Character | C-Layer Code | Spatial Use | Example Coordinate |
|-----------|--------------|-------------|---------------------|
| :rocket: | C245#1 | Launch points | L100-AA10-0317-0 |
| :computer: | C187#1 | Server rooms | L100-AA10-0318-1 |
| :door: | C123#1 | Entrances | L100-AA10-0319-2 |
| :warning: | C345#1 | Hazards | L100-AA10-0320-0 |
| :check: | C211#1 | Status OK | L100-AA10-0321-1 |
| :x: | C212#1 | Status Error | L100-AA10-0322-2 |

### Teletext Spatial Elements

| Character | C-Layer Code | Spatial Use | Example |
|-----------|--------------|-------------|---------|
| [C400#1] | C400#1 | Walls | ━━━━━ |
| [C404#1] | C404#1 | Paths | ━━━━━ |
| [C406#1] | C406#1 | Corners | ┏┓┗┛ |

## 12. Future Development

### Roadmap

**v1.1**: Spatial character visualization tool
**v1.2**: 3D spatial character mapping
**v1.3**: Augmented reality character overlay
**v1.4**: Collaborative spatial character editing

### Planned Features

1. **Spatial Character Layers**: Multiple character layers per coordinate
2. **Character Animation**: Time-based character changes
3. **Character Groups**: Logical grouping of spatial characters
4. **Character Search**: Full-text search across spatial characters

---

© 2024 uCode1 Team
**Integration Version**: 1.0
**Last Updated**: 2024-04-25
**Reference**: uCode1/docs/SPATIAL_CHARACTER_INTEGRATION.md