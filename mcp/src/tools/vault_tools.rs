//! Vault tools for MCP server
//!
//! Provides read/write/search capabilities for the user's vault

use serde::{Serialize, Deserialize};
use serde_json::{json, Value};
use std::path::{PathBuf, Path};
use std::fs;
use std::env;
use chrono::{DateTime, Local};

/// Get vault root path from environment or default
fn get_vault_root() -> PathBuf {
    env::var("UDOS_VAULT")
        .map(PathBuf::from)
        .unwrap_or_else(|_| {
            let home = env::var("HOME").unwrap_or_else(|_| "/Users/fredbook".to_string());
            PathBuf::from(format!("{}/vault", home))
        })
}

/// Ensure path is within vault root (security check)
fn secure_path(vault_root: &Path, path: &Path) -> Result<PathBuf, String> {
    let full_path = vault_root.join(path);
    let canonical_path = full_path.canonicalize()
        .map_err(|e| format!("Failed to canonicalize path: {}", e))?;
    
    // Ensure the path is within vault root
    if !canonical_path.starts_with(vault_root) {
        return Err("Path outside vault root".to_string());
    }
    
    Ok(canonical_path)
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultReadInput {
    pub path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultReadOutput {
    pub content: String,
    pub path: String,
}

pub fn vault_read(input: VaultReadInput) -> Result<VaultReadOutput, String> {
    let vault_root = get_vault_root();
    let path = Path::new(&input.path);
    let full_path = secure_path(&vault_root, path)?;
    
    let content = fs::read_to_string(&full_path)
        .map_err(|e| format!("Failed to read file: {}", e))?;
    
    Ok(VaultReadOutput {
        content,
        path: input.path,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultWriteInput {
    pub path: String,
    pub content: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultWriteOutput {
    pub success: bool,
    pub path: String,
}

pub fn vault_write(input: VaultWriteInput) -> Result<VaultWriteOutput, String> {
    let vault_root = get_vault_root();
    let path = Path::new(&input.path);
    let full_path = secure_path(&vault_root, path)?;
    
    // Create parent directories if needed
    if let Some(parent) = full_path.parent() {
        fs::create_dir_all(parent)
            .map_err(|e| format!("Failed to create directories: {}", e))?;
    }
    
    fs::write(&full_path, input.content)
        .map_err(|e| format!("Failed to write file: {}", e))?;
    
    Ok(VaultWriteOutput {
        success: true,
        path: input.path,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultListInput {
    pub path: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultListOutput {
    pub items: Vec<VaultItem>,
    pub path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultItem {
    pub name: String,
    pub is_directory: bool,
    pub size: Option<u64>,
    pub modified: Option<String>,
}

pub fn vault_list(input: VaultListInput) -> Result<VaultListOutput, String> {
    let vault_root = get_vault_root();
    let path = input.path.as_deref().unwrap_or("");
    let full_path = secure_path(&vault_root, Path::new(path))?;
    
    let mut items = Vec::new();
    
    if full_path.is_dir() {
        let entries = fs::read_dir(&full_path)
            .map_err(|e| format!("Failed to read directory: {}", e))?;
        
        for entry in entries {
            let entry = entry.map_err(|e| format!("Failed to read directory entry: {}", e))?;
            let metadata = entry.metadata().map_err(|e| format!("Failed to read metadata: {}", e))?;
            
            let modified = metadata.modified().ok()
                .map(|t: std::time::SystemTime| {
                    let datetime: DateTime<Local> = t.into();
                    datetime.format("%Y-%m-%d %H:%M:%S").to_string()
                });
            
            items.push(VaultItem {
                name: entry.file_name().to_string_lossy().into_owned(),
                is_directory: metadata.is_dir(),
                size: Some(metadata.len()),
                modified,
            });
        }
    }
    
    Ok(VaultListOutput {
        items,
        path: full_path.to_string_lossy().into_owned(),
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultSearchInput {
    pub query: String,
    pub path: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultSearchOutput {
    pub results: Vec<VaultSearchResult>,
    pub count: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultSearchResult {
    pub path: String,
    pub name: String,
    pub score: f32,
    pub preview: String,
}

pub fn vault_search(input: VaultSearchInput) -> Result<VaultSearchOutput, String> {
    let vault_root = get_vault_root();
    let search_path = input.path.as_deref().unwrap_or("");
    let full_path = secure_path(&vault_root, Path::new(search_path))?;
    
    let mut results = Vec::new();
    
    if full_path.is_dir() {
        // Simple keyword search - walk directory and match filenames/content
        let query_lower = input.query.to_lowercase();
        
        let entries = fs::read_dir(&full_path)
            .map_err(|e| format!("Failed to read directory: {}", e))?;
        
        for entry in entries {
            let entry = entry.map_err(|e| format!("Failed to read directory entry: {}", e))?;
            let path = entry.path();
            let name = entry.file_name().to_string_lossy().into_owned();
            
            // Check if name matches query
            if name.to_lowercase().contains(&query_lower) {
                let preview = if path.is_file() {
                    match fs::read_to_string(&path) {
                        Ok(content) => content.lines().next().unwrap_or("").to_string(),
                        Err(_) => String::new(),
                    }
                } else {
                    String::new()
                };
                
                results.push(VaultSearchResult {
                    path: path.to_string_lossy().into_owned(),
                    name,
                    score: 1.0, // Simple match
                    preview,
                });
            }
        }
    }
    
    let count = results.len();
    Ok(VaultSearchOutput {
        results,
        count,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultDeleteInput {
    pub path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultDeleteOutput {
    pub success: bool,
    pub path: String,
}

pub fn vault_delete(input: VaultDeleteInput) -> Result<VaultDeleteOutput, String> {
    let vault_root = get_vault_root();
    let path = Path::new(&input.path);
    let full_path = secure_path(&vault_root, path)?;
    
    // Move to trash instead of permanent delete
    let trash_path = vault_root.join(".trash").join(
        full_path.file_name().unwrap_or(std::ffi::OsStr::new("deleted_file"))
    );
    
    // Create trash directory if needed
    fs::create_dir_all(trash_path.parent().unwrap())
        .map_err(|e| format!("Failed to create trash directory: {}", e))?;
    
    fs::rename(&full_path, &trash_path)
        .map_err(|e| format!("Failed to move to trash: {}", e))?;
    
    Ok(VaultDeleteOutput {
        success: true,
        path: input.path,
    })
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultMetadataInput {
    pub path: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VaultMetadataOutput {
    pub path: String,
    pub exists: bool,
    pub is_directory: bool,
    pub size: Option<u64>,
    pub created: Option<String>,
    pub modified: Option<String>,
    pub tags: Vec<String>,
}

pub fn vault_metadata(input: VaultMetadataInput) -> Result<VaultMetadataOutput, String> {
    let vault_root = get_vault_root();
    let path = Path::new(&input.path);
    let full_path = secure_path(&vault_root, path)?;
    
    let metadata = fs::metadata(&full_path).ok();
    
    let created = metadata.as_ref().and_then(|m| m.created().ok())
        .map(|t: std::time::SystemTime| {
            let datetime: DateTime<Local> = t.into();
            datetime.format("%Y-%m-%d %H:%M:%S").to_string()
        });
    
    let modified = metadata.as_ref().and_then(|m| m.modified().ok())
        .map(|t: std::time::SystemTime| {
            let datetime: DateTime<Local> = t.into();
            datetime.format("%Y-%m-%d %H:%M:%S").to_string()
        });
    
    // Try to read tags from a .tags file or similar
    let tags = Vec::new(); // TODO: Implement tag reading
    
    Ok(VaultMetadataOutput {
        path: input.path,
        exists: metadata.is_some(),
        is_directory: metadata.as_ref().map(|m| m.is_dir()).unwrap_or(false),
        size: metadata.as_ref().map(|m| m.len()),
        created,
        modified,
        tags,
    })
}
