//! List relics command

use clap::{Arg, ArgMatches, Command};
use std::path::PathBuf;

/// Register list command
pub fn register() -> Command {
    Command::new("list")
        .about("List available relics")
        .arg(
            Arg::new("path")
                .long("path")
                .value_name("PATH")
                .help("Path to relics directory")
                .default_value(".legacy/relics"),
        )
}

/// Handle list command
pub fn handle(matches: &ArgMatches) -> Result<(), Box<dyn std::error::Error>> {
    let path = matches.get_one::<String>("path").unwrap();
    let relics_dir = PathBuf::from(path);
    
    println!("Listing relics in: {}", relics_dir.display());
    
    // Read directory
    let mut entries = std::fs::read_dir(relics_dir)?
        .map(|res| res.map(|e| e.path()))
        .collect::<Result<Vec<_>, std::io::Error>>()?;
    
    // Sort entries
    entries.sort();
    
    // Filter relic files
    let relic_files = entries
        .into_iter()
        .filter(|path| path.extension().and_then(|s| s.to_str()) == Some("relic"));
    
    // Display each relic
    for path in relic_files {
        if let Some(file_name) = path.file_stem() {
            if let Some(relic_id) = file_name.to_str() {
                println!("  - {}", relic_id);
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
    use flate2::write::GzEncoder;
    use flate2::Compression;
    use tempfile::tempdir;

    #[test]
    fn test_list_relics() {
        // Create a temporary directory with test relics
        let dir = tempdir().unwrap();
        let relics_path = dir.path().join("relics");
        std::fs::create_dir_all(&relics_path).unwrap();
        
        // Create test relics
        for i in 1..=3 {
            let snack_yaml = format!(
                r#"
id: TEST-{:03}
name: Test Snack {}
version: 1.0.0
kind: script
runtime: bash
code: echo 'Hello {}'
"#, i, i, i
            );
            
            let relic_path = relics_path.join(format!("TEST-{:03}.relic", i));
            let encoder = GzEncoder::new(Vec::new(), Compression::default());
            let mut writer = std::io::BufWriter::new(encoder);
            std::io::copy(&mut snack_yaml.as_bytes(), &mut writer).unwrap();
            let compressed_data = writer.into_inner().unwrap().finish().unwrap();
            std::fs::write(&relic_path, compressed_data).unwrap();
        }
        
        // Create command
        let cmd = register();
        let matches = cmd.clone().get_matches_from(vec![
            "list",
            "--path",
            relics_path.to_str().unwrap(),
        ]);
        
        // Handle command
        let result = handle(&matches);
        assert!(result.is_ok());
    }
}
