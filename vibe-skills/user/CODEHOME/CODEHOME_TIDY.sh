#!/bin/bash
# CODEHOME TIDY - Organize codehome content preserving structure
# Preserves subfolder structure, handles batch operations

# Configuration
TARGET_FOLDER="${1:-}"
TIDY_DIR="$TARGET_FOLDER/tidy"

# Validate arguments
if [[ -z "$TARGET_FOLDER" ]]; then
  echo "❌ Error: Target folder is required."
  echo "Usage: CODEHOME_TIDY.sh <target-folder>"
  exit 1
fi

SOURCE_PATH="$HOME/Code/$TARGET_FOLDER"

# Check source exists
if [[ ! -d "$SOURCE_PATH" ]]; then
  echo "❌ Error: Target folder '$TARGET_FOLDER' does not exist in ~/Code/"
  exit 1
fi

# Create tidy directory
mkdir -p "$TIDY_DIR"

echo "🧹 CODEHOME TIDY - Organizing $TARGET_FOLDER with structure preservation"
echo "========================================================================="

# Index and process files with duplicate detection
TEMP_INDEX="$(mktemp)"
trap "rm -f $TEMP_INDEX" EXIT

# Process files preserving structure
find "$SOURCE_PATH" -type f | while read -r file; do
  # Get relative path from source
  rel_path="${file#$SOURCE_PATH/}"
  
  # Create corresponding directory structure in tidy
  dest_dir="$TIDY_DIR/$(dirname "$rel_path")"
  mkdir -p "$dest_dir"
  
  # Check for duplicates (same filename in same relative path)
  filename="$(basename "$file")"
  path_key="$(dirname "$rel_path")/$filename"
  
  if grep -q "^$path_key$" "$TEMP_INDEX"; then
    echo "⚠️  Duplicate detected: $rel_path (skipping)"
    continue
  fi
  
  # Add to index
  echo "$path_key" >> "$TEMP_INDEX"
  
  # Copy to tidy directory (preserving structure)
  cp "$file" "$dest_dir/$filename"
  echo "✅ Copied: $rel_path → tidy/$rel_path"
done

echo ""
echo "🎉 CODEHOME TIDY complete!"
echo "   Target: $TARGET_FOLDER/"
echo "   Output: $TARGET_FOLDER/tidy/"
echo "   Structure: Preserved with duplicate detection"
echo "   Ready for CODEHOME CLEAN"
