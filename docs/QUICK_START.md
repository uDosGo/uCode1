# uCode1 Quick Start Guide

## Installation

```bash
# Build from source
git clone https://github.com/your-repo/uCode1.git
cd uCode1
cargo build --release

# Install
cp target/release/uCode1 /usr/local/bin/
```

## First Steps

### 1. Initialize Vault
```bash
mkdir -p ~/Code/Vault
ucode1 --help
```

### 2. Create Your First Note
```bash
ucode1 note create "Welcome" "# Hello uCode1!\n\nThis is my first note."
```

### 3. List Notes
```bash
ucode1 note list
```

### 4. View Note
```bash
ucode1 note show "Welcome"
```

## Common Commands

### Notes
```bash
# Create
ucode1 note create "Meeting Notes" "Discussed project timeline..."

# List
ucode1 note list

# Show
ucode1 note show "Meeting Notes"
```

### OK Agent
```bash
# Ask a question
ucode1 ok "What should I work on today?"
```

### TUI
```bash
# Launch interactive interface
ucode1 tui
```

### Maps
```bash
# Add location
ucode1 map add "Places" 37.7749 -122.4194 "SF Office"

# Find nearby
ucode1 map near 37.77 -122.42 0.5
```

### Feeds
```bash
# Add feed
ucode1 feed add "https://example.com/rss"

# List feeds
ucode1 feed list
```

## Modes

```bash
# User mode (default)
ucode1 --user

# Privacy mode
ucode1 --privacy

# Development mode
ucode1 --dev --debug

# Status mode (MCP server)
ucode1 --status
```

## Help

```bash
# General help
ucode1 --help

# Command-specific help
ucode1 note --help
ucode1 ok --help
ucode1 map --help
ucode1 feed --help
```

## Tips

1. **Use aliases**: `alias un='ucode1 note'`
2. **Markdown support**: Notes support full Markdown formatting
3. **Regular backups**: `cp -r ~/Code/Vault ~/Backups/`
4. **Privacy mode**: Use `--privacy` for sensitive data
5. **TUI for exploration**: `ucode1 tui` for interactive management

## Troubleshooting

```bash
# Debug mode
ucode1 --debug note list

# Check vault permissions
chmod -R 755 ~/Code/Vault
```

## Next Steps

- Explore the [CLI Command Reference](CLI_COMMANDS.md)
- Try the [TUI interface](CLI_README.md#launch-the-tui)
- Set up [feed subscriptions](CLI_README.md#feed-management)
- Learn about [spatial features](CLI_README.md#location-based-workflow)
