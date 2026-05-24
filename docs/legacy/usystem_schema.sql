-- uSystem Database Schema for Command Management
-- This schema defines the structure for storing commands, options, documentation, schemas, users, and permissions

-- Commands table
CREATE TABLE IF NOT EXISTS commands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category TEXT,
    usage TEXT,
    example TEXT,
    is_active BOOLEAN DEFAULT 1,
    is_dev BOOLEAN DEFAULT 0,
    dev_category TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Command options/flags
CREATE TABLE IF NOT EXISTS command_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_id INTEGER,
    name TEXT NOT NULL,
    short_name TEXT,
    description TEXT,
    requires_value BOOLEAN DEFAULT 0,
    default_value TEXT,
    is_required BOOLEAN DEFAULT 0,
    is_dev BOOLEAN DEFAULT 0,
    FOREIGN KEY (command_id) REFERENCES commands(id)
);

-- Command subcommands
CREATE TABLE IF NOT EXISTS subcommands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_id INTEGER,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    usage TEXT,
    example TEXT,
    is_dev BOOLEAN DEFAULT 0,
    FOREIGN KEY (command_id) REFERENCES commands(id)
);

-- Subcommand options
CREATE TABLE IF NOT EXISTS subcommand_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subcommand_id INTEGER,
    name TEXT NOT NULL,
    short_name TEXT,
    description TEXT,
    requires_value BOOLEAN DEFAULT 0,
    default_value TEXT,
    is_required BOOLEAN DEFAULT 0,
    is_dev BOOLEAN DEFAULT 0,
    FOREIGN KEY (subcommand_id) REFERENCES subcommands(id)
);

-- Global options (flags that apply to all commands)
CREATE TABLE IF NOT EXISTS global_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    short_name TEXT,
    description TEXT NOT NULL,
    applies_to_all BOOLEAN DEFAULT 1,
    is_dev BOOLEAN DEFAULT 0
);

-- Documentation pages
CREATE TABLE IF NOT EXISTS documentation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    category TEXT,
    format TEXT DEFAULT 'markdown',
    is_public BOOLEAN DEFAULT 1,
    is_dev BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- uCode Schema Versions
CREATE TABLE IF NOT EXISTS ucode_schemas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    schema_type TEXT NOT NULL,
    schema_content TEXT NOT NULL,
    is_active BOOLEAN DEFAULT 1,
    released_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Vault Schema Versions
CREATE TABLE IF NOT EXISTS vault_schemas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    schema_sql TEXT NOT NULL,
    migration_script TEXT,
    is_active BOOLEAN DEFAULT 1,
    released_at TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Users
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT,
    display_name TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    last_login TEXT,
    is_active BOOLEAN DEFAULT 1
);

-- Roles
CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    is_system_role BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- User Roles
CREATE TABLE IF NOT EXISTS user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assigned_at TEXT DEFAULT (datetime('now')),
    assigned_by INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    UNIQUE(user_id, role_id)
);

-- Permissions
CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT NOT NULL,
    category TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Role Permissions
CREATE TABLE IF NOT EXISTS role_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    granted_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id),
    UNIQUE(role_id, permission_id)
);

-- User Variables
CREATE TABLE IF NOT EXISTS user_variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    value TEXT NOT NULL,
    scope TEXT DEFAULT 'user',
    is_encrypted BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    UNIQUE(user_id, name, scope)
);

-- System Variables
CREATE TABLE IF NOT EXISTS system_variables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    value TEXT NOT NULL,
    scope TEXT DEFAULT 'system',
    is_encrypted BOOLEAN DEFAULT 0,
    is_readonly BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- Installation Records
CREATE TABLE IF NOT EXISTS installations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    installation_id TEXT NOT NULL UNIQUE,
    version TEXT NOT NULL,
    installed_at TEXT DEFAULT (datetime('now')),
    installed_by INTEGER,
    environment TEXT,
    config_hash TEXT,
    FOREIGN KEY (installed_by) REFERENCES users(id)
);

-- Installation Roles
CREATE TABLE IF NOT EXISTS installation_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    installation_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    assigned_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (installation_id) REFERENCES installations(id),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    UNIQUE(installation_id, role_id)
);

-- Permission Matrix
CREATE TABLE IF NOT EXISTS permission_matrix (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    can_read BOOLEAN DEFAULT 0,
    can_write BOOLEAN DEFAULT 0,
    can_delete BOOLEAN DEFAULT 0,
    can_execute BOOLEAN DEFAULT 0,
    can_admin BOOLEAN DEFAULT 0,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    UNIQUE(role_id, resource_type, resource_id)
);

-- Audit Log
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT,
    user_agent TEXT,
    timestamp TEXT DEFAULT (datetime('now'))
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_commands_name ON commands(name);
CREATE INDEX IF NOT EXISTS idx_commands_category ON commands(category);
CREATE INDEX IF NOT EXISTS idx_commands_is_dev ON commands(is_dev);
CREATE INDEX IF NOT EXISTS idx_command_options_command ON command_options(command_id);
CREATE INDEX IF NOT EXISTS idx_subcommands_command ON subcommands(command_id);
CREATE INDEX IF NOT EXISTS idx_subcommand_options_subcommand ON subcommand_options(subcommand_id);
CREATE INDEX IF NOT EXISTS idx_documentation_category ON documentation(category);
CREATE INDEX IF NOT EXISTS idx_documentation_is_dev ON documentation(is_dev);
CREATE INDEX IF NOT EXISTS idx_ucode_schemas_version ON ucode_schemas(version);
CREATE INDEX IF NOT EXISTS idx_vault_schemas_version ON vault_schemas(version);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_roles_name ON roles(name);
CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role ON user_roles(role_id);
CREATE INDEX IF NOT EXISTS idx_permissions_name ON permissions(name);
CREATE INDEX IF NOT EXISTS idx_role_permissions_role ON role_permissions(role_id);
CREATE INDEX IF NOT EXISTS idx_role_permissions_permission ON role_permissions(permission_id);
CREATE INDEX IF NOT EXISTS idx_user_variables_user ON user_variables(user_id);
CREATE INDEX IF NOT EXISTS idx_system_variables_name ON system_variables(name);
CREATE INDEX IF NOT EXISTS idx_installations_id ON installations(installation_id);
CREATE INDEX IF NOT EXISTS idx_permission_matrix_role ON permission_matrix(role_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp);

-- Insert initial global options (excluding --dev which should be separate)
INSERT OR IGNORE INTO global_options (name, short_name, description, is_dev) VALUES
    ('user', NULL, 'Run in user mode (default)', 0),
    ('privacy', NULL, 'Run in privacy mode (no telemetry, no network)', 0),
    ('status', NULL, 'Run in status mode (enables MCP server)', 0),
    ('debug', NULL, 'Enable debug logging', 0),
    ('roadmap', NULL, 'Show development roadmap', 0),
    ('help', 'h', 'Print help information', 0),
    ('version', 'V', 'Print version information', 0);

-- Insert dev-specific global options (tagged as dev)
INSERT OR IGNORE INTO global_options (name, short_name, description, is_dev) VALUES
    ('dev', NULL, 'Run in development mode', 1);

-- Insert default uCode schema
INSERT OR IGNORE INTO ucode_schemas (version, description, schema_type, schema_content, released_at) VALUES
    ('1.0.1', 'Initial uCode1 schema with vault integration', 'core', '{
        "version": "1.0.1",
        "components": [
            "vault-bridge",
            "ok-agent",
            "mcp",
            "tui",
            "spatial",
            "feed-spool"
        ],
        "features": [
            "sqlite-vault",
            "command-management",
            "ai-assistant",
            "spatial-mapping",
            "feed-management"
        ]
    }', '2024-01-15');

-- Insert default vault schema
INSERT OR IGNORE INTO vault_schemas (version, description, schema_sql, released_at) VALUES
    ('1.0.0', 'Initial vault schema with space, doc, and history tables', '
        CREATE TABLE space (...);
        CREATE TABLE doc (...);
        CREATE TABLE history (...);
    ', '2024-01-15');

-- Insert default roles
INSERT OR IGNORE INTO roles (name, description, is_system_role) VALUES
    ('admin', 'Administrator with full access', 1),
    ('user', 'Regular user with standard permissions', 1),
    ('guest', 'Guest user with limited permissions', 1),
    ('developer', 'Developer with extended permissions', 0);

-- Insert default permissions
INSERT OR IGNORE INTO permissions (name, description, category) VALUES
    ('vault_read', 'Read access to vault', 'vault'),
    ('vault_write', 'Write access to vault', 'vault'),
    ('vault_admin', 'Admin access to vault', 'vault'),
    ('command_execute', 'Execute commands', 'system'),
    ('command_admin', 'Administer commands', 'system'),
    ('user_management', 'Manage users', 'system'),
    ('role_management', 'Manage roles', 'system'),
    ('system_settings', 'Modify system settings', 'system');

-- Insert default role permissions
INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES
    -- Admin role
    ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'vault_read')),
    ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'vault_write')),
    ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'vault_admin')),
    ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'command_execute')),
    ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'command_admin')),
    ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'user_management')),
    ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'role_management')),
    ((SELECT id FROM roles WHERE name = 'admin'), (SELECT id FROM permissions WHERE name = 'system_settings')),
    
    -- User role
    ((SELECT id FROM roles WHERE name = 'user'), (SELECT id FROM permissions WHERE name = 'vault_read')),
    ((SELECT id FROM roles WHERE name = 'user'), (SELECT id FROM permissions WHERE name = 'vault_write')),
    ((SELECT id FROM roles WHERE name = 'user'), (SELECT id FROM permissions WHERE name = 'command_execute')),
    
    -- Guest role
    ((SELECT id FROM roles WHERE name = 'guest'), (SELECT id FROM permissions WHERE name = 'vault_read')),
    ((SELECT id FROM roles WHERE name = 'guest'), (SELECT id FROM permissions WHERE name = 'command_execute')),
    
    -- Developer role
    ((SELECT id FROM roles WHERE name = 'developer'), (SELECT id FROM permissions WHERE name = 'vault_read')),
    ((SELECT id FROM roles WHERE name = 'developer'), (SELECT id FROM permissions WHERE name = 'vault_write')),
    ((SELECT id FROM roles WHERE name = 'developer'), (SELECT id FROM permissions WHERE name = 'command_execute')),
    ((SELECT id FROM roles WHERE name = 'developer'), (SELECT id FROM permissions WHERE name = 'command_admin')),
    ((SELECT id FROM roles WHERE name = 'developer'), (SELECT id FROM permissions WHERE name = 'system_settings'));

-- Insert default permission matrix
INSERT OR IGNORE INTO permission_matrix (role_id, resource_type, can_read, can_write, can_delete, can_execute, can_admin) VALUES
    -- Admin permissions
    ((SELECT id FROM roles WHERE name = 'admin'), 'vault', 1, 1, 1, 1, 1),
    ((SELECT id FROM roles WHERE name = 'admin'), 'commands', 1, 1, 1, 1, 1),
    ((SELECT id FROM roles WHERE name = 'admin'), 'system', 1, 1, 1, 1, 1),
    
    -- User permissions
    ((SELECT id FROM roles WHERE name = 'user'), 'vault', 1, 1, 0, 1, 0),
    ((SELECT id FROM roles WHERE name = 'user'), 'commands', 1, 0, 0, 1, 0),
    ((SELECT id FROM roles WHERE name = 'user'), 'system', 1, 0, 0, 0, 0),
    
    -- Guest permissions
    ((SELECT id FROM roles WHERE name = 'guest'), 'vault', 1, 0, 0, 0, 0),
    ((SELECT id FROM roles WHERE name = 'guest'), 'commands', 1, 0, 0, 1, 0),
    ((SELECT id FROM roles WHERE name = 'guest'), 'system', 0, 0, 0, 0, 0),
    
    -- Developer permissions
    ((SELECT id FROM roles WHERE name = 'developer'), 'vault', 1, 1, 1, 1, 0),
    ((SELECT id FROM roles WHERE name = 'developer'), 'commands', 1, 1, 0, 1, 0),
    ((SELECT id FROM roles WHERE name = 'developer'), 'system', 1, 1, 0, 1, 0);
