# uCode1 Documentation

Welcome to the uCode1 documentation hub. Here you'll find comprehensive guides, references, and examples for using uCode1.

## Getting Started

New to uCode1? Start here:

- [Quick Start Guide](QUICK_START.md) - Get up and running in minutes
- [CLI User Guide](CLI_README.md) - Complete user guide
- [CLI Command Reference](CLI_COMMANDS.md) - Detailed command reference

## Documentation Structure

```
docs/
├── README.md                # This file
├── QUICK_START.md           # Quick start guide
├── CLI_README.md            # Comprehensive user guide
├── CLI_COMMANDS.md          # Command reference
└── ../vault-bridge/
    └── SQLITE_IMPLEMENTATION.md  # SQLite vault implementation
```

## Core Concepts

### Vault

The vault is the heart of uCode1, storing all your notes, documents, and data. By default, it's located at `~/Code/Vault`.

### Notes

Notes are Markdown-formatted documents that form the basis of your knowledge base. They support:
- Full Markdown syntax
- Hierarchical organization
- Version history
- Tagging and categorization

### Modes

uCode1 operates in different modes:
- **User Mode**: Default mode for regular usage
- **Privacy Mode**: Disables telemetry and network features
- **Status Mode**: Enables MCP server for inter-process communication
- **Dev Mode**: Development mode with additional features
- **Debug Mode**: Verbose logging for troubleshooting

## CLI Reference

### Basic Commands

```bash
# Get help
ucode1 --help

# Create a note
ucode1 note create "My Note" "Content here"

# List notes
ucode1 note list

# Launch TUI
ucode1 tui
```

### Advanced Usage

```bash
# Privacy mode
ucode1 --privacy note create "Sensitive" "Confidential data"

# Development mode with debug
ucode1 --dev --debug tui

# Status mode for integration
ucode1 --status
```

## Integration

### Marksmith Compatibility

uCode1's vault system is compatible with Marksmith, allowing seamless integration between the two tools.

### MCP Server

The MCP (Multi-Client Protocol) server enables inter-process communication and integration with other tools.

### External Tools

uCode1 can integrate with:
- Version control systems (Git)
- External editors
- Automation scripts
- Monitoring tools

## Development

### Building from Source

```bash
git clone https://github.com/your-repo/uCode1.git
cd uCode1
cargo build --release
```

### Running Tests

```bash
# Run all tests
cargo test

# Run specific package tests
cargo test --package ucode1-vault-bridge
```

### Architecture

uCode1 is built with a modular architecture:
- **Core**: Fundamental data structures and utilities
- **Vault Bridge**: SQLite-based vault management
- **OK Agent**: Local intent assistant
- **MCP**: Multi-client protocol server
- **TUI**: Terminal user interface
- **Spatial**: Geospatial data management
- **Feed Spool**: RSS/Atom feed handling

## Troubleshooting

### Common Issues

**Vault not found:**
```bash
mkdir -p ~/Code/Vault
```

**Permission issues:**
```bash
chmod -R 755 ~/Code/Vault
```

**Database locked:**
```bash
# Ensure no other instances are running
pkill uCode1
```

### Debugging

```bash
# Enable debug logging
ucode1 --debug note list

# Check logs
tail -f ~/.uCode1/logs/ucode1.log
```

## Best Practices

1. **Regular Backups**: Backup your vault directory regularly
2. **Organization**: Use a consistent naming convention for notes
3. **Security**: Use privacy mode for sensitive data
4. **Version Control**: Consider using Git for your vault
5. **Documentation**: Document your workflows and conventions

## Community & Support

### Getting Help

- **In-app help**: `ucode1 --help`
- **Documentation**: This directory
- **Issue Tracker**: GitHub issues
- **Community Forum**: Coming soon

### Contributing

We welcome contributions! See `CONTRIBUTING.md` for guidelines on:
- Reporting bugs
- Suggesting features
- Submitting pull requests
- Code style guidelines

### Roadmap

View the development roadmap:
```bash
ucode1 --roadmap
```

Upcoming features:
- Advanced search and filtering
- Note tagging and categorization
- Export/import functionality
- Collaboration features
- Enhanced spatial analysis tools

## Additional Resources

### Related Documents

- [SQLite Vault Implementation](../vault-bridge/SQLITE_IMPLEMENTATION.md)
- [Architecture Overview](../ARCHITECTURE.md)
- [API Documentation](../API.md)

### External Links

- GitHub Repository: https://github.com/your-repo/uCode1
- Issue Tracker: https://github.com/your-repo/uCode1/issues
- Documentation: https://docs.ucode1.example.com

## License

uCode1 is released under the MIT License. See `LICENSE` for details.

## Changelog

See `CHANGELOG.md` for version history and release notes.

---

© 2024 uCode1 Team. All rights reserved.
