//! Relic system implementation
//!
//! This module provides the core functionality for managing and executing Relics,
//! which are binary executable units in the uDos ecosystem.

pub mod binary;
pub mod registry;
pub mod validator;
pub mod schema;

use serde::{Deserialize, Serialize};
use std::path::PathBuf;

/// Represents a Relic - a binary executable unit
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Relic {
    /// Unique identifier for the relic
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
    /// Type of relic (binary, archive, container)
    pub kind: String,
    /// Platform target
    pub platform: String,
    /// Architecture target
    pub arch: String,
    /// The binary data (base64 encoded)
    pub data: String,
    /// Dependencies (other relic IDs)
    pub requires: Vec<String>,
    /// Input schema
    pub inputs: Vec<RelicInput>,
    /// Output schema
    pub outputs: Vec<RelicOutput>,
    /// Tags for discovery
    pub tags: Vec<String>,
    /// Lexicon translations
    pub lexicon: Option<RelicLexicon>,
    /// Visual representation
    pub visuals: Option<RelicVisuals>,
    /// Resources (cells, files, etc.)
    pub resources: Option<Vec<RelicResource>>,
}

/// Input parameter for a Relic
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RelicInput {
    pub name: String,
    pub r#type: String,
    pub default: Option<serde_json::Value>,
    pub required: bool,
}

/// Output parameter for a Relic
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RelicOutput {
    pub name: String,
    pub r#type: String,
}

/// Lexicon translations for a Relic
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RelicLexicon {
    pub terms: Vec<String>,
    pub emoji: Option<String>,
    pub short: String,
    pub long: String,
}

/// Visual representation for a Relic
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RelicVisuals {
    pub ascii: Option<String>,
    pub teletext: Option<String>,
    pub color: Option<String>,
}

/// Resource requirement for a Relic
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RelicResource {
    pub r#type: String, // "cell", "file", "database", etc.
    pub identifier: String, // e.g., "L100-BB45-1010-2" for cells
    pub mode: String, // "read", "write", "read_write"
    pub description: Option<String>,
}

impl Relic {
    /// Create a new Relic instance
    pub fn new(id: &str, name: &str, version: &str, data: &str) -> Self {
        Relic {
            id: id.to_string(),
            name: name.to_string(),
            version: version.to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "unknown".to_string(),
            arch: "unknown".to_string(),
            data: data.to_string(),
            requires: Vec::new(),
            inputs: Vec::new(),
            outputs: Vec::new(),
            tags: Vec::new(),
            lexicon: None,
            visuals: None,
            resources: None,
        }
    }

    /// Load a Relic from a YAML file
    pub fn load_from_file(path: &PathBuf) -> Result<Self, Box<dyn std::error::Error>> {
        let content = std::fs::read_to_string(path)?;
        let relic = serde_yaml::from_str(&content)?;
        Ok(relic)
    }

    /// Save a Relic to a YAML file
    pub fn save_to_file(&self, path: &PathBuf) -> Result<(), Box<dyn std::error::Error>> {
        let content = serde_yaml::to_string(self)?;
        std::fs::write(path, content)?;
        Ok(())
    }

    /// Extract binary data to a file
    pub fn extract_binary(&self, output_path: &PathBuf) -> Result<(), Box<dyn std::error::Error>> {
        use base64::{engine::general_purpose, Engine as _};
        let decoded = general_purpose::STANDARD.decode(&self.data)?;
        std::fs::write(output_path, decoded)?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_relic_creation() {
        let relic = Relic::new("R100-U899", "Runner", "1.0.0", "base64encoded");
        assert_eq!(relic.id, "R100-U899");
        assert_eq!(relic.name, "Runner");
        assert_eq!(relic.version, "1.0.0");
        assert_eq!(relic.data, "base64encoded");
    }

    #[test]
    fn test_relic_serialization() {
        let mut relic = Relic::new("R100-U899", "Runner", "1.0.0", "base64encoded");
        relic.emoji = Some("🏃".to_string());
        relic.tags = vec!["runner".to_string(), "execute".to_string()];

        let yaml = serde_yaml::to_string(&relic).unwrap();
        let deserialized: Relic = serde_yaml::from_str(&yaml).unwrap();

        assert_eq!(deserialized.id, "R100-U899");
        assert_eq!(deserialized.emoji, Some("🏃".to_string()));
        assert_eq!(deserialized.tags, vec!["runner", "execute"]);
    }

    #[test]
    fn test_relic_file_operations() {
        let relic = Relic::new("R100-U899", "Runner", "1.0.0", "base64encoded");
        let path = PathBuf::from("/tmp/test_relic.yaml");

        // Save to file
        relic.save_to_file(&path).unwrap();

        // Load from file
        let loaded = Relic::load_from_file(&path).unwrap();
        assert_eq!(loaded.id, "R100-U899");

        // Clean up
        std::fs::remove_file(path).unwrap();
    }
}