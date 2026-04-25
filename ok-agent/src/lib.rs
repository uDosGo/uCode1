// OK Agent - Minimal local intent classifier for uCode1
// This is the PRODUCT version - simple, privacy-friendly, no external dependencies

use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct Intent {
    pub name: String,
    pub confidence: f32,
    pub parameters: HashMap<String, String>,
}

pub struct OkAgent {
    // Simple rule-based intent mapping
    intent_rules: HashMap<String, Vec<String>>,
}

impl OkAgent {
    pub fn new() -> Self {
        let mut agent = OkAgent {
            intent_rules: HashMap::new(),
        };
        
        // Basic intent rules
        agent.add_intent_rule("create_note", vec!["create", "new", "make", "add"]);
        agent.add_intent_rule("list_notes", vec!["list", "show", "display", "view"]);
        agent.add_intent_rule("search_notes", vec!["search", "find", "lookup"]);
        agent.add_intent_rule("help", vec!["help", "?", "info", "manual"]);
        
        agent
    }

    pub fn add_intent_rule(&mut self, intent_name: &str, keywords: Vec<&str>) {
        self.intent_rules.insert(
            intent_name.to_string(),
            keywords.iter().map(|s| s.to_lowercase()).collect(),
        );
    }

    /// Classify user intent from text
    pub fn classify_intent(&self, text: &str) -> Option<Intent> {
        let lower_text = text.to_lowercase();
        let words: Vec<&str> = lower_text.split_whitespace().collect();
        
        // Simple keyword matching
        for (intent_name, keywords) in &self.intent_rules {
            for keyword in keywords {
                if words.contains(&keyword.as_str()) {
                    // Extract parameters (simple implementation)
                    let mut parameters = HashMap::new();
                    
                    // Look for "create X" or "new X" patterns
                    if intent_name == "create_note" && words.len() > 1 {
                        if let Some(pos) = words.iter().position(|w| *w == "create" || *w == "new") {
                            if pos + 1 < words.len() {
                                parameters.insert("name".to_string(), words[pos + 1].to_string());
                            }
                        }
                    }
                    
                    return Some(Intent {
                        name: intent_name.clone(),
                        confidence: 0.8, // Simple rules have medium confidence
                        parameters,
                    });
                }
            }
        }
        
        None
    }

    /// Simple response based on intent
    pub fn generate_response(&self, intent: &Intent) -> String {
        match intent.name.as_str() {
            "create_note" => {
                if let Some(name) = intent.parameters.get("name") {
                    format!("I can help you create a note called '{}'. Would you like to proceed?", name)
                } else {
                    "I can help you create a new note. What would you like to call it?".to_string()
                }
            }
            "list_notes" => "I can show you your notes. Would you like to see all notes?".to_string(),
            "search_notes" => "I can search your notes. What are you looking for?".to_string(),
            "help" => "I'm the OK agent. I can help with notes, search, and basic tasks.".to_string(),
            _ => "I'm not sure how to help with that yet.".to_string(),
        }
    }

    /// Privacy-friendly mode check
    pub fn is_privacy_safe(&self) -> bool {
        true // This agent runs locally and doesn't send any data
    }
}

impl Default for OkAgent {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_create_note_intent() {
        let agent = OkAgent::new();
        let result = agent.classify_intent("create test note");
        assert!(result.is_some());
        let intent = result.unwrap();
        assert_eq!(intent.name, "create_note");
        assert_eq!(intent.parameters.get("name").unwrap(), "test");
    }

    #[test]
    fn test_list_notes_intent() {
        let agent = OkAgent::new();
        let result = agent.classify_intent("show my notes");
        assert!(result.is_some());
        let intent = result.unwrap();
        assert_eq!(intent.name, "list_notes");
    }

    #[test]
    fn test_unknown_intent() {
        let agent = OkAgent::new();
        let result = agent.classify_intent("do something random");
        assert!(result.is_none());
    }

    #[test]
    fn test_privacy_safe() {
        let agent = OkAgent::new();
        assert!(agent.is_privacy_safe());
    }
}