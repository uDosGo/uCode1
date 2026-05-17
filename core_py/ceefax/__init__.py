"""
Ceefax — Teletext Rendering Bridge for uCode1

This module provides the teletext rendering bridge that converts
game output (ANSI/ASCII) to teletext grid format (40x25) for
display via CeefaxThinUI.

Key components:
    - GameToTeletextBridge: Converts game output to teletext grid
    - TeletextGrid: 40x25 character grid with colour attributes
    - ColourMapper: Maps game colours to teletext palette
    - CeetexUCodeApp: Textual-based CEETEX teletext RSS reader app
    - CeetexLENSAdapter: LENS state capture for CEETEX
    - CeetexSKINAdapter: SKIN hot-reload for CEETEX
    - CeetexMCPController: MCP remote control for CEETEX
"""

from .bridge import (
    GameToTeletextBridge,
    TeletextGrid,
    TeletextCell,
    ColourMapper,
    TeletextColour,
    create_bridge,
)

from .ceetex_app import (
    CeetexUCodeApp,
    CeetexLENSAdapter,
    CeetexSKINAdapter,
    CeetexMCPController,
    CEETEX_SKINS,
    run_ceetex,
)

__all__ = [
    # Bridge
    "GameToTeletextBridge",
    "TeletextGrid",
    "TeletextCell",
    "ColourMapper",
    "TeletextColour",
    "create_bridge",
    # CEETEX Integration
    "CeetexUCodeApp",
    "CeetexLENSAdapter",
    "CeetexSKINAdapter",
    "CeetexMCPController",
    "CEETEX_SKINS",
    "run_ceetex",
]
