"""
uDos MCP Server package — thin wrapper.

Delegates to the shared mcp_server package in OkAgentDigital.
"""

__version__ = "1.0.0"
__author__ = "uDos Development Team"

# Re-export main from the shared package
import sys
from pathlib import Path

_okagent = Path(__file__).resolve().parent.parent.parent.parent / "OkAgentDigital"
sys.path.insert(0, str(_okagent))

_ucode1 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ucode1))

# Import and run the shared server with uDos tools
def main():
    from mcp_server.server import MCPServerManager
    manager = MCPServerManager(server_name="udos-core")
    manager.load_tools(["udos"])
    manager.run()

__all__ = ["main"]
