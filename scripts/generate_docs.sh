#!/bin/bash

# Generate uSystem documentation
# This script generates markdown documentation from the uSystem database

# Build the project first
cd "$(dirname "$0")/.."
echo "Building uCode1..."
cargo build --release 2>&1 | tail -5

# Generate markdown documentation
echo ""
echo "Generating markdown documentation..."
./target/release/uCode1 docs --format markdown > docs/USYSTEM_COMMANDS.md

if [ $? -eq 0 ]; then
    echo "✓ Documentation generated successfully: docs/USYSTEM_COMMANDS.md"
    echo ""
    echo "File contents:"
    head -20 docs/USYSTEM_COMMANDS.md
else
    echo "✗ Failed to generate documentation"
    exit 1
fi
