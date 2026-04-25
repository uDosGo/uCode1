# uCode1 SPRITE & OBJECT Reference

## Overview

This document provides a comprehensive reference for **SPRITE** and **OBJECT** cell types in uCode1, including their characteristics, usage patterns, and implementation details.

## 1. Cell Type Comparison

### 1.1 SPRITE vs OBJECT

```yaml
SPRITE:
  type: "animated/interactive"
  size: "24×24 pixels (1 CELL)"
  characteristics: "alive, animated, personality"
  examples: ":robot:, :fairy:, :goblin:"
  use_cases: "characters, assistants, NPCs"

OBJECT:
  type: "inanimate/interactive"
  size: "24×24 pixels (1 CELL)"
  characteristics: "static, functional, utilitarian"
  examples: ":pick:, :purse:, :wrench:"
  use_cases: "tools, containers, equipment"
```

### 1.2 Feature Comparison Table

| Feature | SPRITE | OBJECT |
|---------|--------|--------|
| **Animation** | ✅ Yes (pulse, float, spin, etc.) | ❌ No (static) |
| **Personality** | ✅ Yes (traits, behaviors) | ❌ No |
| **AI Behavior** | ✅ Yes (can move, react) | ❌ No |
| **Interactivity** | ✅ Yes (hover, click, complex) | ✅ Yes (use, equip, simple) |
| **Storage** | ✅ 45KB CELL data | ✅ 45KB CELL data |
| **Multiple Frames** | ✅ Yes (animation sequences) | ❌ No (single frame) |
| **Examples** | :robot:, :fairy:, :elf: | :pick:, :purse:, :wrench: |
| **Use Cases** | Characters, assistants, NPCs | Tools, items, containers |

## 2. SPRITE Reference

### 2.1 SPRITE Characteristics

**Animated**: SPRITE cells support multiple animation frames stored in the 45KB CELL data.

**Interactive**: SPRITE cells respond to user interactions with hover effects, click actions, and complex behaviors.

**Personality**: SPRITE cells can have custom personality traits that influence their behavior.

**Behavioral**: SPRITE cells can exhibit AI-driven behaviors and autonomous actions.

### 2.2 SPRITE Types

#### Character SPRITEs

```yaml
character_sprites:
  - type: "assistant"
    examples: [":robot:", ":fairy:", ":genie:"]
    c_layer_range: "C245#1-C245#50"
    characteristics: "helpful, interactive, animated"
    use_cases: "user assistants, guides, helpers"

  - type: "npc"
    examples: [":elf:", ":goblin:", ":wizard:"]
    c_layer_range: "C245#51-C245#100"
    characteristics: "autonomous, behavioral, personality"
    use_cases: "non-player characters, quest givers, story elements"

  - type: "creature"
    examples: [":dragon:", ":unicorn:", ":phoenix:"]
    c_layer_range: "C245#101-C245#150"
    characteristics: "animated, behavioral, complex"
    use_cases: "fantasy creatures, pets, companions"
```

#### Decoration SPRITEs

```yaml
decoration_sprites:
  - type: "effect"
    examples: [":sparkles:", ":stars:", ":fireworks:"]
    c_layer_range: "C245#151-C245#200"
    characteristics: "animated, decorative, atmospheric"
    use_cases: "visual effects, ambiance, mood setting"

  - type: "particle"
    examples: [":zap:", ":boom:", ":dizzy:"]
    c_layer_range: "C245#201-C245#250"
    characteristics: "dynamic, temporary, effect-based"
    use_cases: "magic effects, explosions, status indicators"
```

### 2.3 SPRITE Properties

```yaml
sprite_properties:
  hover_text:
    description: "Text displayed when user hovers over sprite"
    example: "Click for help"
    format: "string"

  click_action:
    description: "Action triggered when user clicks sprite"
    example: "assistant"
    format: "string (action identifier)"

  animation:
    description: "Animation type for sprite"
    options: ["pulse", "float", "spin", "bounce", "shake", "none"]
    example: "pulse"
    format: "string"

  animation_speed:
    description: "Speed of animation"
    options: ["slow", "medium", "fast"]
    example: "slow"
    format: "string"

  personality:
    description: "Personality traits (for character sprites)"
    traits: ["friendly", "helpful", "humorous", "technical", "serious"]
    example: {"friendly": true, "helpful": true}
    format: "JSON object"

  behavior:
    description: "AI behavior pattern"
    options: ["passive", "active", "aggressive", "curious", "shy"]
    example: "active"
    format: "string"
```

### 2.4 SPRITE Examples

#### Assistant SPRITE

```markdown
# Interactive Assistant
:robot: Assistant (C245#1)@L100-AA10-0317-0[
  hover="Click for help",
  click="assistant",
  animation="pulse",
  personality={"friendly":true,"helpful":true,"technical":true}
]
```

#### Fantasy Character SPRITE

```markdown
# Magic Helper
:fairy: Fairy (C245#50)@L100-AA10-0318-1[
  hover="Cast spell",
  click="magic",
  animation="float",
  personality={"friendly":true,"humorous":true,"helpful":true}
]
```

#### Creature SPRITE

```markdown
# Mythical Creature
:dragon: Dragon (C245#101)@L100-AA10-0319-2[
  hover="Beware!",
  click="interact",
  animation="bounce",
  personality={"aggressive":true,"powerful":true}
]
```

#### Effect SPRITE

```markdown
# Visual Effect
:sparkles: Magic (C245#151)@L100-AA10-0320-0[
  animation="pulse",
  speed="medium",
  duration="continuous"
]
```

## 3. OBJECT Reference

### 3.1 OBJECT Characteristics

**Static**: OBJECT cells are single-frame and do not animate.

**Functional**: OBJECT cells serve practical purposes and can be manipulated by users.

**Utilitarian**: OBJECT cells represent tools, containers, and equipment.

**Interactive**: OBJECT cells support basic interactions like use, equip, and open.

### 3.2 OBJECT Types

#### Tool OBJECTs

```yaml
tool_objects:
  - type: "digging"
    examples: [":pick:", ":shovel:"]
    c_layer_range: "C301#1-C301#10"
    characteristics: "durable, functional, equipment"
    use_cases: "construction, mining, excavation"

  - type: "repair"
    examples: [":wrench:", ":hammer:"]
    c_layer_range: "C301#11-C301#20"
    characteristics: "functional, durable, utilitarian"
    use_cases: "maintenance, repair, building"

  - type: "precision"
    examples: [":gear:", ":nut_and_bolt:"]
    c_layer_range: "C301#21-C301#30"
    characteristics: "precise, technical, specialized"
    use_cases: "engineering, mechanics, assembly"
```

#### Container OBJECTs

```yaml
container_objects:
  - type: "storage"
    examples: [":purse:", ":bag:", ":box:"]
    c_layer_range: "C245#11-C245#20"
    characteristics: "capacity, organizable, portable"
    use_cases: "inventory, storage, transportation"

  - type: "specialized"
    examples: [":toolbox:", ":briefcase:", ":backpack:"]
    c_layer_range: "C245#21-C245#30"
    characteristics: "organized, functional, purpose-specific"
    use_cases: "professional, technical, organized storage"
```

#### Utility OBJECTs

```yaml
utility_objects:
  - type: "lighting"
    examples: [":flashlight:", ":bulb:"]
    c_layer_range: "C301#31-C301#40"
    characteristics: "functional, illuminative, portable"
    use_cases: "visibility, exploration, emergency"

  - type: "measurement"
    examples: [":ruler:", ":balance_scale:"]
    c_layer_range: "C301#41-C301#50"
    characteristics: "precise, functional, technical"
    use_cases: "measurement, calibration, analysis"
```

### 3.3 OBJECT Properties

```yaml
object_properties:
  hover_text:
    description: "Text displayed when user hovers over object"
    example: "Digging tool"
    format: "string"

  click_action:
    description: "Primary action when user clicks object"
    options: ["use", "equip", "open", "examine", "pickup"]
    example: "equip"
    format: "string"

  action:
    description: "Specific action performed by object"
    options: ["dig", "repair", "open", "measure", "cut"]
    example: "dig"
    format: "string"

  capacity:
    description: "Storage capacity (for containers)"
    example: 10
    format: "integer"

  durability:
    description: "Usage lifespan (for tools)"
    example: 100
    format: "integer (percentage)"

  material:
    description: "Construction material"
    options: ["steel", "wood", "plastic", "glass", "stone"]
    example: "steel"
    format: "string"

  contents:
    description: "Items contained within (for containers)"
    example: ["key", "coin", "tool"]
    format: "array of strings"
```

### 3.4 OBJECT Examples

#### Tool OBJECT

```markdown
# Digging Tool
:pick: Shovel (C301#1)@L100-AA10-0317-0[
  hover="Digging tool",
  click="equip",
  action="dig",
  durability=100,
  material="steel"
]
```

#### Container OBJECT

```markdown
# Storage Bag
:purse: Bag (C245#11)@L100-AA10-0318-1[
  hover="Storage bag",
  click="open",
  capacity=10,
  contents=["key", "coin", "tool"],
  material="leather"
]
```

#### Utility OBJECT

```markdown
# Repair Tool
:wrench: Wrench (C301#11)@L100-AA10-0319-2[
  hover="Repair tool",
  click="use",
  action="repair",
  durability=75,
  material="steel"
]
```

#### Measurement OBJECT

```markdown
# Precision Tool
:ruler: Ruler (C301#41)@L100-AA10-0320-0[
  hover="Measuring tool",
  click="use",
  action="measure",
  precision="mm",
  material="metal"
]
```

## 4. Implementation Patterns

### 4.1 SPRITE Implementation

```rust
// Create a character SPRITE
let sprite = SpatialCharacter {
    ucode: "L100-AA10-0317-0".to_string(),
    character_code: "C245#1".to_string(),
    character_type: "sprite".to_string(),
    entity_type: Some("character".to_string()),
    description: Some("Assistant Bot".to_string()),
    x_offset: 12,
    y_offset: 12,
    interactive_properties: Some(serde_json::json!({
        "hover": "Click for help",
        "click": "assistant",
        "animation": "pulse"
    })),
    animation_frames: Some(3),
    personality_traits: Some(serde_json::json!({
        "friendly": true,
        "helpful": true,
        "technical": true
    })),
    object_properties: None
};

// Place the SPRITE
usystem.place_spatial_character(sprite);

// Update SPRITE animation
usystem.update_sprite_animation("L100-AA10-0317-0", "C245#1", "float");

// Trigger SPRITE behavior
usystem.trigger_sprite_behavior("L100-AA10-0317-0", "C245#1", "help");
```

### 4.2 OBJECT Implementation

```rust
// Create a tool OBJECT
let tool = SpatialCharacter {
    ucode: "L100-AA10-0318-1".to_string(),
    character_code: "C301#1".to_string(),
    character_type: "object".to_string(),
    entity_type: Some("tool".to_string()),
    description: Some("Shovel".to_string()),
    x_offset: 8,
    y_offset: 8,
    interactive_properties: Some(serde_json::json!({
        "hover": "Digging tool",
        "click": "equip",
        "action": "dig"
    })),
    animation_frames: None,
    personality_traits: None,
    object_properties: Some(serde_json::json!({
        "durability": 100,
        "material": "steel",
        "type": "digging"
    }))
};

// Place the OBJECT
usystem.place_spatial_character(tool);

// Use OBJECT
usystem.use_object("L100-AA10-0318-1", "C301#1");

// Update OBJECT durability
usystem.update_object_durability("L100-AA10-0318-1", "C301#1", 95);
```

### 4.3 SPRITE-OBJECT Interaction

```rust
// SPRITE picks up OBJECT
usystem.sprite_pickup_object(
    "L100-AA10-0317-0",  // SPRITE coordinate
    "C245#1",           // SPRITE code
    "L100-AA10-0318-1",  // OBJECT coordinate
    "C301#1"            // OBJECT code
);

// SPRITE uses OBJECT
usystem.sprite_use_object(
    "L100-AA10-0317-0",  // SPRITE coordinate
    "C245#1",           // SPRITE code
    "L100-AA10-0318-1",  // OBJECT coordinate
    "C301#1"            // OBJECT code
);

// SPRITE drops OBJECT
usystem.sprite_drop_object(
    "L100-AA10-0317-0",  // SPRITE coordinate
    "C245#1",           // SPRITE code
    "L100-AA10-0319-2"   // Target coordinate
);
```

## 5. SPRITE & OBJECT Queries

### 5.1 SQL Queries

```sql
-- Get all SPRITEs at a location
SELECT * FROM spatial_characters
WHERE ucode = 'L100-AA10-0317-0'
AND character_type = 'sprite';

-- Get all OBJECTs in a grid
SELECT * FROM spatial_characters
WHERE ucode LIKE 'L100-AA10-%'
AND character_type = 'object';

-- Get all character SPRITEs with specific personality
SELECT * FROM spatial_characters
WHERE character_type = 'sprite'
AND entity_type = 'character'
AND personality_traits LIKE '%friendly%';

-- Get all tool OBJECTs with low durability
SELECT * FROM spatial_characters
WHERE character_type = 'object'
AND entity_type = 'tool'
AND object_properties LIKE '%durability%'
AND json_extract(object_properties, '$.durability') < 20;
```

### 5.2 CLI Queries

```bash
# List all SPRITEs at coordinate
ucode1 sprite-list L100-AA10-0317-0

# List all OBJECTs in grid
ucode1 object-list L100-AA10-0317-0 L100-AA10-0319-2

# Get SPRITE details
ucode1 sprite-details L100-AA10-0317-0 C245#1

# Get OBJECT details
ucode1 object-details L100-AA10-0318-1 C301#1

# Export SPRITE map
ucode1 sprite-export L100-AA10-0317-0 3x3 markdown

# Export OBJECT inventory
ucode1 object-export L100-AA10-0318-1 2x2 json
```

## 6. SPRITE & OBJECT Best Practices

### 6.1 SPRITE Best Practices

1. **Animation Economy**: Limit animation complexity for performance
2. **Personality Consistency**: Maintain consistent personality traits
3. **Behavior Boundaries**: Define clear behavior rules
4. **Interaction Feedback**: Provide clear user feedback
5. **Performance Optimization**: Cache frequently used SPRITEs

### 6.2 OBJECT Best Practices

1. **Functional Clarity**: Clear purpose and usage
2. **Durability Management**: Track and update durability states
3. **Capacity Limits**: Enforce reasonable capacity limits
4. **Material Realism**: Use appropriate material properties
5. **Interaction Simplicity**: Keep interactions straightforward

### 6.3 Integration Best Practices

1. **Type Separation**: Keep SPRITE and OBJECT logic distinct
2. **Interaction Patterns**: Define clear interaction rules
3. **Performance Balancing**: Optimize SPRITE-OBJECT interactions
4. **State Management**: Track interaction states properly
5. **Error Handling**: Graceful handling of invalid interactions

## 7. SPRITE & OBJECT Reference Tables

### 7.1 Common SPRITE Types

| Type | C-Layer Range | Examples | Characteristics |
|------|---------------|----------|----------------|
| Assistant | C245#1-C245#10 | :robot:, :fairy: | Helpful, interactive |
| NPC | C245#11-C245#50 | :elf:, :goblin: | Autonomous, behavioral |
| Creature | C245#51-C245#100 | :dragon:, :unicorn: | Animated, complex |
| Effect | C245#101-C245#150 | :sparkles:, :zap: | Decorative, dynamic |

### 7.2 Common OBJECT Types

| Type | C-Layer Range | Examples | Characteristics |
|------|---------------|----------|----------------|
| Tool | C301#1-C301#50 | :pick:, :wrench: | Functional, durable |
| Container | C245#11-C245#50 | :purse:, :box: | Storage, portable |
| Utility | C301#51-C301#100 | :flashlight:, :ruler: | Specialized, precise |

### 7.3 Animation Types

| Animation | Description | Speed Options |
|-----------|-------------|---------------|
| pulse | Gentle pulsing effect | slow, medium, fast |
| float | Gentle floating motion | slow, medium, fast |
| spin | Rotational movement | slow, medium, fast |
| bounce | Bouncing effect | slow, medium, fast |
| shake | Shaking motion | slow, medium, fast |
| none | No animation | - |

### 7.4 Personality Traits

| Trait | Description | Applies To |
|-------|-------------|------------|
| friendly | Helpful and approachable | Characters |
| helpful | Provides assistance | Characters |
| humorous | Jokes and lighthearted | Characters |
| technical | Knowledgeable and precise | Characters |
| serious | Professional and formal | Characters |
| aggressive | Confrontational | Creatures |
| powerful | Strong and dominant | Creatures |
| curious | Inquisitive | NPCs |
| shy | Reserved and cautious | NPCs |

## 8. SPRITE & OBJECT Examples

### 8.1 Fantasy Adventure

```markdown
# Fantasy World @L100-AA10-0317-0

## Characters
- :fairy: Guide (C245#50)@L100-AA10-0317-0[hover="Help",click="guide"]
- :goblin: Trader (C245#15)@L100-AA10-0318-1[hover="Trade",click="shop"]

## Objects
- :pick: Mining Tool (C301#1)@L100-AA10-0319-2[hover="Shovel",click="equip"]
- :purse: Treasure Bag (C245#20)@L100-AA10-0320-0[hover="Loot",click="open"]
```

### 8.2 Facility Management

```markdown
# Data Center @L100-AA10-0317-0

## Assistants
- :robot: Tech Bot (C245#1)@L100-AA10-0317-0[hover="Help",click="assist"]
- :computer: AI Helper (C245#2)@L100-AA10-0318-1[hover="Info",click="query"]

## Tools
- :wrench: Repair Kit (C301#11)@L100-AA10-0319-2[hover="Tools",click="use"]
- :flashlight: Inspection Light (C301#31)@L100-AA10-0320-0[hover="Light",click="equip"]
```

### 8.3 Game Inventory

```markdown
# Player Inventory @L100-AA10-0317-0

## Character
- :elf: Hero (C245#12)@L100-AA10-0317-0[hover="Hero",click="stats",animation="pulse"]

## Equipment
- :pick: Mining Pick (C301#1)@L100-AA10-0318-1[hover="Pickaxe",click="equip",durability=85]
- :purse: Backpack (C245#21)@L100-AA10-0319-2[hover="Bag",click="open",capacity=15]
- :wrench: Repair Kit (C301#11)@L100-AA10-0320-0[hover="Tools",click="use",uses=10]
```

## 9. Future Development

### 9.1 SPRITE Enhancements

**v1.1**: Advanced animation system with physics
**v1.2**: SPRITE-to-SPRITE communication
**v1.3**: SPRITE learning and adaptation
**v1.4**: SPRITE emotion system

### 9.2 OBJECT Enhancements

**v1.1**: OBJECT crafting and combination
**v1.2**: OBJECT wear and tear visualization
**v1.3**: OBJECT nesting and containment
**v1.4**: OBJECT market and trading

### 9.3 Integration Enhancements

**v1.1**: SPRITE-OBJECT crafting system
**v1.2**: SPRITE-OBJECT quest system
**v1.3**: SPRITE-OBJECT economy system
**v1.4**: SPRITE-OBJECT social system

---

© 2024 uCode1 Team
**SPRITE/OBJECT Version**: 1.0
**Last Updated**: 2024-04-25
**Reference**: uCode1/docs/SPRITE_OBJECT_REFERENCE.md