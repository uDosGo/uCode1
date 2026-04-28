//! Binder system implementation
//!
//! This module provides the core functionality for managing Binders,
//! which are hierarchical data structures in the uDos ecosystem.

pub mod state;
pub mod registry;

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Represents a Binder - a hierarchical data structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Binder {
    /// Unique identifier for the binder
    pub id: String,
    /// Human-readable name
    pub name: String,
    /// Version in semver format
    pub version: String,
    /// Optional emoji representation
    pub emoji: Option<String>,
    /// Optional single character glyph
    pub glyph: Option<String>,
    /// ASCII representation
    pub ascii: Option<String>,
    /// Parent binder ID (if any)
    pub parent: Option<String>,
    /// Child binder IDs
    pub children: Vec<String>,
    /// Key-value data store
    pub data: HashMap<String, serde_json::Value>,
    /// Tags for discovery
    pub tags: Vec<String>,
    /// Lexicon translations
    pub lexicon: Option<BinderLexicon>,
    /// Visual representation
    pub visuals: Option<BinderVisuals>,
    /// Resources (cells, files, etc.)
    pub resources: Option<Vec<BinderResource>>,
}

/// Lexicon translations for a Binder
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BinderLexicon {
    pub terms: Vec<String>,
    pub emoji: Option<String>,
    pub short: String,
    pub long: String,
}

/// Visual representation for a Binder
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BinderVisuals {
    pub ascii: Option<String>,
    pub teletext: Option<String>,
    pub color: Option<String>,
}

/// Resource requirement for a Binder
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BinderResource {
    pub r#type: String, // "cell", "file", "database", etc.
    pub identifier: String, // e.g., "L100-BB45-1010-2" for cells
    pub mode: String, // "read", "write", "read_write"
    pub description: Option<String>,
}

impl Binder {
    /// Create a new Binder instance
    pub fn new(id: &str, name: &str, version: &str) -> Self {
        Binder {
            id: id.to_string(),
            name: name.to_string(),
            version: version.to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            parent: None,
            children: Vec::new(),
            data: HashMap::new(),
            tags: Vec::new(),
            lexicon: None,
            visuals: None,
            resources: None,
        }
    }

    /// Load a Binder from a YAML file
    pub fn load_from_file(path: &std::path::PathBuf) -> Result<Self, Box<dyn std::error::Error>> {
        let content = std::fs::read_to_string(path)?;
        let binder = serde_yaml::from_str(&content)?;
        Ok(binder)
    }

    /// Save a Binder to a YAML file
    pub fn save_to_file(&self, path: &std::path::PathBuf) -> Result<(), Box<dyn std::error::Error>> {
        let content = serde_yaml::to_string(self)?;
        std::fs::write(path, content)?;
        Ok(())
    }

    /// Add a child binder
    pub fn add_child(&mut self, child_id: &str) {
        if !self.children.contains(&child_id.to_string()) {
            self.children.push(child_id.to_string());
        }
    }

    /// Remove a child binder
    pub fn remove_child(&mut self, child_id: &str) {
        self.children.retain(|id| id != child_id);
    }

    /// Set parent binder
    pub fn set_parent(&mut self, parent_id: &str) {
        self.parent = Some(parent_id.to_string());
    }

    /// Clear parent binder
    pub fn clear_parent(&mut self) {
        self.parent = None;
    }

    /// Set data value
    pub fn set_data(&mut self, key: &str, value: serde_json::Value) {
        self.data.insert(key.to_string(), value);
    }

    /// Get data value
    pub fn get_data(&self, key: &str) -> Option<&serde_json::Value> {
        self.data.get(key)
    }

    /// Remove data value
    pub fn remove_data(&mut self, key: &str) -> Option<serde_json::Value> {
        self.data.remove(key)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_binder_creation() {
        let binder = Binder::new("B100-U899", "MainBinder", "1.0.0");
        assert_eq!(binder.id, "B100-U899");
        assert_eq!(binder.name, "MainBinder");
        assert_eq!(binder.version, "1.0.0");
        assert!(binder.parent.is_none());
        assert!(binder.children.is_empty());
        assert!(binder.data.is_empty());
    }

    #[test]
    fn test_binder_hierarchy() {
        let mut binder = Binder::new("B100-U899", "MainBinder", "1.0.0");
        
        // Test adding children
        binder.add_child("B101-U900");
        binder.add_child("B102-U901");
        assert_eq!(binder.children.len(), 2);
        assert!(binder.children.contains(&"B101-U900".to_string()));
        assert!(binder.children.contains(&"B102-U901".to_string()));
        
        // Test removing child
        binder.remove_child("B101-U900");
        assert_eq!(binder.children.len(), 1);
        assert!(!binder.children.contains(&"B101-U900".to_string()));
        
        // Test setting parent
        binder.set_parent("B099-U898");
        assert_eq!(binder.parent, Some("B099-U898".to_string()));
        
        // Test clearing parent
        binder.clear_parent();
        assert!(binder.parent.is_none());
    }

    #[test]
    fn test_binder_data() {
        let mut binder = Binder::new("B100-U899", "MainBinder", "1.0.0");
        
        // Test setting data
        binder.set_data("key1", serde_json::json!("value1"));
        binder.set_data("key2", serde_json::json!(42));
        assert_eq!(binder.data.len(), 2);
        
        // Test getting data
        assert_eq!(binder.get_data("key1"), Some(&serde_json::json!("value1")));
        assert_eq!(binder.get_data("key2"), Some(&serde_json::json!(42)));
        
        // Test removing data
        let removed = binder.remove_data("key1");
        assert_eq!(removed, Some(serde_json::json!("value1")));
        assert_eq!(binder.data.len(), 1);
        assert!(binder.get_data("key1").is_none());
    }

    #[test]
    fn test_binder_serialization() {
        let mut binder = Binder::new("B100-U899", "MainBinder", "1.0.0");
        binder.emoji = Some("📚".to_string());
        binder.tags = vec!["main".to_string(), "primary".to_string()];
        binder.set_data("config", serde_json::json!({"enabled": true}));

        let yaml = serde_yaml::to_string(&binder).unwrap();
        let deserialized: Binder = serde_yaml::from_str(&yaml).unwrap();

        assert_eq!(deserialized.id, "B100-U899");
        assert_eq!(deserialized.emoji, Some("📚".to_string()));
        assert_eq!(deserialized.tags, vec!["main", "primary"]);
        assert_eq!(deserialized.get_data("config"), Some(&serde_json::json!({"enabled": true})));
    }

    #[test]
    fn test_binder_file_operations() {
        let mut binder = Binder::new("B100-U899", "MainBinder", "1.0.0");
        binder.set_data("test", serde_json::json!("data"));
        let path = PathBuf::from("/tmp/test_binder.yaml");

        // Save to file
        binder.save_to_file(&path).unwrap();

        // Load from file
        let loaded = Binder::load_from_file(&path).unwrap();
        assert_eq!(loaded.id, "B100-U899");
        assert_eq!(loaded.get_data("test"), Some(&serde_json::json!("data")));

        // Clean up
        std::fs::remove_file(path).unwrap();
    }
}