use clap::{Arg, Command};
use std::path::Path;
use std::fs;
use std::collections::HashMap;
use std::io::Write;
use ucode1_vault_bridge::Vault;
use ucode1_ok_agent::{OkAgent, Intent};
use ucode1_mcp::McpServer;
use ucode1_spatial::{SpatialPoint, MapManager};
use ucode1_usystem::USystem;

use geo::Point;

mod tools;

mod modes;
use modes::AppMode;

mod mcp;
use ucode1_mcp::tools::*;

#[tokio::main]
async fn main() {
    // Initialize logging
    env_logger::init();

    let matches = Command::new("uCode1")
        .version("0.1.0")
        .about("uDos Code1 - Next generation uDos platform")
        .arg(Arg::new("user")
            .long("user")
            .help("Run in user mode (default)")
            .action(clap::ArgAction::SetTrue))
        .arg(Arg::new("privacy")
            .long("privacy")
            .help("Run in privacy mode (no telemetry, no network)")
            .action(clap::ArgAction::SetTrue))
        .arg(Arg::new("status")
            .long("status")
            .help("Run in status mode (enables MCP server)")
            .action(clap::ArgAction::SetTrue))
        .arg(Arg::new("dev")
            .long("dev")
            .help("Run in development mode")
            .action(clap::ArgAction::SetTrue))
        .arg(Arg::new("debug")
            .long("debug")
            .help("Enable debug logging")
            .action(clap::ArgAction::SetTrue))
        .arg(Arg::new("roadmap")
            .long("roadmap")
            .help("Show development roadmap")
            .action(clap::ArgAction::SetTrue))
        .subcommand(
            Command::new("note")
                .about("Manage notes in vault")
                .subcommand(
                    Command::new("list")
                        .about("List all notes")
                )
                .subcommand(
                    Command::new("show")
                        .about("Show note content")
                        .arg(Arg::new("name").required(true))
                )
                .subcommand(
                    Command::new("create")
                        .about("Create a new note")
                        .arg(Arg::new("name").required(true))
                        .arg(Arg::new("content").required(false))
                )
        )
        .subcommand(
            Command::new("ok")
                .about("OK agent - local intent assistant")
                .arg(Arg::new("prompt").required(true).help("Your question or command"))
        )
        .subcommand(
            Command::new("tui")
                .about("Launch Terminal User Interface")
        )
        .subcommand(
            Command::new("mcp")
                .about("MCP (Model Context Protocol) tools")
                .subcommand(
                    Command::new("spark-launch")
                        .about("Launch a Spark app")
                        .arg(Arg::new("prompt").required(true).help("Prompt for Spark"))
                )
                .subcommand(
                    Command::new("agentic-workflow")
                        .about("Create an agentic workflow")
                        .arg(Arg::new("repo").required(true).help("Repository (owner/repo)"))
                        .arg(Arg::new("name").required(true).help("Workflow name"))
                        .arg(Arg::new("description").required(true).help("Workflow description"))
                )
                .subcommand(
                    Command::new("flat-data")
                        .about("Schedule flat data fetch")
                        .arg(Arg::new("repo").required(true).help("Repository (owner/repo)"))
                        .arg(Arg::new("url").required(true).help("Data URL"))
                        .arg(Arg::new("schedule").required(true).help("Cron schedule"))
                        .arg(Arg::new("destination").required(true).help("Destination path"))
                )
                .subcommand(
                    Command::new("copernicus-index")
                        .about("Create a Copernicus index")
                        .arg(Arg::new("repo").required(true).help("Repository URL"))
                        .arg(Arg::new("index-path").required(true).help("Index path"))
                )
                .subcommand(
                    Command::new("discover-repo")
                        .about("Discover and test a repository")
                        .arg(Arg::new("repo").required(true).help("Repository URL"))
                )
                .subcommand(
                    Command::new("plugin-list")
                        .about("List available plugins")
                )
                .subcommand(
                    Command::new("system-status")
                        .about("Get system status")
                )
        )
        .subcommand(
            Command::new("map")
                .about("Spatial map operations")
                .subcommand(
                    Command::new("add")
                        .about("Add a point to the map")
                        .arg(Arg::new("layer").required(true).help("Layer name"))
                        .arg(Arg::new("x").required(true).help("X coordinate"))
                        .arg(Arg::new("y").required(true).help("Y coordinate"))
                        .arg(Arg::new("id").required(true).help("Point ID"))
                )
                .subcommand(
                    Command::new("near")
                        .about("Find points near a location")
                        .arg(Arg::new("x").required(true).help("X coordinate"))
                        .arg(Arg::new("y").required(true).help("Y coordinate"))
                        .arg(Arg::new("radius").required(true).help("Search radius"))
                )
        )
        .subcommand(
            Command::new("feed")
                .about("RSS/Atom feed operations")
                .subcommand(
                    Command::new("add")
                        .about("Add a feed subscription")
                        .arg(Arg::new("url").required(true).help("Feed URL"))
                )
                .subcommand(
                    Command::new("list")
                        .about("List all subscribed feeds")
                )
                .subcommand(
                    Command::new("remove")
                        .about("Remove a feed subscription")
                        .arg(Arg::new("url").required(true).help("Feed URL"))
                )
                .subcommand(
                    Command::new("fetch")
                        .about("Fetch and update a feed")
                        .arg(Arg::new("url").required(true).help("Feed URL"))
                )
                .subcommand(
                    Command::new("recent")
                        .about("Show recent feed replies")
                        .arg(Arg::new("limit").long("limit").short('l').help("Number of entries to show").default_value("10"))
                )
                .subcommand(
                    Command::new("search")
                        .about("Search feed replies by tag")
                        .arg(Arg::new("tag").long("tag").short('t').required(true).help("Tag to search for"))
                )
        )
        .subcommand(
            Command::new("docs")
                .about("Display command documentation")
                .arg(
                    Arg::new("format")
                        .long("format")
                        .short('f')
                        .value_name("FORMAT")
                        .help("Output format (text, markdown)")
                        .required(false)
                )
        )

        .get_matches();

    // Parse mode flags
    let mode = AppMode::from_flags(
        matches.get_flag("user"),
        matches.get_flag("privacy"),
        matches.get_flag("status"),
        matches.get_flag("dev"),
        matches.get_flag("debug"),
        matches.get_flag("roadmap"),
    );

    println!("uCode1 {} mode", mode.description());
    
    // Load dev config if in dev mode
    if mode.is_dev() {
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
    
    // Basic vault integration
    let vault_path = "~/Code/Vault".to_string();
    let expanded_vault_path = shellexpand::tilde(&vault_path).to_string();
    
    println!("Vault location: {}", expanded_vault_path);
    
    // Start MCP server if enabled by mode
    if mode.mcp_enabled() {
        println!("MCP server enabled in this mode");
        let mut mcp_server = McpServer::new(&expanded_vault_path);
        
        // Start MCP server in background
        tokio::spawn(async move {
            if let Err(e) = mcp_server.start().await {
                eprintln!("MCP server error: {}", e);
            }
        });
        
        // Give server a moment to start
        tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
    } else {
        println!("MCP server disabled in this mode");
    }
    
    // Expand vault path
    let expanded_vault_path = shellexpand::tilde(&vault_path).to_string();
    
    // Initialize uSystem for dynamic command management
    let usystem_db_path = format!("{}/.uCode1/usystem.db", std::env::var("HOME").unwrap_or_else(|_| ".".to_string()));
    let usystem = USystem::new(&usystem_db_path);
    
    // Initialize default commands if database is empty
    if let Err(e) = usystem.initialize_default_commands() {
        eprintln!("Warning: Failed to initialize uSystem commands: {}", e);
    }
    
    // Handle subcommands
    if let Some(("note", note_matches)) = matches.subcommand() {
        handle_note_command(note_matches, &expanded_vault_path);
    } else if let Some(("ok", ok_matches)) = matches.subcommand() {
        handle_ok_command(ok_matches);
    } else if let Some(("tui", _)) = matches.subcommand() {
        handle_tui_command(&expanded_vault_path).await;
    } else if let Some(("map", map_matches)) = matches.subcommand() {
        handle_map_command(map_matches);
    } else if let Some(("feed", feed_matches)) = matches.subcommand() {
        handle_feed_command(feed_matches, &expanded_vault_path).await;
    } else if let Some(("docs", docs_matches)) = matches.subcommand() {
        if let Some(format) = docs_matches.get_one::<String>("format") {
            if format == "markdown" {
                handle_help_markdown_command(&usystem);
            } else {
                eprintln!("Unknown format: {}", format);
                handle_help_command(&usystem);
            }
        } else {
            handle_help_command(&usystem);
        }

    } else {
        println!("Ready.");
        
        // Keep the process alive if MCP server is enabled (daemon mode)
        if mode.mcp_enabled() {
            println!("Running in daemon mode with MCP server...");
            println!("Press Ctrl+C to exit.");
            
            // Keep the main process alive
            tokio::signal::ctrl_c().await.expect("Failed to listen for Ctrl+C");
            println!("Shutting down...");
        }
    }

    // MCP Tools Command Handler
    if let Some(("mcp", mcp_matches)) = matches.subcommand() {
        match mcp_matches.subcommand() {
            Some(("spark-launch", spark_matches)) => {
                let prompt = spark_matches.get_one::<String>("prompt").unwrap();
                let input = SparkLaunchInput {
                    prompt: prompt.to_string(),
                };
                match spark_launch(input) {
                    Ok(output) => {
                        println!("Spark app launched successfully!");
                        println!("Preview URL: {}", output.preview_url);
                    }
                    Err(e) => {
                        eprintln!("Error launching Spark app: {}", e);
                    }
                }
            }
            Some(("agentic-workflow", workflow_matches)) => {
                let repo = workflow_matches.get_one::<String>("repo").unwrap();
                let name = workflow_matches.get_one::<String>("name").unwrap();
                let description = workflow_matches.get_one::<String>("description").unwrap();
                let input = AgenticWorkflowCreateInput {
                    repo: repo.to_string(),
                    workflow_name: name.to_string(),
                    description: description.to_string(),
                };
                match agentic_workflow_create(input) {
                    Ok(output) => {
                        println!("Agentic workflow created successfully!");
                        println!("{}", output.message);
                    }
                    Err(e) => {
                        eprintln!("Error creating agentic workflow: {}", e);
                    }
                }
            }
            Some(("flat-data", flat_data_matches)) => {
                let repo = flat_data_matches.get_one::<String>("repo").unwrap();
                let url = flat_data_matches.get_one::<String>("url").unwrap();
                let schedule = flat_data_matches.get_one::<String>("schedule").unwrap();
                let destination = flat_data_matches.get_one::<String>("destination").unwrap();
                let input = FlatDataScheduleInput {
                    repo: repo.to_string(),
                    url: url.to_string(),
                    schedule: schedule.to_string(),
                    destination_path: destination.to_string(),
                };
                match flat_data_schedule(input) {
                    Ok(output) => {
                        println!("Flat data schedule created successfully!");
                        println!("{}", output.message);
                    }
                    Err(e) => {
                        eprintln!("Error creating flat data schedule: {}", e);
                    }
                }
            }
            Some(("copernicus-index", copernicus_matches)) => {
                let repo = copernicus_matches.get_one::<String>("repo").unwrap();
                let index_path = copernicus_matches.get_one::<String>("index-path").unwrap();
                let input = CopernicusIndexInput {
                    repo_url: repo.to_string(),
                    index_path: index_path.to_string(),
                };
                match copernicus_index(input) {
                    Ok(output) => {
                        println!("Copernicus index created successfully!");
                        println!("Index path: {}", output.index_path);
                        println!("{}", output.message);
                    }
                    Err(e) => {
                        eprintln!("Error creating Copernicus index: {}", e);
                    }
                }
            }
            Some(("discover-repo", discover_matches)) => {
                let repo = discover_matches.get_one::<String>("repo").unwrap();
                let input = DiscoverRepoInput {
                    repo_url: repo.to_string(),
                };
                match discover_repo(input) {
                    Ok(output) => {
                        println!("Repo discovery completed!");
                        println!("Success: {}", output.success);
                        println!("{}", output.message);
                        println!("\nLogs:\n{}", output.logs);
                    }
                    Err(e) => {
                        eprintln!("Error discovering repo: {}", e);
                    }
                }
            }
            Some(("plugin-list", _)) => {
                match plugin_list(serde_json::json!({})) {
                    Ok(output) => {
                        println!("{}", serde_json::to_string_pretty(&output).unwrap());
                    }
                    Err(e) => {
                        eprintln!("Error listing plugins: {}", e);
                    }
                }
            }
            Some(("system-status", _)) => {
                match system_status(serde_json::json!({})) {
                    Ok(output) => {
                        println!("{}", serde_json::to_string_pretty(&output).unwrap());
                    }
                    Err(e) => {
                        eprintln!("Error getting system status: {}", e);
                    }
                }
            }
            _ => {
                println!("Unknown MCP command");
            }
        }
    }
}

async fn handle_tui_command(vault_path: &str) {
    println!("Launching TUI...");
    
    match ucode1_tui::run_tui(vault_path).await {
        Ok(_) => println!("TUI exited normally"),
        Err(e) => eprintln!("TUI error: {}", e),
    }
}

/// Handle the help command using uSystem
fn handle_help_command(usystem: &USystem) {
    match usystem.generate_help() {
        Ok(help_text) => {
            println!("{}", help_text);
        }
        Err(e) => {
            eprintln!("Failed to generate help: {}", e);
            println!("Falling back to static help...");
            println!("Usage: ucode1 [OPTIONS] [COMMAND]");
            println!("Try 'ucode1 --help' for more information");
        }
    }
}

/// Handle the help markdown command to generate documentation
fn handle_help_markdown_command(usystem: &USystem) {
    match usystem.generate_markdown_doc() {
        Ok(md) => {
            println!("{}", md);
        }
        Err(e) => {
            eprintln!("Failed to generate markdown documentation: {}", e);
        }
    }
}

async fn handle_feed_command(matches: &clap::ArgMatches, vault_path: &str) {
    let spool = ucode1_feed_spool::FeedSpool::new(vault_path);
    spool.ensure_directory().unwrap_or_else(|e| {
        eprintln!("Failed to create feeds directory: {}", e);
    });
    
    match matches.subcommand() {
        Some(("add", add_matches)) => {
            let url = add_matches.get_one::<String>("url").unwrap();
            match spool.add_feed(url) {
                Ok(feed) => {
                    println!("Added feed: {}", feed.url);
                    println!("Feed stored in: {}", spool.spool_dir().display());
                }
                Err(e) => {
                    eprintln!("Failed to add feed: {}", e);
                }
            }
        }
        Some(("list", _)) => {
            match spool.list_feeds() {
                Ok(feeds) => {
                    if feeds.is_empty() {
                        println!("No feeds subscribed.");
                    } else {
                        println!("Subscribed feeds:");
                        for feed in feeds {
                            println!("- {} ({} items)", feed.title, feed.items.len());
                        }
                    }
                }
                Err(e) => {
                    eprintln!("Failed to list feeds: {}", e);
                }
            }
        }
        Some(("remove", remove_matches)) => {
            let url = remove_matches.get_one::<String>("url").unwrap();
            match spool.remove_feed(url) {
                Ok(_) => println!("Removed feed: {}", url),
                Err(e) => eprintln!("Failed to remove feed: {}", e),
            }
        }
        Some(("fetch", fetch_matches)) => {
            let url = fetch_matches.get_one::<String>("url").unwrap();
            println!("Feed fetching not yet implemented for: {}", url);
            println!("This will be added in a future update.");
        }
        Some(("recent", recent_matches)) => {
            let limit: usize = recent_matches.get_one::<String>("limit")
                .unwrap_or(&"10".to_string())
                .parse()
                .unwrap_or(10);
            
            // Read from the feed spool replies file
            let replies_path = format!("{}/.uds/state/feed_spool/replies.jsonl", vault_path);
            let expanded_replies_path = shellexpand::tilde(&replies_path).to_string();
            
            if let Ok(content) = std::fs::read_to_string(&expanded_replies_path) {
                let lines: Vec<&str> = content.lines().collect();
                let start = if lines.len() > limit { lines.len() - limit } else { 0 };
                let recent_lines = &lines[start..];
                
                if recent_lines.is_empty() {
                    println!("No recent feed replies found.");
                } else {
                    println!("Recent feed replies (last {}):", recent_lines.len());
                    for (i, line) in recent_lines.iter().enumerate() {
                        println!("{}. {}", i + 1, line);
                    }
                }
            } else {
                println!("No feed replies found or file doesn't exist.");
            }
        }
        Some(("search", search_matches)) => {
            let tag = search_matches.get_one::<String>("tag").unwrap();
            
            // Read from the feed spool replies file
            let replies_path = format!("{}/.uds/state/feed_spool/replies.jsonl", vault_path);
            let expanded_replies_path = shellexpand::tilde(&replies_path).to_string();
            
            if let Ok(content) = std::fs::read_to_string(&expanded_replies_path) {
                let filtered_lines: Vec<&str> = content.lines()
                    .filter(|line| line.contains(&format!("\"tag\":\"{}\"", tag)) || line.contains(tag))
                    .collect();
                
                if filtered_lines.is_empty() {
                    println!("No feed replies found with tag '{}'.", tag);
                } else {
                    println!("Feed replies with tag '{}' ({} found):", tag, filtered_lines.len());
                    for (i, line) in filtered_lines.iter().enumerate() {
                        println!("{}. {}", i + 1, line);
                    }
                }
            } else {
                println!("No feed replies found or file doesn't exist.");
            }
        }
        _ => {
            println!("Unknown feed command");
        }
    }
}

fn handle_map_command(matches: &clap::ArgMatches) {
    match matches.subcommand() {
        Some(("add", add_matches)) => {
            let layer = add_matches.get_one::<String>("layer").unwrap();
            let x: f64 = add_matches.get_one::<String>("x").unwrap().parse().unwrap();
            let y: f64 = add_matches.get_one::<String>("y").unwrap().parse().unwrap();
            let id = add_matches.get_one::<String>("id").unwrap();
            
            let mut manager = MapManager::new();
            let maps_dir = "~/Code/Vault/maps";
            
            // Load existing maps if any
            let expanded_maps_dir = shellexpand::tilde(maps_dir).to_string();
            if Path::new(&expanded_maps_dir).exists() {
                manager.load_from_directory(&expanded_maps_dir).unwrap_or_else(|e| {
                    eprintln!("Warning: Failed to load existing maps: {}", e);
                });
            }
            
            // Add new point
            let point = SpatialPoint {
                id: id.to_string(),
                point: Point::new(x, y),
                properties: HashMap::new(),
            };
            
            manager.add_point_to_layer(layer, point);
            
            // Save
            std::fs::create_dir_all(&expanded_maps_dir).unwrap();
            manager.save_to_directory(&expanded_maps_dir).unwrap();
            
            println!("Added point {} at ({}, {}) to layer {}", id, x, y, layer);
        }
        Some(("near", near_matches)) => {
            let x: f64 = near_matches.get_one::<String>("x").unwrap().parse().unwrap();
            let y: f64 = near_matches.get_one::<String>("y").unwrap().parse().unwrap();
            let radius: f64 = near_matches.get_one::<String>("radius").unwrap().parse().unwrap();
            
            let mut manager = MapManager::new();
            let maps_dir = "~/Code/Vault/maps";
            let expanded_maps_dir = shellexpand::tilde(maps_dir).to_string();
            
            if Path::new(&expanded_maps_dir).exists() {
                manager.load_from_directory(&expanded_maps_dir).unwrap_or_else(|e| {
                    eprintln!("Warning: Failed to load maps: {}", e);
                    return;
                });
            } else {
                eprintln!("No maps found. Add some points first.");
                return;
            }
            
            let query_point = Point::new(x, y);
            let nearest = manager.nearest_points(&query_point, radius);
            
            if nearest.is_empty() {
                println!("No points found within radius {} of ({}, {})", radius, x, y);
            } else {
                println!("Found {} points within radius {} of ({}, {}):", nearest.len(), radius, x, y);
                for point in nearest {
                    println!("  - {} at ({}, {})", point.id, point.point.x(), point.point.y());
                }
            }
        }
        _ => {
            println!("Unknown map command");
        }
    }
}

fn handle_ok_command(matches: &clap::ArgMatches) {
    let prompt = matches.get_one::<String>("prompt").unwrap();
    let agent = OkAgent::new();
    
    println!("OK agent processing: {}", prompt);
    
    match agent.classify_intent(prompt) {
        Some(intent) => {
            println!("Intent detected: {} (confidence: {:.2})", intent.name, intent.confidence);
            if !intent.parameters.is_empty() {
                println!("Parameters: {:?}", intent.parameters);
            }
            let response = agent.generate_response(&intent);
            println!("Response: {}", response);
        }
        None => {
            println!("No specific intent detected.");
            println!("Response: {}", agent.generate_response(&Intent {
                name: "unknown".to_string(),
                confidence: 0.0,
                parameters: HashMap::new(),
            }));
        }
    }
}

fn handle_note_command(matches: &clap::ArgMatches, vault_path: &str) {
    let vault = Vault::new(vault_path, vault_path);
    
    match matches.subcommand() {
        Some(("list", _)) => {
            println!("Listing notes from: {}", vault_path);
            match vault.list_notes() {
                Ok(notes) => {
                    if notes.is_empty() {
                        println!("No notes found.");
                    } else {
                        println!("Notes:");
                        for note in notes {
                            println!("- {}", note);
                        }
                    }
                }
                Err(e) => {
                    eprintln!("Error listing notes: {}", e);
                }
            }
        }
        Some(("show", show_matches)) => {
            let name = show_matches.get_one::<String>("name").unwrap();
            println!("Showing note: {}", name);
            
            match vault.read_note(name) {
                Ok(note) => {
                    println!("Title: {}", note.title);
                    println!("Tags: {:?}", note.tags);
                    println!("Created: {}", note.created_at);
                    println!("Updated: {}", note.updated_at);
                    println!("---");
                    println!("{}", note.content);
                }
                Err(e) => {
                    eprintln!("Error reading note: {}", e);
                }
            }
        }
        Some(("create", create_matches)) => {
            let name = create_matches.get_one::<String>("name").unwrap();
            let default_content = "".to_string();
            let content = create_matches.get_one::<String>("content").unwrap_or(&default_content);
            println!("Creating note: {}", name);
            
            match vault.create_note(name, content) {
                Ok(_) => {
                    println!("Note created successfully.");
                }
                Err(e) => {
                    eprintln!("Error creating note: {}", e);
                }
            }
        }
        _ => {
            println!("Unknown note command");
        }
    }
}


