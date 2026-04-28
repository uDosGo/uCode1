# uSystem - Dynamic Command Management System

## Overview

uSystem is a dynamic command management system for uCode1 that provides:

1. **Runtime Command Registration**: Commands can be added, modified, and removed at runtime
2. **Dynamic Help Generation**: Help text is generated from the command database
3. **Markdown Documentation**: Automatic generation of documentation in multiple formats
4. **Extensibility**: Easy to add new commands and options without code changes

## Architecture

### Database Schema

uSystem uses SQLite to store command definitions with the following tables:

- **commands**: Main command definitions
- **command_options**: Command-specific options
- **subcommands**: Subcommands for each command
- **subcommand_options**: Options for subcommands
- **global_options**: Global options that apply to all commands
- **documentation**: Additional documentation pages

### Key Components

1. **USystem Struct**: Main interface for command management
2. **Command/Option Structs**: Data structures for command definitions
3. **Help Generators**: Functions to generate help text and markdown
4. **CLI Integration**: Integration with clap for command-line parsing

## Features

### 1. Dynamic Help System

```bash
# Get dynamic help
ucode1 docs

# Get markdown documentation
ucode1 docs --format markdown
```

### 2. Command Management

```rust
// Add a new command
let command = Command {
    id: 0,
    name: "mycommand".to_string(),
    description: "My custom command".to_string(),
    category: Some("Custom".to_string()),
    usage: Some("mycommand [args]".to_string()),
    example: Some("ucode1 mycommand --option value".to_string()),
    is_active: true,
};
usystem.add_command(&command)?;

// List all commands
let commands = usystem.list_commands()?;

// Generate help
let help_text = usystem.generate_help()?;
```

### 3. Documentation Generation

```bash
# Generate markdown documentation
ucode1 docs --format markdown > docs/commands.md

# Generate text help
ucode1 docs > help.txt
```

## Implementation Details

### Database Location

The uSystem database is located at:`~/.uCode1/usystem.db`

### Initialization

On first run, uSystem:
1. Creates the database file
2. Initializes all tables
3. Populates with default commands
4. Sets up indexes for performance

### Help Generation

The help system generates:

1. **Text Help**: Formatted for terminal display
2. **Markdown**: Structured documentation with tables and examples
3. **Dynamic Content**: Always reflects the current command set

### Integration with uCode1

uSystem integrates with uCode1 through:

1. **CLI Commands**: The `docs` command provides access to dynamic help
2. **Runtime**: Commands are loaded at startup
3. **Extensibility**: New commands can be added via the database

## Usage Examples

### Basic Help

```bash
# Get help for all commands
ucode1 docs

# Get help in markdown format
ucode1 docs --format markdown
```

### Documentation Generation

```bash
# Generate documentation file
ucode1 docs --format markdown > USYSTEM_COMMANDS.md

# View generated documentation
cat USYSTEM_COMMANDS.md
```

### Script Integration

```bash
#!/bin/bash

# Update documentation
ucode1 docs --format markdown > docs/USYSTEM_COMMANDS.md

# Commit changes
git add docs/USYSTEM_COMMANDS.md
git commit -m "Update dynamic documentation"
```

## Database Schema

### commands Table

```sql
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category TEXT,
    usage TEXT,
    example TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

### command_options Table

```sql
CREATE TABLE command_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_id INTEGER,
    name TEXT NOT NULL,
    short_name TEXT,
    description TEXT,
    requires_value BOOLEAN DEFAULT 0,
    default_value TEXT,
    is_required BOOLEAN DEFAULT 0,
    FOREIGN KEY (command_id) REFERENCES commands(id)
);
```

### global_options Table

```sql
CREATE TABLE global_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    short_name TEXT,
    description TEXT NOT NULL,
    applies_to_all BOOLEAN DEFAULT 1
);
```

## API Reference

### USystem Struct

```rust
pub struct USystem {
    db_path: PathBuf,
}
```

### Command Struct

```rust
pub struct Command {
    pub id: i64,
    pub name: String,
    pub description: String,
    pub category: Option<String>,
    pub usage: Option<String>,
    pub example: Option<String>,
    pub is_active: bool,
}
```

### Main Methods

```rust
// Initialize uSystem
pub fn new(db_path: &str) -> Self

// Command management
pub fn add_command(&self, command: &Command) -> SqliteResult<()>
pub fn get_command(&self, name: &str) -> SqliteResult<Option<Command>>
pub fn list_commands(&self) -> SqliteResult<Vec<Command>>

// Help generation
pub fn generate_help(&self) -> SqliteResult<String>
pub fn generate_markdown_doc(&self) -> SqliteResult<String>

// Initialization
pub fn initialize_default_commands(&self) -> SqliteResult<()>
```

## Benefits

### 1. Maintainability

- Commands defined in one place (database)
- No need to update help text in multiple locations
- Easy to add/remove commands

### 2. Consistency

- Uniform help format across all commands
- Automatic synchronization between CLI and documentation
- Reduced risk of outdated documentation

### 3. Extensibility

- New commands can be added without code changes
- Plugins can register commands dynamically
- Supports future command discovery

### 4. Documentation

- Always up-to-date documentation
- Multiple output formats
- Easy to integrate with CI/CD

## Future Enhancements

### 1. Command Discovery

- Auto-discover commands from plugins
- Dynamic loading of command modules
- Hot-reloading of commands

### 2. Advanced Documentation

- Man pages generation
- HTML documentation
- Interactive help system

### 3. Command Validation

- Validate command definitions
- Check for conflicts
- Ensure consistency

### 4. Internationalization

- Multi-language support
- Localized help text
- Translated documentation

## Integration Guide

### Adding uSystem to Your Application

1. **Add Dependency**
```toml
[dependencies]
ucode2-usystem = { path = "../uCode2/usystem" }
```

2. **Initialize uSystem**
```rust
let usystem_db_path = format!("{}/.uCode1/usystem.db", std::env::var("HOME").unwrap());
let usystem = USystem::new(&usystem_db_path);
usystem.initialize_default_commands()?;
```

3. **Add CLI Command**
```rust
.subcommand(
    Command::new("docs")
        .about("Display command documentation")
        .arg(
            Arg::new("format")
                .long("format")
                .short('f')
                .value_name("FORMAT")
                .help("Output format (text, markdown)")
        )
)
```

4. **Handle Command**
```rust
if let Some(("docs", docs_matches)) = matches.subcommand() {
    if let Some(format) = docs_matches.get_one::<String>("format") {
        if format == "markdown" {
            let md = usystem.generate_markdown_doc()?;
            println!("{}", md);
        } else {
            let help = usystem.generate_help()?;
            println!("{}", help);
        }
    } else {
        let help = usystem.generate_help()?;
        println!("{}", help);
    }
}
```

## Testing

### Unit Tests

```bash
cargo test --package ucode1-usystem
```

### Integration Tests

```bash
# Test help generation
ucode1 docs

# Test markdown generation
ucode1 docs --format markdown

# Verify documentation
cat docs/USYSTEM_COMMANDS.md
```

## Performance Considerations

- **Database Connection**: Connection is opened on demand
- **Caching**: Consider caching help text for frequent access
- **Indexes**: Proper indexing ensures fast lookups
- **Batch Operations**: Use transactions for bulk updates

## Security Considerations

- **Database Permissions**: Ensure proper file permissions
- **Input Validation**: Validate all command inputs
- **SQL Injection**: Use parameterized queries
- **Backup**: Regularly backup the database

## Troubleshooting

### Database Issues

```bash
# Check database integrity
sqlite3 ~/.uCode1/usystem.db "PRAGMA integrity_check;"

# Repair database
sqlite3 ~/.uCode1/usystem.db "VACUUM;"
```

### Command Not Found

```bash
# Reinitialize commands
# (This will reset to default commands)
rm ~/.uCode1/usystem.db
ucode1 docs
```

### Help Generation Errors

```bash
# Check database file
ls -la ~/.uCode1/usystem.db

# Verify permissions
chmod 644 ~/.uCode1/usystem.db
```

## Best Practices

1. **Regular Backups**: Backup the usystem database
2. **Version Control**: Consider versioning command definitions
3. **Documentation**: Keep documentation in sync with commands
4. **Testing**: Test help generation after command changes
5. **Performance**: Monitor database performance

## Conclusion

uSystem provides a powerful, dynamic command management system for uCode1 that:

- Reduces maintenance burden
- Ensures documentation accuracy
- Enables extensibility
- Supports multiple output formats

By using uSystem, uCode1 can evolve its command set while maintaining consistent, up-to-date documentation automatically.

## License

uSystem is part of uCode1 and is released under the MIT License.

## See Also

- [CLI Command Reference](CLI_COMMANDS.md)
- [SQLite Vault Implementation](../vault-bridge/SQLITE_IMPLEMENTATION.md)
- [uCode1 Architecture](../ARCHITECTURE.md)
