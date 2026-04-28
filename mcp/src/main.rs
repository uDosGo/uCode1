//! MCP Server Binary
//! 
//! This is the main entry point for running the uCode1 MCP server as a standalone binary.
//! The server provides Unix socket-based access to vault operations for MCP-compatible clients.

use std::env;
use log::{info, error};
use ucode1_mcp::McpServer;

#[tokio::main]
async fn main() {
    env_logger::init();
    
    // Default vault path is ~/vault
    let vault_path = match env::var("VAULT_PATH") {
        Ok(path) => path,
        Err(_) => {
            match env::var("HOME") {
                Ok(home) => format!("{}/vault", home),
                Err(_) => {
                    error!("Unable to determine home directory, using current directory");
                    ".".to_string()
                }
            }
        }
    };
    
    info!("Starting uCode1 MCP Server");
    info!("Vault path: {}", vault_path);
    
    let mut server = McpServer::new(&vault_path);
    
    match server.start().await {
        Ok(_) => {
            info!("MCP server started successfully");
            // Keep server running
            tokio::signal::ctrl_c().await.expect("Failed to install Ctrl+C handler");
            info!("Shutting down MCP server...");
            server.stop().await;
        }
        Err(e) => {
            error!("Failed to start MCP server: {}", e);
            std::process::exit(1);
        }
    }
}
