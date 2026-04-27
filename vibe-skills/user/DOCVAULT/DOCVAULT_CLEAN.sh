#!/bin/bash
# DOCVAULT CLEAN - Non-destructive cleanup after DOCVAULT TIDY
# Moves old content to .compost, promotes tidy content to root

# Configuration
TARGET_FOLDER="${1:-}"
TIDY_DIR="$TARGET_FOLDER/tidy"
COMPOST_DIR="$TARGET_FOLDER/.compost"

# Validate arguments
if [[ -z "$TARGET_FOLDER" ]]; then
  echo "❌ Error: Target folder is required."
  echo "Usage: DOCVAULT_CLEAN.sh <target-folder>"
  exit 1
fi

SOURCE_PATH="$HOME/Vault/$TARGET_FOLDER"

# Check source exists
if [[ ! -d "$SOURCE_PATH" ]]; then
  echo "❌ Error: Target folder '$TARGET_FOLDER' does not exist in ~/Vault/"
  exit 1
fi

# Check tidy directory exists
if [[ ! -d "$TIDY_DIR" ]]; then
  echo "❌ Error: Tidy directory not found. Run DOCVAULT TIDY first."
  exit 1
fi

# Create compost directory
mkdir -p "$COMPOST_DIR"

echo "🧹 DOCVAULT CLEAN - Non-destructive cleanup"
echo "============================================"
echo "📁 Processing: $TARGET_FOLDER/"

# Step 1: Move old root content to compost
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OLD_BACKUP="$COMPOST_DIR/old-root-$TIMESTAMP"

# Move all .md files from root to compost
find "$SOURCE_PATH" -maxdepth 1 -name "*.md" -type f -exec mv {} "$OLD_BACKUP/" \;

# Move all subdirectories to compost
find "$SOURCE_PATH" -mindepth 1 -maxdepth 1 -type d ! -name "tidy" ! -name ".compost" -exec mv {} "$COMPOST_DIR/" \;

echo "✅ Old content moved to: $TARGET_FOLDER/.compost/"

# Step 2: Promote tidy content to root
mv "$TIDY_DIR"/* "$SOURCE_PATH/"
rmdir "$TIDY_DIR"

echo "✅ Tidy content promoted to root"
echo "✅ Tidy directory removed"

echo ""
echo "🎉 DOCVAULT CLEAN complete!"
echo "   Target: $TARGET_FOLDER/"
echo "   Old content: .compost/old-root-$TIMESTAMP/"
echo "   Structure: Flat .md files in root"
