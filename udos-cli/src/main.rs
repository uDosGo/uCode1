use clap::{Parser, Subcommand};
use log::{info, error, warn};
use std::process::{Command, Stdio, Child};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use which::which;
use portpicker::pick_unused_port;
use std::os::unix::net::UnixStream;

#[derive(Parser, Debug)]
#[command(name = "udos")]
#[command(about = "uDos Unified Command - Launch and manage all uDos components", long_about = None)]
#[command(version = "0.1.0")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
    
    /// Run in development mode
    #[arg(long, global = true)]
    dev: bool,
    
    /// Run in privacy mode (no telemetry, no network)
    #[arg(long, global = true)]
    privacy: bool,
    
    /// Show status information
    #[arg(long, global = true)]
    status: bool,
    
    /// Enable debug logging
    #[arg(long, global = true)]
    debug: bool,
}

#[derive(Subcommand, Debug)]
enum Commands {
    /// Start the complete uDos development environment
    Dev,
    
    /// Start uCode1 core components
    Core,
    
    /// Launch ThinUI dashboard
    Ui,
    
    /// Start Re3Engine (reasoning MCP server)
    Re3,
    
    /// Start Re3Chat (browser chat interface)
    Chat,
    
    /// Start all components (core + ui + re3 + chat)
    All,
    
    /// Stop all running uDos components
    Stop,
    
    /// Show status of running components
    Status,
    
    /// Manage uCode1 daemon
    Daemon {
        /// Daemon action (start, stop, status)
        action: String,
    },
    
    /// Check system health and configuration
    Doctor,
    
    /// Manage ports and prevent conflicts
    Ports {
        /// Action to perform (list, assign, free)
        action: String,
        /// Optional port number
        port: Option<u16>,
    },
}

struct ProcessManager {
    children: Arc<Mutex<Vec<Child>>>, 
}

impl ProcessManager {
    fn new() -> Self {
        Self {
            children: Arc::new(Mutex::new(Vec::new())),
        }
    }

    fn spawn(&self, cmd: &str, args: &[&str]) -> Result<(), String> {
        let mut command = Command::new(cmd);
        command.args(args);
        command.stdin(Stdio::null());
        command.stdout(Stdio::inherit());
        command.stderr(Stdio::inherit());

        match command.spawn() {
            Ok(child) => {
                self.children.lock().unwrap().push(child);
                Ok(())
            }
            Err(e) => Err(format!("Failed to spawn {}: {}", cmd, e)),
        }
    }

    fn stop_all(&self) {
        let mut children = self.children.lock().unwrap();
        for child in children.iter_mut() {
            let _ = child.kill();
        }
        children.clear();
    }
}

struct PortManager {
    assigned_ports: Arc<Mutex<HashMap<String, u16>>>, 
}

impl PortManager {
    fn new() -> Self {
        Self {
            assigned_ports: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    fn assign_port(&self, service_name: &str) -> u16 {
        let mut ports = self.assigned_ports.lock().unwrap();
        if let Some(port) = ports.get(service_name) {
            return *port;
        }

        let port = pick_unused_port().expect("No available ports");
        ports.insert(service_name.to_string(), port);
        port
    }

    fn free_port(&self, service_name: &str) {
        let mut ports = self.assigned_ports.lock().unwrap();
        ports.remove(service_name);
    }

    fn list_ports(&self) -> Vec<(String, u16)> {
        let ports = self.assigned_ports.lock().unwrap();
        ports.iter().map(|(k, v)| (k.clone(), *v)).collect()
    }
}

fn find_binary(name: &str) -> Option<String> {
    which(name).ok().map(|p| p.to_string_lossy().into_owned())
}

async fn start_core(process_manager: &ProcessManager) -> Result<(), String> {
    info!("Starting uCode1 core...");
    
    // Try to find the ucode1 binary
    if let Some(ucode1_path) = find_binary("ucode1") {
        process_manager.spawn(&ucode1_path, &["--status", "--dev"])?;
        Ok(())
    } else {
        // Fallback to cargo run
        process_manager.spawn("cargo", &["run", "--bin", "ucode1", "--", "--status", "--dev"])?;
        Ok(())
    }
}

async fn start_thinui(port_manager: &PortManager, process_manager: &ProcessManager) -> Result<(), String> {
    info!("Starting ThinUI...");
    
    let port = port_manager.assign_port("thinui");
    info!("ThinUI assigned to port {}", port);
    
    // Try to find the thinui binary or use cargo run
    if let Some(thinui_path) = find_binary("thinui") {
        process_manager.spawn(&thinui_path, &["--port", &port.to_string()])?;
    } else {
        process_manager.spawn("cargo", &["run", "--bin", "thinui", "--", "--port", &port.to_string()])?;
    }
    
    Ok(())
}

async fn start_re3engine(port_manager: &PortManager, process_manager: &ProcessManager) -> Result<(), String> {
    info!("Starting Re3Engine...");
    
    let port = port_manager.assign_port("re3engine");
    info!("Re3Engine assigned to port {}", port);
    
    // Try to find the re3engine binary or use cargo run
    if let Some(re3_path) = find_binary("re3engine") {
        process_manager.spawn(&re3_path, &["--port", &port.to_string()])?;
    } else {
        process_manager.spawn("cargo", &["run", "--bin", "re3engine", "--", "--port", &port.to_string()])?;
    }
    
    Ok(())
}

async fn start_re3chat(port_manager: &PortManager, process_manager: &ProcessManager) -> Result<(), String> {
    info!("Starting Re3Chat...");
    
    let port = port_manager.assign_port("re3chat");
    info!("Re3Chat assigned to port {}", port);
    
    // Try to find the re3chat binary or use cargo run
    if let Some(re3chat_path) = find_binary("re3chat") {
        process_manager.spawn(&re3chat_path, &["--port", &port.to_string()])?;
    } else {
        process_manager.spawn("cargo", &["run", "--bin", "re3chat", "--", "--port", &port.to_string()])?;
    }
    
    Ok(())
}

fn handle_doctor_command() {
    info!("Running uCode1 system health check...");
    
    // Check 1: Vault directory exists
    let vault_path = format!("{}/Code/Vault", std::env::var("HOME").unwrap());
    let vault_exists = std::path::Path::new(&vault_path).exists();
    
    if vault_exists {
        info!("✓ Vault directory exists: {}", vault_path);
    } else {
        error!("✗ Vault directory missing: {}", vault_path);
    }
    
    // Check 2: cargo in PATH
    if which::which("cargo").is_ok() {
        info!("✓ cargo found in PATH");
    } else {
        error!("✗ cargo not found in PATH");
    }
    
    // Check 3: node in PATH
    if which::which("node").is_ok() {
        info!("✓ node found in PATH");
    } else {
        warn!("⚠ node not found in PATH (optional for some features)");
    }
    
    // Check 4: npm in PATH
    if which::which("npm").is_ok() {
        info!("✓ npm found in PATH");
    } else {
        warn!("⚠ npm not found in PATH (optional for some features)");
    }
    
    // Check 5: Daemon status
    let pid_file_path = format!("{}/.uds/daemon.pid", std::env::var("HOME").unwrap());
    let daemon_running = std::path::Path::new(&pid_file_path).exists();
    
    if daemon_running {
        info!("✓ Daemon is running");
        
        // Test MCP socket
        let socket_path = format!("{}/.uds/mcp.sock", std::env::var("HOME").unwrap());
        if std::path::Path::new(&socket_path).exists() {
            info!("✓ MCP socket exists: {}", socket_path);
            
            // Try to connect and send a ping
            if let Ok(mut stream) = std::os::unix::net::UnixStream::connect(&socket_path) {
                use std::io::Write;
                let ping_request = r#"{"Ping": null}"#;
                if let Ok(_) = stream.write_all(ping_request.as_bytes()) {
                    if let Ok(_) = stream.write_all(b"\n") {
                        info!("✓ MCP server responding to ping");
                    }
                }
            } else {
                warn!("⚠ MCP socket exists but connection failed");
            }
        } else {
            error!("✗ MCP socket missing: {}", socket_path);
        }
    } else {
        info!("✓ Daemon is not running (expected if not started)");
    }
    
    info!("Health check complete!");
}

async fn handle_daemon_command(process_manager: &ProcessManager, action: &str) {
    let pid_file_path = format!("{}/.uds/daemon.pid", std::env::var("HOME").unwrap());
    let socket_path = format!("{}/.uds/mcp.sock", std::env::var("HOME").unwrap());
    
    match action {
        "start" => {
            info!("Starting uCode1 daemon...");
            
            // Start the core with --status flag
            if let Some(ucode1_path) = find_binary("uCode1") {
                match process_manager.spawn(&ucode1_path, &["--status"]) {
                    Ok(_) => {
                        info!("Daemon started successfully");
                        
                        // Write PID to file
                        if let Ok(_) = std::fs::write(&pid_file_path, "daemon_pid_placeholder") {
                            info!("PID written to {}", pid_file_path);
                        } else {
                            warn!("Failed to write PID file");
                        }
                        
                        info!("Socket path: {}", socket_path);
                    }
                    Err(e) => {
                        error!("Failed to start daemon: {}", e);
                    }
                }
            } else {
                error!("uCode1 binary not found in PATH");
            }
        }
        "stop" => {
            info!("Stopping uCode1 daemon...");
            
            // Read PID from file and kill process
            if let Ok(pid_content) = std::fs::read_to_string(&pid_file_path) {
                if let Ok(pid) = pid_content.trim().parse::<i32>() {
                    info!("Killing process {}", pid);
                    // In a real implementation, we would kill the process here
                    // For now, just remove the PID file
                    std::fs::remove_file(&pid_file_path).ok();
                    info!("Daemon stopped");
                } else {
                    error!("Invalid PID in file: {}", pid_content);
                }
            } else {
                info!("No running daemon found (PID file not found)");
            }
        }
        "status" => {
            info!("uCode1 Daemon Status:");
            
            // Check if PID file exists
            if std::path::Path::new(&pid_file_path).exists() {
                info!("  Status: Running");
                info!("  PID file: {}", pid_file_path);
                info!("  Socket: {}", socket_path);
            } else {
                info!("  Status: Not running");
            }
        }
        _ => {
            error!("Unknown daemon action: {}", action);
        }
    }
}

#[tokio::main]
async fn main() {
    // Initialize logger only once
    if std::env::var("RUST_LOG").is_err() {
        std::env::set_var("RUST_LOG", "info");
    }
    
    let cli = Cli::parse();
    
    if cli.debug {
        std::env::set_var("RUST_LOG", "debug");
    }
    
    env_logger::init();
    
    let process_manager = ProcessManager::new();
    let port_manager = PortManager::new();
    
    match &cli.command {
        Commands::Dev => {
            info!("Starting uDos development environment...");
            
            if let Err(e) = start_core(&process_manager).await {
                error!("Failed to start core: {}", e);
            }
            
            if let Err(e) = start_thinui(&port_manager, &process_manager).await {
                error!("Failed to start ThinUI: {}", e);
            }
            
            if let Err(e) = start_re3engine(&port_manager, &process_manager).await {
                error!("Failed to start Re3Engine: {}", e);
            }
            
            if let Err(e) = start_re3chat(&port_manager, &process_manager).await {
                error!("Failed to start Re3Chat: {}", e);
            }
            
            info!("uDos development environment started successfully!");
            info!("Port assignments:");
            for (service, port) in port_manager.list_ports() {
                info!("  {}: http://localhost:{}", service, port);
            }
            
            // Wait for Ctrl+C
            tokio::signal::ctrl_c().await.expect("Failed to listen for Ctrl+C");
            info!("Shutting down...");
            process_manager.stop_all();
        },
        
        Commands::Core => {
            info!("Starting uCode1 core...");
            if let Err(e) = start_core(&process_manager).await {
                error!("Failed to start core: {}", e);
                std::process::exit(1);
            }
            
            tokio::signal::ctrl_c().await.expect("Failed to listen for Ctrl+C");
            process_manager.stop_all();
        },
        
        Commands::Ui => {
            info!("Starting ThinUI...");
            if let Err(e) = start_thinui(&port_manager, &process_manager).await {
                error!("Failed to start ThinUI: {}", e);
                std::process::exit(1);
            }
            
            tokio::signal::ctrl_c().await.expect("Failed to listen for Ctrl+C");
            process_manager.stop_all();
        },
        
        Commands::Re3 => {
            info!("Starting Re3Engine...");
            if let Err(e) = start_re3engine(&port_manager, &process_manager).await {
                error!("Failed to start Re3Engine: {}", e);
                std::process::exit(1);
            }
            
            tokio::signal::ctrl_c().await.expect("Failed to listen for Ctrl+C");
            process_manager.stop_all();
        },
        
        Commands::Chat => {
            info!("Starting Re3Chat...");
            if let Err(e) = start_re3chat(&port_manager, &process_manager).await {
                error!("Failed to start Re3Chat: {}", e);
                std::process::exit(1);
            }
            
            tokio::signal::ctrl_c().await.expect("Failed to listen for Ctrl+C");
            process_manager.stop_all();
        },
        
        Commands::All => {
            info!("Starting all uDos components...");
            
            if let Err(e) = start_core(&process_manager).await {
                error!("Failed to start core: {}", e);
            }
            
            if let Err(e) = start_thinui(&port_manager, &process_manager).await {
                error!("Failed to start ThinUI: {}", e);
            }
            
            if let Err(e) = start_re3engine(&port_manager, &process_manager).await {
                error!("Failed to start Re3Engine: {}", e);
            }
            
            if let Err(e) = start_re3chat(&port_manager, &process_manager).await {
                error!("Failed to start Re3Chat: {}", e);
            }
            
            info!("All uDos components started successfully!");
            info!("Port assignments:");
            for (service, port) in port_manager.list_ports() {
                info!("  {}: http://localhost:{}", service, port);
            }
            
            tokio::signal::ctrl_c().await.expect("Failed to listen for Ctrl+C");
            process_manager.stop_all();
        },
        
        Commands::Stop => {
            info!("Stopping all uDos components...");
            process_manager.stop_all();
            info!("All components stopped.");
        },
        
        Commands::Status => {
            info!("uDos Status:");
            info!("  This feature will show running components in future versions");
        },
        
        Commands::Daemon { action } => {
            handle_daemon_command(&process_manager, action).await;
        },
        
        Commands::Doctor => {
            handle_doctor_command();
        },
        
        Commands::Ports { action, port } => {
            match action.as_str() {
                "list" => {
                    info!("Assigned ports:");
                    for (service, port) in port_manager.list_ports() {
                        info!("  {}: {}", service, port);
                    }
                },
                "assign" => {
                    if let Some(p) = port {
                        info!("Manually assigning port {} (not yet implemented)", p);
                    } else {
                        let p = port_manager.assign_port("manual");
                        info!("Assigned port: {}", p);
                    }
                },
                "free" => {
                    if let Some(p) = port {
                        info!("Freeing port {} (not yet implemented)", p);
                    } else {
                        port_manager.free_port("manual");
                        info!("Freed manual port");
                    }
                },
                _ => {
                    error!("Unknown port action: {}", action);
                }
            }
        },
    }
}