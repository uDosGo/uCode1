# uDos Unified Command (udos)

The `udos` command provides a unified entry point for launching and managing all uDos components with a single command.

## Features

- **Single Command Experience**: Start the entire uDos development environment with `udos dev` or `udo dev`
- **Component Management**: Start individual components (core, UI, Re3Engine, Re3Chat)
- **Port Management**: Automatic port assignment to prevent conflicts
- **Process Management**: Graceful startup and shutdown with Ctrl+C
- **Alias Support**: Use `udo` as a convenient shortcut for `udos`

## Installation

### Quick Install

```bash
./install-udos.sh
```

This will:
1. Build the release version of `udos`
2. Install it to `/usr/local/bin/udos`
3. Create a symlink `/usr/local/bin/udo` pointing to `udos`

### Manual Installation

```bash
# Build the release version
cd udos-cli
cargo build --release

# Install to your PATH
cp target/release/udos /usr/local/bin/udos
ln -s /usr/local/bin/udos /usr/local/bin/udo
chmod +x /usr/local/bin/udos /usr/local/bin/udo
```

## Usage

### Start Development Environment

```bash
# Start everything (core + UI + Re3Engine + Re3Chat)
udos dev

# Or use the short alias
udo dev
```

This starts:
- ✅ uCode1 core (MCP server + feed spool + daemon)
- ✅ ThinUI (Teletext dashboard on auto-assigned port)
- ✅ Re3Engine (reasoning MCP server)
- ✅ Re3Chat (browser chat interface)

### Individual Components

```bash
# Start only the core
udos core

# Start only the UI
udos ui

# Start Re3Engine
udos re3

# Start Re3Chat
udos chat

# Start everything
udos all
```

### Port Management

```bash
# List assigned ports
udos ports list

# Assign a port manually
udos ports assign

# Free a port
udos ports free
```

### Process Control

```bash
# Stop all running components
udos stop

# Check status
udos status
```

## Global Flags

All commands support these global flags:

- `--dev`: Run in development mode
- `--privacy`: Run in privacy mode (no telemetry, no network)
- `--status`: Show status information
- `--debug`: Enable debug logging

## Architecture

### Process Manager

The `ProcessManager` handles:
- Spawning child processes
- Tracking running processes
- Graceful shutdown on Ctrl+C
- Error handling and logging

### Port Manager

The `PortManager` handles:
- Automatic port assignment using available ports
- Port conflict prevention
- Port tracking and management
- Manual port assignment/freeing

### Component Launchers

Each component has a dedicated launcher function:
- `start_core()`: Launches uCode1 with MCP server
- `start_thinui()`: Launches ThinUI dashboard
- `start_re3engine()`: Launches Re3Engine
- `start_re3chat()`: Launches Re3Chat browser interface

## Development

### Building

```bash
cargo build          # Debug build
cargo build --release # Optimized release build
```

### Testing

```bash
./test-udos.sh  # Run comprehensive tests
```

### Running

```bash
# Run from source
cargo run -- dev

# Run release version
./target/release/udos dev
```

## Command Reference

| Command | Description |
|---------|-------------|
| `udos dev` | Start complete development environment |
| `udos core` | Start uCode1 core components |
| `udos ui` | Launch ThinUI dashboard |
| `udos re3` | Start Re3Engine |
| `udos chat` | Start Re3Chat |
| `udos all` | Start all components |
| `udos stop` | Stop all running components |
| `udos status` | Show status of components |
| `udos ports list` | List assigned ports |
| `udos ports assign` | Assign a port |
| `udos ports free` | Free a port |

## Dependencies

- `clap` - Command line argument parsing
- `tokio` - Async runtime
- `log` / `env_logger` - Logging
- `which` - Binary location detection
- `portpicker` - Automatic port assignment

## Future Enhancements

- Process status monitoring
- Health checks for running components
- Configuration file support
- Cross-platform service management
- Docker/container integration

## License

MIT License

Copyright (c) 2024 uDos Project
