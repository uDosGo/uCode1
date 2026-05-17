#!/bin/bash
# Script to update the seed vault structure

# Define the seed vault directory
SEED_VAULT_DIR="/Users/fredbook/uDosGo/SeedVault"

# Create the seed vault directory
mkdir -p "$SEED_VAULT_DIR"

# Create the directory structure
mkdir -p "$SEED_VAULT_DIR/{system}/{config}" "$SEED_VAULT_DIR/{system}/{state}" "$SEED_VAULT_DIR/{system}/{cache}" "$SEED_VAULT_DIR/{system}/{user}"
mkdir -p "$SEED_VAULT_DIR/@workspace/active" "$SEED_VAULT_DIR/@workspace/archived" "$SEED_VAULT_DIR/@workspace/shared"
mkdir -p "$SEED_VAULT_DIR/-inbox/incoming" "$SEED_VAULT_DIR/-inbox/processing" "$SEED_VAULT_DIR/-inbox/completed" "$SEED_VAULT_DIR/-inbox/failed"
mkdir -p "$SEED_VAULT_DIR/-outbox/pending" "$SEED_VAULT_DIR/-outbox/sending" "$SEED_VAULT_DIR/-outbox/sent" "$SEED_VAULT_DIR/-outbox/failed"
mkdir -p "$SEED_VAULT_DIR/--dev/experiments" "$SEED_VAULT_DIR/--dev/scratch" "$SEED_VAULT_DIR/--dev/builds" "$SEED_VAULT_DIR/--dev/temp"
mkdir -p "$SEED_VAULT_DIR/.compost/heap" "$SEED_VAULT_DIR/.compost/archive" "$SEED_VAULT_DIR/.compost/vector"
mkdir -p "$SEED_VAULT_DIR/.config/git" "$SEED_VAULT_DIR/.config/ssh" "$SEED_VAULT_DIR/.config/secrets"
mkdir -p "$SEED_VAULT_DIR/docs" "$SEED_VAULT_DIR/notes" "$SEED_VAULT_DIR/learning" "$SEED_VAULT_DIR/templates"

# Create example files
cat > "$SEED_VAULT_DIR/{system}/{config}/README.md" << 'EOF'
# System Configuration
This directory contains system-wide configuration files.
EOF

cat > "$SEED_VAULT_DIR/@workspace/active/README.md" << 'EOF'
# Active Workspaces
This directory contains active workspaces.
EOF

cat > "$SEED_VAULT_DIR/-inbox/README.md" << 'EOF'
# Inbox
This directory contains incoming data to be processed.
EOF

cat > "$SEED_VAULT_DIR/-outbox/README.md" << 'EOF'
# Outbox
This directory contains outgoing data to be sent.
EOF

cat > "$SEED_VAULT_DIR/--dev/README.md" << 'EOF'
# Dev Scratch Space
This directory is for temporary development files.
EOF

cat > "$SEED_VAULT_DIR/.compost/README.md" << 'EOF'
# Compost
This directory contains soft-deleted files.
EOF

cat > "$SEED_VAULT_DIR/.config/README.md" << 'EOF'
# Config
This directory contains user-specific configuration files.
EOF

cat > "$SEED_VAULT_DIR/docs/README.md" << 'EOF'
# Docs
This directory contains documentation.
EOF

cat > "$SEED_VAULT_DIR/notes/README.md" << 'EOF'
# Notes
This directory contains notes.
EOF

cat > "$SEED_VAULT_DIR/learning/README.md" << 'EOF'
# Learning
This directory contains learning materials.
EOF

cat > "$SEED_VAULT_DIR/templates/README.md" << 'EOF'
# Templates
This directory contains templates.
EOF

# Create a manifest file
echo "# Seed Vault Manifest" > "$SEED_VAULT_DIR/MANIFEST.md"
echo "" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "## Directory Structure" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "- **{system}**: System configuration and state" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - {config}: System configuration files" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - {state}: System state files" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - {cache}: System cache files" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - {user}: User-specific system config" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "- **@workspace**: User workspaces" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - active: Active workspaces" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - archived: Archived workspaces" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - shared: Shared workspaces" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "- **-inbox**: Incoming data flow" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - incoming: Raw incoming data" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - processing: Data being processed" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - completed: Processed data" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - failed: Failed processing" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "- **-outbox**: Outgoing data flow" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - pending: Data waiting to be sent" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - sending: Data in transit" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - sent: Sent data" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - failed: Failed sending" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "- **--dev**: Development scratch space" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - experiments: Quick tests" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - scratch: Temporary files" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - builds: Build artifacts" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - temp: Session temporary files" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "- **.compost**: Soft delete" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - heap: Active compost" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - archive: Compressed compost" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - vector: Searchable compost" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "- **.config**: User configuration" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - git: Git configuration" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - ssh: SSH configuration" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "  - secrets: Encrypted secrets" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "- **docs**: Documentation" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "- **notes**: Notes" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "- **learning**: Learning materials" >> "$SEED_VAULT_DIR/MANIFEST.md"
echo "- **templates**: Templates" >> "$SEED_VAULT_DIR/MANIFEST.md"

echo "Seed vault structure updated successfully."