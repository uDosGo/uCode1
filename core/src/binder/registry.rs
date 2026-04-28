//! Binder registry implementation

use super::Binder;
use std::collections::HashMap;

/// Binder registry for managing multiple binders
#[derive(Debug, Default)]
pub struct BinderRegistry {
    binders: HashMap<String, Binder>,
}

impl BinderRegistry {
    /// Create a new empty registry
    pub fn new() -> Self {
        BinderRegistry {
            binders: HashMap::new(),
        }
    }

    /// Add a binder to the registry
    pub fn add_binder(&mut self, binder: Binder) {
        self.binders.insert(binder.id.clone(), binder);
    }

    /// Get a binder by ID
    pub fn get_binder(&self, id: &str) -> Option<&Binder> {
        self.binders.get(id)
    }

    /// Remove a binder by ID
    pub fn remove_binder(&mut self, id: &str) -> Option<Binder> {
        self.binders.remove(id)
    }

    /// List all binder IDs
    pub fn list_binders(&self) -> Vec<String> {
        self.binders.keys().cloned().collect()
    }

    /// Find binders by tag
    pub fn find_by_tag(&self, tag: &str) -> Vec<&Binder> {
        self.binders
            .values()
            .filter(|binder| binder.tags.contains(&tag.to_string()))
            .collect()
    }

    /// Check if a binder exists
    pub fn contains(&self, id: &str) -> bool {
        self.binders.contains_key(id)
    }

    /// Get the number of binders in the registry
    pub fn count(&self) -> usize {
        self.binders.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::binder::Binder;

    #[test]
    fn test_binder_registry() {
        let mut registry = BinderRegistry::new();
        
        let binder1 = Binder::new("B100-U899", "MainBinder", "1.0.0");
        let binder2 = Binder::new("B101-U900", "SubBinder", "1.0.0");

        // Add binders
        registry.add_binder(binder1.clone());
        registry.add_binder(binder2.clone());

        // Test count
        assert_eq!(registry.count(), 2);

        // Test get
        let retrieved = registry.get_binder("B100-U899").unwrap();
        assert_eq!(retrieved.name, "MainBinder");

        // Test contains
        assert!(registry.contains("B100-U899"));
        assert!(!registry.contains("B999-U999"));

        // Test list
        let ids = registry.list_binders();
        assert!(ids.contains(&"B100-U899".to_string()));
        assert!(ids.contains(&"B101-U900".to_string()));

        // Test remove
        let removed = registry.remove_binder("B100-U899").unwrap();
        assert_eq!(removed.id, "B100-U899");
        assert_eq!(registry.count(), 1);
    }

    #[test]
    fn test_find_by_tag() {
        let mut registry = BinderRegistry::new();
        
        let mut binder1 = Binder::new("B100-U899", "MainBinder", "1.0.0");
        binder1.tags = vec!["primary".to_string(), "main".to_string()];
        
        let mut binder2 = Binder::new("B101-U900", "SubBinder", "1.0.0");
        binder2.tags = vec!["secondary".to_string(), "sub".to_string()];
        
        let mut binder3 = Binder::new("B102-U901", "OtherBinder", "1.0.0");
        binder3.tags = vec!["primary".to_string(), "other".to_string()];

        registry.add_binder(binder1);
        registry.add_binder(binder2);
        registry.add_binder(binder3);

        let primary_binders = registry.find_by_tag("primary");
        assert_eq!(primary_binders.len(), 2);
        let binder_ids: Vec<&str> = primary_binders.iter().map(|b| b.id.as_str()).collect();
        assert!(binder_ids.contains(&"B100-U899"));
        assert!(binder_ids.contains(&"B102-U901"));
    }
}