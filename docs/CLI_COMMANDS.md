# uCode1 CLI Command Reference

## Overview

uCode1 is a next-generation uDos platform with a comprehensive CLI interface for managing notes, knowledge, spatial data, and more.

## Basic Usage

```bash
ucode1 [OPTIONS] [SUBCOMMAND]
```

## Global Options

| Option | Description |
|--------|-------------|
| `--user` | Run in user mode (default) |
| `--privacy` | Run in privacy mode (no telemetry, no network) |
| `--status` | Run in status mode (enables MCP server) |
| `--dev` | Run in development mode |
| `--debug` | Enable debug logging |
| `--roadmap` | Show development roadmap |

## Modes

uCode1 operates in different modes that affect its behavior:

- **User Mode** (`--user`): Default mode for regular users
- **Privacy Mode** (`--privacy`): Disables telemetry and network features
- **Status Mode** (`--status`): Enables MCP server for inter-process communication
- **Dev Mode** (`--dev`): Development mode with additional logging and features
- **Debug Mode** (`--debug`): Enables verbose debug logging

## Commands

### 1. Note Management

Manage notes in your vault:

#### List Notes
```bash
ucode1 note list
```

Lists all notes in the current vault.

#### Show Note
```bash
ucode1 note show <name>
```

Display the content of a specific note.

**Arguments:**
- `name`: Name of the note to display

#### Create Note
```bash
ucode1 note create <name> [content]
```

Create a new note in the vault.

**Arguments:**
- `name`: Name of the new note
- `content`: (Optional) Initial content for the note

### 2. OK Agent

Interact with the local intent assistant:

#### Ask Question
```bash
ucode1 ok <prompt>
```

Ask a question or give a command to the OK agent.

**Arguments:**
- `prompt`: Your question or command

### 3. Terminal User Interface

#### Launch TUI
```bash
ucode1 tui
```

Launch the interactive Terminal User Interface for managing your vault.

### 4. Spatial Map Operations

Manage spatial data and maps:

#### Add Point
```bash
ucode1 map add <layer> <x> <y> <id>
```

Add a point to a spatial layer.

**Arguments:**
- `layer`: Name of the layer
- `x`: X coordinate
- `y`: Y coordinate
- `id`: Point identifier

#### Find Nearby Points
```bash
ucode1 map near <x> <y> <radius>
```

Find points near a specific location.

**Arguments:**
- `x`: X coordinate of search center
- `y`: Y coordinate of search center
- `radius`: Search radius

### 5. Feed Operations

Manage RSS/Atom feed subscriptions:

#### Add Feed
```bash
ucode1 feed add <url>
```

Subscribe to a new feed.

**Arguments:**
- `url`: URL of the feed to subscribe to

#### List Feeds
```bash
ucode1 feed list
```

List all subscribed feeds.

#### Remove Feed
```bash
ucode1 feed remove <url>
```

Unsubscribe from a feed.

**Arguments:**
- `url`: URL of the feed to remove

#### Fetch Feed
```bash
ucode1 feed fetch <url>
```

Manually fetch and update a feed.

**Arguments:**
- `url`: URL of the feed to fetch

## Examples

### Basic Workflow

```bash
# Create a new note
ucode1 note create "Project Ideas" "# Project Ideas\n\n1. Build a new CLI tool\n2. Create documentation\n3. Implement testing"

# List all notes
ucode1 note list

# View a specific note
ucode1 note show "Project Ideas"

# Ask the OK agent a question
ucode1 ok "What should I work on next?"

# Launch the TUI for interactive management
ucode1 tui
```

### Spatial Data Management

```bash
# Add locations to a map
ucode1 map add "Coffee Shops" 37.7749 -122.4194 "Blue Bottle"
ucode1 map add "Coffee Shops" 37.7670 -122.4230 "Ritual"

# Find coffee shops near a location
ucode1 map near 37.77 -122.42 0.5
```

### Feed Management

```bash
# Subscribe to feeds
ucode1 feed add "https://example.com/blog/rss"
ucode1 feed add "https://news.ycombinator.com/rss"

# List all subscriptions
ucode1 feed list

# Manually update a feed
ucode1 feed fetch "https://example.com/blog/rss"
```

## Advanced Usage

### Development Mode

```bash
# Run in development mode with debug logging
ucode1 --dev --debug tui
```

### Privacy Mode

```bash
# Run with no telemetry or network access
ucode1 --privacy note list
```

### Status Mode with MCP Server

```bash
# Run with MCP server enabled for inter-process communication
ucode1 --status tui
```

## Configuration

uCode1 uses a configuration file at `~/.uCode1/config.yaml` for persistent settings.

### Dev Configuration

In development mode, uCode1 looks for a `.dev.yaml` file in the current directory for additional development-specific configuration.

## Vault Location

By default, uCode1 stores notes and data in `~/Code/Vault`. This can be configured in the settings.

## Help Command

To get help information:

```bash
# General help
ucode1 --help

# Help for a specific command
ucode1 note --help
ucode1 ok --help
ucode1 map --help
ucode1 feed --help
```

## Roadmap

To view the development roadmap:

```bash
ucode1 --roadmap
```

## Troubleshooting

### Common Issues

**Vault not found:**
```bash
# Ensure the vault directory exists
mkdir -p ~/Code/Vault
```

**Permission issues:**
```bash
# Check directory permissions
chmod -R 755 ~/Code/Vault
```

**Debug mode:**
```bash
# Run with debug logging for troubleshooting
ucode1 --debug note list
```

## Best Practices

1. **Regular Backups**: Backup your vault directory regularly
2. **Use Modes Appropriately**: Use privacy mode when working with sensitive data
3. **Organize Notes**: Use a consistent naming convention for notes
4. **Leverage Spatial Data**: Use the map features for location-based data
5. **Feed Management**: Regularly review and clean up feed subscriptions

## Integration

uCode1 can integrate with:

- **Marksmith**: Shared vault compatibility
- **uDos**: Legacy uDos system integration
- **External Tools**: Via MCP server in status mode

## Future Features

Upcoming features in development:

- Advanced search and filtering
- Note tagging and categorization
- Export/import functionality
- Collaboration features
- Enhanced spatial analysis tools
