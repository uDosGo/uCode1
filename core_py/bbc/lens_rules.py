"""
Game-specific LENS extraction rules for uCode1.

This module provides variable mapping and event detection rules
for supported games (NetHack, Eamon, etc.). These rules define
how LENS extracts game state from memory and detects events.

Each game has:
    - Variable mappings: game variable -> LENS variable name
    - Event triggers: memory changes -> event types
    - Room/level change detection
    - Combat event detection
    - Item pickup/drop detection
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable, Any
from enum import Enum


class GameEvent(Enum):
    """Game events that can be detected by LENS"""
    HP_CHANGE = "hp_change"
    GOLD_CHANGE = "gold_change"
    ROOM_CHANGE = "room_change"
    LEVEL_CHANGE = "level_change"
    COMBAT = "combat"
    ITEM_PICKUP = "item_pickup"
    ITEM_DROP = "item_drop"
    WEAPON_CHANGE = "weapon_change"
    ARMOR_CHANGE = "armor_change"
    SAVE_GAME = "save_game"
    LOAD_GAME = "load_game"
    GAME_OVER = "game_over"
    LEVEL_UP = "level_up"
    STATUS_CHANGE = "status_change"


@dataclass
class VariableMapping:
    """Maps a game variable to a LENS variable"""
    game_name: str           # Game variable name (e.g. "hp", "gold")
    lens_name: str           # LENS variable name (e.g. "HP%", "GOLD%")
    address: str             # Memory address (hex string)
    var_type: str            # "int", "string", "bool"
    length: int = 0          # Length for string types
    description: str = ""    # Human-readable description
    transform: Optional[Callable] = None  # Optional value transform


@dataclass
class EventRule:
    """Defines when a game event should be triggered"""
    event: GameEvent
    variable: str            # Variable to monitor
    condition: str           # "change", "increase", "decrease", "equals", "not_equals"
    threshold: Optional[Any] = None  # Threshold value for condition
    description: str = ""


@dataclass
class GameRules:
    """Complete set of LENS rules for a game"""
    game_id: str
    game_name: str
    variables: Dict[str, VariableMapping] = field(default_factory=dict)
    events: List[EventRule] = field(default_factory=list)
    
    def add_variable(self, mapping: VariableMapping):
        """Add a variable mapping"""
        self.variables[mapping.lens_name] = mapping
    
    def add_event(self, rule: EventRule):
        """Add an event rule"""
        self.events.append(rule)


# ========== NetHack Rules ==========

NETHACK_RULES = GameRules(
    game_id="nethack",
    game_name="NetHack",
    variables={
        "HP%": VariableMapping("hp", "HP%", "0x8000", "int", description="Current hit points percentage"),
        "GOLD%": VariableMapping("gold", "GOLD%", "0x8002", "int", description="Current gold pieces"),
        "XP%": VariableMapping("xp", "XP%", "0x8004", "int", description="Experience points"),
        "STR%": VariableMapping("str", "STR%", "0x8006", "int", description="Strength"),
        "DEX%": VariableMapping("dex", "DEX%", "0x8008", "int", description="Dexterity"),
        "ROOM%": VariableMapping("room", "ROOM%", "0x800A", "int", description="Current room/level number"),
        "DEPTH%": VariableMapping("depth", "DEPTH%", "0x800C", "int", description="Dungeon depth"),
        "AC%": VariableMapping("ac", "AC%", "0x800E", "int", description="Armor class"),
        "WEAPON$": VariableMapping("weapon", "WEAPON$", "0x8100", "string", length=20, description="Current weapon name"),
        "ARMOR$": VariableMapping("armor", "ARMOR$", "0x8120", "string", length=20, description="Current armor name"),
        "RING$": VariableMapping("ring", "RING$", "0x8140", "string", length=20, description="Current ring name"),
        "STATUS$": VariableMapping("status", "STATUS$", "0x8200", "string", length=40, description="Full status line"),
    },
    events=[
        EventRule(GameEvent.HP_CHANGE, "HP%", "change", description="Hit points changed"),
        EventRule(GameEvent.GOLD_CHANGE, "GOLD%", "change", description="Gold changed"),
        EventRule(GameEvent.ROOM_CHANGE, "ROOM%", "change", description="Room changed"),
        EventRule(GameEvent.LEVEL_CHANGE, "DEPTH%", "change", description="Dungeon level changed"),
        EventRule(GameEvent.COMBAT, "HP%", "decrease", threshold=5, description="Combat damage taken"),
        EventRule(GameEvent.ITEM_PICKUP, "WEAPON$", "change", description="Weapon picked up"),
        EventRule(GameEvent.ITEM_DROP, "WEAPON$", "change", description="Weapon dropped"),
        EventRule(GameEvent.WEAPON_CHANGE, "WEAPON$", "change", description="Weapon changed"),
        EventRule(GameEvent.ARMOR_CHANGE, "ARMOR$", "change", description="Armor changed"),
        EventRule(GameEvent.STATUS_CHANGE, "STATUS$", "change", description="Status line changed"),
    ],
)


# ========== Eamon Rules ==========

EAMON_RULES = GameRules(
    game_id="eamon",
    game_name="Eamon",
    variables={
        "HP%": VariableMapping("hp", "HP%", "0x0200", "int", description="Current hit points"),
        "MAXHP%": VariableMapping("maxhp", "MAXHP%", "0x0202", "int", description="Maximum hit points"),
        "GOLD%": VariableMapping("gold", "GOLD%", "0x0204", "int", description="Gold pieces"),
        "STR%": VariableMapping("strength", "STR%", "0x0206", "int", description="Strength"),
        "INT%": VariableMapping("intelligence", "INT%", "0x0208", "int", description="Intelligence"),
        "DEX%": VariableMapping("dexterity", "DEX%", "0x020A", "int", description="Dexterity"),
        "AGI%": VariableMapping("agility", "AGI%", "0x020C", "int", description="Agility"),
        "ROOM%": VariableMapping("room", "ROOM%", "0x020E", "int", description="Current room number"),
        "WEAPON%": VariableMapping("weapon_idx", "WEAPON%", "0x0210", "int", description="Current weapon index"),
        "ARMOR%": VariableMapping("armor_idx", "ARMOR%", "0x0212", "int", description="Current armor index"),
        "WEAPON$": VariableMapping("weapon_name", "WEAPON$", "0x0300", "string", length=20, description="Current weapon name"),
        "ARMOR$": VariableMapping("armor_name", "ARMOR$", "0x0320", "string", length=20, description="Current armor name"),
        "ROOM$": VariableMapping("room_desc", "ROOM$", "0x0400", "string", length=40, description="Current room description"),
        "STATUS$": VariableMapping("status", "STATUS$", "0x0500", "string", length=40, description="Full status line"),
    },
    events=[
        EventRule(GameEvent.HP_CHANGE, "HP%", "change", description="Hit points changed"),
        EventRule(GameEvent.GOLD_CHANGE, "GOLD%", "change", description="Gold changed"),
        EventRule(GameEvent.ROOM_CHANGE, "ROOM%", "change", description="Room changed"),
        EventRule(GameEvent.COMBAT, "HP%", "decrease", threshold=1, description="Combat damage taken"),
        EventRule(GameEvent.ITEM_PICKUP, "WEAPON%", "change", description="Weapon picked up"),
        EventRule(GameEvent.ITEM_DROP, "WEAPON%", "change", description="Weapon dropped"),
        EventRule(GameEvent.WEAPON_CHANGE, "WEAPON$", "change", description="Weapon changed"),
        EventRule(GameEvent.ARMOR_CHANGE, "ARMOR$", "change", description="Armor changed"),
        EventRule(GameEvent.STATUS_CHANGE, "STATUS$", "change", description="Status line changed"),
    ],
)


# ========== Registry ==========

# Registry of all supported games
GAME_RULES_REGISTRY: Dict[str, GameRules] = {
    "nethack": NETHACK_RULES,
    "eamon": EAMON_RULES,
}


def get_game_rules(game_id: str) -> Optional[GameRules]:
    """Get LENS rules for a specific game"""
    return GAME_RULES_REGISTRY.get(game_id)


def get_all_game_rules() -> Dict[str, GameRules]:
    """Get all registered game rules"""
    return dict(GAME_RULES_REGISTRY)


def register_game_rules(game_id: str, rules: GameRules):
    """Register LENS rules for a game"""
    GAME_RULES_REGISTRY[game_id] = rules
