#!/bin/bash
# BACKUP DRYRUN
# Creates a backup with dry-run report and confirmation

# Defaults
SOURCE="${1:-}"
BACKUP_DIR="$HOME/Code/.compost/backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Validate arguments
if [[ -z "$SOURCE" ]]; then
  echo "❌ Error: Source directory is required."
  echo "Usage: backup-dryrun.sh <source-directory>"
  exit 1
fi

# Check source exists
SOURCE_PATH="$HOME/Code/$SOURCE"
if [[ ! -d "$SOURCE_PATH" ]]; then
  echo "❌ Error: Source directory '$SOURCE' does not exist in ~/Code/"
  exit 1
fi

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate dry-run report
BACKUP_NAME="${SOURCE}-backup-${TIMESTAMP}"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

echo "🔍  Backup Dry-Run Report"
echo "========================"
echo ""
echo "Source: $SOURCE_PATH"
echo "Backup: $BACKUP_PATH.tar.gz"
echo "Timestamp: $(date +"%Y-%m-%d %H:%M:%S")"
echo ""

# Analyze source
echo "📊 Source Analysis:"
echo "- File count: $(find "$SOURCE_PATH" -type f 2>/dev/null | wc -l)"
echo "- Directory count: $(find "$SOURCE_PATH" -type d 2>/dev/null | wc -l)"
echo "- Total size: $(du -sh "$SOURCE_PATH" 2>/dev/null | cut -f1)"
echo ""

# Show sample files
echo "📁 Sample files (first 10):"
find "$SOURCE_PATH" -type f 2>/dev/null | head -10 | sed "s|$HOME/Code/||"
echo ""

# Confirmation
read -p "🔄 Proceed with backup? (y/N): " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "❌ Backup cancelled by user."
  exit 0
fi

# Create backup
echo "🛡️  Creating backup: $BACKUP_NAME.tar.gz"

if command -v tar >/dev/null 2>&1; then
  tar -czf "$BACKUP_PATH.tar.gz" -C "$HOME/Code" "$SOURCE"
  echo "✅ Backup created: $BACKUP_PATH.tar.gz"
else
  cp -r "$SOURCE_PATH" "$BACKUP_PATH"
  echo "✅ Backup created: $BACKUP_PATH/"
fi

# Create manifest
MANIFEST="$BACKUP_DIR/BACKUP_MANIFEST.md"
{
  echo "# 🛡️  Backup Manifest"
  echo ""
  echo "## Backup Information"
  echo "- **Created**: $(date +"%Y-%m-%d %H:%M:%S")"
  echo "- **Source**: $SOURCE/"
  echo "- **Backup**: $BACKUP_NAME.tar.gz"
  echo "- **Location**: $BACKUP_DIR/"
  echo ""
  echo "## Contents"
  echo "- File count: $(find "$SOURCE_PATH" -type f 2>/dev/null | wc -l)"
  echo "- Directory count: $(find "$SOURCE_PATH" -type d 2>/dev/null | wc -l)"
  echo "- Total size: $(du -sh "$SOURCE_PATH" 2>/dev/null | cut -f1)"
  echo ""
  echo "## Restoration"
  echo "\`\`\`bash"
  echo "tar -xzf $BACKUP_DIR/$BACKUP_NAME.tar.gz -C ~/Code/"
  echo "\`\`\`"
  echo ""
  echo "---"
} >> "$MANIFEST"

echo "📋 Manifest updated: $BACKUP_DIR/BACKUP_MANIFEST.md"
echo ""
echo "✅ Backup complete!"
