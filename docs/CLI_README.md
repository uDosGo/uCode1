# uCode1 CLI - User Guide

## Introduction

Welcome to uCode1 CLI - a powerful command-line interface for managing your knowledge vault, spatial data, and more. This guide will help you get started with the basic commands and workflows.

## Installation

### Prerequisites

- Rust 1.70+ (recommended)
- SQLite 3.x
- Git (for cloning the repository)

### Building from Source

```bash
# Clone the repository
git clone https://github.com/your-repo/uCode1.git
cd uCode1

# Build the project
cargo build --release

# Install (optional)
cp target/release/uCode1 /usr/local/bin/
```

### Verification

```bash
# Check installation
ucode1 --version

# Display help
ucode1 --help
```

## Getting Started

### First Run

```bash
# Start in user mode (default)
ucode1 --user

# Or start with debug logging
ucode1 --debug
```

### Vault Setup

By default, uCode1 uses `~/Code/Vault` as the vault location. Ensure this directory exists:

```bash
mkdir -p ~/Code/Vault
```

## Basic Commands

### 1. Note Management

Notes are the core of uCode1's knowledge management system.

#### Create Your First Note

```bash
ucode1 note create "Getting Started" "# Welcome to uCode1!\n\nThis is my first note."
```

#### List All Notes

```bash
ucode1 note list
```

#### View a Note

```bash
ucode1 note show "Getting Started"
```

### 2. Launch the TUI

For an interactive experience:

```bash
ucode1 tui
```

### 3. Ask the OK Agent

Get assistance from the local intent agent:

```bash
ucode1 ok "What should I learn today?"
```

## Command Reference

### Global Options

| Option | Description | Example |
|--------|-------------|---------|
| `--user` | User mode (default) | `ucode1 --user` |
| `--privacy` | Privacy mode | `ucode1 --privacy` |
| `--status` | Status mode (MCP server) | `ucode1 --status` |
| `--dev` | Development mode | `ucode1 --dev` |
| `--debug` | Debug logging | `ucode1 --debug` |
| `--roadmap` | Show roadmap | `ucode1 --roadmap` |

### Note Commands

| Command | Description | Example |
|---------|-------------|---------|
| `note list` | List all notes | `ucode1 note list` |
| `note show <name>` | Show note content | `ucode1 note show "Meeting Notes"` |
| `note create <name> [content]` | Create new note | `ucode1 note create "Ideas" "My ideas..."` |

### OK Agent Commands

| Command | Description | Example |
|---------|-------------|---------|
| `ok <prompt>` | Ask a question | `ucode1 ok "What's the weather?"` |

### TUI Command

| Command | Description | Example |
|---------|-------------|---------|
| `tui` | Launch TUI | `ucode1 tui` |

### Map Commands

| Command | Description | Example |
|---------|-------------|---------|
| `map add <layer> <x> <y> <id>` | Add point | `ucode1 map add "Places" 0 0 "Home"` |
| `map near <x> <y> <radius>` | Find nearby | `ucode1 map near 0 0 10` |

### Feed Commands

| Command | Description | Example |
|---------|-------------|---------|
| `feed add <url>` | Add feed | `ucode1 feed add "https://example.com/rss"` |
| `feed list` | List feeds | `ucode1 feed list` |
| `feed remove <url>` | Remove feed | `ucode1 feed remove "https://example.com/rss"` |
| `feed fetch <url>` | Fetch feed | `ucode1 feed fetch "https://example.com/rss"` |

## Workflow Examples

### Daily Knowledge Management

```bash
# Morning - Review notes
ucode1 note list
ucode1 note show "Today's Goals"

# Add new ideas
ucode1 note create "Project Ideas" "1. Implement feature X\n2. Fix bug Y\n3. Write documentation"

# Evening - Review progress
ucode1 tui
```

### Research Workflow

```bash
# Subscribe to relevant feeds
ucode1 feed add "https://techblog.com/rss"
ucode1 feed add "https://researchnews.org/feed"

# Review feeds
ucode1 feed list
ucode1 feed fetch "https://techblog.com/rss"

# Take notes on interesting articles
ucode1 note create "Article Summary" "Key points from today's reading..."
```

### Location-Based Workflow

```bash
# Add important locations
ucode1 map add "Offices" 37.7749 -122.4194 "Main Office"
ucode1 map add "Offices" 37.3352 -121.8811 "South Office"

# Find nearby locations
ucode1 map near 37.77 -122.42 0.5

# Save location notes
ucode1 note create "Office Visits" "Visited main office on 2024-01-15"
```

## Advanced Usage

### Modes

#### Privacy Mode

```bash
# Work with sensitive data
ucode1 --privacy note create "Confidential" "Sensitive information..."
```

#### Development Mode

```bash
# Development and debugging
ucode1 --dev --debug tui
```

#### Status Mode

```bash
# Enable MCP server for integration
ucode1 --status tui
```

### Combining Commands

```bash
# Chain commands using shell scripts
#!/bin/bash
ucode1 note create "Daily Log" "$(date)"
ucode1 feed fetch "https://news.example.com/rss"
ucode1 tui
```

## Configuration

### Configuration File

uCode1 uses `~/.uCode1/config.yaml` for configuration. Example:

```yaml
vault_path: ~/Code/Vault
default_mode: user
logging_level: info
```

### Dev Configuration

In development mode, uCode1 loads `.dev.yaml` from the current directory:

```yaml
debug: true
trace_logging: true
experimental_features: true
```

## Tips and Tricks

### 1. Note Organization

Use a consistent naming convention:
- `Project/Feature Name`
- `Date - Topic`
- `Category/Subcategory`

### 2. Markdown Support

Notes support Markdown formatting:

```bash
ucode1 note create "Formatted Note" "# Heading\n\n**Bold text**\n\n- List item 1\n- List item 2"
```

### 3. Quick Notes

Use shell aliases for common operations:

```bash
# Add to your .bashrc or .zshrc
alias unote='ucode1 note'
alias ulist='ucode1 note list'
alias utui='ucode1 tui'
```

### 4. Integration

Integrate with other tools:

```bash
# Pipe content from other commands
cat todo.txt | xargs -I {} ucode1 note create "Todo" {}

# Use in scripts
notes=$(ucode1 note list)
echo "You have $(echo $notes | wc -w) notes"
```

## Troubleshooting

### Common Issues

#### Vault not found

```bash
mkdir -p ~/Code/Vault
chmod 755 ~/Code/Vault
```

#### Permission denied

```bash
chmod -R 755 ~/Code/Vault
```

#### Database locked

```bash
# Ensure no other uCode1 instances are running
pkill uCode1
# Or wait for the lock to be released
```

### Debugging

```bash
# Run with debug logging
ucode1 --debug note list

# Check logs
tail -f ~/.uCode1/logs/ucode1.log
```

## Best Practices

### 1. Regular Backups

```bash
# Backup your vault regularly
cp -r ~/Code/Vault ~/Backups/Vault-$(date +%Y-%m-%d)
```

### 2. Version Control

Consider using Git for your vault:

```bash
cd ~/Code/Vault
git init
git add .
git commit -m "Initial vault commit"
```

### 3. Organization

- Use folders for related notes
- Tag notes consistently
- Review and archive old notes regularly

### 4. Security

- Use privacy mode for sensitive data
- Encrypt your vault directory if needed
- Regularly audit access permissions

## Roadmap

View the development roadmap:

```bash
ucode1 --roadmap
```

Upcoming features:
- Advanced search and filtering
- Note tagging and categorization
- Export/import functionality
- Collaboration features
- Enhanced spatial analysis

## Community

### Contributing

We welcome contributions! See `CONTRIBUTING.md` for guidelines.

### Reporting Issues

Found a bug? Report it on GitHub:

```bash
git clone https://github.com/your-repo/uCode1.git
# Follow issue template
```

### Feature Requests

Have an idea? Open a feature request with details about your use case.

## Support

### Documentation

- CLI Command Reference: `docs/CLI_COMMANDS.md`
- API Documentation: `docs/API.md`
- Architecture: `docs/ARCHITECTURE.md`

### Getting Help

```bash
# In-app help
ucode1 --help
ucode1 note --help
ucode1 ok --help
```

## License

uCode1 is released under the MIT License. See `LICENSE` for details.

## Changelog

See `CHANGELOG.md` for version history and release notes.

## Contact

For questions and support:
- Email: support@ucode1.example.com
- GitHub: https://github.com/your-repo/uCode1
- Community Forum: https://community.ucode1.example.com

---

© 2024 uCode1 Team. All rights reserved.
