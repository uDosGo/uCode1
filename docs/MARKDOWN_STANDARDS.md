---
title: "uCode1 Markdown Standards"
status: draft
last_updated: 2026-04-25T16:27:54+10:00
category: documentation
tags: [ucode1]
description: "This document establishes the markdown standards for uCode1 documentation, aligning with:"
---
# uCode1 Markdown Standards

## Overview

This document establishes the markdown standards for uCode1 documentation, aligning with:

1. **GitHub Flavored Markdown (GFM)** - https://github.github.com/gfm/
2. **Common Markdown Style Guide** - https://gist.github.com/rxaviers/7360908

## 1. Basic Formatting

### Character Sets and Emoji Usage

**uCode1 Character System**:
- **Base Layer**: C100 (Standard ANSI character set)
- **Emoji Layers**: C101+ (256-character emoji map)
- **Extended Layers**: C101-C899 (multi-layer character collections)
- **Retro Layers**: C64 and Acorn Teletext characters
- **References**: C-layer numbering system (C100-C899)

**Emoji Guidelines**:
- Use `:emoji:` format for consistency
- Reference C-layer positions when needed
- Example: `:rocket:` (C245) for launch-related content
- Example: `:computer:` (C187) for technical documentation

**Special Character Usage**:
- Use Teletext references for block characters: `[C256]`
- Use C64 references for retro characters: `{C64:C65}`
- Use Acorn references: `{ACN:C42}`
- Use ANSI fallbacks when special chars not available

### Headers

Use ATX-style headers with consistent spacing:

```markdown
# Header 1

## Header 2

### Header 3

#### Header 4

##### Header 5

###### Header 6
```

**Best Practices:**
- Always include a space after `#`
- Use consistent header hierarchy
- Don't skip header levels

### Paragraphs

```markdown
This is a paragraph. It should be separated from other paragraphs by a blank line.

This is another paragraph. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
```

**Best Practices:**
- Separate paragraphs with blank lines
- Wrap lines at 80-100 characters for readability
- Avoid trailing whitespace

### Emphasis

```markdown
*Italic* or _Italic_
**Bold** or __Bold__
***Bold Italic*** or ___Bold Italic___
```

**Best Practices:**
- Use `*` for single words/phrases
- Use `_` for longer emphasis
- Be consistent within a document

### Lists

#### Unordered Lists

```markdown
- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3
```

**Best Practices:**
- Use `-` for unordered lists
- Indent nested items with 2 spaces
- Keep list items short and parallel

#### Ordered Lists

```markdown
1. First item
2. Second item
3. Third item
```

**Best Practices:**
- Use `1.` for all items (markdown will auto-number)
- Maintain consistent indentation

### Links

```markdown
[Link text](https://example.com)
[Link with title](https://example.com "Title")
<https://example.com> (auto-linked)
```

**Best Practices:**
- Use descriptive link text
- Avoid "click here" or "read more"
- Use reference-style links for long URLs

### Images

```markdown
![Alt text](/path/to/img.jpg)
![Alt text](/path/to/img.jpg "Title")
```

**Best Practices:**
- Always include alt text
- Keep images in an `images` directory
- Use relative paths

## 2. Code Formatting

### Inline Code

```markdown
Use `code` for inline code references.
```

**Best Practices:**
- Use for commands, variables, file names
- Don't overuse for regular text

### Code Blocks

#### Fenced Code Blocks (Preferred)

````markdown
```rust
fn main() {
    println!("Hello, world!");
}
```
````

**Best Practices:**
- Always specify language for syntax highlighting
- Keep code concise and relevant
- Include necessary context

#### Indented Code Blocks

```markdown
    // Only use when fenced blocks aren't available
    function example() {
        return true;
    }
```

**Best Practices:**
- Prefer fenced code blocks
- Indent with 4 spaces

## 3. Advanced Formatting

### Tables

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Row 1    | Data     | Data     |
| Row 2    | Data     | Data     |
```

**Best Practices:**
- Include header row
- Align columns for readability
- Use for data, not layout

### Blockquotes

```markdown
> This is a blockquote.
> It can span multiple lines.
>
> > Nested blockquotes are possible.
```

**Best Practices:**
- Use for notes, warnings, or citations
- Keep concise
- Don't overuse

### Horizontal Rules

```markdown
---

***

___
```

**Best Practices:**
- Use `---` for consistency
- Separate major sections
- Don't overuse

## 4. GFM-Specific Features

### Task Lists

```markdown
- [x] Completed task
- [ ] Incomplete task
- [ ] Another task
```

**Best Practices:**
- Use for tracking progress
- Keep tasks actionable

### Strikethrough

```markdown
~~strikethrough~~
```

**Best Practices:**
- Use for deprecated features
- Indicate removed content

### Tables with Alignment

```markdown
| Left | Center | Right |
|:-----|:------:|------:|
| Data | Data  | Data  |
```

**Best Practices:**
- Use alignment sparingly
- Keep tables simple

## 5. uCode1-Specific Conventions

### Document Structure

```markdown
# Document Title

## Overview

Brief introduction

## Section 1

Content...

## Section 2

Content...

## See Also

- [Related Document](link)
- [Another Resource](link)

---

© 2024 uCode1 Team
```

### Front Matter

For documents that need metadata:

```markdown
---
title: Document Title
author: uCode1 Team
date: 2024-01-15
category: Documentation
---

# Document Title

Content...
```

### Code Documentation

```markdown
## Function: `do_something()`

**Description**: Does something important

**Parameters**:
- `param1` (Type): Description
- `param2` (Type): Description

**Returns**: Return type and description

**Example**:
```rust
let result = do_something(param1, param2);
```
```

## 6. Best Practices

### General

1. **Consistency**: Be consistent within a document
2. **Readability**: Prioritize human readability
3. **Conciseness**: Be brief but complete
4. **Organization**: Use logical structure

### File Organization

1. **Naming**: Use `KEBAB-CASE.md` for files
2. **Directories**: Group related documents
3. **Index**: Include `README.md` in directories

### Content

1. **Audience**: Write for the intended reader
2. **Purpose**: State the document's goal early
3. **Examples**: Include practical examples
4. **References**: Link to related documents

### Maintenance

1. **Review**: Regularly update documentation
2. **Deprecation**: Mark outdated content
3. **Versioning**: Track document versions

## 7. Tools

### Recommended Editors

- **VS Code** with Markdown extensions
- **Typora** for live preview
- **Obsidian** for knowledge base

### Validation

- **markdownlint**: Lint markdown files
- **Prettier**: Format consistently
- **GFM Validator**: Validate syntax

### Conversion

- **Pandoc**: Convert between formats
- **mdbook**: Create documentation books

## 8. Examples

### Good Example

```markdown
# Vault Schema Management

## Overview

This document explains how uCode1 manages database schemas for the vault system.

## Schema Types

### uCode Schemas

- **Purpose**: Track uCode1 component versions
- **Format**: JSON with version and components
- **Example**:

```json
{
  "version": "1.0.1",
  "components": ["vault-bridge", "ok-agent"]
}
```

### Vault Schemas

- **Purpose**: Track SQLite database structure
- **Format**: SQL DDL statements
- **Example**:

```sql
CREATE TABLE space (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);
```

## Best Practices

1. Use semantic versioning
2. Include release dates
3. Document breaking changes

## See Also

- [Command Reference](../CLI_COMMANDS.md)
- [Architecture Overview](../ARCHITECTURE.md)

---

© 2024 uCode1 Team
```

### Bad Example

```markdown
# vault schemas

this document is about schemas.

## stuff

some text here
more text
no structure

## random

unorganized content
no examples
```

## 9. Character Mapping System

### uCode1 Character Reference Guide

**Base Character Sets**:
- **Default Layer**: C100 (Standard ANSI character set)
- **Emoji Layers**: C101-C356 (256-character emoji map)
- **Teletext Blocks**: C400-C499
- **C64 Characters**: C500-C599
- **Acorn Characters**: C600-C699
- **Extended Layers**: C101-C899 (multi-layer collections)

**Emoji Reference System**:
- Use `:emoji:` notation for standard emoji
- Map to C-layer positions: `:rocket:` = C245
- Reference format: `:emoji:` (CXXX)

**Special Character Examples**:

| Character Type | Format | Example | Reference |
|---------------|--------|---------|-----------|
| Standard Emoji | `:emoji:` | `:rocket:` | C245 |
| Teletext Block | `[CXXX]` | `[C256]` | C256 |
| C64 Character | `{C64:CXX}` | `{C64:C65}` | C565 |
| Acorn Character | `{ACN:CXX}` | `{ACN:C42}` | C642 |

**Character Usage Guidelines**:

1. **Documentation**: Use emoji sparingly for emphasis
2. **Technical Docs**: Prefer ANSI/ASCII for compatibility
3. **UI Elements**: Use Teletext blocks for borders/layouts
4. **Retro Mode**: Use C64/Acorn chars for authentic feel
5. **Fallbacks**: Always provide ANSI alternatives

### Character Map Reference

**Common uCode1 Emoji Mappings**:
- `:rocket:` - Launch/startup (C245)
- `:computer:` - Technical/computing (C187)
- `:book:` - Documentation/learning (C123)
- `:lock:` - Security/privacy (C312)
- `:gear:` - Settings/configuration (C287)
- `:warning:` - Alerts/warnings (C345)
- `:check:` - Success/completion (C211)
- `:x:` - Errors/failure (C212)

**Teletext Block Characters**:
- `[C256]` - Solid block
- `[C257]` - Horizontal line
- `[C258]` | Vertical line
- `[C259]` - Corner piece
- `[C260]` - T-junction

### C-Layer Position Reference

```
C100:          Default Layer (ANSI base)
C101-C356:     Emoji Layers (256 characters)
C400-C499:     Teletext Block Characters
C500-C599:     C64 Character Set
C600-C699:     Acorn Teletext Set  
C700-C799:     Reserved for future expansion
C800-C899:     Custom/user-defined layers
```

**Key Features**:
- **Base Layer**: C100 provides ANSI compatibility
- **Multi-Layer Collections**: Character sets can span multiple C-layers
- **Max Layer**: C899 for maximum flexibility
- **Default Layer**: C100 ensures backward compatibility

## 10. References

- [GitHub Flavored Markdown Spec](https://github.github.com/gfm/)
- [Common Markdown Style Guide](https://gist.github.com/rxaviers/7360908)
- [Markdown Guide](https://www.markdownguide.org/)
- [Unicode Emoji Reference](https://unicode.org/emoji/)
- [Teletext Character Set](https://teletext.mb21.co.uk/)
- [C64 Character Set](https://www.c64-wiki.com/wiki/Character_set)

---

© 2024 uCode1 Team. All rights reserved.
