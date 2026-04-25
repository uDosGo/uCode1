# uCode1

Next generation uDos platform (2026)

## Structure

- `core/` - Main CLI binary and core functionality
- `ok-agent/` - OK helper (local intent/LLM)
- `spatial/` - 2D vector index and maps
- `tui/` - Grid/teletext renderer
- `vault-bridge/` - Vault read/write integration

## Building

```bash
# User mode (default)
cargo build --release

# Dev mode
cargo run -- --dev
```

## Configuration

- User mode: Uses `~/Code/Vault` by default
- Dev mode: Can override with `.dev.yaml`

## License

MIT