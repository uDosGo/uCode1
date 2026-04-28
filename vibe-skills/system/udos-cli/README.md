# uDos CLI Management Skill

A Vibe skill for installing, updating, repairing, and managing the uDos CLI locally.

## Features

- **Install**: Build and install uDos CLI from source
- **Update**: Rebuild and update existing installation
- **Repair**: Fix broken installations automatically
- **Status**: Check current installation status
- **Uninstall**: Remove uDos CLI completely

## Usage

```bash
# Check installation status
vibe udos-cli status

# Install uDos CLI
vibe udos-cli install

# Update uDos CLI
vibe udos-cli update

# Repair installation (automatic detection)
vibe udos-cli repair

# Force repair (reinstall everything)
vibe udos-cli repair yes

# Uninstall uDos CLI
vibe udos-cli uninstall
```

## Installation Details

The skill installs uDos CLI to:
- **Binary**: `~/.local/share/udos/bin/udos`
- **Wrapper**: `~/.local/bin/udos`
- **Alias**: `~/.local/bin/udo` (symlink to wrapper)

## Requirements

- Rust/Cargo for building from source
- uDosGo repository cloned to `~/Code/uDosGo` (configurable via `UDOSGO_ROOT`)
- `~/.local/bin` in your PATH

## Configuration

You can override the default uDosGo location:

```bash
export UDOSGO_ROOT=/path/to/your/uDosGo
vibe udos-cli install
```

## Troubleshooting

If you get "command not found" errors:

1. Make sure `~/.local/bin` is in your PATH:
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

2. Run repair with force flag:
   ```bash
   vibe udos-cli repair yes
   ```

3. Check the status for detailed information:
   ```bash
   vibe udos-cli status
   ```

## Skill Structure

```
uCode1/vibe-skills/system/udos-cli/
├── skill.yaml          # Skill definition
├── udos-cli.sh         # Main script
└── README.md           # Documentation
```

## Development

To test the skill directly:

```bash
cd uCode1/vibe-skills/system/udos-cli
./udos-cli.sh status
./udos-cli.sh install
```