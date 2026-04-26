//! Run snack command

use clap::{Arg, ArgMatches, Command};
use std::path::PathBuf;
use std::process::Command as StdCommand;
use ucode1_core::snack::{Snack, SnackResource};
use std::collections::HashMap;

/// Register run command
pub fn register() -> Command {
    Command::new("run")
        .about("Run a snack")
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
    let path = matches.get_one::<String>("path").unwrap();
    let snacks_dir = PathBuf::from(path);
    
    // Find snack file
    let snack_path = find_snack_file(&snacks_dir, id)?;
    
    // Load snack
    let mut snack = Snack::load_from_file(&snack_path)?;
    
    // Parse parameters
    let params = parse_params(matches);
    
    // Validate inputs
    validate_inputs(&snack, &params)?;
    
    // Prepare resources
    prepare_resources(&snack)?;
    
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

/// Prepare resources (cells, files, etc.)
fn prepare_resources(snack: &Snack) -> Result<(), Box<dyn std::error::Error>> {
    if let Some(resources) = &snack.resources {
        for resource in resources {
            match resource.r#type.as_str() {
                "cell" => {
                    // Ensure cell directory exists
                    let cell_dir = PathBuf::from(".state/cells");
                    if !cell_dir.exists() {
                        std::fs::create_dir_all(&cell_dir)?;
                    }
                }
                "file" => {
                    // Ensure file parent directory exists
                    let file_path = PathBuf::from(&resource.identifier);
                    if let Some(parent) = file_path.parent() {
                        if !parent.exists() {
                            std::fs::create_dir_all(parent)?;
                        }
                    }
                }
                _ => {}
            }
        }
    }
    
    Ok(())
}

/// Execute bash snack
fn execute_bash(snack: &Snack, params: &HashMap<String, String>) -> Result<(), Box<dyn std::error::Error>> {
    println!("Executing bash snack: {}", snack.id);
    
    // Replace parameters in code
    let mut code = snack.code.clone();
    for (key, value) in params {
        code = code.replace(&format!("{{{{{}}}}}", key), value);
    }
    
    // Write to temporary file
    let temp_file = "/tmp/udos_snack_".to_string() + &snack.id.replace('-', "_") + ".sh";
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
    println!("Executing AppleScript snack: {}", snack.id);
    
    // Replace parameters in code
    let mut code = snack.code.clone();
    for (key, value) in params {
        code = code.replace(&format!("{{{{{}}}}}", key), value);
    }
    
    // Write to temporary file
    let temp_file = "/tmp/udos_snack_".to_string() + &snack.id.replace('-', "_") + ".scpt";
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
    println!("Executing Node.js snack: {}", snack.id);
    
    // Replace parameters in code
    let mut code = snack.code.clone();
    for (key, value) in params {
        code = code.replace(&format!("{{{{{}}}}}", key), value);
    }
    
    // Write to temporary file
    let temp_file = "/tmp/udos_snack_".to_string() + &snack.id.replace('-', "_") + ".js";
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
    println!("Executing Python snack: {}", snack.id);
    
    // Replace parameters in code
    let mut code = snack.code.clone();
    for (key, value) in params {
        code = code.replace(&format!("{{{{{}}}}}", key), value);
    }
    
    // Write to temporary file
    let temp_file = "/tmp/udos_snack_".to_string() + &snack.id.replace('-', "_") + ".py";
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
    use tempfile::tempdir;

    #[test]
    fn test_run_bash_snack() {
        // Create a temporary directory with a test snack
        let dir = tempdir().unwrap();
        let snack_path = dir.path().join("test.yaml");
        
        let snack_yaml = r#"
id: TEST-001
name: Test Snack
version: 1.0.0
kind: script
runtime: bash
code: echo "Hello, {{{{name}}}}"
"#;
        
        let mut file = std::fs::File::create(&snack_path).unwrap();
        file.write_all(snack_yaml.as_bytes()).unwrap();
        
        // Create command
        let cmd = register();
        let matches = cmd.clone().get_matches_from(vec![
            "run",
            "TEST-001",
            "--path",
            snack_path.parent().unwrap().to_str().unwrap(),
            "--params",
            "name=World",
        ]);
        
        // Handle command
        let result = handle(&matches);
        assert!(result.is_ok());
    }
}
