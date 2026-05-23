"""
LENS Output Format — Structured Data Export Specification

Defines the output format for LENS-extracted game data, providing
serialization to JSON, structured dicts, and narrative text.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any
import json
import time


@dataclass
class LENSOutputFormat:
    """
    Standard output format for LENS-extracted game data.

    This is the canonical format that all LENS extractors produce,
    designed to be consumed by the Feed, Spool, or external tools.
    """
    game_id: str
    game_name: str
    timestamp: float = 0.0
    version: str = "1.0"

    # Player stats
    player: Optional[Dict[str, Any]] = None

    # Current room
    room: Optional[Dict[str, Any]] = None

    # Tile grid (15x15)
    tile_grid: Optional[Dict[str, Any]] = None

    # Inventory
    inventory: List[Dict[str, Any]] = field(default_factory=list)
    equipment: Dict[str, Any] = field(default_factory=dict)

    # Creatures
    creatures: List[Dict[str, Any]] = field(default_factory=list)

    # Story flags
    story_flags: Optional[Dict[str, Any]] = None

    # Events
    events: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary"""
        return {
            "game_id": self.game_id,
            "game_name": self.game_name,
            "timestamp": self.timestamp,
            "version": self.version,
            "player": self.player,
            "room": self.room,
            "tile_grid": self.tile_grid,
            "inventory": self.inventory,
            "equipment": self.equipment,
            "creatures": self.creatures,
            "story_flags": self.story_flags,
            "events": self.events,
            "metadata": self.metadata,
        }

    def to_json(self, pretty: bool = False) -> str:
        """Serialize to JSON string"""
        indent = 2 if pretty else None
        return json.dumps(self.to_dict(), indent=indent, default=str)

    def to_narrative(self) -> str:
        """Generate a human-readable narrative of the game state"""
        parts = [f"=== {self.game_name} ==="]

        if self.player:
            p = self.player
            parts.append(
                f"HP: {p.get('hp', '?')}/{p.get('max_hp', '?')} | "
                f"Gold: {p.get('gold', '?')} | "
                f"Level: {p.get('level', '?')} | "
                f"Room: {p.get('current_room', '?')}"
            )

        if self.room:
            r = self.room
            parts.append(f"\nLocation: {r.get('name', 'Unknown')}")
            parts.append(r.get('description', ''))
            if r.get('exits'):
                exit_str = ", ".join(e['direction'] for e in r['exits'])
                parts.append(f"Exits: {exit_str}")

        if self.creatures:
            alive = [c for c in self.creatures if c.get('state') != 'dead']
            if alive:
                parts.append(f"\nCreatures: {', '.join(c['creature_name'] for c in alive)}")

        if self.inventory:
            parts.append(f"\nInventory: {len(self.inventory)} item(s)")

        if self.events:
            parts.append(f"\nRecent events: {len(self.events)}")

        return "\n".join(parts)


class LENSOutputWriter:
    """
    Writes LENS output data to files or streams.

    Supports JSON format with optional pretty-printing and
    metadata enrichment.
    """

    def __init__(self):
        self._outputs: List[LENSOutputFormat] = []

    def write_output(self, output: LENSOutputFormat) -> None:
        """Record an output"""
        self._outputs.append(output)

    def write_to_file(self, output: LENSOutputFormat, filepath: str,
                      pretty: bool = True) -> None:
        """
        Write a LENS output to a JSON file.

        Args:
            output: LENSOutputFormat to write
            filepath: Path to output file
            pretty: Whether to pretty-print the JSON
        """
        with open(filepath, 'w') as f:
            f.write(output.to_json(pretty=pretty))

    def write_batch_to_file(self, filepath: str, pretty: bool = True) -> None:
        """
        Write all recorded outputs to a JSON file as an array.

        Args:
            filepath: Path to output file
            pretty: Whether to pretty-print the JSON
        """
        data = [o.to_dict() for o in self._outputs]
        indent = 2 if pretty else None
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=indent, default=str)

    def clear(self) -> None:
        """Clear all recorded outputs"""
        self._outputs.clear()


class LENSOutputReader:
    """
    Reads LENS output data from files or streams.

    Supports loading from JSON format and reconstructing
    LENSOutputFormat objects.
    """

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> LENSOutputFormat:
        """Create a LENSOutputFormat from a dictionary"""
        return LENSOutputFormat(
            game_id=data.get("game_id", "unknown"),
            game_name=data.get("game_name", "Unknown"),
            timestamp=data.get("timestamp", time.time()),
            version=data.get("version", "1.0"),
            player=data.get("player"),
            room=data.get("room"),
            tile_grid=data.get("tile_grid"),
            inventory=data.get("inventory", []),
            equipment=data.get("equipment", {}),
            creatures=data.get("creatures", []),
            story_flags=data.get("story_flags"),
            events=data.get("events", []),
            metadata=data.get("metadata", {}),
        )

    @staticmethod
    def from_json(json_str: str) -> LENSOutputFormat:
        """Create a LENSOutputFormat from a JSON string"""
        data = json.loads(json_str)
        return LENSOutputReader.from_dict(data)

    @staticmethod
    def from_file(filepath: str) -> LENSOutputFormat:
        """Create a LENSOutputFormat from a JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return LENSOutputReader.from_dict(data)

    @staticmethod
    def read_batch_from_file(filepath: str) -> List[LENSOutputFormat]:
        """Read multiple LENS outputs from a JSON file (array format)"""
        with open(filepath, 'r') as f:
            data_list = json.load(f)
        return [LENSOutputReader.from_dict(d) for d in data_list]
