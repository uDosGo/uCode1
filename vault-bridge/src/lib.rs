// Vault Bridge - SQLite-based vault management
use std::fs;
use std::path::PathBuf;
use std::io;
use rusqlite::{Connection, params, Result as SqliteResult};
use uuid::Uuid;
use serde::{Serialize, Deserialize};

mod schema;
pub use schema::*;

#[derive(Debug, Serialize, Deserialize)]
pub struct Note {
    pub title: String,
    pub content: String,
    pub tags: Vec<String>,
    pub created_at: String,
    pub updated_at: String,
}

pub struct Vault {
    db_path: PathBuf,
    base_path: PathBuf,
}

impl Vault {
    pub fn new(db_path: &str, base_path: &str) -> Self {
        let db_path = PathBuf::from(db_path);
        let base_path = PathBuf::from(base_path);
        
        // Ensure base directory exists
        if !base_path.exists() {
            fs::create_dir_all(&base_path).expect("Failed to create base directory");
        }
        
        Vault {
            db_path,
            base_path,
        }
    }

    fn connect(&self) -> SqliteResult<Connection> {
        let conn = Connection::open(&self.db_path)?;
        self.initialize_database(&conn)?;
        Ok(conn)
    }

    fn initialize_database(&self, conn: &Connection) -> SqliteResult<()> {
        // Create tables if they don't exist
        conn.execute(
            "CREATE TABLE IF NOT EXISTS space (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                writeFolderPath TEXT NOT NULL,
                sort INTEGER DEFAULT 0,
                opt TEXT
            )",
            [],
        )?;

        conn.execute(
            "CREATE TABLE IF NOT EXISTS doc (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                spaceId TEXT NOT NULL,
                parentId TEXT,
                folder INTEGER DEFAULT 0,
                schema TEXT,
                links TEXT,
                medias TEXT,
                sort INTEGER DEFAULT 0,
                deleted INTEGER DEFAULT 0,
                FOREIGN KEY (spaceId) REFERENCES space(id),
                FOREIGN KEY (parentId) REFERENCES doc(id)
            )",
            [],
        )?;

        conn.execute(
            "CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                docId TEXT NOT NULL,
                schema TEXT NOT NULL,
                created TEXT NOT NULL,
                FOREIGN KEY (docId) REFERENCES doc(id)
            )",
            [],
        )?;

        // Create indexes for performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_space ON doc(spaceId)", [])?;
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_parent ON doc(parentId)", [])?;
        conn.execute("CREATE INDEX IF NOT EXISTS idx_doc_deleted ON doc(deleted)", [])?;
        conn.execute("CREATE INDEX IF NOT EXISTS idx_history_doc ON history(docId)", [])?;

        Ok(())
    }

    pub fn create_default_space(&self, name: &str, write_folder_path: &str) -> SqliteResult<Space> {
        let conn = self.connect()?;
        let space_id = Uuid::new_v4().to_string();
        
        conn.execute(
            "INSERT INTO space (id, name, writeFolderPath, sort) VALUES (?1, ?2, ?3, 0)",
            params![space_id, name, write_folder_path],
        )?;
        
        Ok(Space {
            id: space_id,
            name: name.to_string(),
            write_folder_path: write_folder_path.to_string(),
            sort: 0,
            opt: None,
        })
    }

    pub fn get_space(&mut self, space_id: &str) -> SqliteResult<Option<Space>> {
        let conn = self.connect()?;
        let mut stmt = conn.prepare("SELECT id, name, writeFolderPath, sort, opt FROM space WHERE id = ?1")?;
        
        let mut space_iter = stmt.query_map(params![space_id], |row| {
            Ok(Space {
                id: row.get(0)?,
                name: row.get(1)?,
                write_folder_path: row.get(2)?,
                sort: row.get(3)?,
                opt: row.get(4)?,
            })
        })?;
        
        Ok(space_iter.next().transpose()?)
    }

    pub fn create_document(&mut self, space_id: &str, name: &str, content: &str, parent_id: Option<&str>, is_folder: bool) -> SqliteResult<Doc> {
        let conn = self.connect()?;
        let doc_id = Uuid::new_v4().to_string();
        let now = chrono::Utc::now().to_rfc3339();
        
        conn.execute(
            "INSERT INTO doc (id, name, spaceId, parentId, folder, schema, sort, deleted) VALUES (?1, ?2, ?3, ?4, ?5, ?6, 0, 0)",
            params![doc_id, name, space_id, parent_id, if is_folder { 1 } else { 0 }, content],
        )?;
        
        // Create initial history entry
        conn.execute(
            "INSERT INTO history (docId, schema, created) VALUES (?1, ?2, ?3)",
            params![doc_id, content, now],
        )?;
        
        Ok(Doc {
            id: doc_id,
            name: name.to_string(),
            space_id: space_id.to_string(),
            parent_id: parent_id.map(|s| s.to_string()),
            folder: is_folder,
            schema: content.to_string(),
            links: None,
            medias: None,
            sort: 0,
            deleted: false,
        })
    }

    pub fn get_document(&mut self, doc_id: &str) -> SqliteResult<Option<Doc>> {
        let conn = self.connect()?;
        let mut stmt = conn.prepare(
            "SELECT id, name, spaceId, parentId, folder, schema, links, medias, sort, deleted FROM doc WHERE id = ?1 AND deleted = 0"
        )?;
        
        let mut doc_iter = stmt.query_map(params![doc_id], |row| {
            let folder_val: i32 = row.get(4)?;
            let deleted_val: i32 = row.get(9)?;
            Ok(Doc {
                id: row.get(0)?,
                name: row.get(1)?,
                space_id: row.get(2)?,
                parent_id: row.get(3)?,
                folder: folder_val != 0,
                schema: row.get(5)?,
                links: row.get(6)?,
                medias: row.get(7)?,
                sort: row.get(8)?,
                deleted: deleted_val != 0,
            })
        })?;
        
        Ok(doc_iter.next().transpose()?)
    }

    pub fn update_document(&mut self, doc_id: &str, content: &str) -> SqliteResult<()> {
        let conn = self.connect()?;
        let now = chrono::Utc::now().to_rfc3339();
        
        // Update document content
        conn.execute(
            "UPDATE doc SET schema = ?1 WHERE id = ?2",
            params![content, doc_id],
        )?;
        
        // Add to history
        conn.execute(
            "INSERT INTO history (docId, schema, created) VALUES (?1, ?2, ?3)",
            params![doc_id, content, now],
        )?;
        
        Ok(())
    }

    pub fn list_documents(&mut self, space_id: &str, parent_id: Option<&str>) -> SqliteResult<Vec<Doc>> {
        let conn = self.connect()?;
        
        let query = if let Some(_parent) = parent_id {
            "SELECT id, name, spaceId, parentId, folder, schema, links, medias, sort, deleted \n             FROM doc \n             WHERE spaceId = ?1 AND parentId = ?2 AND deleted = 0 \n             ORDER BY folder DESC, sort ASC"
        } else {
            "SELECT id, name, spaceId, parentId, folder, schema, links, medias, sort, deleted \n             FROM doc \n             WHERE spaceId = ?1 AND parentId IS NULL AND deleted = 0 \n             ORDER BY folder DESC, sort ASC"
        };
        
        let mut stmt = conn.prepare(query)?;
        
        // Define a helper function to map rows to Docs
        fn map_doc_row(row: &rusqlite::Row) -> SqliteResult<Doc> {
            let folder_val: i32 = row.get(4)?;
            let deleted_val: i32 = row.get(9)?;
            Ok(Doc {
                id: row.get(0)?,
                name: row.get(1)?,
                space_id: row.get(2)?,
                parent_id: row.get(3)?,
                folder: folder_val != 0,
                schema: row.get(5)?,
                links: row.get(6)?,
                medias: row.get(7)?,
                sort: row.get(8)?,
                deleted: deleted_val != 0,
            })
        }
        
        let docs_iter = if let Some(parent) = parent_id {
            stmt.query_map(params![space_id, parent], map_doc_row)?
        } else {
            stmt.query_map(params![space_id], map_doc_row)?
        };
        
        docs_iter.collect()
    }

    pub fn soft_delete_document(&mut self, doc_id: &str) -> SqliteResult<()> {
        let conn = self.connect()?;
        conn.execute(
            "UPDATE doc SET deleted = 1 WHERE id = ?1",
            params![doc_id],
        )?;
        Ok(())
    }

    pub fn restore_document(&mut self, doc_id: &str) -> SqliteResult<()> {
        let conn = self.connect()?;
        conn.execute(
            "UPDATE doc SET deleted = 0 WHERE id = ?1",
            params![doc_id],
        )?;
        Ok(())
    }

    pub fn get_document_history(&mut self, doc_id: &str) -> SqliteResult<Vec<History>> {
        let conn = self.connect()?;
        let mut stmt = conn.prepare(
            "SELECT id, docId, schema, created FROM history WHERE docId = ?1 ORDER BY created DESC"
        )?;
        
        let history_iter = stmt.query_map(params![doc_id], |row| {
            Ok(History {
                id: row.get(0)?,
                doc_id: row.get(1)?,
                schema: row.get(2)?,
                created: row.get(3)?,
            })
        })?;
        
        history_iter.collect()
    }

    // Backward compatibility methods
    pub fn notes_dir(&self) -> PathBuf {
        self.base_path.join("notes")
    }

    pub fn list_notes(&self) -> io::Result<Vec<String>> {
        // This is a simplified version for backward compatibility
        // In a real implementation, you'd query the database for documents
        let notes_dir = self.notes_dir();
        
        if !notes_dir.exists() {
            fs::create_dir_all(&notes_dir)?;
            return Ok(Vec::new());
        }
        
        let mut notes = Vec::new();
        for entry in fs::read_dir(notes_dir)? {
            let entry = entry?;
            let path = entry.path();
            
            if path.is_file() && path.extension().map_or(false, |ext| ext == "md") {
                if let Some(name) = path.file_stem() {
                    notes.push(name.to_string_lossy().into_owned());
                }
            }
        }
        
        Ok(notes)
    }

    pub fn read_note(&self, name: &str) -> io::Result<Note> {
        let note_path = self.notes_dir().join(format!("{}.md", name));
        
        if !note_path.exists() {
            return Err(io::Error::new(io::ErrorKind::NotFound, "Note not found"));
        }
        
        let content = fs::read_to_string(&note_path)?;
        
        // Parse frontmatter (simple implementation for now)
        let (frontmatter, content_body) = parse_frontmatter(&content);
        
        Ok(Note {
            title: name.to_string(),
            content: content_body,
            tags: frontmatter.get("tags").cloned().unwrap_or_default(),
            created_at: frontmatter.get("created").and_then(|v| v.first().cloned()).unwrap_or_else(|| "unknown".to_string()),
            updated_at: frontmatter.get("updated").and_then(|v| v.first().cloned()).unwrap_or_else(|| "unknown".to_string()),
        })
    }

    pub fn create_note(&self, name: &str, content: &str) -> io::Result<()> {
        let notes_dir = self.notes_dir();
        fs::create_dir_all(&notes_dir)?;
        
        let note_path = notes_dir.join(format!("{}.md", name));
        fs::write(note_path, content)?;
        
        Ok(())
    }

    pub fn note_exists(&self, name: &str) -> bool {
        let note_path = self.notes_dir().join(format!("{}.md", name));
        note_path.exists()
    }
}

fn parse_frontmatter(content: &str) -> (std::collections::HashMap<String, Vec<String>>, String) {
    use std::collections::HashMap;
    
    let mut frontmatter: HashMap<String, Vec<String>> = HashMap::new();
    let mut lines = content.lines().peekable();
    
    // Check if content starts with frontmatter delimiter
    if lines.peek().map_or(false, |line| line.trim() == "---") {
        lines.next(); // Consume the first ---
        
        // Parse frontmatter until we hit another ---
        let mut current_key = None;
        
        for line in lines.by_ref() {
            if line.trim() == "---" {
                break;
            }
            
            if line.starts_with(|c: char| c.is_whitespace()) {
                // Continuation of previous value
                if let Some(key) = &current_key {
                    if let Some(values) = frontmatter.get_mut(key) {
                        if let Some(last) = values.last_mut() {
                            last.push_str(" ");
                            last.push_str(line.trim());
                        }
                    }
                }
            } else if let Some((key, value)) = line.split_once(':') {
                current_key = Some(key.trim().to_string());
                let value = value.trim().to_string();
                frontmatter.entry(key.trim().to_string())
                    .or_insert_with(Vec::new)
                    .push(value);
            }
        }
    }
    
    let body = lines.collect::<Vec<_>>().join("\n");
    (frontmatter, body)
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;

    #[test]
    fn test_create_space() {
        let dir = tempdir().unwrap();
        let db_path = dir.path().join("test.db");
        let base_path = dir.path().to_str().unwrap();
        
        let mut vault = Vault::new(db_path.to_str().unwrap(), base_path);
        let space = vault.create_default_space("Main Vault", "/tmp/vault").unwrap();
        
        assert_eq!(space.name, "Main Vault");
        assert_eq!(space.write_folder_path, "/tmp/vault");
    }

    #[test]
    fn test_create_and_get_document() {
        let dir = tempdir().unwrap();
        let db_path = dir.path().join("test.db");
        let base_path = dir.path().to_str().unwrap();
        
        let mut vault = Vault::new(db_path.to_str().unwrap(), base_path);
        let space = vault.create_default_space("Test Space", "/tmp/test").unwrap();
        
        let doc = vault.create_document(&space.id, "Test Doc", "# Content", None, false).unwrap();
        assert_eq!(doc.name, "Test Doc");
        
        let retrieved = vault.get_document(&doc.id).unwrap();
        assert!(retrieved.is_some());
        assert_eq!(retrieved.unwrap().name, "Test Doc");
    }

    #[test]
    fn test_list_documents() {
        let dir = tempdir().unwrap();
        let db_path = dir.path().join("test.db");
        let base_path = dir.path().to_str().unwrap();
        
        let mut vault = Vault::new(db_path.to_str().unwrap(), base_path);
        let space = vault.create_default_space("Test Space", "/tmp/test").unwrap();
        
        vault.create_document(&space.id, "Doc 1", "Content 1", None, false).unwrap();
        vault.create_document(&space.id, "Doc 2", "Content 2", None, false).unwrap();
        
        let docs = vault.list_documents(&space.id, None).unwrap();
        assert_eq!(docs.len(), 2);
    }

    #[test]
    fn test_list_notes_empty() {
        let dir = tempdir().unwrap();
        let mut vault = Vault::new(dir.path().join("test.db").to_str().unwrap(), dir.path().to_str().unwrap());
        let notes = vault.list_notes().unwrap();
        assert_eq!(notes.len(), 0);
    }

    #[test]
    fn test_create_and_read_note() {
        let dir = tempdir().unwrap();
        let mut vault = Vault::new(dir.path().join("test.db").to_str().unwrap(), dir.path().to_str().unwrap());
        
        let content = "# Test Note\n\nThis is a test.";
        vault.create_note("test", content).unwrap();
        
        let notes = vault.list_notes().unwrap();
        assert_eq!(notes.len(), 1);
        assert_eq!(notes[0], "test");
        
        let note = vault.read_note("test").unwrap();
        assert_eq!(note.title, "test");
        assert!(note.content.contains("Test Note"));
    }

    #[test]
    fn test_parse_frontmatter() {
        let content = "---\ntitle: My Note\ntags: [rust, programming]\n---\n\n# Content here";
        let (frontmatter, body) = parse_frontmatter(content);
        
        assert_eq!(frontmatter.get("title").unwrap()[0], "My Note");
        assert!(body.contains("Content here"));
    }
}
