---
title: "uCode1 Character Set Reference"
status: draft
last_updated: 2026-04-25T16:27:54+10:00
category: reference
tags: [reference, ucode1]
description: "uCode1 implements a sophisticated multi-layered character mapping system that combines modern emoji with retro comput..."
---
# uCode1 Character Set Reference

## Overview

uCode1 implements a sophisticated multi-layered character mapping system that combines modern emoji with retro computing character sets, providing a rich visual language for documentation, UI elements, and technical communication.

## Character System Architecture

```
┌───────────────────────────────────────────────────┐
│               uCode1 Character System              │
├───────────────────────────────────────────────────┤
│  Default Layer: C100 (ANSI base)                  │
│  Emoji Layers:   C101-C356 (256 characters)       │
│  Teletext:       C400-C499 (block characters)     │
│  C64 Characters:  C500-C599 (retro computing)      │
│  Acorn:          C600-C699 (UK heritage)         │
│  Reserved:       C700-C799 (future expansion)      │
│  Custom:         C800-C899 (user-defined)        │
└───────────────────────────────────────────────────┘
```

**Key Features**:
- **Base Layer**: C100 provides ANSI compatibility (C100#0-C100#255)
- **Multi-Layer Collections**: Character sets can span multiple C-layers (C101+)
- **Character Format**: C-layer#character (e.g., C100#256)
- **Max Layer**: C899 for maximum flexibility
- **Default Layer**: C100 ensures backward compatibility

**C-Layer Character Format**:
- Format: `CXXX#YYY` where XXX = layer, YYY = character position
- Example: `C100#256` = Default layer, character 256
- Example: `C245#1` = Emoji layer 245, first character
- Last character in layer: `C100#256` (C100#256 would be last of default layer)

## Base Character Sets

### 1. ANSI Character Set (0-127)

Standard ASCII characters for maximum compatibility.

**Range**: 0-127
**Usage**: Default fallback, technical documentation
**Examples**: `A`, `1`, `@`, `[`, `{`

### 2. Extended ASCII (128-255)

Additional characters for European languages and symbols.

**Range**: 128-255  
**Usage**: International text, special symbols
**Examples**: `é`, `ü`, `£`, `§`

## uCode1 Extended Character Map (#100-#356)

### Emoji Reference System

**Format**: `:emoji:` (CXXX#YYY)
**Range**: C101#1-C356#256 (256-character emoji map)
**Usage**: Visual emphasis, status indicators, categorization

#### Common Emoji Mappings

| Emoji | Code | Position | Usage |
|-------|------|----------|------|
| `:rocket:` | `C245#1` | C245#1 | Launch, startup, deployment |
| `:computer:` | `C187#1` | C187#1 | Technical, computing, systems |
| `:book:` | `C123#1` | C123#1 | Documentation, learning, reference |
| `:lock:` | `C312#1` | C312#1 | Security, privacy, encryption |
| `:gear:` | `C287#1` | C287#1 | Settings, configuration, options |
| `:warning:` | `C345#1` | C345#1 | Alerts, warnings, attention |
| `:check:` | `C211#1` | C211#1 | Success, completion, verification |
| `:x:` | `C212#1` | C212#1 | Errors, failure, cancellation |
| `:lightbulb:` | `C198#1` | C198#1 | Ideas, tips, suggestions |
| `:mag:` | `C276#1` | C276#1 | Search, discovery, exploration |
| `:wrench:` | `C301#1` | C301#1 | Tools, utilities, maintenance |
| `:shield:` | `C322#1` | C322#1 | Protection, safety, defense |

### Emoji Usage Guidelines

1. **Consistency**: Use the same emoji for consistent concepts
2. **Moderation**: 1-2 emoji per section maximum
3. **Clarity**: Prefer widely-recognized emoji
4. **Fallbacks**: Provide text alternatives
5. **Documentation**: Reference character positions

## Teletext Block Characters (C400#1-C499#256)

### Format: `[CXXX#YYY]`

**Usage**: UI elements, borders, layouts, diagrams

### Common Block Characters

| Character | Code | Description | Example |
|-----------|------|-------------|---------|
| `[C400#1]` | C400#1 | Solid block | █ |
| `[C401#1]` | C401#1 | Light shade | ░ |
| `[C402#1]` | C402#1 | Medium shade | ▒ |
| `[C403#1]` | C403#1 | Dark shade | ▓ |
| `[C404#1]` | C404#1 | Horizontal line | ━ |
| `[C405#1]` | C405#1 | Vertical line | ┃ |
| `[C406#1]` | C406#1 | Top-left corner | ┏ |
| `[C407#1]` | C407#1 | Top-right corner | ┓ |
| `[C408#1]` | C408#1 | Bottom-left corner | ┗ |
| `[C409#1]` | C409#1 | Bottom-right corner | ┛ |
| `[C410#1]` | C410#1 | T-junction top | ┳ |
| `[C411#1]` | C411#1 | T-junction bottom | ┻ |
| `[C412#1]` | C412#1 | T-junction left | ┣ |
| `[C413#1]` | C413#1 | T-junction right | ┫ |
| `[C414#1]` | C414#1 | Cross junction | ╋ |

### Teletext UI Examples

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃          uCode1 System Status         ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  Database: ✅ Online (#211)            ┃
┃  Commands: 42 Active (#123)            ┃
┃  Users:    8 Online (#187)            ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## C64 Character Set (C500#1-C599#256)

### Format: `{C64:CXXX#YYY}`

**Usage**: Retro computing, authentic C64 feel, gaming references

### Common C64 Characters

| Character | Code | C64 Code | Description |
|-----------|------|----------|-------------|
| `{C64:C00#1}` | C500#1 | 0 | Space |
| `{C64:C01#1}` | C501#1 | 1 | ! |
| `{C64:C02#1}` | C502#1 | 2 | " |
| `{C64:C65#1}` | C565#1 | 65 | A |
| `{C64:C66#1}` | C566#1 | 66 | B |
| `{C64:C97#1}` | C597#1 | 97 | a |
| `{C64:C128#1}` | C628#1 | 128 | Orange A |
| `{C64:C129#1}` | C629#1 | 129 | Orange B |
| `{C64:C144#1}` | C644#1 | 144 | Graphics A |
| `{C64:C145#1}` | C645#1 | 145 | Graphics B |

### C64 Usage Examples

```
{C64:65}{C64:66}{C64:67} = ABC (Standard)
{C64:128}{C64:129}{C64:130} = ABC (Orange)
{C64:144}{C64:145}{C64:146} = ABC (Graphics)
```

## Acorn Teletext Character Set (C600#1-C699#256)

### Format: `{ACN:CXXX#YYY}`

**Usage**: UK computing heritage, Teletext services, retro UI

### Common Acorn Characters

| Character | Code | Acorn Code | Description |
|-----------|------|------------|-------------|
| `{ACN:C00#1}` | C600#1 | 0 | Space |
| `{ACN:C32#1}` | C632#1 | 32 | £ (Pound sign) |
| `{ACN:C64#1}` | C664#1 | 64 | @ |
| `{ACN:C96#1}` | C696#1 | 96 | Graphics block |
| `{ACN:C128#1}` | C728#1 | 128 | Contiguous graphics |
| `{ACN:C160#1}` | C760#1 | 160 | Separated graphics |

## Character System Integration

### Markdown Usage Examples

```markdown
# System Status :rocket: (#245)

## Database Connection ✅ (#211)
- Status: Online
- Response time: 12ms

## Command Processing :gear: (#287)
- Active commands: 42
- Queue depth: 3

┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Performance Metrics  ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  CPU:   12% [#404]    ┃
┃  Memory: 64% [#402]    ┃
┃  Disk:   28% [#401]    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## Implementation Guidelines

### 1. Character Selection

**Priority Order**:
1. Standard ANSI (for compatibility)
2. Emoji (:emoji: format)
3. Teletext blocks ([#XXX])
4. C64 characters ({C64:XX})
5. Acorn characters ({ACN:XX})

### 2. Fallback Strategy

```markdown
# Success ✅ :check: (#211)
# (Fallback: Success [OK])
```

### 3. Documentation Standards

- **Technical Docs**: Prefer ANSI + limited emoji
- **UI Elements**: Use Teletext blocks
- **Retro Content**: Use C64/Acorn characters
- **Status Indicators**: Use emoji with references

### 4. Character Map Reference

Always include character references in documentation:

```markdown
**Status Indicators**:
- ✅ Success :check: (#211)
- ❌ Error :x: (#212)
- ⚠️ Warning :warning: (#345)
```

## Character System Tools

### Character Map Lookup

```bash
# Lookup character position
ucode1 char lookup :rocket:
# Result: :rocket: = #245

# Display character
ucode1 char show #245
# Result: ✅ :rocket:

# List character range
ucode1 char list #200-#250
```

### Character Testing

```bash
# Test character rendering
ucode1 char test :rocket: [#256] {C64:65}

# Validate character set
ucode1 char validate
```

## Best Practices

### 1. Consistency
- Use same characters for same concepts
- Document character choices
- Maintain character reference guide

### 2. Accessibility
- Provide text alternatives
- Ensure sufficient contrast
- Test with different terminals

### 3. Performance
- Limit special character usage
- Cache frequently used characters
- Prefer standard characters for speed

### 4. Internationalization
- Use Unicode-compatible characters
- Provide locale-specific alternatives
- Test with different character encodings

## Character System Reference

### Quick Reference Table

| Category | Format | Range | Usage |
|----------|--------|-------|-------|
| ANSI | Direct | C100#0-C100#255 | Default fallback |
| Extended ASCII | Direct | C100#128-C100#255 | International text |
| Emoji | `:emoji:` | C101#1-C356#256 | Visual emphasis |
| Teletext Blocks | `[CXXX#YYY]` | C400#1-C499#256 | UI elements |
| C64 Characters | `{C64:CXXX#YYY}` | C500#1-C599#256 | Retro computing |
| Acorn Characters | `{ACN:CXXX#YYY}` | C600#1-C699#256 | UK heritage |

### Character Position Reference

```
C100#0-C100#255: Default Layer (ANSI base)
C101#1-C356#256: Emoji Layers (256 characters)
C400#1-C499#256: Teletext Block Characters
C500#1-C599#256: C64 Character Set
C600#1-C699#256: Acorn Teletext Set  
C700#1-C799#256: Reserved for future expansion
C800#1-C899#256: Custom/user-defined layers
```

**C-Layer Character Format Examples**:
- `C100#256` = Default layer, last character (C100#256 would be last of default layer)
- `C245#1` = Emoji layer 245, first character (:rocket:)
- `C404#1` = Teletext horizontal line (━)
- `C565#1` = C64 character 'A'
- `C632#1` = Acorn pound sign (£)

## Future Development

### Planned Enhancements

1. **Character Map Editor**: Visual character selection tool
2. **Theme Support**: Different character sets per theme
3. **Custom Mappings**: User-defined character associations
4. **Performance Optimization**: Character rendering cache
5. **Accessibility Features**: Screen reader compatibility

### Roadmap

- **v1.1**: Character map visualization tool
- **v1.2**: Theme-based character set switching
- **v1.3**: User-customizable character mappings
- **v1.4**: Advanced accessibility features

---

© 2024 uCode1 Team. All rights reserved.

**Character System Version**: 1.0
**Last Updated**: 2024-04-25
**Reference**: uCode1/CHARACTER_SET_REFERENCE.md