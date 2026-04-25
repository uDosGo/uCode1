# SQLite Vault Implementation for uCode1

This document describes the SQLite-based vault implementation for uCode1, which aligns with the Marksmith indexing system for cross-tool compatibility.

## Overview

The implementation uses SQLite (via the `rusqlite` crate) to manage vault contents with the following key features:

- **Workspaces (Spaces)**: Top-level vaults/workspaces
- **Documents & Folders**: Hierarchical document management
- **Version History**: Full document revision history
- **Soft Delete**: Trash/restore functionality
- **Metadata Indexing**: Links, media, and other metadata

## Database Schema

### 1. `space` Table - Workspaces (Vaults)

```sql
CREATE TABLE IF NOT EXISTS space (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    writeFolderPath TEXT NOT NULL,
    sort INTEGER DEFAULT 0,
    opt TEXT
)
```

- `id`: UUID primary key
- `name`: Workspace name (e.g., "Main Vault")
- `writeFolderPath`: Absolute filesystem path for document sync
- `sort`: Ordering in UI
- `opt`: JSON blob for future options

### 2. `doc` Table - Documents & Folders

```sql
CREATE TABLE IF NOT EXISTS doc (
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
)
```

- `id`: UUID primary key
- `name`: Document or folder name
- `spaceId`: Foreign key to `space.id`
- `parentId`: Foreign key to `doc.id` (NULL for root)
- `folder`: `1` = folder, `0` = document
- `schema`: Document content (Markdown/plain text)
- `links`: JSON array of outgoing wikilinks/tags
- `medias`: JSON array of attached media paths
- `sort`: Order within parent folder
- `deleted`: `1` = soft-deleted, `0` = active

### 3. `history` Table - Version History

```sql
CREATE TABLE IF NOT EXISTS history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    docId TEXT NOT NULL,
    schema TEXT NOT NULL,
    created TEXT NOT NULL,
    FOREIGN KEY (docId) REFERENCES doc(id)
)
```

- `id`: Auto-increment primary key
- `docId`: Foreign key to `doc.id`
- `schema`: Snapshot of document content
- `created`: ISO timestamp of snapshot

## Indexes

The following indexes are created for performance:

- `idx_doc_space`: On `doc(spaceId)`
- `idx_doc_parent`: On `doc(parentId)`
- `idx_doc_deleted`: On `doc(deleted)`
- `idx_history_doc`: On `history(docId)`

## Key Features Implemented

### 1. Space Management

```rust
// Create a new workspace
let space = vault.create_default_space("Main Vault", "/tmp/vault")?;

// Retrieve a space
let space = vault.get_space(&space_id)?;
```

### 2. Document Management

```rust
// Create a document
let doc = vault.create_document(&space_id, "My Doc", "# Content", None, false)?;

// Retrieve a document
let doc = vault.get_document(&doc_id)?;

// Update a document
vault.update_document(&doc_id, "# Updated Content")?;

// List documents in a space
let docs = vault.list_documents(&space_id, None)?;

// List documents in a folder
let docs = vault.list_documents(&space_id, Some(&folder_id))?;
```

### 3. Soft Delete & Restore

```rust
// Soft delete a document
vault.soft_delete_document(&doc_id)?;

// Restore a document
vault.restore_document(&doc_id)?;
```

### 4. Version History

```rust
// Get document history
let history = vault.get_document_history(&doc_id)?;
```

## Backward Compatibility

The implementation maintains backward compatibility with the original filesystem-based approach:

- `notes_dir()`: Returns the notes directory path
- `list_notes()`: Lists notes using filesystem
- `read_note()`: Reads notes with frontmatter parsing
- `create_note()`: Creates notes on filesystem
- `note_exists()`: Checks if a note exists

## Usage Example

See `examples/basic_usage.rs` for a complete example demonstrating:

1. Creating a workspace
2. Creating documents
3. Listing documents
4. Updating documents
5. Version history
6. Soft delete and restore

## Testing

Run tests with:

```bash
cargo test --package ucode1-vault-bridge
```

Run the example:

```bash
cargo run --example basic_usage --package ucode1-vault-bridge
```

## Database Location

The database is stored at the path specified when creating the `Vault` instance. For cross-tool compatibility with Marksmith, it's recommended to use:

- **Default location**: `~/.uCode1/vault-index.db`
- **Environment-configurable**: Allow override via environment variables

## Future Enhancements

1. **Filesystem Synchronization**: Automatic monitoring and syncing of filesystem changes
2. **Link & Media Parsing**: Automatic extraction and indexing of links and media from document content
3. **Full-Text Search**: Add FTS5 virtual tables for advanced search
4. **Encryption**: Support for encrypted vaults
5. **Multi-process Safety**: Enhanced locking and retry mechanisms

## Integration with uDos & Marksmith

Both tools can operate on the same vault by:

1. Using the same SQLite database file
2. Respecting the same `writeFolderPath`
3. Using WAL mode for concurrent access
4. Implementing proper error handling for `SQLITE_BUSY`

## Dependencies

- `rusqlite`: SQLite bindings for Rust
- `uuid`: UUID generation
- `chrono`: Timestamp handling
- `serde`: Serialization support

## Performance Considerations

- Batch operations for bulk inserts/updates
- Use prepared statements for repeated queries
- Indexes on frequently queried columns
- WAL mode for better concurrency
