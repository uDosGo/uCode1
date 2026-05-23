"""
Player Stats — ACS Player Statistics Capture

Captures player statistics from ACS game memory with timestamp
and metadata support. Provides change detection and stat history.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import time

from .acs_memory_map import ACSMemoryMap, get_acs_memory_map


@dataclass
class PlayerStatsCapture:
    """A single capture of player statistics"""
    hp: int = 0
    max_hp: int = 0
    gold: int = 0
    strength: int = 0
    intelligence: int = 0
    dexterity: int = 0
    agility: int = 0
    level: int = 1
    xp: int = 0
    ac: int = 0
    damage: int = 0
    status: str = "normal"
    weapon_idx: int = 0
    armor_idx: int = 0
    shield_idx: int = 0
    helm_idx: int = 0
    ring_idx: int = 0
    food: int = 0
    water: int = 0
    torch: int = 0
    keys: int = 0
    player_x: int = 7
    player_y: int = 7
    current_room: int = 0
    prev_room: int = 0
    direction: str = "north"
    turn_count: int = 0
    timestamp: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

    @property
    def health_percent(self) -> float:
        """Get health percentage"""
        if self.max_hp > 0:
            return (self.hp / self.max_hp) * 100.0
        return 0.0

    @property
    def is_alive(self) -> bool:
        """Check if player is alive"""
        return self.hp > 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize player stats to dictionary"""
        return {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "health_percent": self.health_percent,
            "gold": self.gold,
            "strength": self.strength,
            "intelligence": self.intelligence,
            "dexterity": self.dexterity,
            "agility": self.agility,
            "level": self.level,
            "xp": self.xp,
            "ac": self.ac,
            "damage": self.damage,
            "status": self.status,
            "weapon_idx": self.weapon_idx,
            "armor_idx": self.armor_idx,
            "shield_idx": self.shield_idx,
            "helm_idx": self.helm_idx,
            "ring_idx": self.ring_idx,
            "food": self.food,
            "water": self.water,
            "torch": self.torch,
            "keys": self.keys,
            "player_x": self.player_x,
            "player_y": self.player_y,
            "current_room": self.current_room,
            "prev_room": self.prev_room,
            "direction": self.direction,
            "turn_count": self.turn_count,
            "timestamp": self.timestamp,
            "is_alive": self.is_alive,
            "metadata": self.metadata,
        }


class PlayerStats:
    """
    Captures and tracks player statistics from ACS game memory.

    Reads player stats from memory and provides change detection,
    stat history, and summary generation.
    """

    STATUS_MAP: Dict[int, str] = {
        0x00: "normal",
        0x01: "poisoned",
        0x02: "asleep",
        0x04: "paralyzed",
        0x08: "confused",
        0x10: "invisible",
        0x20: "protected",
        0x40: "cursed",
        0x80: "dead",
    }

    DIRECTION_MAP: Dict[int, str] = {
        0: "north", 1: "south", 2: "east", 3: "west",
    }

    def __init__(self, memory_map: Optional[ACSMemoryMap] = None):
        self.memory_map = memory_map or get_acs_memory_map()
        self._last_capture: Optional[PlayerStatsCapture] = None
        self._capture_history: List[PlayerStatsCapture] = []
        self._max_history: int = 1000

    def capture(self, memory_reader, metadata: Optional[Dict[str, Any]] = None) -> PlayerStatsCapture:
        """
        Capture current player statistics from ACS memory.

        Args:
            memory_reader: Object with read_byte(address) and read_word(address) methods
            metadata: Optional metadata to attach to this capture

        Returns:
            PlayerStatsCapture with current stats
        """
        mm = self.memory_map
        base = mm.player_stats_region.start

        hp = memory_reader.read_byte(base + 0x00)
        max_hp = memory_reader.read_byte(base + 0x01)
        gold = memory_reader.read_word(base + 0x02)
        strength = memory_reader.read_byte(base + 0x04)
        intelligence = memory_reader.read_byte(base + 0x05)
        dexterity = memory_reader.read_byte(base + 0x06)
        agility = memory_reader.read_byte(base + 0x07)
        level = memory_reader.read_byte(base + 0x08)
        xp = memory_reader.read_word(base + 0x09)
        ac = memory_reader.read_byte(base + 0x0B)
        damage = memory_reader.read_byte(base + 0x0C)
        status_byte = memory_reader.read_byte(base + 0x0D)
        weapon_idx = memory_reader.read_byte(base + 0x0E)
        armor_idx = memory_reader.read_byte(base + 0x0F)
        shield_idx = memory_reader.read_byte(base + 0x10)
        helm_idx = memory_reader.read_byte(base + 0x11)
        ring_idx = memory_reader.read_byte(base + 0x12)
        food = memory_reader.read_byte(base + 0x15)
        water = memory_reader.read_byte(base + 0x16)
        torch = memory_reader.read_byte(base + 0x17)
        keys = memory_reader.read_byte(base + 0x18)
        player_x = memory_reader.read_byte(base + 0x1A)
        player_y = memory_reader.read_byte(base + 0x1B)
        current_room = memory_reader.read_byte(base + 0x1C)
        prev_room = memory_reader.read_byte(base + 0x1D)
        direction_id = memory_reader.read_byte(base + 0x1E)
        turn_count = memory_reader.read_word(base + 0x1F)

        # Decode status flags
        status_parts = []
        for flag_bit, status_name in self.STATUS_MAP.items():
            if status_byte & flag_bit:
                status_parts.append(status_name)
        status = ", ".join(status_parts) if status_parts else "normal"

        capture = PlayerStatsCapture(
            hp=hp, max_hp=max_hp, gold=gold,
            strength=strength, intelligence=intelligence,
            dexterity=dexterity, agility=agility,
            level=level, xp=xp, ac=ac, damage=damage,
            status=status,
            weapon_idx=weapon_idx, armor_idx=armor_idx,
            shield_idx=shield_idx, helm_idx=helm_idx, ring_idx=ring_idx,
            food=food, water=water, torch=torch, keys=keys,
            player_x=player_x, player_y=player_y,
            current_room=current_room, prev_room=prev_room,
            direction=self.DIRECTION_MAP.get(direction_id, "north"),
            turn_count=turn_count,
            metadata=metadata or {},
        )

        self._last_capture = capture
        self._capture_history.append(capture)
        if len(self._capture_history) > self._max_history:
            self._capture_history.pop(0)

        return capture

    def detect_changes(self, new_capture: PlayerStatsCapture) -> Dict[str, Any]:
        """
        Detect changes between the last capture and a new one.

        Args:
            new_capture: Recently captured player stats

        Returns:
            Dict with 'changes' list and 'summary' string
        """
        if not self._last_capture:
            return {"changes": [], "summary": "initial capture"}

        old = self._last_capture
        changes = []

        tracked_fields = [
            ("hp", "HP"), ("max_hp", "Max HP"), ("gold", "Gold"),
            ("level", "Level"), ("xp", "XP"),
            ("strength", "STR"), ("intelligence", "INT"),
            ("dexterity", "DEX"), ("agility", "AGI"),
            ("ac", "AC"), ("damage", "Damage"),
            ("status", "Status"),
            ("food", "Food"), ("water", "Water"), ("torch", "Torch"),
            ("keys", "Keys"),
            ("player_x", "X"), ("player_y", "Y"),
            ("current_room", "Room"), ("direction", "Direction"),
            ("turn_count", "Turns"),
        ]

        for field_name, display_name in tracked_fields:
            old_val = getattr(old, field_name)
            new_val = getattr(new_capture, field_name)
            if old_val != new_val:
                changes.append({
                    "field": field_name,
                    "name": display_name,
                    "old": old_val,
                    "new": new_val,
                })

        parts = []
        if changes:
            for c in changes:
                parts.append(f"{c['name']}: {c['old']} -> {c['new']}")

        return {
            "changes": changes,
            "summary": ", ".join(parts) if parts else "no changes",
        }

    def get_summary(self, capture: Optional[PlayerStatsCapture] = None) -> str:
        """Get a human-readable summary of player stats"""
        c = capture or self._last_capture
        if not c:
            return "No stats captured"

        return (
            f"Level {c.level} | HP: {c.hp}/{c.max_hp} ({c.health_percent:.0f}%) | "
            f"Gold: {c.gold} | XP: {c.xp} | "
            f"STR:{c.strength} INT:{c.intelligence} DEX:{c.dexterity} AGI:{c.agility} | "
            f"AC:{c.ac} DMG:{c.damage} | "
            f"Room:{c.current_room} ({c.direction}) | "
            f"Turns:{c.turn_count} | Status: {c.status}"
        )

    def get_history(self) -> List[PlayerStatsCapture]:
        """Get the capture history"""
        return list(self._capture_history)

    def clear_history(self) -> None:
        """Clear capture history"""
        self._capture_history.clear()
        self._last_capture = None
