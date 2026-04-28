//! Stub implementation for plugin_list
//!
//! This is a placeholder implementation. Full functionality will be implemented
//! based on the uDos specifications.

use serde::{Serialize, Deserialize};
use serde_json::{json, Value};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginListInput {
    // Empty for now
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginListOutput {
    pub plugins: Vec<PluginInfo>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PluginInfo {
    pub id: String,
    pub name: String,
    pub version: String,
    pub enabled: bool,
}

pub fn plugin_list(_input: Value) -> Result<Value, String> {
    // Stub implementation
    Ok(json!({
        "plugins": [
            {"id": "teletext", "name": "Teletext Renderer", "version": "1.0.0", "enabled": true},
            {"id": "vault", "name": "Vault Bridge", "version": "1.0.0", "enabled": true},
            {"id": "spatial", "name": "Spatial Index", "version": "1.0.0", "enabled": true}
        ]
    }))
}
