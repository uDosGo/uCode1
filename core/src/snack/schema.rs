//! Snack schema definitions and validation

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Snack schema definition
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnackSchema {
    pub id: String,
    pub name: String,
    pub version: String,
    pub kind: String,
    pub runtime: String,
    pub code: String,
    pub requires: Vec<String>,
    pub inputs: Vec<SnackInputSchema>,
    pub outputs: Vec<SnackOutputSchema>,
    pub tags: Vec<String>,
}

/// Input schema for a Snack
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnackInputSchema {
    pub name: String,
    pub r#type: String,
    pub default: Option<serde_json::Value>,
    pub required: bool,
}

/// Output schema for a Snack
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SnackOutputSchema {
    pub name: String,
    pub r#type: String,
}

/// Valid snack kinds
pub const VALID_SNACK_KINDS: [&str; 6] = ["script", "skill", "spark", "wasm", "snackbox", "vibe-skill"];

/// Valid snack runtimes
pub const VALID_SNACK_RUNTIMES: [&str; 8] = [
    "bash",
    "apple-script-osx",
    "node",
    "python",
    "wasm",
    "spark-runtime",
    "vibe-skill",
    "github-spark",
];

/// Validate a snack schema
pub fn validate_snack_schema(schema: &SnackSchema) -> Result<(), String> {
    // Validate ID format
    if schema.id.is_empty() {
        return Err("Snack ID cannot be empty".to_string());
    }

    // Validate name
    if schema.name.is_empty() {
        return Err("Snack name cannot be empty".to_string());
    }

    // Validate version (basic semver check)
    if !is_valid_semver(&schema.version) {
        return Err("Invalid version format. Use semver (e.g., 1.0.0)".to_string());
    }

    // Validate kind
    if !VALID_SNACK_KINDS.contains(&schema.kind.as_str()) {
        return Err(format!(
            "Invalid snack kind: {}. Must be one of: {}",
            schema.kind,
            VALID_SNACK_KINDS.join(", ")
        ));
    }

    // Validate runtime
    if !VALID_SNACK_RUNTIMES.contains(&schema.runtime.as_str()) {
        return Err(format!(
            "Invalid runtime: {}. Must be one of: {}",
            schema.runtime,
            VALID_SNACK_RUNTIMES.join(", ")
        ));
    }

    // Validate code
    if schema.code.is_empty() {
        return Err("Snack code cannot be empty".to_string());
    }

    // Validate inputs
    let mut input_names = HashMap::new();
    for input in &schema.inputs {
        if input.name.is_empty() {
            return Err("Input name cannot be empty".to_string());
        }
        if input_names.contains_key(&input.name) {
            return Err(format!("Duplicate input name: {}", input.name));
        }
        input_names.insert(input.name.clone(), true);
    }

    // Validate outputs
    let mut output_names = HashMap::new();
    for output in &schema.outputs {
        if output.name.is_empty() {
            return Err("Output name cannot be empty".to_string());
        }
        if output_names.contains_key(&output.name) {
            return Err(format!("Duplicate output name: {}", output.name));
        }
        output_names.insert(output.name.clone(), true);
    }

    Ok(())
}

/// Check if a string is a valid semver version
fn is_valid_semver(version: &str) -> bool {
    // Simple semver regex: major.minor.patch
    let parts: Vec<&str> = version.split('.').collect();
    if parts.len() != 3 {
        return false;
    }
    
    for part in parts {
        if part.parse::<u32>().is_err() {
            return false;
        }
    }
    
    true
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_valid_snack_schema() {
        let schema = SnackSchema {
            id: "P100-U899".to_string(),
            name: "Postie".to_string(),
            version: "1.0.0".to_string(),
            kind: "script".to_string(),
            runtime: "bash".to_string(),
            code: "echo 'Hello'".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec!["email".to_string()],
        };

        assert!(validate_snack_schema(&schema).is_ok());
    }

    #[test]
    fn test_invalid_snack_id() {
        let mut schema = SnackSchema {
            id: "".to_string(),
            name: "Postie".to_string(),
            version: "1.0.0".to_string(),
            kind: "script".to_string(),
            runtime: "bash".to_string(),
            code: "echo 'Hello'".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
        };

        assert!(validate_snack_schema(&schema).is_err());
    }

    #[test]
    fn test_invalid_version() {
        let mut schema = SnackSchema {
            id: "P100-U899".to_string(),
            name: "Postie".to_string(),
            version: "invalid".to_string(),
            kind: "script".to_string(),
            runtime: "bash".to_string(),
            code: "echo 'Hello'".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
        };

        assert!(validate_snack_schema(&schema).is_err());
    }

    #[test]
    fn test_invalid_kind() {
        let mut schema = SnackSchema {
            id: "P100-U899".to_string(),
            name: "Postie".to_string(),
            version: "1.0.0".to_string(),
            kind: "invalid".to_string(),
            runtime: "bash".to_string(),
            code: "echo 'Hello'".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
        };

        assert!(validate_snack_schema(&schema).is_err());
    }

    #[test]
    fn test_duplicate_inputs() {
        let schema = SnackSchema {
            id: "P100-U899".to_string(),
            name: "Postie".to_string(),
            version: "1.0.0".to_string(),
            kind: "script".to_string(),
            runtime: "bash".to_string(),
            code: "echo 'Hello'".to_string(),
            requires: vec![],
            inputs: vec![
                SnackInputSchema {
                    name: "mailbox".to_string(),
                    r#type: "string".to_string(),
                    default: Some(serde_json::json!("inbox")),
                    required: false,
                },
                SnackInputSchema {
                    name: "mailbox".to_string(),
                    r#type: "string".to_string(),
                    default: Some(serde_json::json!("inbox")),
                    required: false,
                },
            ],
            outputs: vec![],
            tags: vec![],
        };

        assert!(validate_snack_schema(&schema).is_err());
    }
}
