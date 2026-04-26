//! Unpack relic command

use clap::{Arg, ArgMatches, Command};
use std::path::PathBuf;
use std::fs::File;
use std::io::Read;
use flate2::read::GzDecoder;
use ucode1_core::snack::Snack;

/// Register unpack command
pub fn register() -> Command {
    Command::new("unpack")
        .about("Unpack a relic to a snack")
        .arg(
            Arg::new("id")
                .help("Relic ID")
                .required(true),
        )
        .arg(
            Arg::new("path")
                .long("path")
                .value_name("PATH")
                .help("Path to relics directory")
                .default_value(".legacy/relics"),
        )
        .arg(
            Arg::new("output")
                .long("output")
                .value_name("OUTPUT")
                .help("Output snack path")
                .default_value(".state/snacks"),
        )
}

/// Handle unpack command
pub fn handle(matches: &ArgMatches) -> Result<(), Box<dyn std::error::Error>> {
    let id = matches.get_one::<String>("id").unwrap();
    let relics_path = matches.get_one::<String>("path").unwrap();
    let output_path = matches.get_one::<String>("output").unwrap();
    
    // Find relic file
    let relic_path = find_relic_file(PathBuf::from(relics_path), id)?;
    
    // Load and decompress relic
    let yaml = decompress_relic(&relic_path)?;
    
    // Parse YAML to Snack
    let snack: Snack = serde_yaml::from_str(&yaml)?;
    
    // Ensure output directory exists
    let output_dir = PathBuf::from(output_path);
    if !output_dir.exists() {
        std::fs::create_dir_all(&output_dir)?;
    }
    
    // Save snack
    let snack_path = output_dir.join(format!("{}.yaml", snack.id));
    snack.save_to_file(&snack_path)?;
    
    println!("Unpacked relic: {}", id);
    println!("Saved to: {}", snack_path.display());
    
    Ok(())
}

/// Find relic file by ID
fn find_relic_file(relics_dir: PathBuf, id: &str) -> Result<PathBuf, Box<dyn std::error::Error>> {
    let relic_path = relics_dir.join(format!("{}.relic", id));
    if relic_path.exists() {
        Ok(relic_path)
    } else {
        Err(format!("Relic {} not found in {}", id, relics_dir.display()).into())
    }
}

/// Decompress relic to YAML
fn decompress_relic(relic_path: &PathBuf) -> Result<String, Box<dyn std::error::Error>> {
    let file = File::open(relic_path)?;
    let mut decoder = GzDecoder::new(file);
    let mut decompressed = String::new();
    decoder.read_to_string(&mut decompressed)?;
    
    Ok(decompressed)
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::ArgMatches;
    use std::io::Write;
    use flate2::write::GzEncoder;
    use flate2::Compression;
    use tempfile::tempdir;

    #[test]
    fn test_unpack_relic() {
        // Create a temporary directory
        let dir = tempdir().unwrap();
        let relics_path = dir.path().join("relics");
        let output_path = dir.path().join("snacks");
        std::fs::create_dir_all(&relics_path).unwrap();
        std::fs::create_dir_all(&output_path).unwrap();
        
        // Create a test relic
        let snack_yaml = r#"
id: TEST-001
name: Test Snack
version: 1.0.0
kind: script
runtime: bash
code: echo 'Hello'
"#;
        
        let relic_path = relics_path.join("TEST-001.relic");
        let encoder = GzEncoder::new(Vec::new(), Compression::default());
        let mut writer = std::io::BufWriter::new(encoder);
        std::io::copy(&mut snack_yaml.as_bytes(), &mut writer).unwrap();
        let compressed_data = writer.into_inner().unwrap().finish().unwrap();
        std::fs::write(&relic_path, compressed_data).unwrap();
        
        // Create command
        let cmd = register();
        let matches = cmd.clone().get_matches_from(vec![
            "unpack",
            "TEST-001",
            "--path",
            relics_path.to_str().unwrap(),
            "--output",
            output_path.to_str().unwrap(),
        ]);
        
        // Handle command
        let result = handle(&matches);
        assert!(result.is_ok());
        
        // Verify snack was created
        let snack_path = output_path.join("TEST-001.yaml");
        assert!(snack_path.exists());
        
        // Verify snack content
        let snack = Snack::load_from_file(&snack_path).unwrap();
        assert_eq!(snack.id, "TEST-001");
        assert_eq!(snack.name, "Test Snack");
    }
}
