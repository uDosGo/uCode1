# uSystem Documentation in Vault

## Important Notice

**These documents are automatically generated from usystem.db and synced ONE-WAY to your Vault.**

### What This Means:

1. **Read-Only Reference**: These documents are for your reference only
2. **No Reverse Sync**: Modifying these documents will NOT update usystem.db
3. **Regeneration**: Documents can be regenerated at any time from usystem.db
4. **Source of Truth**: The usystem.db database is the authoritative source

## Documentation Sync Process

### How Documents Are Created:

```
usystem.db → uCode1 Vault Sync → Your Vault Documents
                    (one-way)
```

### When Documents Are Updated:

1. **Initial Setup**: When you first initialize uCode1
2. **Version Updates**: When uCode1 is updated to new versions
3. **Manual Sync**: When you run `ucode1 vault sync-docs`

### For Developers:

If you need to modify system documentation:

1. Update the source in `usystem_schema.sql` or Rust code
2. Rebuild uCode1: `cargo build --release`
3. Regenerate documents: `./scripts/generate_docs.sh`
4. Sync to vault: `ucode1 vault sync-docs`

## Document Types in Vault

### 1. Command Reference

Automatically generated from registered commands in usystem.db:
- Command names and descriptions
- Usage examples
- Available options

### 2. Schema Documentation

Versioned schemas for uCode1 components:
- uCode core schemas
- Vault database schemas
- Module schemas

### 3. System Documentation

Reference documentation for:
- Permission matrix
- Role definitions
- System variables

## Working with Vault Documents

### Best Practices:

1. **Don't Modify**: Treat as read-only reference
2. **Create New**: Add your own documents for custom workflows
3. **Version Control**: Use Git to track your custom documents
4. **Backup**: Regularly backup your Vault directory

### Recommended Workflow:

```bash
# 1. Review system documentation
ucode1 docs

# 2. Create your own documentation in Vault
ucode1 note create "My Workflow" "# My Custom Process..."

# 3. Organize with folders/tags
ucode1 note create "Project/Setup" "# Project setup steps..."

# 4. Backup your customizations
git add ~/Code/Vault
```

## Indexing Vault Documents

### Important Note:

**Vault documents are NOT automatically indexed.** This is by design to:

1. **Maintain Control**: You decide what gets indexed
2. **Avoid Clutter**: Only important documents in search
3. **Performance**: Faster searches with curated index

### How to Index Documents:

```bash
# Index a specific document
ucode1 vault index-doc "Document Name"

# Index all documents in a category
ucode1 vault index-category "Getting Started"

# View indexed documents
ucode1 vault list-indexed
```

### Indexing Best Practices:

1. **Curate Carefully**: Only index documents you frequently search
2. **Use Categories**: Group related documents
3. **Review Regularly**: Clean up unused indexed documents
4. **Performance**: Too many indexed docs slow down search

## Roadmap for Documentation Features

### uCode1.1+ Development Plan:

1. **Health Commands** (Priority)
   - `ucode1 vault health-check`
   - `ucode1 vault optimize`
   - `ucode1 vault repair`

2. **Maintenance Commands`
   - `ucode1 vault cleanup`
   - `ucode1 vault defrag`
   - `ucode1 vault backup`

3. **Advanced Indexing`
   - Automatic indexing suggestions
   - Index usage analytics
   - Smart indexing recommendations

4. **Documentation Management`
   - Versioned document history
   - Document change tracking
   - Collaboration features

## Getting Help

### System Documentation:
```bash
# View all commands
ucode1 docs

# Get markdown reference
ucode1 docs --format markdown

# View specific help
ucode1 note --help
```

### Community Resources:
- GitHub Issues: https://github.com/your-repo/uCode1/issues
- Documentation: https://docs.ucode1.example.com
- Community Forum: https://community.ucode1.example.com

## License

This documentation template is part of uCode1 and is released under the MIT License.

---

© 2024 uCode1 Team. All rights reserved.
