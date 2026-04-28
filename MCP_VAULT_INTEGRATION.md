# MCP Vault Integration Guide

This guide explains how to integrate external web chat UIs with the uDos vault using the Model Context Protocol (MCP).

## Overview

The uDos MCP server provides a Unix socket interface that allows any MCP-compatible client to read from and write to the user's vault. The vault can be either:

1. **A local directory** on the master node (default: `~/vault/`)
2. **A private GitHub repository** synced with the local vault

## MCP Server

The MCP server is implemented in Rust as part of the `ucode2-mcp` crate (in the uCode2 workspace) and provides the following vault operations:

### Available Tools

| Tool | Description | Request | Response |
|------|-------------|---------|----------|
| `vault_read` | Read file content | `VaultRead { path: String }` | `VaultContent { path: String, content: String }` |
| `vault_write` | Write file content | `VaultWrite { path: String, content: String }` | `Success { data: Value }` |
| `vault_list` | List directory contents | `VaultList { path: String }` | `VaultList { path: String, items: Vec<String> }` |
| `vault_search` | Search files by content | `VaultSearch { query: String }` | `VaultSearchResults { query: String, results: Vec<String> }` |
| `vault_delete` | Move file to trash | `VaultDelete { path: String }` | `Success { data: Value }` |
| `vault_metadata` | Get file metadata | `VaultMetadata { path: String }` | `VaultMetadata { path: String, size: u64, modified: String, tags: Vec<String> }` |
| `vault_watch` | Watch for changes | `VaultWatch { path: String }` | `VaultWatchEvent { event: String, path: String }` (not yet implemented) |

## Socket Location

The MCP server creates a Unix domain socket at:
```
~/vault/.local/mcp.sock
```

## Protocol

The MCP server uses a simple JSON-based protocol over Unix sockets:

### Request Format
```json
{
  "type": "request",
  "id": "unique-request-id",
  "method": "vault_read",
  "params": {
    "path": "document.md"
  }
}
```

### Response Format
```json
{
  "type": "response",
  "id": "unique-request-id",
  "result": {
    "path": "document.md",
    "content": "File content..."
  },
  "error": null
}
```

## Integration Modes

### Mode A: Local Network Access (Recommended)

For chat UIs running on the same local network:

1. **Direct connection**: Connect to the MCP server via local network
2. **Socket forwarding**: Use `socat` or similar to forward the Unix socket to TCP

```bash
# Forward Unix socket to TCP port
socat TCP-LISTEN:3010,reuseaddr,fork UNIX-CONNECT:~/vault/.local/mcp.sock
```

Then configure your chat UI to connect to `tcp://localhost:3010`

### Mode B: Cloud Access with Tunnel

For cloud-based chat UIs (LeChat, Claude.ai, etc.):

1. **Tailscale Funnel**: Expose the local service securely
   ```bash
   tailscale funnel --bg 3010
   ```

2. **Ngrok**: Create a public tunnel
   ```bash
   ngrok tcp 3010
   ```

3. **Custom bridge**: Create a small HTTPS server that forwards to the Unix socket

### Mode C: GitHub Sync

For maximum security, use GitHub as the sync point:

1. **Local changes** → GitHub: Use a GitHub Action that watches the repo and pulls changes
2. **Remote changes** → Local: Use MCP tools to commit and push changes to GitHub

## Starting the MCP Server

The MCP server is started automatically when you run:
```bash
udos dev
```

Or manually:
```bash
cargo run --bin mcp-server
```

## Example Usage

### Reading a File

**Request:**
```json
{
  "type": "request",
  "id": "1",
  "method": "vault_read",
  "params": {
    "path": "notes/project-ideas.md"
  }
}
```

**Response:**
```json
{
  "type": "response",
  "id": "1",
  "result": {
    "path": "notes/project-ideas.md",
    "content": "# Project Ideas\n\n1. Implement MCP vault integration\n2. Add GitHub sync support\n..."
  },
  "error": null
}
```

### Writing a File

**Request:**
```json
{
  "type": "request",
  "id": "2",
  "method": "vault_write",
  "params": {
    "path": "notes/meeting-notes.md",
    "content": "# Meeting Notes\n\n- Discussed MCP integration\n- Decided on Unix socket approach\n..."
  }
}
```

**Response:**
```json
{
  "type": "response",
  "id": "2",
  "result": {
    "message": "File written successfully"
  },
  "error": null
}
```

## Security Considerations

1. **Permissions**: The Unix socket has restrictive permissions (600) - only the owner can access
2. **Authentication**: Consider adding token-based auth for remote access
3. **Encryption**: Use TLS for any network-exposed endpoints
4. **Rate limiting**: Implement rate limiting for public endpoints

## Configuration

Configure the vault location in `~/vault/system/settings.obf`:
```yaml
vault:
  path: "~/vault"
  mcp:
    enabled: true
    socket: ".local/mcp.sock"
    network:
      enabled: false
      port: 3010
```

## Connecting Chat UIs

### LeChat Configuration

```json
{
  "mcp": {
    "enabled": true,
    "endpoint": "ws://localhost:3010",
    "tools": ["vault_read", "vault_write", "vault_list", "vault_search"]
  }
}
```

### Claude Desktop Configuration

```json
{
  "external_tools": {
    "udos_vault": {
      "type": "mcp",
      "url": "ws://localhost:3010",
      "capabilities": ["read", "write", "list", "search"]
    }
  }
}
```

## Troubleshooting

**Socket not found:**
- Ensure the MCP server is running: `udos dev`
- Check socket permissions: `ls -la ~/vault/.local/`
- Verify socket path in settings

**Permission denied:**
- Check socket permissions: `chmod 600 ~/vault/.local/mcp.sock`
- Ensure your user owns the socket

**Connection refused:**
- Check if the server is running: `ps aux | grep mcp`
- Verify the socket exists: `ls ~/vault/.local/mcp.sock`
- Check for port conflicts if using TCP forwarding

## Future Enhancements

1. **WebSocket support**: Add WebSocket protocol for browser-based clients
2. **Authentication**: Implement token-based authentication
3. **Watch API**: Complete the file watch functionality
4. **Batch operations**: Add support for batch requests
5. **Versioning**: Implement file versioning and history

## Development

To test the MCP server:
```bash
# Start the server
cargo run --bin mcp-server

# Test with netcat
nc -U ~/vault/.local/mcp.sock
```

To add new tools:
1. Add the request/response types to `McpRequest` and `McpResponse` enums
2. Implement the handler in the `handle_connection` method
3. Add any required vault methods to the vault bridge
4. Update this documentation

## License

MIT License - See LICENSE for details.