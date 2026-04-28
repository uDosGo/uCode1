#!/bin/bash
# uDos CLI Management Skill
# Install, update, repair, and manage uDos CLI locally

set -e

# Configuration
UDOSGO_ROOT="${UDOSGO_ROOT:-$HOME/Code/uDosGo}"
UDOS_CLI_DIR="$UDOSGO_ROOT/uCode1"
INSTALL_DIR="$HOME/.local/share/udos/bin"
BIN_DIR="$HOME/.local/bin"

# Default action and force flag
ACTION="${1:-status}"
FORCE="${2:-no}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if uDosGo repository exists
check_repo() {
    if [ ! -d "$UDOS_CLI_DIR" ]; then
        echo -e "${RED}❌ Error: uDosGo repository not found at $UDOS_CLI_DIR${NC}"
        echo "Please clone the repository first:"
        echo "  git clone https://github.com/your-repo/uDosGo.git $UDOSGO_ROOT"
        exit 1
    fi
}

# Function to check installation status
check_status() {
    echo -e "${BLUE}🔍 uDos CLI Installation Status${NC}"
    echo "====================================="
    
    # Check if binary exists
    if [ -f "$INSTALL_DIR/udos" ]; then
        echo -e "${GREEN}✅ Binary installed: $INSTALL_DIR/udos${NC}"
        BINARY_SIZE=$(du -h "$INSTALL_DIR/udos" | cut -f1)
        echo "   Size: $BINARY_SIZE"
    else
        echo -e "${RED}❌ Binary not found: $INSTALL_DIR/udos${NC}"
    fi
    
    # Check if wrapper exists
    if [ -f "$BIN_DIR/udos" ]; then
        echo -e "${GREEN}✅ Wrapper installed: $BIN_DIR/udos${NC}"
    else
        echo -e "${RED}❌ Wrapper not found: $BIN_DIR/udos${NC}"
    fi
    
    # Check if symlink exists
    if [ -L "$BIN_DIR/udo" ]; then
        echo -e "${GREEN}✅ Symlink installed: $BIN_DIR/udo${NC}"
    else
        echo -e "${RED}❌ Symlink not found: $BIN_DIR/udo${NC}"
    fi
    
    # Check if command is available
    if command -v udos >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Command available: $(command -v udos)${NC}"
    else
        echo -e "${RED}❌ Command not available in PATH${NC}"
        echo "   Make sure $BIN_DIR is in your PATH"
    fi
    
    # Check if alias is available
    if command -v udo >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Alias available: $(command -v udo)${NC}"
    else
        echo -e "${RED}❌ Alias not available in PATH${NC}"
    fi
    
    echo "====================================="
    
    # Overall status
    if [ -f "$INSTALL_DIR/udos" ] && [ -f "$BIN_DIR/udos" ] && [ -L "$BIN_DIR/udo" ] && command -v udos >/dev/null 2>&1; then
        echo -e "${GREEN}🎉 uDos CLI is properly installed and working!${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  uDos CLI installation has issues${NC}"
        echo "Run 'vibe udos-cli repair' to fix problems"
        return 1
    fi
}

# Function to install uDos CLI
install_cli() {
    echo -e "${BLUE}🎮 Installing uDos CLI${NC}"
    echo "====================================="
    
    check_repo
    
    # Build the release version
    echo "🔨 Building uCode1..."
    cd "$UDOS_CLI_DIR"
    cargo build --release
    
    # Create directory structure
    echo "📁 Creating directory structure..."
    mkdir -p "$INSTALL_DIR"
    
    # Copy the built binary
    echo "📦 Installing udos binary..."
    cp target/release/uCode1 "$INSTALL_DIR/udos"
    
    # Create the wrapper script
    echo "🔧 Creating wrapper script..."
    cat > "$BIN_DIR/udos" << 'EOF'
#!/bin/bash
export PATH="$HOME/.local/share/udos/bin:$PATH"
exec "$HOME/.local/share/udos/bin/udos" "$@"
EOF
    
    # Make executables
    chmod +x "$INSTALL_DIR/udos"
    chmod +x "$BIN_DIR/udos"
    
    # Create udo symlink
    echo "🔗 Creating udo symlink..."
    ln -sf "$BIN_DIR/udos" "$BIN_DIR/udo"
    
    # Test the installation
    echo "🧪 Testing installation..."
    if command -v udos >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Installation successful!${NC}"
        echo ""
        echo "You can now use:"
        echo "  udos --help   - See available commands"
        echo "  udos status   - Check uDos status"
        echo "  udo status    - Same as above (short alias)"
    else
        echo -e "${RED}❌ Installation failed${NC}"
        exit 1
    fi
}

# Function to update uDos CLI
update_cli() {
    echo -e "${BLUE}🔄 Updating uDos CLI${NC}"
    echo "====================================="
    
    check_repo
    
    # Build the release version
    echo "🔨 Rebuilding uCode1..."
    cd "$UDOS_CLI_DIR"
    cargo build --release
    
    # Copy the updated binary
    echo "📦 Updating udos binary..."
    cp target/release/uCode1 "$INSTALL_DIR/udos"
    
    # Make sure it's executable
    chmod +x "$INSTALL_DIR/udos"
    
    # Test the update
    echo "🧪 Testing update..."
    if command -v udos >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Update successful!${NC}"
        echo ""
        echo "uDos CLI has been updated to the latest version."
    else
        echo -e "${RED}❌ Update failed${NC}"
        exit 1
    fi
}

# Function to repair uDos CLI installation
repair_cli() {
    echo -e "${BLUE}🛠️ Repairing uDos CLI Installation${NC}"
    echo "====================================="
    
    check_repo
    
    # Check if we should force reinstall
    if [ "$FORCE" = "yes" ]; then
        echo "🔥 Force flag detected - reinstalling everything"
        install_cli
        return
    fi
    
    # Check what needs to be fixed
    NEEDS_FIX=0
    
    if [ ! -f "$INSTALL_DIR/udos" ]; then
        echo "❌ Binary missing - will reinstall"
        NEEDS_FIX=1
    fi
    
    if [ ! -f "$BIN_DIR/udos" ]; then
        echo "❌ Wrapper missing - will reinstall"
        NEEDS_FIX=1
    fi
    
    if [ ! -L "$BIN_DIR/udo" ]; then
        echo "❌ Symlink missing - will reinstall"
        NEEDS_FIX=1
    fi
    
    if [ $NEEDS_FIX -eq 0 ]; then
        echo "✅ All components are present"
        echo "🧪 Testing if command works..."
        if command -v udos >/dev/null 2>&1; then
            echo -e "${GREEN}✅ uDos CLI is working properly${NC}"
            return
        else
            echo "❌ Command not available - will reinstall"
            NEEDS_FIX=1
        fi
    fi
    
    if [ $NEEDS_FIX -eq 1 ]; then
        echo "🔧 Fixing installation..."
        install_cli
    fi
}

# Function to uninstall uDos CLI
uninstall_cli() {
    echo -e "${BLUE}🗑️ Uninstalling uDos CLI${NC}"
    echo "====================================="
    
    # Remove binary
    if [ -f "$INSTALL_DIR/udos" ]; then
        echo "📦 Removing binary..."
        rm -f "$INSTALL_DIR/udos"
    fi
    
    # Remove wrapper
    if [ -f "$BIN_DIR/udos" ]; then
        echo "🔧 Removing wrapper..."
        rm -f "$BIN_DIR/udos"
    fi
    
    # Remove symlink
    if [ -L "$BIN_DIR/udo" ]; then
        echo "🔗 Removing symlink..."
        rm -f "$BIN_DIR/udo"
    fi
    
    # Remove directory if empty
    if [ -d "$INSTALL_DIR" ] && [ -z "$(ls -A "$INSTALL_DIR")" ]; then
        echo "📁 Removing empty directory..."
        rmdir "$INSTALL_DIR"
    fi
    
    echo -e "${GREEN}✅ Uninstallation complete${NC}"
    echo "uDos CLI has been removed from your system."
}

# Main script logic
case "$ACTION" in
  "status")
    check_status
    ;;
  "install")
    install_cli
    ;;
  "update")
    update_cli
    ;;
  "repair")
    repair_cli
    ;;
  "uninstall")
    uninstall_cli
    ;;
  *)
    echo -e "${RED}❌ Unknown action: $ACTION${NC}"
    echo "Usage: udos-cli.sh [status|install|update|repair|uninstall] [force]"
    exit 1
    ;;
esac