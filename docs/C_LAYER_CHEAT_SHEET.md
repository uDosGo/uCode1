---
title: "uCode1 C-Layer Character System Cheat Sheet"
status: draft
last_updated: 2026-04-25T16:27:54+10:00
category: documentation
tags: [ucode1]
description: "- **CXXX**: Layer number (100-899)"
---
# uCode1 C-Layer Character System Cheat Sheet

## 🎯 Quick Reference

### C-Layer Format: `CXXX#YYY`
- **CXXX**: Layer number (100-899)
- **YYY**: Character position within layer (1-256)
- **Example**: `C245#1` = Emoji layer 245, character 1 (:rocket:)

## 📚 Layer Reference

### Default Layer (C100)
```
C100#0-C100#255: Standard ANSI + Extended ASCII
- C100#0-C100#127: Standard ANSI characters
- C100#128-C100#255: Extended ASCII characters
- C100#256: Last character of default layer
```

### Emoji Layers (C101-C356)
```
C101#1-C356#256: 256-character emoji map
- C245#1: :rocket: (Launch/startup)
- C187#1: :computer: (Technical/systems)
- C123#1: :book: (Documentation/learning)
- C312#1: :lock: (Security/privacy)
- C287#1: :gear: (Settings/configuration)
- C345#1: :warning: (Alerts/warnings)
- C211#1: :check: (Success/completion)
- C212#1: :x: (Errors/failure)
```

### Teletext Blocks (C400-C499)
```
C400#1-C499#256: UI elements and borders
Format: [CXXX#YYY]
- [C400#1]: █ (Solid block)
- [C404#1]: ━ (Horizontal line)
- [C405#1]: ┃ (Vertical line)
- [C406#1]: ┏ (Top-left corner)
- [C407#1]: ┓ (Top-right corner)
- [C408#1]: ┗ (Bottom-left corner)
- [C409#1]: ┛ (Bottom-right corner)
```

### C64 Characters (C500-C599)
```
C500#1-C599#256: Retro computing characters
Format: {C64:CXXX#YYY}
- {C64:C00#1}: Space
- {C64:C65#1}: A (Standard)
- {C64:C128#1}: A (Orange)
- {C64:C144#1}: Graphics A
```

### Acorn Characters (C600-C699)
```
C600#1-C699#256: UK heritage characters
Format: {ACN:CXXX#YYY}
- {ACN:C00#1}: Space
- {ACN:C32#1}: £ (Pound sign)
- {ACN:C64#1}: @
- {ACN:C96#1}: Graphics block
```

## 🎨 Common Character Combinations

### Status Indicators
```markdown
✅ Success :check: (C211#1)
❌ Error :x: (C212#1)
⚠️ Warning :warning: (C345#1)
🔒 Secure :lock: (C312#1)
```

### UI Elements
```markdown
┏━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  Title Here [C404#1]      ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━┫
┃  Content...              ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Technical Documentation
```markdown
# System Status :rocket: (C245#1)

## Database Connection ✅ (C211#1)
- Status: Online
- Response time: 12ms

## Command Processing :gear: (C287#1)
- Active commands: 42
- Queue depth: 3
```

## 🔤 Character Format Examples

### Emoji Format
```markdown
:emoji: (CXXX#YYY)
:rocket: (C245#1)
:computer: (C187#1)
```

### Teletext Format
```markdown
[CXXX#YYY]
[C400#1] = █
[C404#1] = ━
```

### C64 Format
```markdown
{C64:CXXX#YYY}
{C64:C65#1} = A
{C64:C128#1} = A (orange)
```

### Acorn Format
```markdown
{ACN:CXXX#YYY}
{ACN:C32#1} = £
{ACN:C64#1} = @
```

## 📊 Layer Range Summary

| Layer Range | Purpose | Format | Example |
|-------------|---------|--------|---------|
| C100#0-C100#255 | Default (ANSI/ASCII) | Direct | `A` |
| C101#1-C356#256 | Emoji | `:emoji:` | `:rocket:` (C245#1) |
| C400#1-C499#256 | Teletext Blocks | `[CXXX#YYY]` | `[C404#1]` (━) |
| C500#1-C599#256 | C64 Characters | `{C64:CXXX#YYY}` | `{C64:C65#1}` (A) |
| C600#1-C699#256 | Acorn Characters | `{ACN:CXXX#YYY}` | `{ACN:C32#1}` (£) |
| C700#1-C799#256 | Reserved | - | - |
| C800#1-C899#256 | Custom | - | - |

## 🎯 Usage Guidelines

### Priority Order
1. **Standard ANSI** (C100) - Maximum compatibility
2. **Emoji** (:emoji:) - Visual emphasis
3. **Teletext Blocks** ([CXXX#YYY]) - UI elements
4. **C64 Characters** ({C64:CXXX#YYY}) - Retro computing
5. **Acorn Characters** ({ACN:CXXX#YYY}) - UK heritage

### Best Practices
- **Consistency**: Use same characters for same concepts
- **Moderation**: 1-2 special characters per section max
- **Fallbacks**: Always provide ANSI alternatives
- **Documentation**: Include C-layer references
- **Testing**: Verify rendering in different terminals

## 🔧 Quick Reference Table

### Common Emoji Shortcuts
```
✅ Success = :check: (C211#1)
❌ Error = :x: (C212#1)
⚠️ Warning = :warning: (C345#1)
🔒 Security = :lock: (C312#1)
⚙️ Settings = :gear: (C287#1)
🚀 Launch = :rocket: (C245#1)
💻 Tech = :computer: (C187#1)
📖 Docs = :book: (C123#1)
```

### Common UI Elements
```
█ Block = [C400#1]
━ Line = [C404#1]
┃ Vertical = [C405#1]
┏ Corner = [C406#1]
┓ Corner = [C407#1]
┗ Corner = [C408#1]
┛ Corner = [C409#1]
```

## 🎓 Learning Resources

### Character System Layers
```
C100: Default Layer (ANSI base)
C101-C356: Emoji Layers (256 chars each)
C400-C499: Teletext Blocks
C500-C599: C64 Character Set
C600-C699: Acorn Character Set
C700-C799: Reserved
C800-C899: Custom
```

### Remember
- **C100#256**: Last character of default layer
- **CXXX#YYY**: Layer#Character format
- **Multi-layer**: Collections can span multiple C-layers

---

© 2024 uCode1 Team
**Cheat Sheet Version**: 1.0
**Last Updated**: 2024-04-25
**Reference**: uCode1/docs/C_LAYER_CHEAT_SHEET.md