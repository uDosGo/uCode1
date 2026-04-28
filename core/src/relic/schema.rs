//! Relic schema definitions and validation

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Relic schema definition
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RelicSchema {
    pub id: String,
    pub name: String,
    pub version: String,
    pub kind: String,
    pub platform: String,
    pub arch: String,
    pub data: String,
    pub requires: Vec<String>,
    pub inputs: Vec<RelicInputSchema>,
    pub outputs: Vec<RelicOutputSchema>,
    pub tags: Vec<String>,
}

/// Input schema for a Relic
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RelicInputSchema {
    pub name: String,
    pub r#type: String,
    pub default: Option<serde_json::Value>,
    pub required: bool,
}

/// Output schema for a Relic
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RelicOutputSchema {
    pub name: String,
    pub r#type: String,
}

/// Valid relic kinds
pub const VALID_RELIC_KINDS: [&str; 4] = ["binary", "archive", "container", "library"];

/// Valid platforms
pub const VALID_PLATFORMS: [&str; 4] = ["linux", "macos", "windows", "universal"];

/// Valid architectures
pub const VALID_ARCHS: [&str; 4] = ["x86_64", "aarch64", "arm", "universal"];

/// Validate a relic schema
pub fn validate_relic_schema(schema: &RelicSchema) -> Result<(), String> {
    // Validate ID format
    if schema.id.is_empty() {
        return Err("Relic ID cannot be empty".to_string());
    }

    // Validate name
    if schema.name.is_empty() {
        return Err("Relic name cannot be empty".to_string());
    }

    // Validate version (basic semver check)
    if !is_valid_semver(&schema.version) {
        return Err("Invalid version format. Use semver (e.g., 1.0.0)".to_string());
    }

    // Validate kind
    if !VALID_RELIC_KINDS.contains(&schema.kind.as_str()) {
        return Err(format!(
            "Invalid relic kind: {}. Must be one of: {}",
            schema.kind,
            VALID_RELIC_KINDS.join(", ")
        ));
    }

    // Validate platform
    if !VALID_PLATFORMS.contains(&schema.platform.as_str()) {
        return Err(format!(
            "Invalid platform: {}. Must be one of: {}",
            schema.platform,
            VALID_PLATFORMS.join(", ")
        ));
    }

    // Validate architecture
    if !VALID_ARCHS.contains(&schema.arch.as_str()) {
        return Err(format!(
            "Invalid architecture: {}. Must be one of: {}",
            schema.arch,
            VALID_ARCHS.join(", ")
        ));
    }

    // Validate data
    if schema.data.is_empty() {
        return Err("Relic data cannot be empty".to_string());
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
    fn test_valid_relic_schema() {
        let schema = RelicSchema {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec!["runner".to_string()],
        };

        assert!(validate_relic_schema(&schema).is_ok());
    }

    #[test]
    fn test_invalid_relic_id() {
        let mut schema = RelicSchema {
            id: "".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
        };

        assert!(validate_relic_schema(&schema).is_err());
    }

    #[test]
    fn test_invalid_version() {
        let mut schema = RelicSchema {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "invalid".to_string(),
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
        };

        assert!(validate_relic_schema(&schema).is_err());
    }

    #[test]
    fn test_invalid_kind() {
        let mut schema = RelicSchema {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            kind: "invalid".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
        };

        assert!(validate_relic_schema(&schema).is_err());
    }

    #[test]
    fn test_duplicate_inputs() {
        let schema = RelicSchema {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![
                RelicInputSchema {
                    name: "input1".to_string(),
                    r#type: "string".to_string(),
                    default: Some(serde_json::json!("default")),
                    required: false,
                },
                RelicInputSchema {
                    name: "input1".to_string(),
                    r#type: "string".to_string(),
                    default: Some(serde_json::json!("default")),
                    required: false,
                },
            ],
            outputs: vec![],
            tags: vec![],
        };

        assert!(validate_relic_schema(&schema).is_err());
    }
}