// uSystem - Dynamic Command Management System
use rusqlite::{Connection, params, Result as SqliteResult};
use std::path::{Path, PathBuf};

#[derive(Debug, Clone)]
pub struct Command {
    pub id: i64,
    pub name: String,
    pub description: String,
    pub category: Option<String>,
    pub usage: Option<String>,
    pub example: Option<String>,
    pub is_active: bool,
    pub is_dev: bool,
}

#[derive(Debug, Clone)]
pub struct CommandOption {
    pub id: i64,
    pub name: String,
    pub short_name: Option<String>,
    pub description: String,
    pub requires_value: bool,
    pub default_value: Option<String>,
    pub is_required: bool,
}

#[derive(Debug, Clone)]
pub struct Subcommand {
    pub id: i64,
    pub name: String,
    pub description: String,
    pub usage: Option<String>,
    pub example: Option<String>,
}

#[derive(Debug, Clone)]
pub struct GlobalOption {
    pub id: i64,
    pub name: String,
    pub short_name: Option<String>,
    pub description: String,
    pub is_dev: bool,
}

#[derive(Debug, Clone)]
pub struct Documentation {
    pub id: i64,
    pub title: String,
    pub content: String,
    pub category: Option<String>,
    pub format: String,
    pub is_public: bool,
    pub is_dev: bool,
}

#[derive(Debug, Clone)]
pub struct UCodeSchema {
    pub id: i64,
    pub version: String,
    pub description: String,
    pub schema_type: String,
    pub schema_content: String,
    pub is_active: bool,
    pub released_at: Option<String>,
}

#[derive(Debug, Clone)]
pub struct VaultSchema {
    pub id: i64,
    pub version: String,
    pub description: String,
    pub schema_sql: String,
    pub migration_script: Option<String>,
    pub is_active: bool,
    pub released_at: Option<String>,
}

#[derive(Debug, Clone)]
pub struct User {
    pub id: i64,
    pub username: String,
    pub email: Option<String>,
    pub display_name: Option<String>,
    pub is_active: bool,
}

#[derive(Debug, Clone)]
pub struct Role {
    pub id: i64,
    pub name: String,
    pub description: String,
    pub is_system_role: bool,
}

#[derive(Debug, Clone)]
pub struct Permission {
    pub id: i64,
    pub name: String,
    pub description: String,
    pub category: Option<String>,
}

#[derive(Debug, Clone)]
pub struct PermissionMatrixEntry {
    pub id: i64,
    pub role_id: i64,
    pub resource_type: String,
    pub resource_id: Option<String>,
    pub can_read: bool,
    pub can_write: bool,
    pub can_delete: bool,
    pub can_execute: bool,
    pub can_admin: bool,
}

#[derive(Debug, Clone)]
pub struct UserVariable {
    pub id: i64,
    pub user_id: i64,
    pub name: String,
    pub value: String,
    pub scope: String,
    pub is_encrypted: bool,
}

#[derive(Debug, Clone)]
pub struct SystemVariable {
    pub id: i64,
    pub name: String,
    pub value: String,
    pub scope: String,
    pub is_encrypted: bool,
    pub is_readonly: bool,
}

pub struct USystem {
    db_path: PathBuf,
}

impl USystem {
    pub fn new(db_path: &str) -> Self {
        let db_path = PathBuf::from(db_path);
        
        // Ensure parent directory exists
        if let Some(parent) = db_path.parent() {
            std::fs::create_dir_all(parent).expect("Failed to create usystem directory");
        }
        
        USystem { db_path }
    }

    fn connect(&self) -> SqliteResult<Connection> {
        let conn = Connection::open(&self.db_path)?;
        self.initialize_database(&conn)?;
        Ok(conn)
    }

    fn initialize_database(&self, conn: &Connection) -> SqliteResult<()> {
        // Read schema from file
        let schema_path = Path::new("docs/usystem_schema.sql");
        if !schema_path.exists() {
            // Fallback to embedded schema if file not found
            return self.initialize_embedded_database(conn);
        }
        
        let schema = match std::fs::read_to_string(schema_path) {
            Ok(content) => content,
            Err(e) => {
                eprintln!("Warning: Failed to read schema file: {}", e);
                return self.initialize_embedded_database(conn);
            }
        };
        conn.execute_batch(&schema)?;
        
        Ok(())
    }

    fn initialize_embedded_database(&self, conn: &Connection) -> SqliteResult<()> {
        // Create tables
        conn.execute(
            "CREATE TABLE IF NOT EXISTS commands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                category TEXT,
                usage TEXT,
                example TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )",
            [],
        )?;

        conn.execute(
            "CREATE TABLE IF NOT EXISTS command_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_id INTEGER,
                name TEXT NOT NULL,
                short_name TEXT,
                description TEXT,
                requires_value BOOLEAN DEFAULT 0,
                default_value TEXT,
                is_required BOOLEAN DEFAULT 0,
                FOREIGN KEY (command_id) REFERENCES commands(id)
            )",
            [],
        )?;

        conn.execute(
            "CREATE TABLE IF NOT EXISTS subcommands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_id INTEGER,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                usage TEXT,
                example TEXT,
                FOREIGN KEY (command_id) REFERENCES commands(id)
            )",
            [],
        )?;

        conn.execute(
            "CREATE TABLE IF NOT EXISTS subcommand_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subcommand_id INTEGER,
                name TEXT NOT NULL,
                short_name TEXT,
                description TEXT,
                requires_value BOOLEAN DEFAULT 0,
                default_value TEXT,
                is_required BOOLEAN DEFAULT 0,
                FOREIGN KEY (subcommand_id) REFERENCES subcommands(id)
            )",
            [],
        )?;

        conn.execute(
            "CREATE TABLE IF NOT EXISTS global_options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                short_name TEXT,
                description TEXT NOT NULL,
                applies_to_all BOOLEAN DEFAULT 1
            )",
            [],
        )?;

        conn.execute(
            "CREATE TABLE IF NOT EXISTS documentation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                content TEXT NOT NULL,
                category TEXT,
                format TEXT DEFAULT 'markdown',
                is_public BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )",
            [],
        )?;

        // Create indexes
        conn.execute("CREATE INDEX IF NOT EXISTS idx_commands_name ON commands(name)", [])?;
        conn.execute("CREATE INDEX IF NOT EXISTS idx_commands_category ON commands(category)", [])?;
        conn.execute("CREATE INDEX IF NOT EXISTS idx_command_options_command ON command_options(command_id)", [])?;
        conn.execute("CREATE INDEX IF NOT EXISTS idx_subcommands_command ON subcommands(command_id)", [])?;
        conn.execute("CREATE INDEX IF NOT EXISTS idx_subcommand_options_subcommand ON subcommand_options(subcommand_id)", [])?;
        conn.execute("CREATE INDEX IF NOT EXISTS idx_documentation_category ON documentation(category)", [])?;

        // Insert default global options
        let defaults = [
            ("user", None as Option<&str>, "Run in user mode (default)"),
            ("privacy", None, "Run in privacy mode (no telemetry, no network)"),
            ("status", None, "Run in status mode (enables MCP server)"),
            ("dev", None, "Run in development mode"),
            ("debug", None, "Enable debug logging"),
            ("roadmap", None, "Show development roadmap"),
            ("help", Some("h"), "Print help information"),
            ("version", Some("V"), "Print version information"),
        ];

        for (name, short_name, description) in defaults {
            conn.execute(
                "INSERT OR IGNORE INTO global_options (name, short_name, description) VALUES (?1, ?2, ?3)",
                params![name, short_name, description],
            )?;
        }

        Ok(())
    }

    // Command Management
    pub fn add_command(&self, command: &Command) -> SqliteResult<()> {
        let conn = self.connect()?;
        
        conn.execute(
            "INSERT OR REPLACE INTO commands (id, name, description, category, usage, example, is_active, created_at, updated_at) 
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, datetime('now'), datetime('now'))",
            params![
                command.id,
                command.name,
                command.description,
                command.category,
                command.usage,
                command.example,
                command.is_active
            ],
        )?;
        
        Ok(())
    }

    pub fn get_command(&self, name: &str) -> SqliteResult<Option<Command>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, name, description, category, usage, example, is_active, is_dev 
             FROM commands WHERE name = ?1 AND is_active = 1"
        )?;
        
        let mut command_iter = stmt.query_map(params![name], |row| {
            Ok(Command {
                id: row.get(0)?,
                name: row.get(1)?,
                description: row.get(2)?,
                category: row.get(3)?,
                usage: row.get(4)?,
                example: row.get(5)?,
                is_active: row.get(6)?,
                is_dev: row.get(7)?,
            })
        })?;
        
        Ok(command_iter.next().transpose()?)
    }

    pub fn list_commands(&self) -> SqliteResult<Vec<Command>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, name, description, category, usage, example, is_active, is_dev 
             FROM commands WHERE is_active = 1 ORDER BY name"
        )?;
        
        let commands_iter = stmt.query_map([], |row| {
            Ok(Command {
                id: row.get(0)?,
                name: row.get(1)?,
                description: row.get(2)?,
                category: row.get(3)?,
                usage: row.get(4)?,
                example: row.get(5)?,
                is_active: row.get(6)?,
                is_dev: row.get(7)?,
            })
        })?;
        
        commands_iter.collect()
    }

    pub fn list_active_commands(&self) -> SqliteResult<Vec<Command>> {
        self.list_commands()
    }

    // Global Options Management
    pub fn list_global_options(&self) -> SqliteResult<Vec<GlobalOption>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, name, short_name, description, is_dev FROM global_options ORDER BY name"
        )?;
        
        let options_iter = stmt.query_map([], |row| {
            Ok(GlobalOption {
                id: row.get(0)?,
                name: row.get(1)?,
                short_name: row.get(2)?,
                description: row.get(3)?,
                is_dev: row.get(4)?,
            })
        })?;
        
        options_iter.collect()
    }

    // Documentation Management
    pub fn add_documentation(&self, doc: &Documentation) -> SqliteResult<()> {
        let conn = self.connect()?;
        
        conn.execute(
            "INSERT OR REPLACE INTO documentation (id, title, content, category, format, is_public, created_at, updated_at) 
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, datetime('now'), datetime('now'))",
            params![
                doc.id,
                doc.title,
                doc.content,
                doc.category,
                doc.format,
                doc.is_public
            ],
        )?;
        
        Ok(())
    }

    pub fn get_documentation(&self, title: &str) -> SqliteResult<Option<Documentation>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, title, content, category, format, is_public, is_dev 
             FROM documentation WHERE title = ?1 AND is_public = 1"
        )?;
        
        let mut doc_iter = stmt.query_map(params![title], |row| {
            Ok(Documentation {
                id: row.get(0)?,
                title: row.get(1)?,
                content: row.get(2)?,
                category: row.get(3)?,
                format: row.get(4)?,
                is_public: row.get(5)?,
                is_dev: row.get(6)?,
            })
        })?;
        
        Ok(doc_iter.next().transpose()?)
    }

    pub fn generate_help(&self) -> SqliteResult<String> {
        let commands = self.list_active_commands()?;
        let global_options = self.list_global_options()?;
        
        let mut help = String::new();
        help.push_str("uDos Code1 - Next generation uDos platform\n\n");
        help.push_str("Usage: uCode1 [OPTIONS] [COMMAND]\n\n");
        
        // Commands section
        help.push_str("Commands:\n");
        for command in commands {
            help.push_str(&format!("  {:<12} {}\n", command.name, command.description));
        }
        
        // Global options section
        help.push_str("\nOptions:\n");
        for option in global_options {
            if let Some(short_name) = option.short_name {
                help.push_str(&format!("  -{}, --{:<12} {}\n", short_name, option.name, option.description));
            } else {
                help.push_str(&format!("      --{:<12} {}\n", option.name, option.description));
            }
        }
        
        help.push_str("  -h, --help\n\n");
        
        Ok(help)
    }

    pub fn generate_markdown_doc(&self) -> SqliteResult<String> {
        let commands = self.list_active_commands()?;
        let global_options = self.list_global_options()?;
        
        let mut md = String::new();
        md.push_str("# uCode1 Command Reference (Dynamic)\n\n");
        md.push_str("Generated from uSystem database\n\n");
        
        // Table of contents
        md.push_str("## Table of Contents\n\n");
        for command in &commands {
            md.push_str(&format!("- [{}](#{})\n", command.name, command.name.to_lowercase()));
        }
        
        // Commands section
        md.push_str("\n## Commands\n\n");
        for command in commands {
            md.push_str(&format!("### {}\n\n", command.name));
            md.push_str(&format!("**Description:** {}\n\n", command.description));
            
            if let Some(usage) = command.usage {
                md.push_str(&format!("**Usage:** `ucode1 {}`\n\n", usage));
            }
            
            if let Some(example) = command.example {
                md.push_str(&format!("**Example:**\n```bash\n{}\n```\n\n", example));
            }
        }
        
        // Global options section
        md.push_str("## Global Options\n\n");
        md.push_str("| Option | Description |\n");
        md.push_str("|--------|-------------|\n");
        
        for option in global_options {
            if let Some(short_name) = option.short_name {
                md.push_str(&format!("| `-{}` `---{}` | {} |\n", short_name, option.name, option.description));
            } else {
                md.push_str(&format!("| `--{}` | {} |\n", option.name, option.description));
            }
        }
        
        Ok(md)
    }

    // Initialize with default commands
    pub fn initialize_default_commands(&self) -> SqliteResult<()> {
        let conn = self.connect()?;
        
        // Check if commands already exist
        let count: i32 = conn.query_row("SELECT COUNT(*) FROM commands", [], |row| row.get(0))?;
        if count > 0 {
            return Ok(()); // Already initialized
        }
        
        // Insert default commands
        let commands = vec![
            Command {
                id: 0,
                name: "note".to_string(),
                description: "Manage notes in vault".to_string(),
                category: Some("Content Management".to_string()),
                usage: Some("note [subcommand]".to_string()),
                example: Some("ucode1 note list".to_string()),
                is_active: true,
                is_dev: false,
            },
            Command {
                id: 0,
                name: "ok".to_string(),
                description: "OK agent - local intent assistant".to_string(),
                category: Some("AI Assistance".to_string()),
                usage: Some("ok <prompt>".to_string()),
                example: Some("ucode1 ok \"What should I work on?\"".to_string()),
                is_active: true,
                is_dev: false,
            },
            Command {
                id: 0,
                name: "tui".to_string(),
                description: "Launch Terminal User Interface".to_string(),
                category: Some("Interface".to_string()),
                usage: Some("tui".to_string()),
                example: Some("ucode1 tui".to_string()),
                is_active: true,
                is_dev: false,
            },
            Command {
                id: 0,
                name: "map".to_string(),
                description: "Spatial map operations".to_string(),
                category: Some("Spatial".to_string()),
                usage: Some("map [subcommand]".to_string()),
                example: Some("ucode1 map add\n".to_string()),
                is_active: true,
                is_dev: false,
            },
            Command {
                id: 0,
                name: "feed".to_string(),
                description: "RSS/Atom feed operations".to_string(),
                category: Some("Content Management".to_string()),
                usage: Some("feed [subcommand]".to_string()),
                example: Some("ucode1 feed list".to_string()),
                is_active: true,
                is_dev: false,
            },
        ];
        
        for cmd in commands {
            self.add_command(&cmd)?;
        }
        
        Ok(())
    }

    // Schema Management Methods
    pub fn add_ucode_schema(&self, schema: &UCodeSchema) -> SqliteResult<()> {
        let conn = self.connect()?;
        
        conn.execute(
            "INSERT OR REPLACE INTO ucode_schemas (id, version, description, schema_type, schema_content, is_active, released_at, created_at, updated_at) 
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, datetime('now'), datetime('now'))",
            params![
                schema.id,
                schema.version,
                schema.description,
                schema.schema_type,
                schema.schema_content,
                schema.is_active,
                schema.released_at
            ],
        )?;
        
        Ok(())
    }

    pub fn get_ucode_schema(&self, version: &str) -> SqliteResult<Option<UCodeSchema>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, version, description, schema_type, schema_content, is_active, released_at 
             FROM ucode_schemas WHERE version = ?1"
        )?;
        
        let mut schema_iter = stmt.query_map(params![version], |row| {
            Ok(UCodeSchema {
                id: row.get(0)?,
                version: row.get(1)?,
                description: row.get(2)?,
                schema_type: row.get(3)?,
                schema_content: row.get(4)?,
                is_active: row.get(5)?,
                released_at: row.get(6)?,
            })
        })?;
        
        Ok(schema_iter.next().transpose()?)
    }

    pub fn list_ucode_schemas(&self) -> SqliteResult<Vec<UCodeSchema>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, version, description, schema_type, schema_content, is_active, released_at 
             FROM ucode_schemas ORDER BY version DESC"
        )?;
        
        let schemas_iter = stmt.query_map([], |row| {
            Ok(UCodeSchema {
                id: row.get(0)?,
                version: row.get(1)?,
                description: row.get(2)?,
                schema_type: row.get(3)?,
                schema_content: row.get(4)?,
                is_active: row.get(5)?,
                released_at: row.get(6)?,
            })
        })?;
        
        schemas_iter.collect()
    }

    pub fn add_vault_schema(&self, schema: &VaultSchema) -> SqliteResult<()> {
        let conn = self.connect()?;
        
        conn.execute(
            "INSERT OR REPLACE INTO vault_schemas (id, version, description, schema_sql, migration_script, is_active, released_at, created_at, updated_at) 
             VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7, datetime('now'), datetime('now'))",
            params![
                schema.id,
                schema.version,
                schema.description,
                schema.schema_sql,
                schema.migration_script,
                schema.is_active,
                schema.released_at
            ],
        )?;
        
        Ok(())
    }

    pub fn get_vault_schema(&self, version: &str) -> SqliteResult<Option<VaultSchema>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, version, description, schema_sql, migration_script, is_active, released_at 
             FROM vault_schemas WHERE version = ?1"
        )?;
        
        let mut schema_iter = stmt.query_map(params![version], |row| {
            Ok(VaultSchema {
                id: row.get(0)?,
                version: row.get(1)?,
                description: row.get(2)?,
                schema_sql: row.get(3)?,
                migration_script: row.get(4)?,
                is_active: row.get(5)?,
                released_at: row.get(6)?,
            })
        })?;
        
        Ok(schema_iter.next().transpose()?)
    }

    pub fn list_vault_schemas(&self) -> SqliteResult<Vec<VaultSchema>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, version, description, schema_sql, migration_script, is_active, released_at 
             FROM vault_schemas ORDER BY version DESC"
        )?;
        
        let schemas_iter = stmt.query_map([], |row| {
            Ok(VaultSchema {
                id: row.get(0)?,
                version: row.get(1)?,
                description: row.get(2)?,
                schema_sql: row.get(3)?,
                migration_script: row.get(4)?,
                is_active: row.get(5)?,
                released_at: row.get(6)?,
            })
        })?;
        
        schemas_iter.collect()
    }

    // User and Role Management Methods
    pub fn add_user(&self, user: &User) -> SqliteResult<()> {
        let conn = self.connect()?;
        
        conn.execute(
            "INSERT OR REPLACE INTO users (id, username, email, display_name, is_active, created_at, updated_at) 
             VALUES (?1, ?2, ?3, ?4, ?5, datetime('now'), datetime('now'))",
            params![
                user.id,
                user.username,
                user.email,
                user.display_name,
                user.is_active
            ],
        )?;
        
        Ok(())
    }

    pub fn get_user(&self, username: &str) -> SqliteResult<Option<User>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, username, email, display_name, is_active 
             FROM users WHERE username = ?1"
        )?;
        
        let mut user_iter = stmt.query_map(params![username], |row| {
            Ok(User {
                id: row.get(0)?,
                username: row.get(1)?,
                email: row.get(2)?,
                display_name: row.get(3)?,
                is_active: row.get(4)?,
            })
        })?;
        
        Ok(user_iter.next().transpose()?)
    }

    pub fn list_users(&self) -> SqliteResult<Vec<User>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, username, email, display_name, is_active 
             FROM users ORDER BY username"
        )?;
        
        let users_iter = stmt.query_map([], |row| {
            Ok(User {
                id: row.get(0)?,
                username: row.get(1)?,
                email: row.get(2)?,
                display_name: row.get(3)?,
                is_active: row.get(4)?,
            })
        })?;
        
        users_iter.collect()
    }

    pub fn add_role(&self, role: &Role) -> SqliteResult<()> {
        let conn = self.connect()?;
        
        conn.execute(
            "INSERT OR REPLACE INTO roles (id, name, description, is_system_role, created_at, updated_at) 
             VALUES (?1, ?2, ?3, ?4, datetime('now'), datetime('now'))",
            params![
                role.id,
                role.name,
                role.description,
                role.is_system_role
            ],
        )?;
        
        Ok(())
    }

    pub fn get_role(&self, name: &str) -> SqliteResult<Option<Role>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, name, description, is_system_role 
             FROM roles WHERE name = ?1"
        )?;
        
        let mut role_iter = stmt.query_map(params![name], |row| {
            Ok(Role {
                id: row.get(0)?,
                name: row.get(1)?,
                description: row.get(2)?,
                is_system_role: row.get(3)?,
            })
        })?;
        
        Ok(role_iter.next().transpose()?)
    }

    pub fn list_roles(&self) -> SqliteResult<Vec<Role>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, name, description, is_system_role 
             FROM roles ORDER BY name"
        )?;
        
        let roles_iter = stmt.query_map([], |row| {
            Ok(Role {
                id: row.get(0)?,
                name: row.get(1)?,
                description: row.get(2)?,
                is_system_role: row.get(3)?,
            })
        })?;
        
        roles_iter.collect()
    }

    pub fn get_permission_matrix(&self) -> SqliteResult<Vec<PermissionMatrixEntry>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, role_id, resource_type, resource_id, can_read, can_write, can_delete, can_execute, can_admin 
             FROM permission_matrix ORDER BY role_id, resource_type"
        )?;
        
        let matrix_iter = stmt.query_map([], |row| {
            Ok(PermissionMatrixEntry {
                id: row.get(0)?,
                role_id: row.get(1)?,
                resource_type: row.get(2)?,
                resource_id: row.get(3)?,
                can_read: row.get(4)?,
                can_write: row.get(5)?,
                can_delete: row.get(6)?,
                can_execute: row.get(7)?,
                can_admin: row.get(8)?,
            })
        })?;
        
        matrix_iter.collect()
    }

    // System Variable Management
    pub fn get_system_variable(&self, name: &str) -> SqliteResult<Option<SystemVariable>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, name, value, scope, is_encrypted, is_readonly 
             FROM system_variables WHERE name = ?1"
        )?;
        
        let mut var_iter = stmt.query_map(params![name], |row| {
            Ok(SystemVariable {
                id: row.get(0)?,
                name: row.get(1)?,
                value: row.get(2)?,
                scope: row.get(3)?,
                is_encrypted: row.get(4)?,
                is_readonly: row.get(5)?,
            })
        })?;
        
        Ok(var_iter.next().transpose()?)
    }

    pub fn list_system_variables(&self) -> SqliteResult<Vec<SystemVariable>> {
        let conn = self.connect()?;
        
        let mut stmt = conn.prepare(
            "SELECT id, name, value, scope, is_encrypted, is_readonly 
             FROM system_variables ORDER BY name"
        )?;
        
        let vars_iter = stmt.query_map([], |row| {
            Ok(SystemVariable {
                id: row.get(0)?,
                name: row.get(1)?,
                value: row.get(2)?,
                scope: row.get(3)?,
                is_encrypted: row.get(4)?,
                is_readonly: row.get(5)?,
            })
        })?;
        
        vars_iter.collect()
    }

    // Enhanced help generation with schema information
    pub fn generate_extended_help(&self) -> SqliteResult<String> {
        let commands = self.list_active_commands()?;
        let global_options = self.list_global_options()?;
        let ucode_schemas = self.list_ucode_schemas()?;
        let vault_schemas = self.list_vault_schemas()?;
        
        let mut help = String::new();
        help.push_str("uDos Code1 - Next generation uDos platform\n\n");
        help.push_str("Usage: uCode1 [OPTIONS] [COMMAND]\n\n");
        
        // Commands section
        help.push_str("Commands:\n");
        for command in commands {
            if command.is_dev {
                help.push_str(&format!("  {:<12} {} (dev)\n", command.name, command.description));
            } else {
                help.push_str(&format!("  {:<12} {}\n", command.name, command.description));
            }
        }
        
        // Global options section
        help.push_str("\nOptions:\n");
        for option in global_options {
            if option.is_dev {
                if let Some(short_name) = option.short_name {
                    help.push_str(&format!("  -{}, --{:<12} {} (dev)\n", short_name, option.name, option.description));
                } else {
                    help.push_str(&format!("      --{:<12} {} (dev)\n", option.name, option.description));
                }
            } else {
                if let Some(short_name) = option.short_name {
                    help.push_str(&format!("  -{}, --{:<12} {}\n", short_name, option.name, option.description));
                } else {
                    help.push_str(&format!("      --{:<12} {}\n", option.name, option.description));
                }
            }
        }
        
        // Schema information
        if !ucode_schemas.is_empty() {
            help.push_str("\nSchemas:\n");
            help.push_str("  uCode Versions:\n");
            for schema in ucode_schemas {
                help.push_str(&format!("    {:<10} {}\n", schema.version, schema.description));
            }
        }
        
        if !vault_schemas.is_empty() {
            help.push_str("  Vault Versions:\n");
            for schema in vault_schemas {
                help.push_str(&format!("    {:<10} {}\n", schema.version, schema.description));
            }
        }
        
        help.push_str("\n");
        
        Ok(help)
    }

    /// Generate vault documentation template with instructions
    pub fn generate_vault_docs_template(&self) -> SqliteResult<String> {
        let template = r##"# uSystem Documentation in Vault

## Important Notice

**These documents are automatically generated from usystem.db and synced ONE-WAY to your Vault.**

### What This Means:

1. **Read-Only Reference**: These documents are for your reference only
2. **No Reverse Sync**: Modifying these documents will NOT update usystem.db
3. **Regeneration**: Documents can be regenerated at any time from usystem.db
4. **Source of Truth**: The usystem.db database is the authoritative source

## Documentation Sync Process

### How Documents Are Created:

```
usystem.db → uCode1 Vault Sync → Your Vault Documents
                    (one-way)
```

### When Documents Are Updated:

1. **Initial Setup**: When you first initialize uCode1
2. **Version Updates**: When uCode1 is updated to new versions
3. **Manual Sync**: When you run `ucode1 vault sync-docs`

### For Developers:

If you need to modify system documentation:

1. Update the source in `usystem_schema.sql` or Rust code
2. Rebuild uCode1: `cargo build --release`
3. Regenerate documents: `./scripts/generate_docs.sh`
4. Sync to vault: `ucode1 vault sync-docs`

## Document Types in Vault

### 1. Command Reference

Automatically generated from registered commands in usystem.db:
- Command names and descriptions
- Usage examples
- Available options

### 2. Schema Documentation

Versioned schemas for uCode1 components:
- uCode core schemas
- Vault database schemas
- Module schemas

### 3. System Documentation

Reference documentation for:
- Permission matrix
- Role definitions
- System variables

## Working with Vault Documents

### Best Practices:

1. **Don't Modify**: Treat as read-only reference
2. **Create New**: Add your own documents for custom workflows
3. **Version Control**: Use Git to track your custom documents
4. **Backup**: Regularly backup your Vault directory

### Recommended Workflow:

```bash
# 1. Review system documentation
ucode1 docs

# 2. Create your own documentation in Vault
ucode1 note create "My Workflow" "# My Custom Process..."

# 3. Organize with folders/tags
ucode1 note create "Project/Setup" "# Project setup steps..."

# 4. Backup your customizations
git add ~/Code/Vault
```

## Indexing Vault Documents

### Important Note:

**Vault documents are NOT automatically indexed.** This is by design to:

1. **Maintain Control**: You decide what gets indexed
2. **Avoid Clutter**: Only important documents in search
3. **Performance**: Faster searches with curated index

### How to Index Documents:

```bash
# Index a specific document
ucode1 vault index-doc "Document Name"

# Index all documents in a category
ucode1 vault index-category "Getting Started"

# View indexed documents
ucode1 vault list-indexed
```

### Indexing Best Practices:

1. **Curate Carefully**: Only index documents you frequently search
2. **Use Categories**: Group related documents
3. **Review Regularly**: Clean up unused indexed documents
4. **Performance**: Too many indexed docs slow down search

## Roadmap for Documentation Features

### uCode1.1+ Development Plan:

1. **Health Commands** (Priority)
   - `ucode1 vault health-check`
   - `ucode1 vault optimize`
   - `ucode1 vault repair`

2. **Maintenance Commands**
   - `ucode1 vault cleanup`
   - `ucode1 vault defrag`
   - `ucode1 vault backup`

3. **Advanced Indexing**
   - Automatic indexing suggestions
   - Index usage analytics
   - Smart indexing recommendations

4. **Documentation Management**
   - Versioned document history
   - Document change tracking
   - Collaboration features

## Getting Help

### System Documentation:
```bash
# View all commands
ucode1 docs

# Get markdown reference
ucode1 docs --format markdown

# View specific help
ucode1 note --help
```

### Community Resources:
- GitHub Issues: https://github.com/your-repo/uCode1/issues
- Documentation: https://docs.ucode1.example.com
- Community Forum: https://community.ucode1.example.com

## License

This documentation template is part of uCode1 and is released under the MIT License.

---

© 2024 uCode1 Team. All rights reserved.
"##;
        
        Ok(template.to_string())
    }

    /// Populate usystem documentation into Vault
    /// Returns a vector of documents to be created in the vault
    pub fn generate_vault_docs(&self) -> SqliteResult<Vec<(String, String)>> {
        let mut docs = Vec::new();
        
        // 1. Add vault documentation template
        let template = self.generate_vault_docs_template()?;
        docs.push(("USYSTEM_VAULT_DOCS".to_string(), template));
        
        // 2. Add command reference
        let commands = self.list_active_commands()?;
        if !commands.is_empty() {
            let mut md = String::new();
            md.push_str("# Command Reference\n\n");
            md.push_str("Generated from uSystem database\n\n");
            
            for command in commands {
                if command.is_dev {
                    continue; // Skip dev commands for user vault
                }
                
                md.push_str(&format!("## {}\n\n", command.name));
                md.push_str(&format!("{}\n\n", command.description));
                
                if let Some(usage) = command.usage {
                    md.push_str(&format!("**Usage:** `ucode1 {}`\n\n", usage));
                }
                
                if let Some(example) = command.example {
                    md.push_str(&format!("**Example:**\n```bash\n{}\n```\n\n", example));
                }
            }
            
            docs.push(("USYSTEM_COMMANDS".to_string(), md));
        }
        
        // 3. Add schema documentation
        let ucode_schemas = self.list_ucode_schemas()?;
        if !ucode_schemas.is_empty() {
            let mut md = String::new();
            md.push_str("# uCode Schema Versions\n\n");
            md.push_str("Version history of uCode1 components\n\n");
            
            for schema in ucode_schemas {
                md.push_str(&format!("## Version {}\n\n", schema.version));
                md.push_str(&format!("{}\n\n", schema.description));
                md.push_str(&format!("**Type:** {}\n\n", schema.schema_type));
                md.push_str(&format!("**Released:** {}\n\n", schema.released_at.unwrap_or_else(|| "Unknown".to_string())));
            }
            
            docs.push(("USYSTEM_SCHEMAS".to_string(), md));
        }
        
        // 4. Add permission matrix
        let matrix = self.get_permission_matrix()?;
        let roles = self.list_roles()?;
        
        if !matrix.is_empty() && !roles.is_empty() {
            let mut md = String::new();
            md.push_str("# Permission Matrix\n\n");
            md.push_str("Role-based access control for uCode1 resources\n\n");
            
            for role in roles {
                md.push_str(&format!("## {}\n\n", role.name));
                
                let role_matrix: Vec<&PermissionMatrixEntry> = matrix.iter()
                    .filter(|e| e.role_id == role.id)
                    .collect();
                
                if role_matrix.is_empty() {
                    continue;
                }
                
                md.push_str("| Resource Type | Read | Write | Delete | Execute | Admin |\n");
                md.push_str("|---------------|------|-------|--------|---------|-------|\n");
                
                for entry in role_matrix {
                    md.push_str(&format!("| {} | {} | {} | {} | {} | {} |\n",
                        entry.resource_type,
                        if entry.can_read { "✓" } else { "✗" },
                        if entry.can_write { "✓" } else { "✗" },
                        if entry.can_delete { "✓" } else { "✗" },
                        if entry.can_execute { "✓" } else { "✗" },
                        if entry.can_admin { "✓" } else { "✗" }
                    ));
                }
                md.push_str("\n");
            }
            
            docs.push(("USYSTEM_PERMISSIONS".to_string(), md));
        }
        
        Ok(docs)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn test_usystem_initialization() {
        let dir = tempdir().unwrap();
        let db_path = dir.path().join("usystem.db");
        
        let usystem = USystem::new(db_path.to_str().unwrap());
        let conn_result = usystem.connect();
        
        assert!(conn_result.is_ok());
    }

    #[test]
    fn test_add_and_get_command() {
        let dir = tempdir().unwrap();
        let db_path = dir.path().join("usystem.db");
        
        let usystem = USystem::new(db_path.to_str().unwrap());
        
        let test_cmd = Command {
            id: 0,
            name: "test".to_string(),
            description: "Test command".to_string(),
            category: Some("Test".to_string()),
            usage: Some("test".to_string()),
            example: Some("ucode1 test".to_string()),
            is_active: true,
            is_dev: false,
        };
        
        usystem.add_command(&test_cmd).unwrap();
        let retrieved = usystem.get_command("test").unwrap();
        
        assert!(retrieved.is_some());
        assert_eq!(retrieved.unwrap().name, "test");
    }

    #[test]
    fn test_list_commands() {
        let dir = tempdir().unwrap();
        let db_path = dir.path().join("usystem.db");
        
        let usystem = USystem::new(db_path.to_str().unwrap());
        usystem.initialize_default_commands().unwrap();
        
        let commands = usystem.list_commands().unwrap();
        assert!(!commands.is_empty());
        assert!(commands.iter().any(|c| c.name == "note"));
    }

    #[test]
    fn test_generate_help() {
        let dir = tempdir().unwrap();
        let db_path = dir.path().join("usystem.db");
        
        let usystem = USystem::new(db_path.to_str().unwrap());
        usystem.initialize_default_commands().unwrap();
        
        let help_text = usystem.generate_help().unwrap();
        assert!(help_text.contains("uDos Code1"));
        assert!(help_text.contains("note"));
        assert!(help_text.contains("Commands:"));
    }

    #[test]
    fn test_generate_markdown() {
        let dir = tempdir().unwrap();
        let db_path = dir.path().join("usystem.db");
        
        let usystem = USystem::new(db_path.to_str().unwrap());
        usystem.initialize_default_commands().unwrap();
        
        let md = usystem.generate_markdown_doc().unwrap();
        assert!(md.contains("# uCode1 Command Reference"));
        assert!(md.contains("## Commands"));
        assert!(md.contains("## Global Options"));
    }
}
