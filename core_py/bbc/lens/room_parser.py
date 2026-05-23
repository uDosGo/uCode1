"""
Room Parser — ACS Room Description Parsing

Parses room description strings from ACS game memory and extracts
structured room data including exits, features, and narrative text.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import re
import time

from .acs_memory_map import ACSMemoryMap, get_acs_memory_map


@dataclass
class RoomExit:
    """An exit from a room"""
    direction: str  # "north", "south", "east", "west", "up", "down"
    target_room: int
    is_locked: bool = False
    is_secret: bool = False
    is_blocked: bool = False
    key_id: Optional[int] = None
    description: str = ""


@dataclass
class RoomFeature:
    """A notable feature in a room"""
    name: str
    description: str
    feature_type: str = "generic"  # "altar", "fountain", "chest", "statue", etc.
    interactable: bool = False
    is_trap: bool = False
    is_container: bool = False
    contains_item: Optional[int] = None


@dataclass
class RoomDescription:
    """A fully parsed room description"""
    room_id: int
    name: str
    description: str
    room_type: str = "dungeon"
    exits: List[RoomExit] = field(default_factory=list)
    features: List[RoomFeature] = field(default_factory=list)
    light_level: int = 50
    temperature: int = 50
    is_dark: bool = False
    is_magic: bool = False
    is_safe: bool = False
    is_trapped: bool = False
    is_locked: bool = False
    is_secret: bool = False
    is_boss_room: bool = False
    is_exit: bool = False
    creature_count: int = 0
    item_count: int = 0
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize room description to dictionary"""
        return {
            "room_id": self.room_id,
            "name": self.name,
            "description": self.description,
            "room_type": self.room_type,
            "exits": [{"direction": e.direction, "target_room": e.target_room,
                       "is_locked": e.is_locked, "is_secret": e.is_secret,
                       "description": e.description} for e in self.exits],
            "features": [{"name": f.name, "description": f.description,
                          "feature_type": f.feature_type, "interactable": f.interactable}
                         for f in self.features],
            "light_level": self.light_level,
            "temperature": self.temperature,
            "is_dark": self.is_dark,
            "is_magic": self.is_magic,
            "is_safe": self.is_safe,
            "is_trapped": self.is_trapped,
            "is_locked": self.is_locked,
            "is_secret": self.is_secret,
            "is_boss_room": self.is_boss_room,
            "is_exit": self.is_exit,
            "creature_count": self.creature_count,
            "item_count": self.item_count,
            "timestamp": self.timestamp,
        }

    def get_narrative(self) -> str:
        """Generate a narrative description of the room"""
        parts = [self.description]

        if self.exits:
            exit_desc = "Exits: " + ", ".join(
                f"{e.direction}" + (" (locked)" if e.is_locked else "")
                for e in self.exits
            )
            parts.append(exit_desc)

        if self.features:
            feature_desc = "You see: " + ", ".join(f.name for f in self.features)
            parts.append(feature_desc)

        if self.creature_count > 0:
            parts.append(f"There are {self.creature_count} creature(s) here.")

        if self.item_count > 0:
            parts.append(f"You spot {self.item_count} item(s) on the ground.")

        return "\n".join(parts)


class RoomParser:
    """
    Parses room descriptions from ACS game memory.

    Reads room data from memory and produces structured RoomDescription
    objects with parsed exits, features, and narrative text.
    """

    def __init__(self, memory_map: Optional[ACSMemoryMap] = None):
        """
        Initialize room parser.

        Args:
            memory_map: ACS memory map instance (uses singleton if None)
        """
        self.memory_map = memory_map or get_acs_memory_map()

    def parse_room(self, memory_reader, room_id: int) -> RoomDescription:
        """
        Parse a room description from ACS memory.

        Args:
            memory_reader: Object with read_byte(address) and read_string(address, length) methods
            room_id: Room identifier

        Returns:
            RoomDescription with parsed data
        """
        mm = self.memory_map

        # Read room data block
        room_addr = mm.get_room_definition_address(room_id)

        # Read room name from description string
        desc_addr = mm.get_room_description_address(room_id)
        raw_description = memory_reader.read_string(desc_addr, 64)

        # Parse room name (first line) and description (rest)
        name, description = self._parse_name_and_description(raw_description)

        # Read room type and flags
        room_type_id = memory_reader.read_byte(room_addr + 0x01)
        light_level = memory_reader.read_byte(room_addr + 0x02)
        temperature = memory_reader.read_byte(room_addr + 0x03)
        flags = memory_reader.read_byte(room_addr + 0x04)

        # Read exits
        exits = self._parse_exits(memory_reader, room_addr)

        # Read creature and item counts
        creature_count = memory_reader.read_byte(room_addr + 0x0B)
        item_count = memory_reader.read_byte(room_addr + 0x0C)

        # Parse features from description
        features = self._parse_features(description)

        room_type_names = {
            0: "dungeon", 1: "cavern", 2: "outdoor", 3: "town",
            4: "castle", 5: "temple", 6: "forest", 7: "water",
        }

        return RoomDescription(
            room_id=room_id,
            name=name,
            description=description,
            room_type=room_type_names.get(room_type_id, "unknown"),
            exits=exits,
            features=features,
            light_level=light_level,
            temperature=temperature,
            is_dark=bool(flags & 0x01),
            is_magic=bool(flags & 0x02),
            is_safe=bool(flags & 0x04),
            is_trapped=bool(flags & 0x08),
            is_locked=bool(flags & 0x10),
            is_secret=bool(flags & 0x20),
            is_boss_room=bool(flags & 0x40),
            is_exit=bool(flags & 0x80),
            creature_count=creature_count,
            item_count=item_count,
        )

    def _parse_name_and_description(self, raw: str) -> Tuple[str, str]:
        """Parse room name and description from raw string"""
        lines = raw.strip().split("\n")
        name = lines[0].strip() if lines else "Unknown Room"
        description = "\n".join(lines[1:]).strip() if len(lines) > 1 else ""
        return name, description

    def _parse_exits(self, memory_reader, room_addr: int) -> List[RoomExit]:
        """Parse room exits from memory"""
        directions = ["north", "south", "east", "west", "up", "down"]
        exit_offsets = [0x05, 0x06, 0x07, 0x08, 0x09, 0x0A]
        exits = []

        for direction, offset in zip(directions, exit_offsets):
            target = memory_reader.read_byte(room_addr + offset)
            if target != 0:
                exits.append(RoomExit(
                    direction=direction,
                    target_room=target,
                ))

        return exits

    def _parse_features(self, description: str) -> List[RoomFeature]:
        """Parse room features from description text"""
        features = []
        feature_keywords = {
            "altar": "altar",
            "fountain": "fountain",
            "chest": "chest",
            "statue": "statue",
            "table": "table",
            "chair": "chair",
            "bed": "bed",
            "bookshelf": "bookshelf",
            "cabinet": "cabinet",
            "barrel": "barrel",
            "crate": "crate",
            "pillar": "pillar",
            "brazier": "brazier",
            "torch": "torch",
            "pool": "pool",
            "bridge": "bridge",
        }

        desc_lower = description.lower()
        for keyword, feature_type in feature_keywords.items():
            if keyword in desc_lower:
                features.append(RoomFeature(
                    name=keyword.capitalize(),
                    description=f"A {keyword} is here.",
                    feature_type=feature_type,
                    interactable=True,
                ))

        return features

    def parse_room_from_raw(self, room_id: int, raw_description: str,
                             room_type_id: int = 0,
                             flags: int = 0,
                             exits: Optional[List[Tuple[str, int]]] = None,
                             creature_count: int = 0,
                             item_count: int = 0) -> RoomDescription:
        """
        Parse a room description from raw data (useful for testing).

        Args:
            room_id: Room identifier
            raw_description: Raw room description string
            room_type_id: Room type identifier
            flags: Room flags byte
            exits: List of (direction, target_room) tuples
            creature_count: Number of creatures
            item_count: Number of items

        Returns:
            RoomDescription with parsed data
        """
        name, description = self._parse_name_and_description(raw_description)

        room_type_names = {
            0: "dungeon", 1: "cavern", 2: "outdoor", 3: "town",
            4: "castle", 5: "temple", 6: "forest", 7: "water",
        }

        parsed_exits = []
        if exits:
            for direction, target in exits:
                parsed_exits.append(RoomExit(direction=direction, target_room=target))

        features = self._parse_features(description)

        return RoomDescription(
            room_id=room_id,
            name=name,
            description=description,
            room_type=room_type_names.get(room_type_id, "unknown"),
            exits=parsed_exits,
            features=features,
            is_dark=bool(flags & 0x01),
            is_magic=bool(flags & 0x02),
            is_safe=bool(flags & 0x04),
            is_trapped=bool(flags & 0x08),
            is_locked=bool(flags & 0x10),
            is_secret=bool(flags & 0x20),
            is_boss_room=bool(flags & 0x40),
            is_exit=bool(flags & 0x80),
            creature_count=creature_count,
            item_count=item_count,
        )
