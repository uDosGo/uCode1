use clap::{Arg, Command};
use std::path::Path;
use std::fs;

#[cfg(user_mode)]
const MODE: &str = "user";

#[cfg(not(user_mode))]
const MODE: &str = "dev";

fn main() {
    let matches = Command::new("uCode1")
        .version("0.1.0")
        .about("uDos Code1 - Next generation uDos platform")
        .arg(Arg::new("dev")
            .long("dev")
            .help("Run in development mode")
            .action(clap::ArgAction::SetTrue))
        .get_matches();

    let is_dev = matches.get_flag("dev");
    
    println!("uCode1 {} mode", if is_dev { "dev" } else { MODE });
    
    if is_dev {
        // Try to load dev config
        let dev_config_path = Path::new(".dev.yaml");
        if dev_config_path.exists() {
            println!("Dev mode active, using config from .dev.yaml");
            if let Ok(config) = fs::read_to_string(dev_config_path) {
                println!("Dev config loaded: {} bytes", config.len());
            }
        } else {
            println!("Dev mode active, but no .dev.yaml found");
        }
    }
    
    // Basic vault integration demo
    let vault_path = if is_dev {
        // In dev mode, we might override vault path from .dev.yaml
        "~/Code/Vault".to_string()
    } else {
        "~/Code/Vault".to_string()
    };
    
    println!("Vault location: {}", vault_path);
    println!("Ready.");
}