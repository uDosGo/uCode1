use clap::{Parser, Subcommand};
use log::{info, error, warn};
use std::process::{Command, Stdio, Child};
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use which::which;
use portpicker::pick_unused_port;
use std::os::unix::net::UnixStream;

// Import snack, relic, and publish commands
mod commands;
use commands::snack;
use commands::relic;
use commands::publish;

// Forward declaration for GridCommands
#[derive(Subcommand, Debug)]
enum GridCommands {
    /// Initialize a new grid
    Init {
        /// Grid width
        width: usize,
        /// Grid height
        height: usize,
    },
    
    /// Add a text layer to the grid
    Text {
        /// Layer name
        layer: String,
        /// Text to display
        text: String,
        /// X position
        x: usize,
        /// Y position
        y: usize,
        /// Foreground color (0-255)
        #[arg(default_value_t = 7)]
        fg: u8,
        /// Background color (0-255)
        #[arg(default_value_t = 0)]
        bg: u8,
    },
    
    /// Draw a border on a layer
    Border {
        /// Layer name
        layer: String,
    },
    
    /// Show current grid state
    Show,
    
    /// Demo grid with multiple layers
    Demo,
    
    /// Export grid to monodraw format
    Export {
        /// Output file path
        path: String,
    },
    
    /// Import grid from monodraw format
    Import {
        /// Input file path
        path: String,
    },
}

/// Snack commands
#[derive(Subcommand, Debug)]
enum SnackCommands {
    /// List available snacks
    List {
        /// Path to snacks directory
        #[arg(long, default_value = ".state/snacks")]
        path: String,
    },
    
    /// Show details of a snack
    Show {
        /// Snack ID
        id: String,
        /// Path to snacks directory
        #[arg(long, default_value = ".state/snacks")]
        path: String,
    },
    
    /// Run a snack
    Run {
        /// Snack ID
        id: String,
        /// Path to snacks directory
        #[arg(long, default_value = ".state/snacks")]
        path: String,
        /// Input parameters (KEY=VALUE format)
        #[arg(long, value_name = "KEY=VALUE", multiple_values = true)]
        params: Vec<String>,
    },
    
    /// Create a new snack
    Create {
        /// Snack ID
        id: String,
        /// Snack name
        #[arg(long)]
        name: String,
        /// Snack version
        #[arg(long, default_value = "1.0.0")]
        version: String,
        /// Snack kind
        #[arg(long, default_value = "script")]
        kind: String,
        /// Runtime environment
        #[arg(long, default_value = "bash")]
        runtime: String,
        /// Snack code
        #[arg(long)]
        code: String,
        /// Emoji representation
        #[arg(long)]
        emoji: Option<String>,
        /// Comma-separated tags
        #[arg(long)]
        tags: Option<String>,
        /// Path to save snack
        #[arg(long, default_value = ".state/snacks")]
        path: String,
    },
}

/// Relic commands
#[derive(Subcommand, Debug)]
enum RelicCommands {
    /// Create a relic from a snack
    Create {
        /// Snack ID
        id: String,
        /// Path to snacks directory
        #[arg(long, default_value = ".state/snacks")]
        path: String,
        /// Output relic path
        #[arg(long, default_value = ".legacy/relics")]
        output: String,
    },
    
    /// Unpack a relic to a snack
    Unpack {
        /// Relic ID
        id: String,
        /// Path to relics directory
        #[arg(long, default_value = ".legacy/relics")]
        path: String,
        /// Output snack path
        #[arg(long, default_value = ".state/snacks")]
        output: String,
    },
    
    /// List available relics
    List {
        /// Path to relics directory
        #[arg(long, default_value = ".legacy/relics")]
        path: String,
    },
    
    /// Run a relic
    Run {
        /// Relic ID
        id: String,
        /// Path to relics directory
        #[arg(long, default_value = ".legacy/relics")]
        path: String,
        /// Input parameters (KEY=VALUE format)
        #[arg(long, value_name = "KEY=VALUE", multiple_values = true)]
        params: Vec<String>,
    },
}

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
    
    /// Grid operations and visual display
    Grid {
        #[command(subcommand)]
        command: GridCommands,
    },
    
    /// Manage executable snacks
    Snack {
        #[command(subcommand)]
        command: SnackCommands,
    },
    
    /// Manage snack relics (compressed snacks)
    Relic {
        #[command(subcommand)]
        command: RelicCommands,
    },
    
    /// Publish documentation
    Publish {
        /// Publishing engine
        #[arg(long, default_value = "publishlane")]
        use: String,
        /// Config file path
        #[arg(long, default_value = ".publishlane/config.yaml")]
        config: String,
        /// Only build, don't deploy
        #[arg(long)]
        build_only: bool,
    },

#[derive(Subcommand, Debug)]
#[derive(Debug)]
struct ProcessManager {
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

async fn handle_grid_command(command: &GridCommands) {
    use grid_core::{GridCanvas, GridLayer, Cell, CellChar};
    use std::fs;
    use std::io::Write;
    
    match command {
        GridCommands::Init { width, height } => {
            info!("Initializing grid: {}x{}", width, height);
            let mut canvas = GridCanvas::new(*width, *height);
            
            // Add a base layer with border
            let mut base = GridLayer::new("base", *width, *height);
            base.draw_border();
            canvas.add_layer(base);
            
            // Save to file
            save_grid(&canvas, "grid.json");
            info!("✅ Grid initialized and saved to grid.json");
        }
        
        GridCommands::Text { layer, text, x, y, fg, bg } => {
            info!("Adding text to layer '{}': '{}' at ({},{})", layer, text, x, y);
            
            let grid_file = "grid.json";
            if !std::path::Path::new(grid_file).exists() {
                error!("Grid not initialized. Run 'udos grid init' first.");
                return;
            }
            
            let mut canvas: GridCanvas = load_grid(grid_file);
            canvas.add_text_layer(layer, text, *x, *y, *fg, *bg);
            save_grid(&canvas, grid_file);
            info!("✅ Text added to layer '{}'", layer);
        }
        
        GridCommands::Border { layer } => {
            info!("Adding border to layer '{}'", layer);
            
            let grid_file = "grid.json";
            if !std::path::Path::new(grid_file).exists() {
                error!("Grid not initialized. Run 'udos grid init' first.");
                return;
            }
            
            let mut canvas: GridCanvas = load_grid(grid_file);
            if let Some(layer) = canvas.get_layer_mut(layer) {
                layer.draw_border();
                save_grid(&canvas, grid_file);
                info!("✅ Border added to layer '{}'", layer.name);
            } else {
                error!("Layer '{}' not found.", layer);
            }
        }
        
        GridCommands::Show => {
            info!("Displaying grid state");
            
            let grid_file = "grid.json";
            if !std::path::Path::new(grid_file).exists() {
                error!("Grid not initialized. Run 'udos grid init' first.");
                return;
            }
            
            let canvas: GridCanvas = load_grid(grid_file);
            let rendered = canvas.render();
            
            info!("Grid: {}x{}", canvas.width, canvas.height);
            info!("Layers: {}", canvas.layers.len());
            for layer in &canvas.layers {
                info!("  - {} ({}x{}) {}", layer.name, layer.width, layer.height, if layer.visible { "visible" } else { "hidden" });
            }
            
            // Simple ASCII preview
            info!("\nPreview (first 10x10):");
            for y in 0..10.min(canvas.height) {
                let mut line = String::new();
                for x in 0..10.min(canvas.width) {
                    let cell = &rendered[y * canvas.width + x];
                    let ch = match cell.ch {
                        CellChar::Ascii(c) => c,
                        CellChar::TeletextBlock(b) => if b < 32 { ' ' } else { b as char },
                        CellChar::Custom(ref s) => s.chars().next().unwrap_or('?'),
                    };
                    line.push(ch);
                }
                info!("{}", line);
            }
        }
        
        GridCommands::Demo => {
            info!("Running grid demo...");
            
            let mut canvas = GridCanvas::new(40, 20);
            
            // Base layer with border
            let mut base = GridLayer::new("base", 40, 20);
            base.draw_border();
            canvas.add_layer(base);
            
            // Title
            canvas.add_text_layer("title", "uCode1 Grid Demo", 2, 1, 14, 0);
            
            // Player @ symbol
            if let Some(layer) = canvas.get_layer_mut("base") {
                layer.set_cell(20, 10, Cell {
                    ch: CellChar::Ascii('@'),
                    fg: 10,
                    bg: 0,
                    bold: true,
                    blink: false,
                });
            }
            
            // Instructions
            canvas.add_text_layer("help", "Arrow keys: move", 2, 18, 11, 0);
            
            // Save and show
            save_grid(&canvas, "demo_grid.json");
            info!("✅ Demo grid created and saved to demo_grid.json");
            
            // Show preview
            let rendered = canvas.render();
            info!("\nDemo Preview:");
            for y in 0..20 {
                let mut line = String::new();
                for x in 0..40 {
                    let cell = &rendered[y * 40 + x];
                    let ch = match cell.ch {
                        CellChar::Ascii(c) => c,
                        CellChar::TeletextBlock(b) => if b < 32 { ' ' } else { b as char },
                        CellChar::Custom(ref s) => s.chars().next().unwrap_or('?'),
                    };
                    line.push(ch);
                }
                info!("{}", line);
            }
        }
        
        GridCommands::Export { path } => {
            info!("Exporting grid to monodraw format: {}", path);
            
            let grid_file = "grid.json";
            if !std::path::Path::new(grid_file).exists() {
                error!("Grid not initialized. Run 'udos grid init' first.");
                return;
            }
            
            let canvas: GridCanvas = load_grid(grid_file);
            
            // Convert to monodraw format (simple text representation)
            let rendered = canvas.render();
            let mut monodraw = String::new();
            
            for y in 0..canvas.height {
                let mut line = String::new();
                for x in 0..canvas.width {
                    let cell = &rendered[y * canvas.width + x];
                    let ch = match cell.ch {
                        CellChar::Ascii(c) => c,
                        CellChar::TeletextBlock(b) => if b < 32 { ' ' } else { b as char },
                        CellChar::Custom(ref s) => s.chars().next().unwrap_or('?'),
                    };
                    line.push(ch);
                }
                monodraw.push_str(&line);
                monodraw.push('\n');
            }
            
            if let Err(e) = fs::write(path, monodraw) {
                error!("Failed to export: {}", e);
            } else {
                info!("✅ Grid exported to {}", path);
            }
        }
        
        GridCommands::Import { path } => {
            info!("Importing grid from monodraw format: {}", path);
            
            if let Ok(content) = fs::read_to_string(path) {
                let lines: Vec<&str> = content.lines().collect();
                let height = lines.len();
                let width = lines.first().map_or(0, |line| line.chars().count());
                
                if width == 0 || height == 0 {
                    error!("Invalid monodraw file: empty or malformed");
                    return;
                }
                
                let mut canvas = GridCanvas::new(width, height);
                let mut base = GridLayer::new("imported", width, height);
                
                for (y, line) in lines.iter().enumerate() {
                    for (x, ch) in line.chars().enumerate() {
                        base.set_cell(x, y, Cell {
                            ch: CellChar::Ascii(ch),
                            fg: 7,
                            bg: 0,
                            bold: false,
                            blink: false,
                        });
                    }
                }
                
                canvas.add_layer(base);
                save_grid(&canvas, "grid.json");
                info!("✅ Grid imported from {}", path);
                info!("   Size: {}x{}", width, height);
            } else {
                error!("Failed to read file: {}", path);
            }
        }
    }
}

fn save_grid(canvas: &GridCanvas, path: &str) {
    let json = serde_json::to_string_pretty(canvas).unwrap();
    fs::write(path, json).expect("Unable to write grid file");
}

fn load_grid(path: &str) -> GridCanvas {
    let data = fs::read_to_string(path).expect("Unable to read grid file");
    serde_json::from_str(&data).expect("Unable to parse grid file")
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
        
        Commands::Grid { command } => {
            handle_grid_command(command).await;
        },
        Commands::Snack { command } => {
            handle_snack_command(command).await;
        },
        Commands::Relic { command } => {
            handle_relic_command(command).await;
        },
        Commands::Publish { use: engine, config, build_only } => {
            handle_publish_command(engine, config, build_only).await;
        },
    }
}

/// Handle publish command
async fn handle_publish_command(engine: String, config: String, build_only: bool) {
    match commands::publish::handle(&commands::publish::register().get_matches_from(vec![
        "publish",
        "--use", &engine,
        "--config", &config,
        "--build-only", build_only.to_string().as_str()
    ])) {
        Ok(_) => info!("Publish completed successfully"),
        Err(e) => error!("Publish failed: {}", e),
    }
}

/// Handle snack commands
async fn handle_snack_command(command: SnackCommands) {
    match command {
        SnackCommands::List { path } => {
            if let Err(e) = snack::list::handle(&snack::list::register().get_matches_from(vec!["list", "--path", &path])) {
                error!("Failed to list snacks: {}", e);
            }
        }
        SnackCommands::Show { id, path } => {
            if let Err(e) = snack::show::handle(&snack::show::register().get_matches_from(vec!["show", &id, "--path", &path])) {
                error!("Failed to show snack: {}", e);
            }
        }
        SnackCommands::Run { id, path, params } => {
            let mut args = vec!["run", &id, "--path", &path];
            for param in params {
                args.push("--params");
                args.push(&param);
            }
            if let Err(e) = snack::run::handle(&snack::run::register().get_matches_from(args)) {
                error!("Failed to run snack: {}", e);
            }
        }
        SnackCommands::Create { id, name, version, kind, runtime, code, emoji, tags, path } => {
            let mut args = vec!["create", &id, "--name", &name, "--version", &version, "--kind", &kind, "--runtime", &runtime, "--code", &code, "--path", &path];
            if let Some(emoji_val) = emoji {
                args.push("--emoji");
                args.push(&emoji_val);
            }
            if let Some(tags_val) = tags {
                args.push("--tags");
                args.push(&tags_val);
            }
            if let Err(e) = snack::create::handle(&snack::create::register().get_matches_from(args)) {
                error!("Failed to create snack: {}", e);
            }
        }
    }
}

/// Handle relic commands
async fn handle_relic_command(command: RelicCommands) {
    match command {
        RelicCommands::Create { id, path, output } => {
            if let Err(e) = relic::create::handle(&relic::create::register().get_matches_from(vec!["create", &id, "--path", &path, "--output", &output])) {
                error!("Failed to create relic: {}", e);
            }
        }
        RelicCommands::Unpack { id, path, output } => {
            if let Err(e) = relic::unpack::handle(&relic::unpack::register().get_matches_from(vec!["unpack", &id, "--path", &path, "--output", &output])) {
                error!("Failed to unpack relic: {}", e);
            }
        }
        RelicCommands::List { path } => {
            if let Err(e) = relic::list::handle(&relic::list::register().get_matches_from(vec!["list", "--path", &path])) {
                error!("Failed to list relics: {}", e);
            }
        }
        RelicCommands::Run { id, path, params } => {
            let mut args = vec!["run", &id, "--path", &path];
            for param in params {
                args.push("--params");
                args.push(&param);
            }
            if let Err(e) = relic::run::handle(&relic::run::register().get_matches_from(args)) {
                error!("Failed to run relic: {}", e);
            }
        }
    }
}}
