#!/bin/bash

# Sync uSystem documentation to Vault
# This script generates documentation from usystem.db and creates notes in the vault
# Handles uCode1 character sets including emoji, Teletext blocks, and retro characters

set -e

echo "=== uSystem Vault Documentation Sync ==="
echo "Character System: ANSI + Emoji (:emoji:) + Teletext ([#XXX]) + C64 ({C64:XX}) + Acorn ({ACN:XX})"
echo ""

# Set locale to support UTF-8 characters
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

# Build the project
cd "$(dirname "$0")/.."
echo "Building uCode1..."
cargo build --release 2>&1 | tail -5

echo ""
echo "Generating vault documentation..."

# Create a temporary directory for the docs
TEMP_DIR=$(mktemp -d)
echo "Using temp directory: $TEMP_DIR"

# Generate each document type
./target/release/uCode1 docs --format markdown > "$TEMP_DIR/USYSTEM_COMMANDS.md"
echo "✓ Generated command reference"

# Check if vault path exists, create if not
VAULT_PATH="$HOME/Code/Vault"
if [ ! -d "$VAULT_PATH" ]; then
    echo "Creating vault directory: $VAULT_PATH"
    mkdir -p "$VAULT_PATH"
fi

# Copy documents to vault
echo ""
echo "Syncing documents to vault..."

# Document 1: Vault Docs Template
cat > "$TEMP_DIR/USYSTEM_VAULT_DOCS.md" << 'EOF'
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
EOF

echo "✓ Generated vault docs template"

# Document 2: Permission Matrix
cat > "$TEMP_DIR/USYSTEM_PERMISSIONS.md" << 'EOF'
# Permission Matrix

Role-based access control for uCode1 resources

## admin

| Resource Type | Read | Write | Delete | Execute | Admin |
|---------------|------|-------|--------|---------|-------|
| vault | ✓ | ✓ | ✓ | ✓ | ✓ |
| commands | ✓ | ✓ | ✓ | ✓ | ✓ |
| system | ✓ | ✓ | ✓ | ✓ | ✓ |

## user

| Resource Type | Read | Write | Delete | Execute | Admin |
|---------------|------|-------|--------|---------|-------|
| vault | ✓ | ✓ | ✗ | ✓ | ✗ |
| commands | ✓ | ✗ | ✗ | ✓ | ✗ |
| system | ✓ | ✗ | ✗ | ✗ | ✗ |

## guest

| Resource Type | Read | Write | Delete | Execute | Admin |
|---------------|------|-------|--------|---------|-------|
| vault | ✓ | ✗ | ✗ | ✗ | ✗ |
| commands | ✓ | ✗ | ✗ | ✓ | ✗ |
| system | ✗ | ✗ | ✗ | ✗ | ✗ |

## developer

| Resource Type | Read | Write | Delete | Execute | Admin |
|---------------|------|-------|--------|---------|-------|
| vault | ✓ | ✓ | ✓ | ✓ | ✗ |
| commands | ✓ | ✓ | ✗ | ✓ | ✗ |
| system | ✓ | ✓ | ✗ | ✓ | ✗ |
EOF

echo "✓ Generated permission matrix"

# Document 3: Schemas
cat > "$TEMP_DIR/USYSTEM_SCHEMAS.md" << 'EOF'
# uCode Schema Versions

Version history of uCode1 components

## Version 1.0.1

Initial uCode1 schema with vault integration

**Type:** core

**Released:** 2024-01-15
EOF

echo "✓ Generated schemas documentation"

# Character system validation (C-layer format: CXXX#YYY)
validate_characters() {
    local file="$1"
    echo "Validating C-layer character set in $file..."
    
    # Check for proper emoji format
    if grep -q ":[a-z_][a-z_]*:" "$file"; then
        echo "  ✓ Emoji format detected (:emoji:)"
    fi
    
    # Check for C-layer Teletext block format [CXXX#YYY]
    if grep -q "\[C[0-9][0-9][0-9]#[0-9][0-9][0-9]\]" "$file"; then
        echo "  ✓ C-layer Teletext blocks detected ([CXXX#YYY])"
    fi
    
    # Check for C-layer C64 character format {C64:CXXX#YYY}
    if grep -q "{C64:C[0-9][0-9][0-9]#[0-9][0-9][0-9]}" "$file"; then
        echo "  ✓ C-layer C64 characters detected ({C64:CXXX#YYY})"
    fi
    
    # Check for C-layer Acorn character format {ACN:CXXX#YYY}
    if grep -q "{ACN:C[0-9][0-9][0-9]#[0-9][0-9][0-9]}" "$file"; then
        echo "  ✓ C-layer Acorn characters detected ({ACN:CXXX#YYY})"
    fi
    
    # Validate UTF-8 encoding
    if file -i "$file" | grep -q "utf-8"; then
        echo "  ✓ UTF-8 encoding confirmed"
    else
        echo "  ⚠️  Character encoding: $(file -i "$file" | cut -d' ' -f2)"
    fi
    
    # Check for C-layer references in comments
    if grep -q "(C[0-9][0-9][0-9]#[0-9][0-9][0-9])" "$file"; then
        echo "  ✓ C-layer references detected (CXXX#YYY)"
    fi
}

# Copy all documents to vault
cp "$TEMP_DIR"/*.md "$VAULT_PATH"/

echo ""
echo "✓ Synced $(ls "$TEMP_DIR"/*.md | wc -l) documents to vault"

# Validate character systems in generated documents
echo ""
echo "=== Character System Validation ==="
for doc in "$VAULT_PATH"/USYSTEM_*.md; do
    if [ -f "$doc" ]; then
        validate_characters "$doc"
    fi
done

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "=== Documentation Sync Complete ==="
echo ""
echo "Documents available in your vault:"
ls -1 "$VAULT_PATH"/USYSTEM_*.md 2>/dev/null || echo "No USYSTEM documents found"
echo ""
echo "To view a document:"
echo "  ucode1 note show "USYSTEM_VAULT_DOCS""
echo ""
echo "To index a document for search:"
echo "  ucode1 vault index-doc "USYSTEM_VAULT_DOCS""
