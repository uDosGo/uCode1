//! Show snack details command

use clap::{Arg, ArgMatches, Command};
use std::path::PathBuf;
use ucode1_core::snack::Snack;

/// Register show command
pub fn register() -> Command {
    Command::new("show")
        .about("Show details of a snack")
        .arg(
            Arg::new("id")
                .help("Snack ID")
                .required(true),
        )
        .arg(
            Arg::new("path")
                .long("path")
                .value_name("PATH")
                .help("Path to snacks directory")
                .default_value(".state/snacks"),
        )
}

/// Handle show command
pub fn handle(matches: &ArgMatches) -> Result<(), Box<dyn std::error::Error>> {
    let id = matches.get_one::<String>("id").unwrap();
    let path = matches.get_one::<String>("path").unwrap();
    let snacks_dir = PathBuf::from(path);
    
    // Find snack file
    let snack_path = find_snack_file(&snacks_dir, id)?;
    
    // Load snack
    let snack = Snack::load_from_file(&snack_path)?;
    
    // Display snack details
    println!("Snack: {}", snack.id);
    println!("Name: {}", snack.name);
    println!("Version: {}", snack.version);
    if let Some(emoji) = &snack.emoji {
        println!("Emoji: {}", emoji);
    }
    if let Some(glyph) = &snack.glyph {
        println!("Glyph: {}", glyph);
    }
    if let Some(ascii) = &snack.ascii {
        println!("ASCII: {}", ascii);
    }
    println!("Kind: {}", snack.kind);
    println!("Runtime: {}", snack.runtime);
    
    if !snack.requires.is_empty() {
        println!("\nDependencies:");
        for dep in &snack.requires {
            println!("  - {}", dep);
        }
    }
    
    if !snack.inputs.is_empty() {
        println!("\nInputs:");
        for input in &snack.inputs {
            println!("  {} ({}):", input.name, input.r#type);
            if let Some(default) = &input.default {
                println!("    Default: {}", default);
            }
            println!("    Required: {}", input.required);
        }
    }
    
    if !snack.outputs.is_empty() {
        println!("\nOutputs:");
        for output in &snack.outputs {
            println!("  {} ({})", output.name, output.r#type);
        }
    }
    
    if !snack.tags.is_empty() {
        println!("\nTags: {}", snack.tags.join(", "));
    }
    
    if let Some(lexicon) = &snack.lexicon {
        println!("\nLexicon:");
        println!("  Terms: {}", lexicon.terms.join(", "));
        if let Some(emoji) = &lexicon.emoji {
            println!("  Emoji: {}", emoji);
        }
        println!("  Short: {}", lexicon.short);
        println!("  Long: {}", lexicon.long);
    }
    
    if let Some(visuals) = &snack.visuals {
        println!("\nVisuals:");
        if let Some(ascii) = &visuals.ascii {
            println!("  ASCII: {}", ascii);
        }
        if let Some(teletext) = &visuals.teletext {
            println!("  Teletext: {}", teletext);
        }
        if let Some(color) = &visuals.color {
            println!("  Color: {}", color);
        }
    }
    
    if let Some(chain) = &snack.chain {
        println!("\nChaining:");
        if !chain.can_be_before.is_empty() {
            println!("  Can be before: {}", chain.can_be_before.join(", "));
        }
        if !chain.can_be_after.is_empty() {
            println!("  Can be after: {}", chain.can_be_after.join(", "));
        }
        println!("  Can be parallel: {}", chain.can_be_parallel);
    }
    
    if let Some(resources) = &snack.resources {
        println!("\nResources:");
        for resource in resources {
            println!("  {} ({}):", resource.identifier, resource.r#type);
            println!("    Mode: {}", resource.mode);
            if let Some(desc) = &resource.description {
                println!("    Description: {}", desc);
            }
        }
    }
    
    Ok(())
}

/// Find snack file by ID
fn find_snack_file(snacks_dir: &PathBuf, id: &str) -> Result<PathBuf, Box<dyn std::error::Error>> {
    for entry in std::fs::read_dir(snacks_dir)? {
        let entry = entry?;
        let path = entry.path();
        if path.extension().and_then(|s| s.to_str()) == Some("yaml") {
            let snack = Snack::load_from_file(&path)?;
            if snack.id == id {
                return Ok(path);
            }
        }
    }
    Err(format!("Snack {} not found in {}", id, snacks_dir.display()).into())
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::ArgMatches;
    use std::io::Write;
    use tempfile::tempdir;

    #[test]
    fn test_show_snack() {
        // Create a temporary directory with a test snack
        let dir = tempdir().unwrap();
        let snack_path = dir.path().join("test.yaml");
        
        let snack_yaml = r#"
id: TEST-001
name: Test Snack
version: 1.0.0
kind: script
runtime: bash
code: echo 'Hello'
emoji: 📬
tags:
  - test
  - example
inputs:
  - name: mailbox
    type: string
    default: inbox
    required: false
outputs:
  - name: result
    type: string
"#;
        
        let mut file = std::fs::File::create(&snack_path).unwrap();
        file.write_all(snack_yaml.as_bytes()).unwrap();
        
        // Create command
        let cmd = register();
        let matches = cmd.clone().get_matches_from(vec![
            "show",
            "TEST-001",
            "--path",
            snack_path.parent().unwrap().to_str().unwrap(),
        ]);
        
        // Handle command
        let result = handle(&matches);
        assert!(result.is_ok());
    }
}
