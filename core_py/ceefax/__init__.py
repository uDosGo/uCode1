"""
Ceefax — Teletext Rendering Bridge for uCode1

This module provides the teletext rendering bridge that converts
game output (ANSI/ASCII) to teletext grid format (40x25) for
display via GridUI.

Key components:
    - GameToTeletextBridge: Converts game output to teletext grid
    - TeletextGrid: 40x25 character grid with colour attributes
    - ColourMapper: Maps game colours to teletext palette
"""

from .bridge import (
    GameToTeletextBridge,
    TeletextGrid,
    TeletextCell,
    ColourMapper,
    TeletextColour,
    create_bridge,
)

__all__ = [
    "GameToTeletextBridge",
    "TeletextGrid",
    "TeletextCell",
    "ColourMapper",
    "TeletextColour",
    "create_bridge",
]
