//! List snacks command

use clap::{Arg, ArgMatches, Command};
use std::path::PathBuf;
use ucode1_core::snack::Snack;

/// Register list command
pub fn register() -> Command {
    Command::new("list")
        .about("List available snacks")
        .arg(
            Arg::new("path")
                .long("path")
                .value_name("PATH")
                .help("Path to snacks directory")
                .default_value(".state/snacks"),
        )
}

/// Handle list command
pub fn handle(matches: &ArgMatches) -> Result<(), Box<dyn std::error::Error>> {
    let path = matches.get_one::<String>("path").unwrap();
    let snacks_dir = PathBuf::from(path);
    
    println!("Listing snacks in: {}", snacks_dir.display());
    
    // Read directory
    let mut entries = std::fs::read_dir(snacks_dir)?
        .map(|res| res.map(|e| e.path()))
        .collect::<Result<Vec<_>, std::io::Error>>()?;
    
    // Sort entries
    entries.sort();
    
    // Filter YAML files
    let yaml_files = entries
        .into_iter()
        .filter(|path| path.extension().and_then(|s| s.to_str()) == Some("yaml"));
    
    // Load and display each snack
    for path in yaml_files {
        match Snack::load_from_file(&path) {
            Ok(snack) => {
                println!("\n{}", snack.id);
                println!("  Name: {}", snack.name);
                println!("  Version: {}", snack.version);
                if let Some(emoji) = &snack.emoji {
                    println!("  Emoji: {}", emoji);
                }
                println!("  Kind: {}", snack.kind);
                println!("  Runtime: {}", snack.runtime);
                if !snack.tags.is_empty() {
                    println!("  Tags: {}", snack.tags.join(", "));
                }
            }
            Err(e) => {
                eprintln!("Warning: Failed to load {}: {}", path.display(), e);
            }
        }
    }
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::ArgMatches;
    use std::io::Write;
    use tempfile::tempdir;

    #[test]
    fn test_list_snacks() {
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
tags:
  - test
  - example
"#;
        
        let mut file = std::fs::File::create(&snack_path).unwrap();
        file.write_all(snack_yaml.as_bytes()).unwrap();
        
        // Create command
        let cmd = register();
        let matches = cmd.clone().get_matches_from(vec![
            "list",
            "--path",
            snack_path.parent().unwrap().to_str().unwrap(),
        ]);
        
        // Handle command
        let result = handle(&matches);
        assert!(result.is_ok());
    }
}
