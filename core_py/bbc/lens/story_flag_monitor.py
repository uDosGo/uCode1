"""
Story Flag Monitor — ACS Story Flag Tracking

Monitors story flags in ACS game memory to track quest progress,
narrative milestones, and game state changes.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
import time

from .acs_memory_map import ACSMemoryMap, get_acs_memory_map


@dataclass
class StoryFlag:
    """A single story flag in the game"""
    index: int
    name: str
    value: bool = False
    description: str = ""
    category: str = "general"  # "quest", "milestone", "event", "state", "general"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize story flag to dictionary"""
        return {
            "index": self.index,
            "name": self.name,
            "value": self.value,
            "description": self.description,
            "category": self.category,
        }


@dataclass
class StoryFlagState:
    """Complete snapshot of all story flags"""
    flags: Dict[int, StoryFlag] = field(default_factory=dict)
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()

    def get_active_flags(self) -> List[StoryFlag]:
        """Get all flags that are currently set"""
        return [f for f in self.flags.values() if f.value]

    def get_flags_by_category(self, category: str) -> List[StoryFlag]:
        """Get all flags in a specific category"""
        return [f for f in self.flags.values() if f.category == category]

    def get_quest_flags(self) -> List[StoryFlag]:
        """Get all quest-related flags"""
        return self.get_flags_by_category("quest")

    def get_milestone_flags(self) -> List[StoryFlag]:
        """Get all milestone flags"""
        return self.get_flags_by_category("milestone")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize story flag state to dictionary"""
        return {
            "timestamp": self.timestamp,
            "active_count": len(self.get_active_flags()),
            "total_count": len(self.flags),
            "flags": {str(k): v.to_dict() for k, v in self.flags.items()},
        }


# Known story flag names for common ACS games
# These map flag indices to meaningful names
KNOWN_STORY_FLAGS: Dict[int, Dict[str, Any]] = {
    # Quest flags (0-63)
    0: {"name": "quest_started", "category": "quest", "description": "Main quest has begun"},
    1: {"name": "quest_completed", "category": "quest", "description": "Main quest completed"},
    2: {"name": "side_quest_1", "category": "quest", "description": "Side quest 1 active"},
    3: {"name": "side_quest_2", "category": "quest", "description": "Side quest 2 active"},
    4: {"name": "side_quest_3", "category": "quest", "description": "Side quest 3 active"},
    5: {"name": "boss_defeated_1", "category": "quest", "description": "First boss defeated"},
    6: {"name": "boss_defeated_2", "category": "quest", "description": "Second boss defeated"},
    7: {"name": "boss_defeated_3", "category": "quest", "description": "Third boss defeated"},
    8: {"name": "artifact_found", "category": "quest", "description": "Quest artifact found"},
    9: {"name": "prince_rescued", "category": "quest", "description": "Prince/Princess rescued"},
    10: {"name": "dragon_slain", "category": "quest", "description": "Dragon slain"},
    11: {"name": "cursed_lifted", "category": "quest", "description": "Curse lifted"},
    12: {"name": "temple_cleansed", "category": "quest", "description": "Temple cleansed"},
    13: {"name": "village_saved", "category": "quest", "description": "Village saved"},
    14: {"name": "treasure_found", "category": "quest", "description": "Legendary treasure found"},
    15: {"name": "kingdom_restored", "category": "quest", "description": "Kingdom restored"},

    # Milestone flags (64-127)
    64: {"name": "entered_dungeon", "category": "milestone", "description": "First entered dungeon"},
    65: {"name": "reached_town", "category": "milestone", "description": "First reached town"},
    66: {"name": "found_inn", "category": "milestone", "description": "Found the inn"},
    67: {"name": "found_shop", "category": "milestone", "description": "Found the shop"},
    68: {"name": "found_temple", "category": "milestone", "description": "Found the temple"},
    69: {"name": "found_castle", "category": "milestone", "description": "Found the castle"},
    70: {"name": "found_forest", "category": "milestone", "description": "Entered the forest"},
    71: {"name": "found_cave", "category": "milestone", "description": "Entered the cave"},
    72: {"name": "found_water", "category": "milestone", "description": "Found water source"},
    73: {"name": "found_bridge", "category": "milestone", "description": "Found the bridge"},
    74: {"name": "leveled_up", "category": "milestone", "description": "Character leveled up"},
    75: {"name": "died_once", "category": "milestone", "description": "Character has died"},
    76: {"name": "rested_at_inn", "category": "milestone", "description": "Rested at an inn"},
    77: {"name": "bought_item", "category": "milestone", "description": "Bought first item"},
    78: {"name": "sold_item", "category": "milestone", "description": "Sold first item"},

    # Event flags (128-191)
    128: {"name": "event_met_merchant", "category": "event", "description": "Met the merchant"},
    129: {"name": "event_met_wizard", "category": "event", "description": "Met the wizard"},
    130: {"name": "event_met_king", "category": "event", "description": "Met the king"},
    131: {"name": "event_met_princess", "category": "event", "description": "Met the princess"},
    132: {"name": "event_met_thief", "category": "event", "description": "Met the thief"},
    133: {"name": "event_met_guard", "category": "event", "description": "Met the guard"},
    134: {"name": "event_trapped", "category": "event", "description": "Triggered a trap"},
    135: {"name": "event_found_secret", "category": "event", "description": "Found a secret passage"},
    136: {"name": "event_solved_puzzle", "category": "event", "description": "Solved a puzzle"},
    137: {"name": "event_opened_chest", "category": "event", "description": "Opened a chest"},
    138: {"name": "event_read_scroll", "category": "event", "description": "Read a scroll"},
    139: {"name": "event_drank_potion", "category": "event", "description": "Drank a potion"},
    140: {"name": "event_equipped_item", "category": "event", "description": "Equipped an item"},
    141: {"name": "event_cast_spell", "category": "event", "description": "Cast a spell"},
    142: {"name": "event_rested", "category": "event", "description": "Rested to recover"},

    # State flags (192-255)
    192: {"name": "state_daytime", "category": "state", "description": "It is daytime"},
    193: {"name": "state_nighttime", "category": "state", "description": "It is nighttime"},
    194: {"name": "state_raining", "category": "state", "description": "It is raining"},
    195: {"name": "state_foggy", "category": "state", "description": "It is foggy"},
    196: {"name": "state_dark", "category": "state", "description": "Area is dark"},
    197: {"name": "state_safe", "category": "state", "description": "In a safe zone"},
    198: {"name": "state_combat", "category": "state", "description": "In combat"},
    199: {"name": "state_poisoned", "category": "state", "description": "Player is poisoned"},
    200: {"name": "state_confused", "category": "state", "description": "Player is confused"},
    201: {"name": "state_invisible", "category": "state", "description": "Player is invisible"},
    202: {"name": "state_protected", "category": "state", "description": "Player is protected"},
    203: {"name": "state_cursed", "category": "state", "description": "Player is cursed"},
    204: {"name": "state_blessed", "category": "state", "description": "Player is blessed"},
    205: {"name": "state_hungry", "category": "state", "description": "Player is hungry"},
    206: {"name": "state_thirsty", "category": "state", "description": "Player is thirsty"},
}


class StoryFlagMonitor:
    """
    Monitors story flags in ACS game memory.

    Reads the 256 story flags from memory and tracks changes,
    generating events when flags are set or cleared.
    """

    def __init__(self, memory_map: Optional[ACSMemoryMap] = None):
        self.memory_map = memory_map or get_acs_memory_map()
        self._last_state: Optional[StoryFlagState] = None
        self._flag_history: List[StoryFlagState] = []
        self._max_history: int = 100
        self._flag_names: Dict[int, Dict[str, Any]] = dict(KNOWN_STORY_FLAGS)

    def register_flag_name(self, index: int, name: str,
                           category: str = "general",
                           description: str = "") -> None:
        """Register a custom name for a story flag"""
        self._flag_names[index] = {
            "name": name,
            "category": category,
            "description": description,
        }

    def extract_flags(self, memory_reader) -> StoryFlagState:
        """
        Extract all story flags from ACS memory.

        Args:
            memory_reader: Object with read_byte(address) method

        Returns:
            StoryFlagState with all flags
        """
        mm = self.memory_map
        state = StoryFlagState()

        for i in range(mm.STORY_FLAG_COUNT):
            addr = mm.get_story_flag_address(i)
            value = memory_reader.read_byte(addr) != 0

            flag_info = self._flag_names.get(i, {})
            flag = StoryFlag(
                index=i,
                name=flag_info.get("name", f"flag_{i}"),
                value=value,
                description=flag_info.get("description", ""),
                category=flag_info.get("category", "general"),
            )
            state.flags[i] = flag

        self._last_state = state
        self._flag_history.append(state)
        if len(self._flag_history) > self._max_history:
            self._flag_history.pop(0)

        return state

    def detect_flag_changes(self, new_state: StoryFlagState) -> Dict[str, Any]:
        """
        Detect which flags changed between the last extraction and a new one.

        Args:
            new_state: Recently extracted story flag state

        Returns:
            Dict with 'set', 'cleared' lists and 'summary' string
        """
        if not self._last_state:
            return {"set": [], "cleared": [], "summary": "initial capture"}

        set_flags = []
        cleared_flags = []

        for idx, flag in new_state.flags.items():
            old_flag = self._last_state.flags.get(idx)
            if old_flag and old_flag.value != flag.value:
                if flag.value:
                    set_flags.append(flag.to_dict())
                else:
                    cleared_flags.append(flag.to_dict())

        parts = []
        if set_flags:
            names = [f["name"] for f in set_flags]
            parts.append(f"flags set: {', '.join(names)}")
        if cleared_flags:
            names = [f["name"] for f in cleared_flags]
            parts.append(f"flags cleared: {', '.join(names)}")

        return {
            "set": set_flags,
            "cleared": cleared_flags,
            "summary": ", ".join(parts) if parts else "no changes",
        }

    def get_active_flag_names(self) -> List[str]:
        """Get names of all currently active flags"""
        if not self._last_state:
            return []
        return [f.name for f in self._last_state.get_active_flags()]

    def is_flag_set(self, flag_index: int) -> bool:
        """Check if a specific flag is set"""
        if not self._last_state:
            return False
        flag = self._last_state.flags.get(flag_index)
        return flag.value if flag else False

    def get_flag_history(self) -> List[StoryFlagState]:
        """Get the history of extracted flag states"""
        return list(self._flag_history)

    def clear_history(self) -> None:
        """Clear flag extraction history"""
        self._flag_history.clear()
        self._last_state = None
