//! Snack validator implementation

use crate::snack::schema::{validate_snack_schema, SnackSchema, SnackInputSchema, SnackOutputSchema};
use crate::snack::Snack;
use std::path::PathBuf;

/// Validate a Snack instance
pub fn validate_snack(snack: &Snack) -> Result<(), String> {
    // Convert Snack to SnackSchema for validation
    let schema = SnackSchema {
        id: snack.id.clone(),
        name: snack.name.clone(),
        version: snack.version.clone(),
        kind: snack.kind.clone(),
        runtime: snack.runtime.clone(),
        code: snack.code.clone(),
        requires: snack.requires.clone(),
        inputs: snack
            .inputs
            .iter()
            .map(|input| SnackInputSchema {
                name: input.name.clone(),
                r#type: input.r#type.clone(),
                default: input.default.clone(),
                required: input.required,
            })
            .collect(),
        outputs: snack
            .outputs
            .iter()
            .map(|output| SnackOutputSchema {
                name: output.name.clone(),
                r#type: output.r#type.clone(),
            })
            .collect(),
        tags: snack.tags.clone(),
    };

    validate_snack_schema(&schema)
}

/// Validate a Snack from a YAML file
pub fn validate_snack_file(path: &PathBuf) -> Result<(), String> {
    let snack = Snack::load_from_file(path)
        .map_err(|e| format!("Failed to load snack: {}", e))?;
    validate_snack(&snack)
}

/// Validate resource requirements for a Snack
pub fn validate_snack_resources(snack: &Snack) -> Result<(), String> {
    if let Some(resources) = &snack.resources {
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
    use crate::snack::Snack;
    use std::path::PathBuf;

    #[test]
    fn test_validate_valid_snack() {
        let snack = Snack {
            id: "P100-U899".to_string(),
            name: "Postie".to_string(),
            version: "1.0.0".to_string(),
            emoji: Some("📬".to_string()),
            glyph: None,
            ascii: None,
            kind: "script".to_string(),
            runtime: "bash".to_string(),
            code: "echo 'Hello'".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec!["email".to_string()],
            lexicon: None,
            visuals: None,
            chain: None,
            resources: None,
        };

        assert!(validate_snack(&snack).is_ok());
    }

    #[test]
    fn test_validate_invalid_snack() {
        let snack = Snack {
            id: "".to_string(),
            name: "Postie".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "script".to_string(),
            runtime: "bash".to_string(),
            code: "echo 'Hello'".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
            lexicon: None,
            visuals: None,
            chain: None,
            resources: None,
        };

        assert!(validate_snack(&snack).is_err());
    }

    #[test]
    fn test_validate_snack_file() {
        let snack = Snack {
            id: "P100-U899".to_string(),
            name: "Postie".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "script".to_string(),
            runtime: "bash".to_string(),
            code: "echo 'Hello'".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
            lexicon: None,
            visuals: None,
            chain: None,
            resources: None,
        };

        let path = PathBuf::from("/tmp/test_snack_validation.yaml");
        snack.save_to_file(&path).unwrap();

        let result = validate_snack_file(&path);
        assert!(result.is_ok());

        std::fs::remove_file(path).unwrap();
    }

    #[test]
    fn test_validate_snack_resources() {
        let snack = Snack {
            id: "P100-U899".to_string(),
            name: "Postie".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "script".to_string(),
            runtime: "bash".to_string(),
            code: "echo 'Hello'".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
            lexicon: None,
            visuals: None,
            chain: None,
            resources: Some(vec![
                crate::snack::SnackResource {
                    r#type: "cell".to_string(),
                    identifier: "L100-BB45-1010-2".to_string(),
                    mode: "read_write".to_string(),
                    description: Some("VIP email storage".to_string()),
                },
            ]),
        };

        assert!(validate_snack_resources(&snack).is_ok());
    }

    #[test]
    fn test_validate_invalid_cell_identifier() {
        let snack = Snack {
            id: "P100-U899".to_string(),
            name: "Postie".to_string(),
            version: "1.0.0".to_string(),
            emoji: None,
            glyph: None,
            ascii: None,
            kind: "script".to_string(),
            runtime: "bash".to_string(),
            code: "echo 'Hello'".to_string(),
            requires: vec![],
            inputs: vec![],
            outputs: vec![],
            tags: vec![],
            lexicon: None,
            visuals: None,
            chain: None,
            resources: Some(vec![
                crate::snack::SnackResource {
                    r#type: "cell".to_string(),
                    identifier: "invalid-cell-id".to_string(),
                    mode: "read".to_string(),
                    description: None,
                },
            ]),
        };

        assert!(validate_snack_resources(&snack).is_err());
    }
}
