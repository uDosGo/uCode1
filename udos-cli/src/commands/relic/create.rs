//! Create relic command

use clap::{Arg, ArgMatches, Command};
use std::path::PathBuf;
use std::fs::File;
use std::io::{Read, Write};
use flate2::write::GzEncoder;
use flate2::Compression;
use ucode1_core::snack::Snack;

/// Register create command
pub fn register() -> Command {
    Command::new("create")
        .about("Create a relic from a snack")
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
        .arg(
            Arg::new("output")
                .long("output")
                .value_name("OUTPUT")
                .help("Output relic path")
                .default_value(".legacy/relics"),
        )
}

/// Handle create command
pub fn handle(matches: &ArgMatches) -> Result<(), Box<dyn std::error::Error>> {
    let id = matches.get_one::<String>("id").unwrap();
    let snacks_path = matches.get_one::<String>("path").unwrap();
    let output_path = matches.get_one::<String>("output").unwrap();
    
    // Find snack file
    let snack_path = find_snack_file(PathBuf::from(snacks_path), id)?;
    
    // Load snack
    let snack = Snack::load_from_file(&snack_path)?;
    
    // Create relic
    let relic_data = create_relic(&snack)?;
    
    // Ensure output directory exists
    let output_dir = PathBuf::from(output_path);
    if !output_dir.exists() {
        std::fs::create_dir_all(&output_dir)?;
    }
    
    // Save relic
    let relic_path = output_dir.join(format!("{}.relic", id));
    std::fs::write(&relic_path, relic_data)?;
    
    println!("Created relic: {}", id);
    println!("Saved to: {}", relic_path.display());
    
    Ok(())
}

/// Find snack file by ID
fn find_snack_file(snacks_dir: PathBuf, id: &str) -> Result<PathBuf, Box<dyn std::error::Error>> {
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
    Err(format!("Snack {} not found", id).into())
}

/// Create a relic from a snack
fn create_relic(snack: &Snack) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    // Convert snack to YAML
    let yaml = serde_yaml::to_string(snack)?;
    
    // Compress using gzip
    let encoder = GzEncoder::new(Vec::new(), Compression::default());
    let mut writer = std::io::BufWriter::new(encoder);
    std::io::copy(&mut yaml.as_bytes(), &mut writer)?;
    
    let compressed_data = writer.into_inner()?.finish()?;
    
    Ok(compressed_data)
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::ArgMatches;
    use std::io::Write;
    use tempfile::tempdir;

    #[test]
    fn test_create_relic() {
        // Create a temporary directory with a test snack
        let dir = tempdir().unwrap();
        let snacks_path = dir.path().join("snacks");
        std::fs::create_dir_all(&snacks_path).unwrap();
        
        let snack_path = snacks_path.join("test.yaml");
        let snack_yaml = r#"
id: TEST-001
name: Test Snack
version: 1.0.0
kind: script
runtime: bash
code: echo 'Hello'
"#;
        
        let mut file = std::fs::File::create(&snack_path).unwrap();
        file.write_all(snack_yaml.as_bytes()).unwrap();
        
        // Create output directory
        let output_path = dir.path().join("relics");
        
        // Create command
        let cmd = register();
        let matches = cmd.clone().get_matches_from(vec![
            "create",
            "TEST-001",
            "--path",
            snacks_path.to_str().unwrap(),
            "--output",
            output_path.to_str().unwrap(),
        ]);
        
        // Handle command
        let result = handle(&matches);
        assert!(result.is_ok());
        
        // Verify relic was created
        let relic_path = output_path.join("TEST-001.relic");
        assert!(relic_path.exists());
    }
}
