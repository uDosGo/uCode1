//! Create snack command

use clap::{Arg, ArgMatches, Command};
use std::path::PathBuf;
use ucode1_core::snack::Snack;
use std::io::Write;

/// Register create command
pub fn register() -> Command {
    Command::new("create")
        .about("Create a new snack")
        .arg(
            Arg::new("id")
                .help("Snack ID")
                .required(true),
        )
        .arg(
            Arg::new("name")
                .long("name")
                .value_name("NAME")
                .help("Snack name")
                .required(true),
        )
        .arg(
            Arg::new("version")
                .long("version")
                .value_name("VERSION")
                .help("Snack version")
                .default_value("1.0.0"),
        )
        .arg(
            Arg::new("kind")
                .long("kind")
                .value_name("KIND")
                .help("Snack kind")
                .default_value("script"),
        )
        .arg(
            Arg::new("runtime")
                .long("runtime")
                .value_name("RUNTIME")
                .help("Runtime environment")
                .default_value("bash"),
        )
        .arg(
            Arg::new("code")
                .long("code")
                .value_name("CODE")
                .help("Snack code")
                .required(true),
        )
        .arg(
            Arg::new("emoji")
                .long("emoji")
                .value_name("EMOJI")
                .help("Emoji representation"),
        )
        .arg(
            Arg::new("tags")
                .long("tags")
                .value_name("TAGS")
                .help("Comma-separated tags"),
        )
        .arg(
            Arg::new("path")
                .long("path")
                .value_name("PATH")
                .help("Path to save snack")
                .default_value(".state/snacks"),
        )
}

/// Handle create command
pub fn handle(matches: &ArgMatches) -> Result<(), Box<dyn std::error::Error>> {
    let id = matches.get_one::<String>("id").unwrap();
    let name = matches.get_one::<String>("name").unwrap();
    let version = matches.get_one::<String>("version").unwrap();
    let kind = matches.get_one::<String>("kind").unwrap();
    let runtime = matches.get_one::<String>("runtime").unwrap();
    let code = matches.get_one::<String>("code").unwrap();
    let emoji = matches.get_one::<String>("emoji").map(|s| s.to_string());
    let tags = matches.get_one::<String>("tags")
        .map(|s| s.split(',').map(|t| t.trim().to_string()).collect::<Vec<_>>())
        .unwrap_or_default();
    let path = matches.get_one::<String>("path").unwrap();
    
    // Create snack
    let mut snack = Snack::new(id, name, version, code);
    snack.kind = kind.to_string();
    snack.runtime = runtime.to_string();
    snack.emoji = emoji;
    snack.tags = tags;
    
    // Ensure directory exists
    let save_path = PathBuf::from(path);
    if !save_path.exists() {
        std::fs::create_dir_all(&save_path)?;
    }
    
    // Save snack
    let file_path = save_path.join(format!("{}.yaml", id));
    snack.save_to_file(&file_path)?;
    
    println!("Created snack: {}", id);
    println!("Saved to: {}", file_path.display());
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::ArgMatches;
    use tempfile::tempdir;

    #[test]
    fn test_create_snack() {
        // Create a temporary directory
        let dir = tempdir().unwrap();
        let save_path = dir.path().join("snacks");
        
        // Create command
        let cmd = register();
        let matches = cmd.clone().get_matches_from(vec![
            "create",
            "TEST-001",
            "--name", "Test Snack",
            "--version", "1.0.0",
            "--kind", "script",
            "--runtime", "bash",
            "--code", "echo 'Hello'",
            "--emoji", "📬",
            "--tags", "test,example",
            "--path",
            save_path.to_str().unwrap(),
        ]);
        
        // Handle command
        let result = handle(&matches);
        assert!(result.is_ok());
        
        // Verify file was created
        let file_path = save_path.join("TEST-001.yaml");
        assert!(file_path.exists());
        
        // Verify file content
        let snack = Snack::load_from_file(&file_path).unwrap();
        assert_eq!(snack.id, "TEST-001");
        assert_eq!(snack.name, "Test Snack");
        assert_eq!(snack.emoji, Some("📬".to_string()));
        assert_eq!(snack.tags, vec!["test", "example"]);
    }
}
