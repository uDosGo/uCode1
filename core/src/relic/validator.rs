//! Relic validator implementation

use super::{Relic, RelicInput, RelicOutput};
use super::schema::{validate_relic_schema, RelicSchema, RelicInputSchema, RelicOutputSchema};
use std::path::PathBuf;

/// Validate a Relic instance
pub fn validate_relic(relic: &Relic) -> Result<(), String> {
    // Convert Relic to RelicSchema for validation
    let schema = RelicSchema {
        id: relic.id.clone(),
        name: relic.name.clone(),
        version: relic.version.clone(),
        kind: relic.kind.clone(),
        platform: relic.platform.clone(),
        arch: relic.arch.clone(),
        data: relic.data.clone(),
        requires: relic.requires.clone(),
        inputs: relic
            .inputs
            .iter()
            .map(|input| RelicInputSchema {
                name: input.name.clone(),
                r#type: input.r#type.clone(),
                default: input.default.clone(),
                required: input.required,
            })
            .collect(),
        outputs: relic
            .outputs
            .iter()
            .map(|output| RelicOutputSchema {
                name: output.name.clone(),
                r#type: output.r#type.clone(),
            })
            .collect(),
        tags: relic.tags.clone(),
    };

    validate_relic_schema(&schema)
}

/// Validate a Relic from a YAML file
pub fn validate_relic_file(path: &PathBuf) -> Result<(), String> {
    let relic = Relic::load_from_file(path)
        .map_err(|e| format!("Failed to load relic: {}", e))?;
    validate_relic(&relic)
}

/// Validate resource requirements for a Relic
pub fn validate_relic_resources(relic: &Relic) -> Result<(), String> {
    if let Some(resources) = &relic.resources {
        for resource in resources {
            // Validate resource type
            match resource.r#type.as_str() {
                "cell" => {
                    // Validate cell identifier format
                    if !is_valid_cell_identifier(&resource.identifier) {
                        return Err(format!(
                            "Invalid cell identifier: {}",
                            resource.identifier
                        ));
                    }
                }
                "file" | "database" | "api" => {
                    // Additional validation for other resource types
                    if resource.identifier.is_empty() {
                        return Err(format!(
                            "Resource identifier cannot be empty for type: {}",
                            resource.r#type
                        ));
                    }
                }
                _ => {
                    return Err(format!("Invalid resource type: {}", resource.r#type));
                }
            }

            // Validate resource mode
            match resource.mode.as_str() {
                "read" | "write" | "read_write" => {}
                _ => {
                    return Err(format!("Invalid resource mode: {}", resource.mode));
                }
            }
        }
    }
    
    Ok(())
}

/// Check if a cell identifier is valid
fn is_valid_cell_identifier(identifier: &str) -> bool {
    // Cell identifier format: L<level>-<gridXY>-<cellXY>-<layer>
    // Example: L100-BB45-1010-2
    let parts: Vec<&str> = identifier.split('-').collect();
    if parts.len() != 4 {
        return false;
    }
    
    // Check level prefix
    if !parts[0].starts_with('L') {
        return false;
    }
    
    // Check that all parts are non-empty
    for part in parts {
        if part.is_empty() {
            return false;
        }
    }
    
    true
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::relic::Relic;
    use std::path::PathBuf;

    #[test]
    fn test_validate_valid_relic() {
        let relic = Relic {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            emoji: Some("🏃".to_string()),
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec!["runner".to_string()],
            lexicon: None,
            visuals: None,
            resources: None,
        };

        assert!(validate_relic(&relic).is_ok());
    }

    #[test]
    fn test_validate_invalid_relic() {
        let relic = Relic {
            id: "".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
            lexicon: None,
            visuals: None,
            resources: None,
        };

        assert!(validate_relic(&relic).is_err());
    }

    #[test]
    fn test_validate_relic_file() {
        let relic = Relic {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
            lexicon: None,
            visuals: None,
            resources: None,
        };

        let path = PathBuf::from("/tmp/test_relic_validation.yaml");
        relic.save_to_file(&path).unwrap();

        let result = validate_relic_file(&path);
        assert!(result.is_ok());

        std::fs::remove_file(path).unwrap();
    }

    #[test]
    fn test_validate_relic_resources() {
        let relic = Relic {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
            lexicon: None,
            visuals: None,
            resources: Some(vec![
                crate::relic::RelicResource {
                    r#type: "cell".to_string(),
                    identifier: "L100-BB45-1010-2".to_string(),
                    mode: "read_write".to_string(),
                    description: Some("VIP data storage".to_string()),
                },
            ]),
        };

        assert!(validate_relic_resources(&relic).is_ok());
    }

    #[test]
    fn test_validate_invalid_cell_identifier() {
        let relic = Relic {
            id: "R100-U899".to_string(),
            name: "Runner".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "binary".to_string(),
            platform: "linux".to_string(),
            arch: "x86_64".to_string(),
            data: "base64encoded".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
            lexicon: None,
            visuals: None,
            resources: Some(vec![
                crate::relic::RelicResource {
                    r#type: "cell".to_string(),
                    identifier: "invalid-cell-id".to_string(),
                    mode: "read".to_string(),
                    description: None,
                },
            ]),
        };

        assert!(validate_relic_resources(&relic).is_err());
    }
}