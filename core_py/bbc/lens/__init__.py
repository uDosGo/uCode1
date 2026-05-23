"""
LENS Layer — Data Extraction Engine for uCode1

The LENS (Looking Into the Game) layer reads emulated game memory and
emits structured data to the Feed or Spool. This package provides
game-specific extraction capabilities for supported games.

Submodules:
    acs_memory_map     — ACS memory map with known addresses
    tile_extractor     — Tile grid extraction (15x15 maps)
    room_parser        — Room description parsing
    inventory_extractor — Inventory data extraction
    creature_tracker   — Creature/character tracking
    story_flag_monitor — Story flag monitoring
    player_stats       — Player statistics capture
    output_format      — LENS output format specification
"""

from .acs_memory_map import ACSMemoryMap, ACS_MEMORY_MAP, get_acs_memory_map
from .tile_extractor import TileExtractor, TileGrid, Tile
from .room_parser import RoomParser, RoomDescription
from .inventory_extractor import InventoryExtractor, InventoryItem, InventorySlot
from .creature_tracker import CreatureTracker, Creature, CreatureState
from .story_flag_monitor import StoryFlagMonitor, StoryFlag, StoryFlagState
from .player_stats import PlayerStats, PlayerStatsCapture
from .output_format import LENSOutputFormat, LENSOutputWriter, LENSOutputReader

__all__ = [
    "ACSMemoryMap", "ACS_MEMORY_MAP", "get_acs_memory_map",
    "TileExtractor", "TileGrid", "Tile",
    "RoomParser", "RoomDescription",
    "InventoryExtractor", "InventoryItem", "InventorySlot",
    "CreatureTracker", "Creature", "CreatureState",
    "StoryFlagMonitor", "StoryFlag", "StoryFlagState",
    "PlayerStats", "PlayerStatsCapture",
    "LENSOutputFormat", "LENSOutputWriter", "LENSOutputReader",
]
