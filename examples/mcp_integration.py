#!/usr/bin/env python3
"""
MCP Integration Example

This example demonstrates how uCode1 (Python) communicates with uCode2 (Rust)
via the MCP server socket.

Prerequisites:
1. uCode2 MCP server must be running
2. Socket must be available at ~/.local/mcp.sock

Usage:
    python examples/mcp_integration.py
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core_py.mcp_client import (
    McpClient,
    McpConnectionError,
    test_connection,
    get_default_socket_path
)


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_result(label, value):
    """Print a labeled result."""
    print(f"  {label}: {value}")


def print_error(label, error):
    """Print an error."""
    print(f"  {label}: ERROR - {error}")


def main():
    """Main example function."""
    print_header("uCode1/uCode2 MCP Integration Demo")
    
    # Check socket path
    socket_path = get_default_socket_path()
    print_result("MCP Socket Path", str(socket_path))
    
    # Test if server is available
    print("\n  Testing MCP server connection...")
    if test_connection():
        print("  ✓ MCP server is running and responding")
    else:
        print("  ✗ MCP server is not available")
        print("\n  To start the MCP server:")
        print("    cd uCode2 && cargo run --package ucode2-mcp")
        print("  Or start uCode1 CLI:")
        print("    cd uCode2 && cargo run --package ucode1-cli -- --status")
        return 1
    
    # Create client
    print("\n  Creating MCP client...")
    try:
        client = McpClient()
        print("  ✓ Client created and connected")
    except McpConnectionError as e:
        print_error("Client connection", e)
        return 1
    
    # Test ping
    print_header("Testing MCP Operations")
    print("\n  1. Ping Test")
    try:
        response = client.ping()
        print_result("Ping", "Pong!" if response.is_success else "Failed")
    except Exception as e:
        print_error("Ping", e)
    
    # Test status
    print("\n  2. Status Test")
    try:
        response = client.status()
        if response.status_info:
            for key, value in response.status_info.items():
                print_result(f"  Status {key}", value)
        else:
            print_result("Status", response.raw_data)
    except Exception as e:
        print_error("Status", e)
    
    # Test notes operations
    print("\n  3. Notes Operations")
    try:
        response = client.list_notes()
        if response.notes:
            print_result("Notes count", len(response.notes))
            for note in response.notes[:5]:  # Show first 5
                print(f"    - {note}")
            if len(response.notes) > 5:
                print(f"    ... and {len(response.notes) - 5} more")
        else:
            print("    No notes found")
    except Exception as e:
        print_error("List notes", e)
    
    # Test vault operations
    print("\n  4. Vault Operations")
    try:
        response = client.vault_list("/")
        if response.vault_list:
            items = response.vault_list.get("items", [])
            print_result("Vault items", len(items))
            for item in items[:10]:
                print(f"    - {item}")
            if len(items) > 10:
                print(f"    ... and {len(items) - 10} more")
        else:
            print("    No vault items found")
    except Exception as e:
        print_error("Vault list", e)
    
    # Test intent classification
    print("\n  5. Intent Classification")
    try:
        response = client.classify_intent("What is the weather today?")
        if response.intent:
            print_result("Intent", response.intent.get("intent", "unknown"))
            print_result("Confidence", response.intent.get("confidence", 0))
        else:
            print("    No intent detected")
    except Exception as e:
        print_error("Classify intent", e)
    
    # Close client
    client.close()
    print("\n  ✓ Client disconnected")
    
    print_header("Demo Complete")
    print("\n  Next steps:")
    print("  - Explore the MCP API in core_py/mcp_client.py")
    print("  - Check uCode2/mcp/src/lib.rs for server implementation")
    print("  - Run all tests: pytest uCode1/tests/ uCode1/test_*.py")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
