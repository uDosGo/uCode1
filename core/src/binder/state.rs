//! Binder state management

use super::Binder;
use std::collections::HashMap;

/// Binder state manager
#[derive(Debug, Default)]
pub struct BinderState {
    binders: HashMap<String, Binder>,
    hierarchy_cache: HashMap<String, Vec<String>>, // Cache for hierarchy lookups
}

impl BinderState {
    /// Create a new state manager
    pub fn new() -> Self {
        BinderState {
            binders: HashMap::new(),
            hierarchy_cache: HashMap::new(),
        }
    }

    /// Add a binder to the state
    pub fn add_binder(&mut self, binder: Binder) {
        self.binders.insert(binder.id.clone(), binder);
        self.hierarchy_cache.clear(); // Invalidate cache
    }

    /// Get a binder by ID
    pub fn get_binder(&self, id: &str) -> Option<&Binder> {
        self.binders.get(id)
    }

    /// Remove a binder by ID
    pub fn remove_binder(&mut self, id: &str) -> Option<Binder> {
        self.hierarchy_cache.clear(); // Invalidate cache
        self.binders.remove(id)
    }

    /// Get all binder IDs
    pub fn list_binders(&self) -> Vec<String> {
        self.binders.keys().cloned().collect()
    }

    /// Get the hierarchy for a binder (cached)
    pub fn get_hierarchy(&mut self, id: &str) -> Vec<String> {
        if let Some(cached) = self.hierarchy_cache.get(id) {
            return cached.clone();
        }

        let mut hierarchy = Vec::new();
        let mut current_id = id;

        while let Some(binder) = self.binders.get(current_id) {
            hierarchy.push(binder.id.clone());
            if let Some(parent_id) = &binder.parent {
                current_id = parent_id;
            } else {
                break;
            }
        }

        self.hierarchy_cache.insert(id.to_string(), hierarchy.clone());
        hierarchy
    }

    /// Get all children of a binder (recursive)
    pub fn get_children_recursive(&self, id: &str) -> Vec<String> {
        let mut children = Vec::new();
        let mut stack = vec![id.to_string()];

        while let Some(current_id) = stack.pop() {
            if let Some(binder) = self.binders.get(&current_id) {
                for child_id in &binder.children {
                    if !children.contains(child_id) {
                        children.push(child_id.clone());
                        stack.push(child_id.clone());
                    }
                }
            }
        }

        children
    }

    /// Find binders by tag
    pub fn find_by_tag(&self, tag: &str) -> Vec<&Binder> {
        self.binders
            .values()
            .filter(|binder| binder.tags.contains(&tag.to_string()))
            .collect()
    }

    /// Clear all binders
    pub fn clear(&mut self) {
        self.binders.clear();
        self.hierarchy_cache.clear();
    }

    /// Get count of binders
    pub fn count(&self) -> usize {
        self.binders.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::binder::Binder;

    #[test]
    fn test_binder_state_basic() {
        let mut state = BinderState::new();
        
        let binder1 = Binder::new("B100-U899", "MainBinder", "1.0.0");
        let binder2 = Binder::new("B101-U900", "SubBinder", "1.0.0");

        // Add binders
        state.add_binder(binder1.clone());
        state.add_binder(binder2.clone());

        // Test count
        assert_eq!(state.count(), 2);

        // Test get
        let retrieved = state.get_binder("B100-U899").unwrap();
        assert_eq!(retrieved.name, "MainBinder");

        // Test list
        let ids = state.list_binders();
        assert!(ids.contains(&"B100-U899".to_string()));
        assert!(ids.contains(&"B101-U900".to_string()));

        // Test remove
        let removed = state.remove_binder("B100-U899").unwrap();
        assert_eq!(removed.id, "B100-U899");
        assert_eq!(state.count(), 1);
    }

    #[test]
    fn test_binder_hierarchy() {
        let mut state = BinderState::new();
        
        let mut binder1 = Binder::new("B100-U899", "RootBinder", "1.0.0");
        let mut binder2 = Binder::new("B101-U900", "ChildBinder", "1.0.0");
        let mut binder3 = Binder::new("B102-U901", "GrandchildBinder", "1.0.0");
        
        binder2.set_parent("B100-U899");
        binder3.set_parent("B101-U900");
        
        state.add_binder(binder1);
        state.add_binder(binder2);
        state.add_binder(binder3);

        // Test hierarchy
        let hierarchy = state.get_hierarchy("B102-U901");
        assert_eq!(hierarchy.len(), 3);
        assert_eq!(hierarchy[0], "B102-U901");
        assert_eq!(hierarchy[1], "B101-U900");
        assert_eq!(hierarchy[2], "B100-U899");
    }

    #[test]
    fn test_binder_children_recursive() {
        let mut state = BinderState::new();
        
        let mut binder1 = Binder::new("B100-U899", "RootBinder", "1.0.0");
        let mut binder2 = Binder::new("B101-U900", "ChildBinder", "1.0.0");
        let mut binder3 = Binder::new("B102-U901", "GrandchildBinder", "1.0.0");
        
        binder1.add_child("B101-U900");
        binder2.add_child("B102-U901");
        
        state.add_binder(binder1);
        state.add_binder(binder2);
        state.add_binder(binder3);

        // Test recursive children
        let children = state.get_children_recursive("B100-U899");
        assert_eq!(children.len(), 2);
        assert!(children.contains(&"B101-U900".to_string()));
        assert!(children.contains(&"B102-U901".to_string()));
    }

    #[test]
    fn test_find_by_tag() {
        let mut state = BinderState::new();
        
        let mut binder1 = Binder::new("B100-U899", "MainBinder", "1.0.0");
        binder1.tags = vec!["primary".to_string(), "main".to_string()];
        
        let mut binder2 = Binder::new("B101-U900", "SubBinder", "1.0.0");
        binder2.tags = vec!["secondary".to_string(), "sub".to_string()];
        
        let mut binder3 = Binder::new("B102-U901", "OtherBinder", "1.0.0");
        binder3.tags = vec!["primary".to_string(), "other".to_string()];
        
        state.add_binder(binder1);
        state.add_binder(binder2);
        state.add_binder(binder3);

        let primary_binders = state.find_by_tag("primary");
        assert_eq!(primary_binders.len(), 2);
        let binder_ids: Vec<&str> = primary_binders.iter().map(|b| b.id.as_str()).collect();
        assert!(binder_ids.contains(&"B100-U899"));
        assert!(binder_ids.contains(&"B102-U901"));
    }
}