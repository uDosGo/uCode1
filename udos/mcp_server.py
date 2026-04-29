#!/usr/bin/env python3
"""
MCP Server for uDos Core — thin wrapper.

This module now delegates to the shared mcp_server package in OkAgentDigital.
See: ~/Code/OkAgentDigital/mcp_server/

Usage (unchanged):
    python -m udos.mcp_server
"""

import sys
import os
from pathlib import Path

# Add OkAgentDigital to path so mcp_server package is importable
_okagent_root = Path(__file__).resolve().parent.parent.parent.parent / "OkAgentDigital"
sys.path.insert(0, str(_okagent_root))

# Also add uCode1 root so core_py is found when mcp_server.tools.udos loads
_ucode1_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ucode1_root))

from mcp_server.__main__ import main

if __name__ == "__main__":
    main()
