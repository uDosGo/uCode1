//! Snack module for uDos
//!
//! This module provides the core functionality for managing and executing Snacks,
//! which are atomic executable units in the uDos ecosystem.

pub mod schema;
pub mod validator;

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Represents a Snack - an atomic executable unit
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Snack {
    /// Unique identifier for the snack
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
    /// Type of snack (script, skill, spark, wasm, snackbox)
    pub kind: String,
    /// Runtime environment
    pub runtime: String,
    /// The executable code
    pub code: String,
    /// Dependencies (other snack IDs)
    pub requires: Vec<String>,
    /// Input schema
    pub inputs: Vec<SnackInput>,
    /// Output schema
    pub outputs: Vec<SnackOutput>,
    /// Tags for discovery
    pub tags: Vec<String>,
    /// Lexicon translations
    pub lexicon: Option<SnackLexicon>,
    /// Visual representation
    pub visuals: Option<SnackVisuals>,
    /// Chaining rules
    pub chain: Option<SnackChain>,
    /// Resources (cells, files, etc.)
    pub resources: Option<Vec<SnackResource>>,
}

/// Input parameter for a Snack
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnackInput {
    pub name: String,
    pub r#type: String,
    pub default: Option<serde_json::Value>,
    pub required: bool,
}

/// Output parameter for a Snack
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnackOutput {
    pub name: String,
    pub r#type: String,
}

/// Lexicon translations for a Snack
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnackLexicon {
    pub terms: Vec<String>,
    pub emoji: Option<String>,
    pub short: String,
    pub long: String,
}

/// Visual representation for a Snack
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnackVisuals {
    pub ascii: Option<String>,
    pub teletext: Option<String>,
    pub color: Option<String>,
}

/// Chaining rules for a Snack
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnackChain {
    pub can_be_before: Vec<String>,
    pub can_be_after: Vec<String>,
    pub can_be_parallel: bool,
}

/// Resource requirement for a Snack
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnackResource {
    pub r#type: String, // "cell", "file", "database", etc.
    pub identifier: String, // e.g., "L100-BB45-1010-2" for cells
    pub mode: String, // "read", "write", "read_write"
    pub description: Option<String>,
}

impl Snack {
    /// Create a new Snack instance
    pub fn new(id: &str, name: &str, version: &str, code: &str) -> Self {
        Snack {
            id: id.to_string(),
            name: name.to_string(),
            version: version.to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "script".to_string(),
            runtime: "bash".to_string(),
            code: code.to_string(),
            requires: Vec::new(),
            inputs: Vec::new(),
            outputs: Vec::new(),
            tags: Vec::new(),
            lexicon: None,
            visuals: None,
            chain: None,
            resources: None,
        }
    }

    /// Load a Snack from a YAML file
    pub fn load_from_file(path: &PathBuf) -> Result<Self, Box<dyn std::error::Error>> {
        let content = std::fs::read_to_string(path)?;
        let snack = serde_yaml::from_str(&content)?;
        Ok(snack)
    }

    /// Save a Snack to a YAML file
    pub fn save_to_file(&self, path: &PathBuf) -> Result<(), Box<dyn std::error::Error>> {
        let content = serde_yaml::to_string(self)?;
        std::fs::write(path, content)?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_snack_creation() {
        let snack = Snack::new("P100-U899", "Postie", "1.0.0", "echo 'Hello'");
        assert_eq!(snack.id, "P100-U899");
        assert_eq!(snack.name, "Postie");
        assert_eq!(snack.version, "1.0.0");
        assert_eq!(snack.code, "echo 'Hello'");
    }

    #[test]
    fn test_snack_serialization() {
        let mut snack = Snack::new("P100-U899", "Postie", "1.0.0", "echo 'Hello'");
        snack.emoji = Some("📬".to_string());
        snack.tags = vec!["email".to_string(), "ingest".to_string()];

        let yaml = serde_yaml::to_string(&snack).unwrap();
        let deserialized: Snack = serde_yaml::from_str(&yaml).unwrap();

        assert_eq!(deserialized.id, "P100-U899");
        assert_eq!(deserialized.emoji, Some("📬".to_string()));
        assert_eq!(deserialized.tags, vec!["email", "ingest"]);
    }

    #[test]
    fn test_snack_file_operations() {
        let snack = Snack::new("P100-U899", "Postie", "1.0.0", "echo 'Hello'");
        let path = PathBuf::from("/tmp/test_snack.yaml");

        // Save to file
        snack.save_to_file(&path).unwrap();

        // Load from file
        let loaded = Snack::load_from_file(&path).unwrap();
        assert_eq!(loaded.id, "P100-U899");

        // Clean up
        std::fs::remove_file(path).unwrap();
    }
}
