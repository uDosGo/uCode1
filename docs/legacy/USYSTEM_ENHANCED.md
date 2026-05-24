# Enhanced uSystem - Complete Specification

## Overview

The enhanced uSystem provides a comprehensive command, schema, user, and permission management system for uCode1. This document describes the complete specification including:

1. **Command Management** - Dynamic command registration and help generation
2. **Schema Management** - uCode and Vault schema versioning
3. **User & Role Management** - User accounts, roles, and permissions
4. **Variable Management** - System and user variables
5. **Permission Matrix** - Fine-grained access control

## Database Schema

### Core Tables

#### 1. Commands (Enhanced)
```sql
CREATE TABLE commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category TEXT,
    usage TEXT,
    example TEXT,
    is_active BOOLEAN DEFAULT 1,
    is_dev BOOLEAN DEFAULT 0,          -- NEW: Tag dev commands
    dev_category TEXT,                -- NEW: Dev command category
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

#### 2. UCode Schemas (NEW)
```sql
CREATE TABLE ucode_schemas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    schema_type TEXT NOT NULL,        -- core, module, plugin, etc.
    schema_content TEXT NOT NULL,     -- JSON schema definition
    is_active BOOLEAN DEFAULT 1,
    released_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

#### 3. Vault Schemas (NEW)
```sql
CREATE TABLE vault_schemas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    schema_sql TEXT NOT NULL,          -- SQLite schema
    migration_script TEXT,            -- Optional migration script
    is_active BOOLEAN DEFAULT 1,
    released_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

#### 4. Users (NEW)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT,
    display_name TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    last_login TEXT,
    is_active BOOLEAN DEFAULT 1
);
```

#### 5. Roles (NEW)
```sql
CREATE TABLE roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    is_system_role BOOLEAN DEFAULT 0,  -- System roles cannot be deleted
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

#### 6. Permissions (NEW)
```sql
CREATE TABLE permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category TEXT,                    -- vault, system, commands, etc.
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

#### 7. Permission Matrix (NEW)
```sql
CREATE TABLE permission_matrix (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    resource_type TEXT NOT NULL,      -- vault, commands, system, etc.
    resource_id TEXT,                -- Optional specific resource ID
    can_read BOOLEAN DEFAULT 0,
    can_write BOOLEAN DEFAULT 0,
    can_delete BOOLEAN DEFAULT 0,
    can_execute BOOLEAN DEFAULT 0,
    can_admin BOOLEAN DEFAULT 0,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    UNIQUE(role_id, resource_type, resource_id)
);
```

#### 8. System Variables (NEW)
```sql
CREATE TABLE system_variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    scope TEXT DEFAULT 'system',      -- system, module, plugin
    is_encrypted BOOLEAN DEFAULT 0,
    is_readonly BOOLEAN DEFAULT 0,    -- Cannot be modified by users
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);
```

## Dev Command Separation

### Strategy

All development-related commands and options are tagged with `is_dev = 1` and stored separately:

1. **Dev Commands**: Stored in `commands` table with `is_dev = 1`
2. **Dev Options**: Stored in `command_options`/`global_options` with `is_dev = 1`
3. **Dev Documentation**: Stored in `documentation` table with `is_dev = 1`

### Storage Locations

1. **DevStudio (Ecosystem)**: Development environment commands
2. **uCodeGo/Dev/... (System)**: System-level dev commands
3. **User Vault (User)**: User-specific dev configurations

### Example Dev Commands

```sql
INSERT INTO commands (name, description, is_dev, dev_category) VALUES
    ('dev-reload', 'Reload modules in development mode', 1, 'core'),
    ('dev-profile', 'Performance profiling', 1, 'tools'),
    ('dev-debug', 'Advanced debugging tools', 1, 'tools');
```

## Schema Management

### uCode Schema Versions

```rust
let schema = UCodeSchema {
    id: 0,
    version: "1.0.1".to_string(),
    description: "Initial uCode1 schema".to_string(),
    schema_type: "core".to_string(),
    schema_content: json!({
        "version": "1.0.1",
        "components": ["vault-bridge", "ok-agent", "mcp", "tui"],
        "features": ["sqlite-vault", "command-management"]
    }).to_string(),
    is_active: true,
    released_at: Some("2024-01-15".to_string()),
};

usystem.add_ucode_schema(&schema)?;
```

### Vault Schema Versions

```rust
let vault_schema = VaultSchema {
    id: 0,
    version: "1.0.0".to_string(),
    description: "Initial vault schema".to_string(),
    schema_sql: "CREATE TABLE space (...);".to_string(),
    migration_script: None,
    is_active: true,
    released_at: Some("2024-01-15".to_string()),
};

usystem.add_vault_schema(&vault_schema)?;
```

## User & Role Management

### Default Roles

| Role | Description | System Role |
|------|-------------|-------------|
| admin | Full access | Yes |
| user | Standard permissions | Yes |
| guest | Limited access | Yes |
| developer | Extended permissions | No |

### Role Permissions Matrix

```sql
-- Admin: Full access
INSERT INTO permission_matrix (role_id, resource_type, can_read, can_write, can_delete, can_execute, can_admin)
VALUES (
    (SELECT id FROM roles WHERE name = 'admin'),
    'vault', 1, 1, 1, 1, 1
);

-- User: Read/Write vault, Execute commands
INSERT INTO permission_matrix (role_id, resource_type, can_read, can_write, can_delete, can_execute, can_admin)
VALUES (
    (SELECT id FROM roles WHERE name = 'user'),
    'vault', 1, 1, 0, 1, 0
);

-- Guest: Read-only
INSERT INTO permission_matrix (role_id, resource_type, can_read, can_write, can_delete, can_execute, can_admin)
VALUES (
    (SELECT id FROM roles WHERE name = 'guest'),
    'vault', 1, 0, 0, 0, 0
);
```

### User Management API

```rust
// Add user
let user = User {
    id: 0,
    username: "john_doe".to_string(),
    email: Some("john@example.com".to_string()),
    display_name: Some("John Doe".to_string()),
    is_active: true,
};
usystem.add_user(&user)?;

// Get user
if let Some(user) = usystem.get_user("john_doe")? {
    println!("Found user: {}", user.username);
}

// List users
let users = usystem.list_users()?;
for user in users {
    println!("- {}", user.username);
}
```

## System Variables

### Default System Variables

```sql
INSERT INTO system_variables (name, value, scope, is_readonly) VALUES
    ('vault.path', '~/Code/Vault', 'system', 0),
    ('log.level', 'info', 'system', 0),
    ('max.connections', '100', 'system', 0),
    ('api.timeout', '30', 'system', 0);
```

### Variable Management

```rust
// Get system variable
if let Some(var) = usystem.get_system_variable("vault.path")? {
    println!("Vault path: {}", var.value);
}

// List all variables
let vars = usystem.list_system_variables()?;
for var in vars {
    println!("{}: {}", var.name, var.value);
}
```

## Enhanced Help Generation

### Extended Help with Schema Information

```rust
let extended_help = usystem.generate_extended_help()?;
println!("{}", extended_help);
```

Output includes:
- All active commands (dev commands marked)
- Global options (dev options marked)
- uCode schema versions
- Vault schema versions

### Markdown Documentation with Permissions

```rust
pub fn generate_permissions_doc(&self) -> SqliteResult<String> {
    let roles = self.list_roles()?;
    let matrix = self.get_permission_matrix()?;
    
    let mut md = String::new();
    md.push_str("# Permission Matrix\n\n");
    
    for role in roles {
        md.push_str(&format!("## {}\n\n", role.name));
        md.push_str(&format!("{}\n\n", role.description));
        
        md.push_str("| Resource Type | Read | Write | Delete | Execute | Admin |\n");
        md.push_str("|---------------|------|-------|--------|---------|-------|\n");
        
        for entry in &matrix {
            if entry.role_id == role.id {
                md.push_str(&format!("| {} | {} | {} | {} | {} | {} |\n",
                    entry.resource_type,
                    if entry.can_read { "✓" } else { "✗" },
                    if entry.can_write { "✓" } else { "✗" },
                    if entry.can_delete { "✓" } else { "✗" },
                    if entry.can_execute { "✓" } else { "✗" },
                    if entry.can_admin { "✓" } else { "✗" }
                ));
            }
        }
        md.push_str("\n");
    }
    
    Ok(md)
}
```

## Integration with uCode1

### CLI Commands

```bash
# Get extended help with schemas
ucode1 docs

# Get markdown documentation
ucode1 docs --format markdown

# List uCode schemas
# (Would require additional command implementation)
```

### Rust API Integration

```rust
// Initialize uSystem with enhanced schema
let usystem = USystem::new("~/.uCode1/usystem.db");
usystem.initialize_database()?;

// Load all schemas
let ucode_schemas = usystem.list_ucode_schemas()?;
let vault_schemas = usystem.list_vault_schemas()?;

// Check user permissions (pseudo-code)
let current_user = usystem.get_user("current")?;
let user_roles = get_user_roles(&usystem, current_user.id)?;
let has_permission = check_permission(&usystem, &user_roles, "vault", "write")?;
```

## Security Considerations

### Dev Command Isolation

1. **Tagging**: All dev commands tagged with `is_dev = 1`
2. **Separation**: Dev commands stored separately from production commands
3. **Access Control**: Dev commands require special permissions

### Permission Management

1. **Least Privilege**: Roles have minimum required permissions
2. **Audit Trail**: All permission changes logged
3. **Validation**: Permission matrix validated on changes

### Data Protection

1. **Encryption**: Sensitive variables can be encrypted
2. **Read-only**: Critical system variables protected
3. **Backup**: Regular database backups recommended

## Migration Strategy

### From Previous Versions

1. **Backup**: Backup existing usystem.db
2. **Update Schema**: Run new schema SQL
3. **Reinitialize**: Initialize default data
4. **Migrate**: Migrate existing commands/users

### Dev Command Migration

```sql
-- Tag existing dev commands
UPDATE commands SET is_dev = 1 WHERE name LIKE 'dev-%';

-- Move dev commands to appropriate storage
-- (Implementation depends on specific requirements)
```

## Best Practices

### Command Organization

1. **Categorize**: Use categories for related commands
2. **Document**: Always include usage and examples
3. **Tag**: Clearly mark dev vs production commands

### Schema Management

1. **Version**: Use semantic versioning
2. **Document**: Include release notes
3. **Test**: Validate schemas before activation

### Permission Design

1. **Role-Based**: Design roles for common use cases
2. **Granular**: Use permission matrix for fine control
3. **Review**: Regularly audit permissions

## Future Enhancements

### 1. Dev Environment Management
- DevStudio integration
- Sandbox environments
- Dev command isolation

### 2. Advanced Schema Features
- Schema validation
- Migration tools
- Version compatibility checks

### 3. Enhanced Security
- Permission inheritance
- Temporary permissions
- Audit logging

### 4. User Experience
- Interactive permission editor
- Role templates
- Permission wizards

## Example: Complete Setup

```rust
use ucode1_usystem::{USystem, UCodeSchema, VaultSchema, User, Role};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize uSystem
    let usystem = USystem::new("~/.uCode1/usystem.db");
    usystem.initialize_database()?;
    
    // Add uCode schema
    let ucode_schema = UCodeSchema {
        id: 0,
        version: "1.0.1".to_string(),
        description: "Initial release".to_string(),
        schema_type: "core".to_string(),
        schema_content: "{...}".to_string(),
        is_active: true,
        released_at: Some("2024-01-15".to_string()),
    };
    usystem.add_ucode_schema(&ucode_schema)?;
    
    // Add vault schema
    let vault_schema = VaultSchema {
        id: 0,
        version: "1.0.0".to_string(),
        description: "Initial vault schema".to_string(),
        schema_sql: "CREATE TABLE space (...)".to_string(),
        migration_script: None,
        is_active: true,
        released_at: Some("2024-01-15".to_string()),
    };
    usystem.add_vault_schema(&vault_schema)?;
    
    // Add admin user
    let admin = User {
        id: 0,
        username: "admin".to_string(),
        email: Some("admin@example.com".to_string()),
        display_name: Some("Administrator".to_string()),
        is_active: true,
    };
    usystem.add_user(&admin)?;
    
    // Generate documentation
    let markdown = usystem.generate_markdown_doc()?;
    std::fs::write("docs/USYSTEM_COMMANDS.md", markdown)?;
    
    println!("uSystem initialized successfully!");
    Ok(())
}
```

## Conclusion

The enhanced uSystem provides a comprehensive foundation for:

- **Command Management**: Dynamic, extensible command system
- **Schema Versioning**: Track uCode and Vault evolution
- **User & Role Management**: Fine-grained access control
- **Dev/Prod Separation**: Clear distinction between environments
- **Documentation**: Automatic, always up-to-date

This system enables uCode1 to grow while maintaining security, organization, and documentation quality.

## Appendix: SQL Queries

### List All Active Commands (Non-Dev)
```sql
SELECT name, description, category 
FROM commands 
WHERE is_active = 1 AND is_dev = 0 
ORDER BY category, name;
```

### List Dev Commands
```sql
SELECT name, description, dev_category 
FROM commands 
WHERE is_dev = 1 
ORDER BY dev_category, name;
```

### Get Permission Matrix for Role
```sql
SELECT p.name as permission, pm.can_read, pm.can_write, pm.can_delete, pm.can_execute, pm.can_admin
FROM permission_matrix pm
JOIN permissions p ON pm.permission_id = p.id
WHERE pm.role_id = (SELECT id FROM roles WHERE name = 'user');
```

### Find Schemas by Type
```sql
SELECT version, description, released_at 
FROM ucode_schemas 
WHERE schema_type = 'core' 
ORDER BY version DESC;
```

## License

This specification is part of uCode1 and is released under the MIT License.
