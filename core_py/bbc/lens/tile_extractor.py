"""
Tile Extractor — ACS Tile Grid Extraction (15x15 Maps)

Extracts tile grid data from ACS game memory and converts it into
structured tile maps suitable for rendering, analysis, and export.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple, Set
from enum import Enum, auto
import time

from .acs_memory_map import ACSMemoryMap, get_acs_memory_map


class TileCategory(Enum):
    """Category of tile for rendering and gameplay purposes"""
    WALL = auto()
    FLOOR = auto()
    DOOR = auto()
    TERRAIN = auto()
    WATER = auto()
    HAZARD = auto()
    OBJECT = auto()
    FURNITURE = auto()
    DECORATION = auto()
    MAGIC = auto()
    EXIT = auto()
    UNKNOWN = auto()


@dataclass
class Tile:
    """A single tile in the ACS tile grid"""
    x: int
    y: int
    tile_id: int
    tile_name: str
    category: TileCategory = TileCategory.UNKNOWN
    walkable: bool = False
    transparent: bool = False
    blocks_sight: bool = False
    is_door: bool = False
    is_trap: bool = False
    is_container: bool = False
    is_stairs: bool = False
    description: str = ""
    teleport_target: Optional[Tuple[int, int, int]] = None  # (room, x, y)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tile to dictionary"""
        return {
            "x": self.x,
            "y": self.y,
            "tile_id": self.tile_id,
            "tile_name": self.tile_name,
            "category": self.category.name,
            "walkable": self.walkable,
            "transparent": self.transparent,
            "blocks_sight": self.blocks_sight,
            "is_door": self.is_door,
            "is_trap": self.is_trap,
            "is_container": self.is_container,
            "is_stairs": self.is_stairs,
            "description": self.description,
        }


@dataclass
class TileGrid:
    """A complete 15x15 tile grid for a room"""
    room_id: int
    width: int = 15
    height: int = 15
    tiles: List[List[Tile]] = field(default_factory=list)
    player_x: int = 7
    player_y: int = 7
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.tiles:
            self.tiles = [[Tile(x, y, 0, "empty")
                          for x in range(self.width)]
                         for y in range(self.height)]
        if not self.timestamp:
            self.timestamp = time.time()

    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """Get tile at position"""
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.tiles[y][x]
        return None

    def set_tile(self, x: int, y: int, tile: Tile) -> None:
        """Set tile at position"""
        if 0 <= y < self.height and 0 <= x < self.width:
            self.tiles[y][x] = tile

    def find_player_position(self) -> Optional[Tuple[int, int]]:
        """Find the player's position on the grid"""
        return (self.player_x, self.player_y)

    def find_creatures(self, creature_positions: List[Tuple[int, int]]) -> List[Tuple[int, int, Tile]]:
        """Find creature positions on the grid"""
        results = []
        for cx, cy in creature_positions:
            tile = self.get_tile(cx, cy)
            if tile:
                results.append((cx, cy, tile))
        return results

    def get_walkable_tiles(self) -> List[Tuple[int, int]]:
        """Get all walkable tile positions"""
        walkable = []
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                if tile.walkable:
                    walkable.append((x, y))
        return walkable

    def get_exits(self) -> List[Tuple[int, int, str]]:
        """Get all exit tile positions with direction hints"""
        exits = []
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                if tile.is_stairs or tile.tile_name == "exit":
                    direction = "unknown"
                    if y == 0:
                        direction = "north"
                    elif y == self.height - 1:
                        direction = "south"
                    elif x == 0:
                        direction = "west"
                    elif x == self.width - 1:
                        direction = "east"
                    exits.append((x, y, direction))
        return exits

    def to_ascii(self, player_char: str = "@",
                 creature_positions: Optional[Dict[Tuple[int, int], str]] = None) -> str:
        """Render the tile grid as ASCII art"""
        TILE_CHARS = {
            "empty": " ",
            "wall": "#",
            "floor": ".",
            "door": "+",
            "locked_door": "+",
            "secret_door": "+",
            "stairs_up": "<",
            "stairs_down": ">",
            "water": "~",
            "lava": "~",
            "trap": "^",
            "chest": "=",
            "altar": "&",
            "fountain": "&",
            "torch": "i",
            "brazier": "O",
            "table": "_",
            "chair": "h",
            "bed": "=",
            "bookshelf": "#",
            "cabinet": "#",
            "barrel": "O",
            "crate": "O",
            "pillar": "O",
            "statue": "&",
            "pool": "~",
            "bridge": "=",
            "chasm": " ",
            "web": ";",
            "moss": ":",
            "rubble": ",",
            "grass": ",",
            "tree": "T",
            "bush": "#",
            "flower": '"',
            "path": ".",
            "road": ".",
            "teleporter": "O",
            "spinner": "O",
            "pit": " ",
            "spikes": "^",
            "exit": ">",
        }

        creature_map = creature_positions or {}
        lines = []
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                if (x, y) in creature_map:
                    row += creature_map[(x, y)]
                elif x == self.player_x and y == self.player_y:
                    row += player_char
                else:
                    tile = self.tiles[y][x]
                    char = TILE_CHARS.get(tile.tile_name, "?")
                    row += char
            lines.append(row)
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tile grid to dictionary"""
        return {
            "room_id": self.room_id,
            "width": self.width,
            "height": self.height,
            "player_x": self.player_x,
            "player_y": self.player_y,
            "timestamp": self.timestamp,
            "tiles": [[t.to_dict() for t in row] for row in self.tiles],
        }


# Tile property lookup table
TILE_PROPERTIES: Dict[int, Dict[str, Any]] = {
    0x00: {"name": "empty", "walkable": True, "transparent": True, "category": TileCategory.FLOOR},
    0x01: {"name": "wall", "walkable": False, "transparent": False, "category": TileCategory.WALL},
    0x02: {"name": "floor", "walkable": True, "transparent": True, "category": TileCategory.FLOOR},
    0x03: {"name": "door", "walkable": True, "transparent": True, "is_door": True, "category": TileCategory.DOOR},
    0x04: {"name": "locked_door", "walkable": False, "transparent": True, "is_door": True, "category": TileCategory.DOOR},
    0x05: {"name": "secret_door", "walkable": True, "transparent": False, "is_door": True, "category": TileCategory.DOOR},
    0x06: {"name": "stairs_up", "walkable": True, "transparent": True, "is_stairs": True, "category": TileCategory.EXIT},
    0x07: {"name": "stairs_down", "walkable": True, "transparent": True, "is_stairs": True, "category": TileCategory.EXIT},
    0x08: {"name": "water", "walkable": False, "transparent": True, "category": TileCategory.WATER},
    0x09: {"name": "lava", "walkable": False, "transparent": True, "category": TileCategory.HAZARD},
    0x0A: {"name": "trap", "walkable": True, "transparent": True, "is_trap": True, "category": TileCategory.HAZARD},
    0x0B: {"name": "chest", "walkable": False, "transparent": True, "is_container": True, "category": TileCategory.OBJECT},
    0x0C: {"name": "altar", "walkable": False, "transparent": True, "category": TileCategory.OBJECT},
    0x0D: {"name": "fountain", "walkable": False, "transparent": True, "category": TileCategory.OBJECT},
    0x0E: {"name": "torch", "walkable": False, "transparent": True, "category": TileCategory.DECORATION},
    0x0F: {"name": "brazier", "walkable": False, "transparent": True, "category": TileCategory.DECORATION},
    0x10: {"name": "table", "walkable": False, "transparent": True, "category": TileCategory.FURNITURE},
    0x11: {"name": "chair", "walkable": False, "transparent": True, "category": TileCategory.FURNITURE},
    0x12: {"name": "bed", "walkable": False, "transparent": True, "category": TileCategory.FURNITURE},
    0x13: {"name": "bookshelf", "walkable": False, "transparent": False, "category": TileCategory.FURNITURE},
    0x14: {"name": "cabinet", "walkable": False, "transparent": False, "category": TileCategory.FURNITURE},
    0x15: {"name": "barrel", "walkable": False, "transparent": True, "category": TileCategory.OBJECT},
    0x16: {"name": "crate", "walkable": False, "transparent": True, "category": TileCategory.OBJECT},
    0x17: {"name": "pillar", "walkable": False, "transparent": False, "category": TileCategory.DECORATION},
    0x18: {"name": "statue", "walkable": False, "transparent": True, "category": TileCategory.DECORATION},
    0x19: {"name": "fountain", "walkable": False, "transparent": True, "category": TileCategory.OBJECT},
    0x1A: {"name": "pool", "walkable": False, "transparent": True, "category": TileCategory.WATER},
    0x1B: {"name": "bridge", "walkable": True, "transparent": True, "category": TileCategory.TERRAIN},
    0x1C: {"name": "chasm", "walkable": False, "transparent": True, "category": TileCategory.HAZARD},
    0x1D: {"name": "web", "walkable": True, "transparent": True, "category": TileCategory.HAZARD},
    0x1E: {"name": "moss", "walkable": True, "transparent": True, "category": TileCategory.DECORATION},
    0x1F: {"name": "rubble", "walkable": True, "transparent": True, "category": TileCategory.TERRAIN},
    0x20: {"name": "grass", "walkable": True, "transparent": True, "category": TileCategory.TERRAIN},
    0x21: {"name": "tree", "walkable": False, "transparent": False, "category": TileCategory.TERRAIN},
    0x22: {"name": "bush", "walkable": False, "transparent": False, "category": TileCategory.TERRAIN},
    0x23: {"name": "flower", "walkable": True, "transparent": True, "category": TileCategory.DECORATION},
    0x24: {"name": "path", "walkable": True, "transparent": True, "category": TileCategory.TERRAIN},
    0x25: {"name": "road", "walkable": True, "transparent": True, "category": TileCategory.TERRAIN},
    0x3B: {"name": "teleporter", "walkable": True, "transparent": True, "category": TileCategory.MAGIC},
    0x3C: {"name": "spinner", "walkable": True, "transparent": True, "category": TileCategory.MAGIC},
    0x3D: {"name": "pit", "walkable": False, "transparent": True, "category": TileCategory.HAZARD},
    0x3E: {"name": "spikes", "walkable": False, "transparent": True, "category": TileCategory.HAZARD},
    0x3F: {"name": "exit", "walkable": True, "transparent": True, "is_stairs": True, "category": TileCategory.EXIT},
}


class TileExtractor:
    """
    Extracts tile grid data from ACS game memory.

    Reads the 15x15 tile grid from memory and converts raw tile IDs
    into structured Tile objects with properties, descriptions, and
    rendering hints.
    """

    def __init__(self, memory_map: Optional[ACSMemoryMap] = None):
        """
        Initialize tile extractor.

        Args:
            memory_map: ACS memory map instance (uses singleton if None)
        """
        self.memory_map = memory_map or get_acs_memory_map()
        self._last_grid: Optional[TileGrid] = None
        self._grid_history: List[TileGrid] = []
        self._max_history: int = 100

    def extract_grid(self, memory_reader, room_id: int,
                     player_x: int = 7, player_y: int = 7) -> TileGrid:
        """
        Extract the 15x15 tile grid from ACS memory.

        Args:
            memory_reader: Object with read_byte(address) method
            room_id: Current room identifier
            player_x: Player X position
            player_y: Player Y position

        Returns:
            TileGrid with extracted tiles
        """
        grid = TileGrid(
            room_id=room_id,
            player_x=player_x,
            player_y=player_y,
        )

        mm = self.memory_map
        for y in range(mm.TILE_GRID_HEIGHT):
            row = []
            for x in range(mm.TILE_GRID_WIDTH):
                addr = mm.get_tile_grid_address(x, y)
                tile_id = memory_reader.read_byte(addr)
                tile = self._create_tile(x, y, tile_id)
                row.append(tile)
            grid.tiles.append(row)

        self._last_grid = grid
        self._grid_history.append(grid)
        if len(self._grid_history) > self._max_history:
            self._grid_history.pop(0)

        return grid

    def extract_grid_from_raw(self, raw_data: bytes, room_id: int,
                               player_x: int = 7, player_y: int = 7) -> TileGrid:
        """
        Extract tile grid from raw byte data (225 bytes).

        Args:
            raw_data: 225 bytes of tile grid data
            room_id: Current room identifier
            player_x: Player X position
            player_y: Player Y position

        Returns:
            TileGrid with extracted tiles
        """
        grid = TileGrid(
            room_id=room_id,
            player_x=player_x,
            player_y=player_y,
        )

        mm = self.memory_map
        for y in range(mm.TILE_GRID_HEIGHT):
            row = []
            for x in range(mm.TILE_GRID_WIDTH):
                idx = y * mm.TILE_GRID_WIDTH + x
                tile_id = raw_data[idx] if idx < len(raw_data) else 0
                tile = self._create_tile(x, y, tile_id)
                row.append(tile)
            grid.tiles.append(row)

        return grid

    def _create_tile(self, x: int, y: int, tile_id: int) -> Tile:
        """Create a Tile object from a tile ID"""
        props = TILE_PROPERTIES.get(tile_id, {})
        name = props.get("name", self.memory_map.get_tile_name(tile_id))

        return Tile(
            x=x,
            y=y,
            tile_id=tile_id,
            tile_name=name,
            category=props.get("category", TileCategory.UNKNOWN),
            walkable=props.get("walkable", False),
            transparent=props.get("transparent", False),
            blocks_sight=not props.get("transparent", True),
            is_door=props.get("is_door", False),
            is_trap=props.get("is_trap", False),
            is_container=props.get("is_container", False),
            is_stairs=props.get("is_stairs", False),
            description=props.get("description", ""),
        )

    def detect_grid_changes(self, new_grid: TileGrid) -> Dict[str, Any]:
        """
        Detect changes between the last extracted grid and a new one.

        Args:
            new_grid: Recently extracted tile grid

        Returns:
            Dict with 'changed_tiles' list and 'summary' string
        """
        if not self._last_grid:
            return {"changed_tiles": [], "summary": "initial capture"}

        changes = []
        for y in range(new_grid.height):
            for x in range(new_grid.width):
                old_tile = self._last_grid.get_tile(x, y)
                new_tile = new_grid.get_tile(x, y)
                if old_tile and new_tile and old_tile.tile_id != new_tile.tile_id:
                    changes.append({
                        "x": x, "y": y,
                        "old": old_tile.tile_name,
                        "new": new_tile.tile_name,
                    })

        return {
            "changed_tiles": changes,
            "summary": f"{len(changes)} tile(s) changed" if changes else "no changes",
        }

    def get_grid_history(self) -> List[TileGrid]:
        """Get the history of extracted grids"""
        return list(self._grid_history)

    def clear_history(self) -> None:
        """Clear grid extraction history"""
        self._grid_history.clear()
        self._last_grid = None
