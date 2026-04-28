//! Relic registry implementation

use super::Relic;
use std::collections::HashMap;

/// Relic registry for managing multiple relics
#[derive(Debug, Default)]
pub struct RelicRegistry {
    relics: HashMap<String, Relic>,
}

impl RelicRegistry {
    /// Create a new empty registry
    pub fn new() -> Self {
        RelicRegistry {
            relics: HashMap::new(),
        }
    }

    /// Add a relic to the registry
    pub fn add_relic(&mut self, relic: Relic) {
        self.relics.insert(relic.id.clone(), relic);
    }

    /// Get a relic by ID
    pub fn get_relic(&self, id: &str) -> Option<&Relic> {
        self.relics.get(id)
    }

    /// Remove a relic by ID
    pub fn remove_relic(&mut self, id: &str) -> Option<Relic> {
        self.relics.remove(id)
    }

    /// List all relic IDs
    pub fn list_relics(&self) -> Vec<String> {
        self.relics.keys().cloned().collect()
    }

    /// Find relics by tag
    pub fn find_by_tag(&self, tag: &str) -> Vec<&Relic> {
        self.relics
            .values()
            .filter(|relic| relic.tags.contains(&tag.to_string()))
            .collect()
    }

    /// Check if a relic exists
    pub fn contains(&self, id: &str) -> bool {
        self.relics.contains_key(id)
    }

    /// Get the number of relics in the registry
    pub fn count(&self) -> usize {
        self.relics.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::relic::Relic;

    #[test]
    fn test_relic_registry() {
        let mut registry = RelicRegistry::new();
        
        let relic1 = Relic::new("R100-U899", "Runner", "1.0.0", "data1");
        let relic2 = Relic::new("R101-U900", "Builder", "1.0.0", "data2");

        // Add relics
        registry.add_relic(relic1.clone());
        registry.add_relic(relic2.clone());

        // Test count
        assert_eq!(registry.count(), 2);

        // Test get
        let retrieved = registry.get_relic("R100-U899").unwrap();
        assert_eq!(retrieved.name, "Runner");

        // Test contains
        assert!(registry.contains("R100-U899"));
        assert!(!registry.contains("R999-U999"));

        // Test list
        let ids = registry.list_relics();
        assert!(ids.contains(&"R100-U899".to_string()));
        assert!(ids.contains(&"R101-U900".to_string()));

        // Test remove
        let removed = registry.remove_relic("R100-U899").unwrap();
        assert_eq!(removed.id, "R100-U899");
        assert_eq!(registry.count(), 1);
    }

    #[test]
    fn test_find_by_tag() {
        let mut registry = RelicRegistry::new();
        
        let mut relic1 = Relic::new("R100-U899", "Runner", "1.0.0", "data1");
        relic1.tags = vec!["execution".to_string(), "fast".to_string()];
        
        let mut relic2 = Relic::new("R101-U900", "Builder", "1.0.0", "data2");
        relic2.tags = vec!["build".to_string(), "slow".to_string()];
        
        let mut relic3 = Relic::new("R102-U901", "Compiler", "1.0.0", "data3");
        relic3.tags = vec!["execution".to_string(), "build".to_string()];

        registry.add_relic(relic1);
        registry.add_relic(relic2);
        registry.add_relic(relic3);

        let execution_relics = registry.find_by_tag("execution");
        assert_eq!(execution_relics.len(), 2);
        let relic_ids: Vec<&str> = execution_relics.iter().map(|r| r.id.as_str()).collect();
        assert!(relic_ids.contains(&"R100-U899"));
        assert!(relic_ids.contains(&"R102-U901"));
    }
}