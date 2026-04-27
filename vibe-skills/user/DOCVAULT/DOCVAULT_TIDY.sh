#!/bin/bash
# DOCVAULT TIDY - Organize docvault content into flat tidy subfolder
# Preserves only .md files, collapses subfolder structure

# Configuration
TARGET_FOLDER="${1:-}"
TIDY_DIR="$TARGET_FOLDER/tidy"

# Validate arguments
if [[ -z "$TARGET_FOLDER" ]]; then
  echo "❌ Error: Target folder is required."
  echo "Usage: DOCVAULT_TIDY.sh <target-folder>"
  exit 1
fi

SOURCE_PATH="$HOME/Vault/$TARGET_FOLDER"

# Check source exists
if [[ ! -d "$SOURCE_PATH" ]]; then
  echo "❌ Error: DocVault directory '$SOURCE_DIR' does not exist in ~/Vault/"
  exit 1
fi

# Create tidy directory
mkdir -p "$TIDY_DIR"

echo "🧹 DOCVAULT TIDY - Organizing $SOURCE_DIR into flat structure"
echo "============================================================"

# Index and process files
TEMP_INDEX="$(mktemp)"
trap "rm -f $TEMP_INDEX" EXIT

# Find all .md files and create index
find "$SOURCE_PATH" -name "*.md" -type f | while read -r file; do
  # Get relative path from source
  rel_path="${file#$SOURCE_PATH/}"
  filename="$(basename "$file")"
  
  # Check for duplicates (same filename)
  if grep -q "^$filename$" "$TEMP_INDEX"; then
    echo "⚠️  Duplicate detected: $rel_path (skipping)"
    continue
  fi
  
  # Add to index
  echo "$filename" >> "$TEMP_INDEX"
  
  # Copy to tidy directory (flat structure)
  cp "$file" "$TIDY_DIR/$filename"
  echo "✅ Copied: $rel_path → tidy/$filename"
done

echo ""
echo "🎉 DOCVAULT TIDY complete!"
echo "   Target: $TARGET_FOLDER/"
echo "   Output: $TARGET_FOLDER/tidy/"
echo "   Ready for DOCVAULT CLEAN"
