//! Run relic command

use clap::{Arg, ArgMatches, Command};
use std::path::PathBuf;
use std::collections::HashMap;
use ucode1_core::snack::Snack;

/// Register run command
pub fn register() -> Command {
    Command::new("run")
        .about("Run a relic")
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
            Arg::new("params")
                .long("params")
                .value_name("KEY=VALUE")
                .help("Input parameters")
                .multiple_values(true),
        )
}

/// Handle run command
pub fn handle(matches: &ArgMatches) -> Result<(), Box<dyn std::error::Error>> {
    let id = matches.get_one::<String>("id").unwrap();
    let relics_path = matches.get_one::<String>("path").unwrap();
    
    // Find relic file
    let relic_path = find_relic_file(PathBuf::from(relics_path), id)?;
    
    // Load and decompress relic
    let yaml = decompress_relic(&relic_path)?;
    
    // Parse YAML to Snack
    let mut snack: Snack = serde_yaml::from_str(&yaml)?;
    
    // Parse parameters
    let params = parse_params(matches);
    
    // Validate inputs
    validate_inputs(&snack, &params)?;
    
    // Execute snack based on runtime
    match snack.runtime.as_str() {
        "bash" => execute_bash(&snack, &params)?,
        "apple-script-osx" => execute_applescript(&snack, &params)?,
        "node" => execute_node(&snack, &params)?,
        "python" => execute_python(&snack, &params)?,
        _ => return Err(format!("Unsupported runtime: {}", snack.runtime).into()),
    }
    
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
    use std::fs::File;
    use std::io::Read;
    use flate2::read::GzDecoder;
    
    let file = File::open(relic_path)?;
    let mut decoder = GzDecoder::new(file);
    let mut decompressed = String::new();
    decoder.read_to_string(&mut decompressed)?;
    
    Ok(decompressed)
}

/// Parse parameters from command line
fn parse_params(matches: &ArgMatches) -> HashMap<String, String> {
    let mut params = HashMap::new();
    
    if let Some(values) = matches.get_many::<String>("params") {
        for value in values {
            if let Some((key, val)) = value.split_once('=') {
                params.insert(key.to_string(), val.to_string());
            }
        }
    }
    
    params
}

/// Validate inputs
fn validate_inputs(snack: &Snack, params: &HashMap<String, String>) -> Result<(), Box<dyn std::error::Error>> {
    for input in &snack.inputs {
        if input.required && !params.contains_key(&input.name) {
            return Err(format!("Missing required input: {}", input.name).into());
        }
    }
    
    Ok(())
}

/// Execute bash snack
fn execute_bash(snack: &Snack, params: &HashMap<String, String>) -> Result<(), Box<dyn std::error::Error>> {
    use std::process::Command as StdCommand;
    
    println!("Executing bash relic: {}", snack.id);
    
    // Replace parameters in code
    let mut code = snack.code.clone();
    for (key, value) in params {
        code = code.replace(&format!("{{{{{}}}}}", key), value);
    }
    
    // Write to temporary file
    let temp_file = "/tmp/udos_relic_".to_string() + &snack.id.replace('-', "_") + ".sh";
    std::fs::write(&temp_file, code)?;
    
    // Make executable
    #[cfg(unix)]
    {
        use std::os::unix::fs::PermissionsExt;
        let mut perms = std::fs::metadata(&temp_file)?.permissions();
        perms.set_mode(0o755);
        std::fs::set_permissions(&temp_file, perms)?;
    }
    
    // Execute
    let output = StdCommand::new("bash")
        .arg(&temp_file)
        .output()?;
    
    println!("Exit status: {}", output.status);
    println!("Stdout: {}", String::from_utf8_lossy(&output.stdout));
    if !output.stderr.is_empty() {
        eprintln!("Stderr: {}", String::from_utf8_lossy(&output.stderr));
    }
    
    // Clean up
    std::fs::remove_file(&temp_file)?;
    
    Ok(())
}

/// Execute AppleScript snack
fn execute_applescript(snack: &Snack, params: &HashMap<String, String>) -> Result<(), Box<dyn std::error::Error>> {
    use std::process::Command as StdCommand;
    
    println!("Executing AppleScript relic: {}", snack.id);
    
    // Replace parameters in code
    let mut code = snack.code.clone();
    for (key, value) in params {
        code = code.replace(&format!("{{{{{}}}}}", key), value);
    }
    
    // Write to temporary file
    let temp_file = "/tmp/udos_relic_".to_string() + &snack.id.replace('-', "_") + ".scpt";
    std::fs::write(&temp_file, code)?;
    
    // Execute
    let output = StdCommand::new("osascript")
        .arg(&temp_file)
        .output()?;
    
    println!("Exit status: {}", output.status);
    println!("Stdout: {}", String::from_utf8_lossy(&output.stdout));
    if !output.stderr.is_empty() {
        eprintln!("Stderr: {}", String::from_utf8_lossy(&output.stderr));
    }
    
    // Clean up
    std::fs::remove_file(&temp_file)?;
    
    Ok(())
}

/// Execute Node.js snack
fn execute_node(snack: &Snack, params: &HashMap<String, String>) -> Result<(), Box<dyn std::error::Error>> {
    use std::process::Command as StdCommand;
    
    println!("Executing Node.js relic: {}", snack.id);
    
    // Replace parameters in code
    let mut code = snack.code.clone();
    for (key, value) in params {
        code = code.replace(&format!("{{{{{}}}}}", key), value);
    }
    
    // Write to temporary file
    let temp_file = "/tmp/udos_relic_".to_string() + &snack.id.replace('-', "_") + ".js";
    std::fs::write(&temp_file, code)?;
    
    // Execute
    let output = StdCommand::new("node")
        .arg(&temp_file)
        .output()?;
    
    println!("Exit status: {}", output.status);
    println!("Stdout: {}", String::from_utf8_lossy(&output.stdout));
    if !output.stderr.is_empty() {
        eprintln!("Stderr: {}", String::from_utf8_lossy(&output.stderr));
    }
    
    // Clean up
    std::fs::remove_file(&temp_file)?;
    
    Ok(())
}

/// Execute Python snack
fn execute_python(snack: &Snack, params: &HashMap<String, String>) -> Result<(), Box<dyn std::error::Error>> {
    use std::process::Command as StdCommand;
    
    println!("Executing Python relic: {}", snack.id);
    
    // Replace parameters in code
    let mut code = snack.code.clone();
    for (key, value) in params {
        code = code.replace(&format!("{{{{{}}}}}", key), value);
    }
    
    // Write to temporary file
    let temp_file = "/tmp/udos_relic_".to_string() + &snack.id.replace('-', "_") + ".py";
    std::fs::write(&temp_file, code)?;
    
    // Execute
    let output = StdCommand::new("python3")
        .arg(&temp_file)
        .output()?;
    
    println!("Exit status: {}", output.status);
    println!("Stdout: {}", String::from_utf8_lossy(&output.stdout));
    if !output.stderr.is_empty() {
        eprintln!("Stderr: {}", String::from_utf8_lossy(&output.stderr));
    }
    
    // Clean up
    std::fs::remove_file(&temp_file)?;
    
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
    fn test_run_bash_relic() {
        // Create a temporary directory with a test relic
        let dir = tempdir().unwrap();
        let relics_path = dir.path().join("relics");
        std::fs::create_dir_all(&relics_path).unwrap();
        
        let snack_yaml = r#"
id: TEST-001
name: Test Relic
version: 1.0.0
kind: script
runtime: bash
code: echo "Hello, {{{{name}}}}"
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
            "run",
            "TEST-001",
            "--path",
            relics_path.to_str().unwrap(),
            "--params",
            "name=World",
        ]);
        
        // Handle command
        let result = handle(&matches);
        assert!(result.is_ok());
    }
}
