#!/bin/bash
# CONDENSE - Content Quality Filtering and Consolidation
# Filters out brief documents (<25 lines or <100 words) and consolidates into condensed/ subfolder

# Configuration
SOURCE_DIR="${1:-}"
MIN_LINES="${2:-25}"  # Minimum lines to keep (default 25)
MIN_WORDS="${3:-100}"  # Minimum words to keep (default 100)

# Validate arguments
if [[ -z "$SOURCE_DIR" ]]; then
  echo "❌ Error: Source directory is required."
  echo "Usage: CONDENSE_filtered.sh <source-dir> [min-lines] [min-words]"
  exit 1
fi

SOURCE_PATH="$HOME/Code/$SOURCE_DIR"
OUTPUT_PATH="$SOURCE_PATH/condensed"

# Check source exists
if [[ ! -d "$SOURCE_PATH" ]]; then
  echo "❌ Error: Source directory '$SOURCE_DIR' does not exist in ~/Code/"
  exit 1
fi

# Create condensed subfolder within the processed folder
mkdir -p "$OUTPUT_PATH"

# Statistics
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT
STATS_FILE="$TEMP_DIR/stats.txt"
echo "0 0 0 0" > "$STATS_FILE"  # TOTAL KEPT FILTERED DUPLICATES

echo "🔍 CONDENSE - Content Quality Filtering"
echo "======================================"
echo "📁 Source: $SOURCE_DIR/"
echo "📁 Output: $SOURCE_DIR/condensed/"
echo "📊 Min lines: $MIN_LINES | Min words: $MIN_WORDS"
echo "======================================"

# Function to check if file has meaningful content
is_contentful() {
  local file="$1"
  
  # Check line count
  local lines=$(wc -l < "$file" | tr -d ' ')
  if [[ $lines -lt $MIN_LINES ]]; then
    return 1  # Not contentful
  fi
  
  # Check word count
  local words=$(wc -w < "$file" | tr -d ' ')
  if [[ $words -lt $MIN_WORDS ]]; then
    return 1  # Not contentful
  fi
  
  # Check for meaningful content (not just headers, lists, etc.)
  local content=$(cat "$file" | grep -vE '^#|^\[|^\*|^\-|^\||^\+|^=|^\_{3,}')
  if [[ -z "$content" ]]; then
    return 1  # No real content
  fi
  
  return 0  # Contentful
}

# Get total files
TOTAL_FILES=$(find "$SOURCE_PATH" -name "*.md" -type f | wc -l)
echo "📊 Processing $TOTAL_FILES files..."

# Process files
find "$SOURCE_PATH" -name "*.md" -type f | while read -r file; do
  filename=$(basename "$file")
  
  # Read current stats
  TOTAL=$(cat "$STATS_FILE" | cut -d' ' -f1)
  KEPT=$(cat "$STATS_FILE" | cut -d' ' -f2)
  FILTERED=$(cat "$STATS_FILE" | cut -d' ' -f3)
  DUPLICATES=$(cat "$STATS_FILE" | cut -d' ' -f4)
  
  # Check if contentful
  if ! is_contentful "$file"; then
    echo "🗑️  Filtered (brief/empty): $filename"
    FILTERED=$((FILTERED + 1))
    echo "$TOTAL $KEPT $FILTERED $DUPLICATES" > "$STATS_FILE"
    continue
  fi
  
  dest="$OUTPUT_PATH/$filename"
  
  # Check if file exists
  if [[ -f "$dest" ]]; then
    # Compare content
    if cmp -s "$file" "$dest"; then
      echo "⚠️  Duplicate skipped: $filename"
      DUPLICATES=$((DUPLICATES + 1))
    else
      # Different content - create versioned copy
      base="${filename%.md}"
      ext="md"
      counter=2
      while [[ -f "$OUTPUT_PATH/${base}-v$counter.$ext" ]]; do
        counter=$((counter + 1))
      done
      version_name="${base}-v$counter.$ext"
      cp "$file" "$OUTPUT_PATH/$version_name"
      echo "🔄 Versioned: $filename → $version_name"
    fi
  else
    # First copy
    cp "$file" "$dest"
    KEPT=$((KEPT + 1))
    echo "✅ Kept: $filename"
  fi
  
  # Update stats
  echo "$TOTAL $KEPT $FILTERED $DUPLICATES" > "$STATS_FILE"
done

# Read final stats
TOTAL=$(cat "$STATS_FILE" | cut -d' ' -f1)
KEPT=$(cat "$STATS_FILE" | cut -d' ' -f2)
FILTERED=$(cat "$STATS_FILE" | cut -d' ' -f3)
DUPLICATES=$(cat "$STATS_FILE" | cut -d' ' -f4)

echo ""
echo "🎉 Quality filtering complete!"
echo "======================================="
echo "📊 Statistics:"
echo "   Total files processed: $TOTAL_FILES"
echo "   Contentful files kept: $KEPT"
echo "   Brief/empty files filtered: $FILTERED"
echo "   Duplicates skipped: $DUPLICATES"
if [[ $TOTAL_FILES -gt 0 ]]; then
  FILTER_PERCENT=$(((FILTERED * 100) / TOTAL_FILES))
  echo "   Filtered: $FILTER_PERCENT%"
else
  echo "   Filtered: 0%"
fi
echo ""
echo "📁 Results:"
echo "   Source: $SOURCE_DIR/"
echo "   Output: $SOURCE_DIR/condensed/"
echo ""
echo "💡 Strategy: Content quality filtering + consolidation"
echo "   - Filtered brief documents (<$MIN_LINES lines, <$MIN_WORDS words)"
echo "   - Removed empty/non-contentful files"
echo "   - Deduplicated exact copies"
echo "   - Versioned different content"
echo "   - Preserved all meaningful content"
