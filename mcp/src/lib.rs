// MCP Server - Model Context Protocol for uCode1
// Provides local API access to vault for OK agent and other tools

use std::path::PathBuf;
use std::sync::Arc;
use tokio::sync::Mutex;
use serde::{Serialize, Deserialize};
use log::{info, error, debug};
use std::fs;
use std::os::unix::net::{UnixListener, UnixStream};
use std::io::{Write, BufRead, BufReader, BufWriter};
use std::thread;

#[derive(Debug, Serialize, Deserialize)]
pub enum McpRequest {
    ListNotes,
    ReadNote { name: String },
    SearchNotes { query: String },
    ClassifyIntent { text: String },
    Status,
    Ping,
    Shutdown,
}

#[derive(Debug, Serialize, Deserialize)]
pub enum McpResponse {
    Success { data: serde_json::Value },
    Error { message: String },
    Notes { list: Vec<String> },
    NoteContent { name: String, content: String },
    Intent { intent: String, confidence: f32, parameters: std::collections::HashMap<String, String> },
    StatusInfo { version: String, mode: String, vault_path: String },
    Pong,
    Acknowledged,
}

pub struct McpServer {
    socket_path: PathBuf,
    vault: Arc<Mutex<ucode1_vault_bridge::Vault>>,
    ok_agent: Arc<Mutex<ucode1_ok_agent::OkAgent>>,
    running: Arc<Mutex<bool>>,
}

impl McpServer {
    pub fn new(vault_path: &str) -> Self {
        let socket_path = PathBuf::from(vault_path).join(".uds/mcp.sock");
        
        McpServer {
            socket_path,
            vault: Arc::new(Mutex::new(ucode1_vault_bridge::Vault::new(vault_path, vault_path))),
            ok_agent: Arc::new(Mutex::new(ucode1_ok_agent::OkAgent::new())),
            running: Arc::new(Mutex::new(false)),
        }
    }

    pub async fn start(&mut self) -> std::io::Result<()> {
        // Clean up any existing socket
        if self.socket_path.exists() {
            fs::remove_file(&self.socket_path)?;
        }
        
        // Create .uds directory if it doesn't exist
        if let Some(parent) = self.socket_path.parent() {
            fs::create_dir_all(parent)?;
        }
        
        let listener = UnixListener::bind(&self.socket_path)?;
        
        // Set restrictive permissions (owner only)
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            if let Ok(metadata) = fs::metadata(&self.socket_path) {
                let mut permissions = metadata.permissions();
                permissions.set_mode(0o600);
                fs::set_permissions(&self.socket_path, permissions)?;
            }
        }
        
        *self.running.lock().await = true;
        info!("MCP server started on {}", self.socket_path.display());
        
        // Accept connections in a separate thread to avoid blocking
        let running = self.running.clone();
        let vault = self.vault.clone();
        let ok_agent = self.ok_agent.clone();
        
        thread::spawn(move || {
            for stream in listener.incoming() {
                if !*running.blocking_lock() {
                    break;
                }
                
                match stream {
                    Ok(stream) => {
                        let vault = vault.clone();
                        let ok_agent = ok_agent.clone();
                        let running = running.clone();
                        
                        // Handle each connection in a separate thread
                        thread::spawn(move || {
                            if let Err(e) = Self::handle_connection(stream, vault, ok_agent, running) {
                                error!("Connection error: {}", e);
                            }
                        });
                    }
                    Err(e) => {
                        error!("Accept error: {}", e);
                        break;
                    }
                }
            }
        });
        
        Ok(())
    }

    pub async fn stop(&mut self) {
        *self.running.lock().await = false;
        // Remove socket file to force clients to disconnect
        fs::remove_file(&self.socket_path).ok();
        info!("MCP server stopped");
    }

    fn handle_connection(
        stream: UnixStream,
        vault: Arc<Mutex<ucode1_vault_bridge::Vault>>,
        ok_agent: Arc<Mutex<ucode1_ok_agent::OkAgent>>,
        running: Arc<Mutex<bool>>,
    ) -> std::io::Result<()> {
        let mut reader = BufReader::new(stream.try_clone()?);
        let mut writer = BufWriter::new(stream);
        
        let mut buffer = String::new();
        reader.read_line(&mut buffer)?;
        
        if buffer.trim().is_empty() {
            return Ok(());
        }
        
        debug!("Received MCP request: {}", buffer.trim());
        
        let request: McpRequest = match serde_json::from_str(&buffer.trim()) {
            Ok(req) => req,
            Err(e) => {
                error!("Failed to parse request: {}", e);
                let response = McpResponse::Error {
                    message: format!("Invalid request: {}", e),
                };
                let response_str = serde_json::to_string(&response).unwrap() + "\n";
                writer.write_all(response_str.as_bytes())?;
                writer.flush()?;
                return Ok(());
            }
        };
        
        let response = match request {
            McpRequest::ListNotes => {
                let vault = vault.blocking_lock();
                match vault.list_notes() {
                    Ok(notes) => McpResponse::Notes { list: notes },
                    Err(e) => McpResponse::Error { message: e.to_string() },
                }
            }
            McpRequest::ReadNote { name } => {
                let vault = vault.blocking_lock();
                match vault.read_note(&name) {
                    Ok(note) => McpResponse::NoteContent {
                        name: note.title,
                        content: note.content,
                    },
                    Err(e) => McpResponse::Error { message: e.to_string() },
                }
            }
            McpRequest::SearchNotes { query } => {
                let vault = vault.blocking_lock();
                match vault.list_notes() {
                    Ok(notes) => {
                        let results = notes.into_iter()
                            .filter(|n| n.contains(&query))
                            .collect();
                        McpResponse::Notes { list: results }
                    }
                    Err(e) => McpResponse::Error { message: e.to_string() },
                }
            }
            McpRequest::ClassifyIntent { text } => {
                let agent = ok_agent.blocking_lock();
                match agent.classify_intent(&text) {
                    Some(intent) => McpResponse::Intent {
                        intent: intent.name,
                        confidence: intent.confidence,
                        parameters: intent.parameters,
                    },
                    None => McpResponse::Error {
                        message: "No intent detected".to_string(),
                    },
                }
            }
            McpRequest::Status => {
                McpResponse::StatusInfo {
                    version: "0.1.0".to_string(),
                    mode: "user".to_string(),
                    vault_path: ".uds/mcp.sock".to_string(),
                }
            }
            McpRequest::Ping => {
                McpResponse::Success { data: serde_json::json!({"result": "pong"}) }
            }
            McpRequest::Shutdown => {
                *running.blocking_lock() = false;
                McpResponse::Acknowledged
            }
        };
        
        let response_str = serde_json::to_string(&response).unwrap() + "\n";
        writer.write_all(response_str.as_bytes())?;
        writer.flush()?;
        
        Ok(())
    }

    pub fn is_running(&self) -> bool {
        *self.running.blocking_lock()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;
    use std::path::Path;

    #[test]
    fn test_mcp_server_creation() {
        let dir = tempdir().unwrap();
        let vault_path = dir.path().to_str().unwrap();
        
        let server = McpServer::new(vault_path);
        assert!(server.socket_path.ends_with(".uds/mcp.sock"));
    }

    #[test]
    fn test_socket_path() {
        let dir = tempdir().unwrap();
        let vault_path = dir.path().to_str().unwrap();
        
        let server = McpServer::new(vault_path);
        assert!(server.socket_path.ends_with(".uds/mcp.sock"));
    }
}