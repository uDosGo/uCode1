"""
Creature Tracker — ACS Creature/Character Tracking

Tracks creatures and NPCs in ACS game memory, monitoring their
positions, states, and interactions with the player.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time

from .acs_memory_map import ACSMemoryMap, get_acs_memory_map


class CreatureState(Enum):
    """State of a creature in the game"""
    IDLE = "idle"
    WANDERING = "wandering"
    ALERT = "alert"
    ATTACKING = "attacking"
    FLEEING = "fleeing"
    SLEEPING = "sleeping"
    DEAD = "dead"
    ASLEEP = "asleep"
    UNKNOWN = "unknown"


@dataclass
class Creature:
    """A creature or NPC in the game"""
    slot_index: int
    creature_id: int
    creature_name: str
    hp: int = 0
    max_hp: int = 0
    x: int = 0
    y: int = 0
    state: CreatureState = CreatureState.IDLE
    direction: str = "north"
    is_hostile: bool = False
    is_friendly: bool = False
    is_boss: bool = False
    is_unique: bool = False
    is_invisible: bool = False
    is_ethereal: bool = False
    is_guarding: bool = False
    is_quest_target: bool = False
    damage: int = 0
    ac: int = 0
    xp_value: int = 0
    gold_value: int = 0
    item_drop: int = 0
    alert_range: int = 5
    speed: int = 1
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

    @property
    def is_alive(self) -> bool:
        """Check if creature is alive"""
        return self.state not in (CreatureState.DEAD, CreatureState.UNKNOWN)

    @property
    def is_aggro(self) -> bool:
        """Check if creature is aggressive toward player"""
        return self.state in (CreatureState.ALERT, CreatureState.ATTACKING)

    @property
    def health_percent(self) -> float:
        """Get health percentage"""
        if self.max_hp > 0:
            return (self.hp / self.max_hp) * 100.0
        return 0.0

    def distance_to(self, x: int, y: int) -> float:
        """Calculate distance to a point"""
        return ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5

    def to_dict(self) -> Dict[str, Any]:
        """Serialize creature to dictionary"""
        return {
            "slot_index": self.slot_index,
            "creature_id": self.creature_id,
            "creature_name": self.creature_name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "health_percent": self.health_percent,
            "x": self.x,
            "y": self.y,
            "state": self.state.value,
            "direction": self.direction,
            "is_hostile": self.is_hostile,
            "is_friendly": self.is_friendly,
            "is_boss": self.is_boss,
            "is_unique": self.is_unique,
            "is_invisible": self.is_invisible,
            "is_ethereal": self.is_ethereal,
            "is_guarding": self.is_guarding,
            "is_quest_target": self.is_quest_target,
            "damage": self.damage,
            "ac": self.ac,
            "xp_value": self.xp_value,
            "gold_value": self.gold_value,
            "item_drop": self.item_drop,
            "alert_range": self.alert_range,
            "speed": self.speed,
            "timestamp": self.timestamp,
        }


class CreatureTracker:
    """
    Tracks creatures in ACS game memory.

    Reads creature data from memory slots and monitors their
    positions, states, and interactions. Provides change detection
    and event generation for creature-related game events.
    """

    def __init__(self, memory_map: Optional[ACSMemoryMap] = None):
        self.memory_map = memory_map or get_acs_memory_map()
        self._last_creatures: Dict[int, Creature] = {}
        self._creature_history: List[Dict[int, Creature]] = []
        self._max_history: int = 100

    def extract_creatures(self, memory_reader) -> Dict[int, Creature]:
        """
        Extract all creatures from ACS memory.

        Args:
            memory_reader: Object with read_byte(address) method

        Returns:
            Dict mapping slot index to Creature objects
        """
        mm = self.memory_map
        creatures: Dict[int, Creature] = {}

        for slot in range(mm.MAX_CREATURES):
            addr = mm.get_creature_slot_address(slot)
            creature_id = memory_reader.read_byte(addr)

            if creature_id == 0x00:
                continue

            hp = memory_reader.read_byte(addr + 0x01)
            max_hp = memory_reader.read_byte(addr + 0x02)
            x = memory_reader.read_byte(addr + 0x03)
            y = memory_reader.read_byte(addr + 0x04)
            state_id = memory_reader.read_byte(addr + 0x05)
            direction_id = memory_reader.read_byte(addr + 0x06)
            flags = memory_reader.read_byte(addr + 0x07)
            damage = memory_reader.read_byte(addr + 0x08)
            ac = memory_reader.read_byte(addr + 0x09)
            xp_value = memory_reader.read_byte(addr + 0x0A)
            gold_value = memory_reader.read_byte(addr + 0x0B)
            item_drop = memory_reader.read_byte(addr + 0x0C)
            alert_range = memory_reader.read_byte(addr + 0x0D)
            speed = memory_reader.read_byte(addr + 0x0E)

            state_map = {
                0: CreatureState.IDLE, 1: CreatureState.WANDERING,
                2: CreatureState.ALERT, 3: CreatureState.ATTACKING,
                4: CreatureState.FLEEING, 5: CreatureState.SLEEPING,
                6: CreatureState.DEAD, 7: CreatureState.ASLEEP,
            }
            direction_map = {0: "north", 1: "south", 2: "east", 3: "west"}

            creature = Creature(
                slot_index=slot,
                creature_id=creature_id,
                creature_name=mm.get_creature_name(creature_id),
                hp=hp,
                max_hp=max_hp,
                x=x,
                y=y,
                state=state_map.get(state_id, CreatureState.UNKNOWN),
                direction=direction_map.get(direction_id, "north"),
                is_hostile=bool(flags & 0x01),
                is_friendly=bool(flags & 0x02),
                is_boss=bool(flags & 0x04),
                is_unique=bool(flags & 0x08),
                is_invisible=bool(flags & 0x10),
                is_ethereal=bool(flags & 0x20),
                is_guarding=bool(flags & 0x40),
                is_quest_target=bool(flags & 0x80),
                damage=damage,
                ac=ac,
                xp_value=xp_value,
                gold_value=gold_value,
                item_drop=item_drop,
                alert_range=alert_range,
                speed=speed,
            )
            creatures[slot] = creature

        self._last_creatures = creatures
        self._creature_history.append(dict(creatures))
        if len(self._creature_history) > self._max_history:
            self._creature_history.pop(0)

        return creatures

    def detect_creature_changes(self, new_creatures: Dict[int, Creature]) -> Dict[str, Any]:
        """
        Detect changes between the last extraction and a new one.

        Args:
            new_creatures: Recently extracted creature dict

        Returns:
            Dict with 'spawned', 'died', 'moved', 'state_changed', 'aggro' lists
        """
        if not self._last_creatures:
            return {"spawned": [], "died": [], "moved": [],
                    "state_changed": [], "aggro": [], "summary": "initial capture"}

        spawned = []
        died = []
        moved = []
        state_changed = []
        aggro = []

        for slot, creature in new_creatures.items():
            if slot not in self._last_creatures:
                spawned.append(creature.to_dict())
            else:
                old = self._last_creatures[slot]
                if old.is_alive and not creature.is_alive:
                    died.append(creature.to_dict())
                if (old.x, old.y) != (creature.x, creature.y):
                    moved.append({
                        "slot": slot,
                        "name": creature.creature_name,
                        "from": (old.x, old.y),
                        "to": (creature.x, creature.y),
                    })
                if old.state != creature.state:
                    state_changed.append({
                        "slot": slot,
                        "name": creature.creature_name,
                        "old_state": old.state.value,
                        "new_state": creature.state.value,
                    })
                if creature.is_aggro and not old.is_aggro:
                    aggro.append(creature.to_dict())

        for slot, creature in self._last_creatures.items():
            if slot not in new_creatures:
                died.append(creature.to_dict())

        parts = []
        if spawned:
            parts.append(f"{len(spawned)} creature(s) appeared")
        if died:
            parts.append(f"{len(died)} creature(s) died/despawned")
        if moved:
            parts.append(f"{len(moved)} creature(s) moved")
        if aggro:
            parts.append(f"{len(aggro)} creature(s) aggro!")

        return {
            "spawned": spawned,
            "died": died,
            "moved": moved,
            "state_changed": state_changed,
            "aggro": aggro,
            "summary": ", ".join(parts) if parts else "no changes",
        }

    def get_creatures_in_range(self, x: int, y: int, radius: int = 5) -> List[Creature]:
        """Get creatures within a certain range of a point"""
        in_range = []
        for creature in self._last_creatures.values():
            if creature.is_alive and creature.distance_to(x, y) <= radius:
                in_range.append(creature)
        return in_range

    def get_hostile_creatures(self) -> List[Creature]:
        """Get all hostile creatures"""
        return [c for c in self._last_creatures.values()
                if c.is_alive and c.is_hostile]

    def get_friendly_creatures(self) -> List[Creature]:
        """Get all friendly creatures"""
        return [c for c in self._last_creatures.values()
                if c.is_alive and c.is_friendly]

    def get_creature_positions(self) -> Dict[Tuple[int, int], str]:
        """Get creature positions as (x, y) -> char mapping for ASCII rendering"""
        positions = {}
        for creature in self._last_creatures.values():
            if creature.is_alive:
                char = "F" if creature.is_friendly else "C"
                if creature.is_boss:
                    char = "B"
                elif creature.is_quest_target:
                    char = "Q"
                positions[(creature.x, creature.y)] = char
        return positions
