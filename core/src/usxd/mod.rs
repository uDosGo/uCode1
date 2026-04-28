//! USXD (Universal Spatial eXchange Format) implementation
//!
//! This module provides the core functionality for managing USXD documents,
//! which are ASCII-based spatial data formats in the uDos ecosystem.

pub mod parser;
pub mod grid;

use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use std::collections::HashMap;

/// Represents a USXD document
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UsxdDocument {
    /// Document version
    pub version: String,
    /// Document title
    pub title: String,
    /// Document description
    pub description: Option<String>,
    /// Grid dimensions (rows, cols)
    pub dimensions: (usize, usize),
    /// Grid data (2D vector of cells)
    pub grid: Vec<Vec<UsxdCell>>,
    /// Metadata
    pub metadata: HashMap<String, String>,
    /// Components mapping
    pub components: HashMap<String, UsxdComponent>,
}

/// USXD cell representation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UsxdCell {
    /// Character representation
    pub char: char,
    /// Foreground color (ANSI color code)
    pub fg_color: Option<String>,
    /// Background color (ANSI color code)
    pub bg_color: Option<String>,
    /// Component ID (if this cell is part of a component)
    pub component_id: Option<String>,
    /// Cell metadata
    pub metadata: HashMap<String, String>,
}

/// USXD component definition
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UsxdComponent {
    /// Component ID
    pub id: String,
    /// Component name
    pub name: String,
    /// Component type
    pub r#type: String,
    /// Component properties
    pub properties: HashMap<String, serde_json::Value>,
    /// Component cells (relative coordinates)
    pub cells: Vec<(usize, usize)>,
}

impl UsxdDocument {
    /// Create a new USXD document
    pub fn new(title: &str, rows: usize, cols: usize) -> Self {
        let mut grid = Vec::with_capacity(rows);
        for _ in 0..rows {
            let row = vec![UsxdCell::default(); cols];
            grid.push(row);
        }

        UsxdDocument {
            version: "1.0".to_string(),
            title: title.to_string(),
            description: None,
            dimensions: (rows, cols),
            grid,
            metadata: HashMap::new(),
            components: HashMap::new(),
        }
    }

    /// Load a USXD document from a YAML file
    pub fn load_from_file(path: &PathBuf) -> Result<Self, Box<dyn std::error::Error>> {
        let content = std::fs::read_to_string(path)?;
        let doc = serde_yaml::from_str(&content)?;
        Ok(doc)
    }

    /// Save a USXD document to a YAML file
    pub fn save_to_file(&self, path: &PathBuf) -> Result<(), Box<dyn std::error::Error>> {
        let content = serde_yaml::to_string(self)?;
        std::fs::write(path, content)?;
        Ok(())
    }

    /// Get cell at position
    pub fn get_cell(&self, row: usize, col: usize) -> Option<&UsxdCell> {
        self.grid.get(row).and_then(|r| r.get(col))
    }

    /// Set cell at position
    pub fn set_cell(&mut self, row: usize, col: usize, cell: UsxdCell) -> Result<(), String> {
        if row >= self.dimensions.0 || col >= self.dimensions.1 {
            return Err(format!("Position ({}, {}) out of bounds", row, col));
        }
        self.grid[row][col] = cell;
        Ok(())
    }

    /// Add a component
    pub fn add_component(&mut self, component: UsxdComponent) {
        self.components.insert(component.id.clone(), component);
    }

    /// Get a component by ID
    pub fn get_component(&self, id: &str) -> Option<&UsxdComponent> {
        self.components.get(id)
    }

    /// Remove a component by ID
    pub fn remove_component(&mut self, id: &str) -> Option<UsxdComponent> {
        self.components.remove(id)
    }
}

impl Default for UsxdCell {
    fn default() -> Self {
        UsxdCell {
            char: ' ',
            fg_color: None,
            bg_color: None,
            component_id: None,
            metadata: HashMap::new(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::path::PathBuf;

    #[test]
    fn test_usxd_creation() {
        let doc = UsxdDocument::new("Test Grid", 10, 20);
        assert_eq!(doc.title, "Test Grid");
        assert_eq!(doc.dimensions, (10, 20));
        assert_eq!(doc.grid.len(), 10);
        assert_eq!(doc.grid[0].len(), 20);
    }

    #[test]
    fn test_usxd_cell_operations() {
        let mut doc = UsxdDocument::new("Test Grid", 5, 5);
        
        // Test setting cell
        let mut cell = UsxdCell::default();
        cell.char = 'A';
        cell.fg_color = Some("red".to_string());
        doc.set_cell(2, 3, cell).unwrap();
        
        // Test getting cell
        let retrieved = doc.get_cell(2, 3).unwrap();
        assert_eq!(retrieved.char, 'A');
        assert_eq!(retrieved.fg_color, Some("red".to_string()));
    }

    #[test]
    fn test_usxd_component_operations() {
        let mut doc = UsxdDocument::new("Test Grid", 5, 5);
        
        // Test adding component
        let component = UsxdComponent {
            id: "comp1".to_string(),
            name: "TestComponent".to_string(),
            r#type: "widget".to_string(),
            properties: HashMap::new(),
            cells: vec![(0, 0), (1, 1)],
        };
        doc.add_component(component);
        
        // Test getting component
        let retrieved = doc.get_component("comp1").unwrap();
        assert_eq!(retrieved.name, "TestComponent");
        
        // Test removing component
        let removed = doc.remove_component("comp1").unwrap();
        assert_eq!(removed.id, "comp1");
        assert!(doc.get_component("comp1").is_none());
    }

    #[test]
    fn test_usxd_serialization() {
        let mut doc = UsxdDocument::new("Test Grid", 3, 3);
        doc.description = Some("A test grid".to_string());
        doc.metadata.insert("author".to_string(), "test".to_string());
        
        let mut cell = UsxdCell::default();
        cell.char = 'X';
        doc.set_cell(1, 1, cell).unwrap();

        let yaml = serde_yaml::to_string(&doc).unwrap();
        let deserialized: UsxdDocument = serde_yaml::from_str(&yaml).unwrap();

        assert_eq!(deserialized.title, "Test Grid");
        assert_eq!(deserialized.description, Some("A test grid".to_string()));
        assert_eq!(deserialized.get_cell(1, 1).unwrap().char, 'X');
    }

    #[test]
    fn test_usxd_file_operations() {
        let mut doc = UsxdDocument::new("Test Grid", 2, 2);
        let mut cell = UsxdCell::default();
        cell.char = 'T';
        doc.set_cell(0, 0, cell).unwrap();
        
        let path = PathBuf::from("/tmp/test_usxd.yaml");

        // Save to file
        doc.save_to_file(&path).unwrap();

        // Load from file
        let loaded = UsxdDocument::load_from_file(&path).unwrap();
        assert_eq!(loaded.title, "Test Grid");
        assert_eq!(loaded.get_cell(0, 0).unwrap().char, 'T');

        // Clean up
        std::fs::remove_file(path).unwrap();
    }
}