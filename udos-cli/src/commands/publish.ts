//! Publish command for uDos CLI
// Integrates with PublishLane for documentation publishing

use clap::{Arg, ArgMatches, Command};
use std::process::Command as StdCommand;
use std::io::{self, Write};

/// Register publish command
pub fn register() -> Command {
    Command::new("publish")
        .about("Publish documentation using PublishLane")
        .arg(
            Arg::new("use")
                .long("use")
                .value_name("ENGINE")
                .help("Publishing engine")
                .default_value("publishlane"),
        )
        .arg(
            Arg::new("config")
                .long("config")
                .value_name("PATH")
                .help("PublishLane config file")
                .default_value(".publishlane/config.yaml"),
        )
        .arg(
            Arg::new("build-only")
                .long("build-only")
                .help("Only build, don't deploy")
                .action(clap::ArgAction::SetTrue),
        )
}

/// Handle publish command
pub fn handle(matches: &ArgMatches) -> Result<(), Box<dyn std::error::Error>> {
    let engine = matches.get_one::<String>("use").unwrap();
    let config = matches.get_one::<String>("config").unwrap();
    let build_only = matches.get_flag("build-only");
    
    match engine.as_str() {
        "publishlane" => {
            // Check if PublishLane is installed
            if which::which("publishlane").is_err() {
                return Err("PublishLane not found. Install with: npm install -g @okagent/publishlane".into());
            }
            
            // Run build
            let build_status = StdCommand::new("publishlane")
                .args(&["build", "--config", config])
                .status()?;
            
            if !build_status.success() {
                return Err("Build failed".into());
            }
            
            println!("✅ Build complete");
            
            // Deploy unless build-only flag is set
            if !build_only {
                let deploy_status = StdCommand::new("publishlane")
                    .args(&["deploy", "--config", config])
                    .status()?;
                
                if !deploy_status.success() {
                    return Err("Deployment failed".into());
                }
                
                println!("✅ Deployment complete");
            }
        }
        _ => return Err(format!("Unknown publishing engine: {}", engine).into()),
    }
    
    Ok(())
}

/// Interactive setup for PublishLane
pub async fn setup_publishlane() -> Result<(), Box<dyn std::error::Error>> {
    println!("\n🛠️  Setting up PublishLane for uDos...\n");
    
    // Check if already initialized
    if std::path::Path::new(".publishlane/config.yaml").exists() {
        println!("⚠️  PublishLane is already initialized.");
        print!("Overwrite configuration? (y/n): ");
        io::stdout().flush()?;
        
        let mut input = String::new();
        io::stdin().read_line(&mut input)?;
        
        if input.trim().to_lowercase() != "y" {
            return Ok(());
        }
    }
    
    // Create .publishlane directory
    std::fs::create_dir_all(".publishlane")?;
    
    // Create default config
    let config_content = r#"# PublishLane Configuration for uDos
version: 1

# Source and output directories
source: docs
output: _site

# Build format: jekyll, static, or nextjs
format: jekyll

# GitHub deployment settings
github:
  repo: uDosGo/uDosGo
  branch: gh-pages
  token: ${GITHUB_TOKEN}

# Theme settings
themes:
  primary: minima
  fallback: default
"#;
    
    std::fs::write(".publishlane/config.yaml", config_content)?;
    
    // Create status config
    let status_content = r#"# Document Status Definitions
version: 1

statuses:
  - id: draft
    name: Draft
    color: gray
    description: "Work in progress"
    next: [review]
  
  - id: review
    name: In Review
    color: yellow
    description: "Ready for review"
    next: [approved, draft]
  
  - id: approved
    name: Approved
    color: blue
    description: "Approved for publication"
    next: [published]
  
  - id: published
    name: Published
    color: green
    description: "Live on GitHub Pages"
    next: [deprecated]
"#;
    
    std::fs::write(".publishlane/status.yaml", status_content)?;
    
    // Create GitHub Actions workflow
    let workflow_content = r#"name: Publish Documentation

on:
  push:
    branches: [ main, dev ]
    paths:
      - 'docs/**'
      - '.publishlane/**'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v3
        with:
          node-version: 20
      - run: npm install -g @okagent/publishlane
      - run: publishlane build --config .publishlane/config.yaml
      - run: publishlane deploy --config .publishlane/config.yaml
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
"#;
    
    std::fs::create_dir_all(".github/workflows")?;
    std::fs::write(".github/workflows/publish.yml", workflow_content)?;
    
    println!("✅ PublishLane setup complete!");
    println!("\nNext steps:");
    println!("1. Install PublishLane: npm install -g @okagent/publishlane");
    println!("2. Build docs: ucode publish");
    println!("3. Push to trigger GitHub Actions deployment");
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use clap::ArgMatches;
    
    #[test]
    fn test_publish_command_registration() {
        let cmd = register();
        assert_eq!(cmd.get_name(), "publish");
        assert_eq!(cmd.get_about(), "Publish documentation using PublishLane");
    }
}
