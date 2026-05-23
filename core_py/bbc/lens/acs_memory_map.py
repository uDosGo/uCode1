"""
ACS Memory Map — Known Memory Addresses for Adventure Construction Set

This module documents the memory layout of Adventure Construction Set (ACS)
games, providing known addresses for tile grids, room data, inventory,
creatures, story flags, and player statistics.

The ACS memory map is based on the Apple II version of Adventure Construction
Set by Stuart Smith (Electronic Arts, 1984). Memory addresses are mapped
relative to the game's loaded memory space.

Memory Layout:
    0x0000 - 0x00FF: Zero page / system variables
    0x0100 - 0x01FF: Stack
    0x0200 - 0x02FF: Player stats block
    0x0300 - 0x03FF: Current room data
    0x0400 - 0x04FF: Tile grid (15x15 = 225 bytes)
    0x0500 - 0x05FF: Creature data block
    0x0600 - 0x06FF: Inventory data block
    0x0700 - 0x07FF: Story flags
    0x0800 - 0x0FFF: Room descriptions (string data)
    0x1000 - 0x1FFF: Tile definitions
    0x2000 - 0x2FFF: Creature definitions
    0x3000 - 0x3FFF: Item definitions
    0x4000 - 0x4FFF: Room definitions
    0x5000 - 0x5FFF: Message strings
    0x6000 - 0x6FFF: Game logic / scripts
    0x7000 - 0x7FFF: Extended data
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple


# ── Memory Region Definitions ──────────────────────────────────────

@dataclass
class MemoryRegion:
    """A named region in ACS memory"""
    name: str
    start: int
    size: int
    description: str
    structure: str = "raw"  # "raw", "grid", "block", "string_table"


@dataclass
class MemoryField:
    """A specific field within a memory region"""
    name: str
    offset: int
    size: int
    field_type: str  # "uint8", "uint16", "string", "bool", "enum"
    description: str
    enum_values: Optional[Dict[int, str]] = None


@dataclass
class ACSMemoryMap:
    """
    Complete memory map for Adventure Construction Set.

    Provides address lookups for all game state data, including
    tile grids, room data, inventory, creatures, story flags,
    and player statistics.
    """

    # ── Regions ────────────────────────────────────────────────────

    regions: Dict[str, MemoryRegion] = field(default_factory=dict)

    # ── Player Stats (0x0200-0x02FF) ───────────────────────────────

    player_stats_region: MemoryRegion = field(
        default_factory=lambda: MemoryRegion(
            "player_stats", 0x0200, 256,
            "Player statistics block",
            structure="block"
        )
    )

    player_stats_fields: Dict[str, MemoryField] = field(default_factory=lambda: {
        "hp": MemoryField("hp", 0x00, 1, "uint8", "Current hit points"),
        "max_hp": MemoryField("max_hp", 0x01, 1, "uint8", "Maximum hit points"),
        "gold": MemoryField("gold", 0x02, 2, "uint16", "Gold pieces"),
        "strength": MemoryField("strength", 0x04, 1, "uint8", "Strength attribute"),
        "intelligence": MemoryField("intelligence", 0x05, 1, "uint8", "Intelligence attribute"),
        "dexterity": MemoryField("dexterity", 0x06, 1, "uint8", "Dexterity attribute"),
        "agility": MemoryField("agility", 0x07, 1, "uint8", "Agility attribute"),
        "level": MemoryField("level", 0x08, 1, "uint8", "Character level"),
        "xp": MemoryField("xp", 0x09, 2, "uint16", "Experience points"),
        "ac": MemoryField("ac", 0x0B, 1, "uint8", "Armor class"),
        "damage": MemoryField("damage", 0x0C, 1, "uint8", "Base damage"),
        "status": MemoryField("status", 0x0D, 1, "uint8", "Status effect flags",
                              enum_values={
                                  0x00: "normal",
                                  0x01: "poisoned",
                                  0x02: "asleep",
                                  0x04: "paralyzed",
                                  0x08: "confused",
                                  0x10: "invisible",
                                  0x20: "protected",
                                  0x40: "cursed",
                                  0x80: "dead",
                              }),
        "weapon_idx": MemoryField("weapon_idx", 0x0E, 1, "uint8", "Current weapon index"),
        "armor_idx": MemoryField("armor_idx", 0x0F, 1, "uint8", "Current armor index"),
        "shield_idx": MemoryField("shield_idx", 0x10, 1, "uint8", "Current shield index"),
        "helm_idx": MemoryField("helm_idx", 0x11, 1, "uint8", "Current helm index"),
        "ring_idx": MemoryField("ring_idx", 0x12, 1, "uint8", "Current ring index"),
        "potion_idx": MemoryField("potion_idx", 0x13, 1, "uint8", "Current potion index"),
        "scroll_idx": MemoryField("scroll_idx", 0x14, 1, "uint8", "Current scroll index"),
        "food": MemoryField("food", 0x15, 1, "uint8", "Food units remaining"),
        "water": MemoryField("water", 0x16, 1, "uint8", "Water units remaining"),
        "torch": MemoryField("torch", 0x17, 1, "uint8", "Torch duration remaining"),
        "keys": MemoryField("keys", 0x18, 1, "uint8", "Number of keys held"),
        "specials": MemoryField("specials", 0x19, 1, "uint8", "Special item flags"),
        "player_x": MemoryField("player_x", 0x1A, 1, "uint8", "Player X position on tile grid"),
        "player_y": MemoryField("player_y", 0x1B, 1, "uint8", "Player Y position on tile grid"),
        "current_room": MemoryField("current_room", 0x1C, 1, "uint8", "Current room number"),
        "prev_room": MemoryField("prev_room", 0x1D, 1, "uint8", "Previous room number"),
        "direction": MemoryField("direction", 0x1E, 1, "uint8", "Facing direction",
                                  enum_values={
                                      0: "north",
                                      1: "south",
                                      2: "east",
                                      3: "west",
                                  }),
        "turn_count": MemoryField("turn_count", 0x1F, 2, "uint16", "Total turns taken"),
    })

    # ── Current Room Data (0x0300-0x03FF) ──────────────────────────

    room_data_region: MemoryRegion = field(
        default_factory=lambda: MemoryRegion(
            "room_data", 0x0300, 256,
            "Current room data block",
            structure="block"
        )
    )

    room_data_fields: Dict[str, MemoryField] = field(default_factory=lambda: {
        "room_id": MemoryField("room_id", 0x00, 1, "uint8", "Room identifier"),
        "room_type": MemoryField("room_type", 0x01, 1, "uint8", "Room type",
                                  enum_values={
                                      0: "dungeon",
                                      1: "cavern",
                                      2: "outdoor",
                                      3: "town",
                                      4: "castle",
                                      5: "temple",
                                      6: "forest",
                                      7: "water",
                                  }),
        "light_level": MemoryField("light_level", 0x02, 1, "uint8", "Light level (0-100)"),
        "temperature": MemoryField("temperature", 0x03, 1, "uint8", "Temperature (0-100)"),
        "room_flags": MemoryField("room_flags", 0x04, 1, "uint8", "Room flags",
                                   enum_values={
                                       0x01: "dark",
                                       0x02: "magic",
                                       0x04: "safe",
                                       0x08: "trapped",
                                       0x10: "locked",
                                       0x20: "secret",
                                       0x40: "boss",
                                       0x80: "exit",
                                   }),
        "north_exit": MemoryField("north_exit", 0x05, 1, "uint8", "Room to north (0=none)"),
        "south_exit": MemoryField("south_exit", 0x06, 1, "uint8", "Room to south (0=none)"),
        "east_exit": MemoryField("east_exit", 0x07, 1, "uint8", "Room to east (0=none)"),
        "west_exit": MemoryField("west_exit", 0x08, 1, "uint8", "Room to west (0=none)"),
        "up_exit": MemoryField("up_exit", 0x09, 1, "uint8", "Room above (0=none)"),
        "down_exit": MemoryField("down_exit", 0x0A, 1, "uint8", "Room below (0=none)"),
        "creature_count": MemoryField("creature_count", 0x0B, 1, "uint8", "Number of creatures in room"),
        "item_count": MemoryField("item_count", 0x0C, 1, "uint8", "Number of items in room"),
        "room_description_offset": MemoryField("room_desc_offset", 0x0D, 2, "uint16",
                                                "Offset to room description string"),
    })

    # ── Tile Grid (0x0400-0x04FF) ──────────────────────────────────

    tile_grid_region: MemoryRegion = field(
        default_factory=lambda: MemoryRegion(
            "tile_grid", 0x0400, 225,
            "Tile grid (15x15 = 225 bytes)",
            structure="grid"
        )
    )

    TILE_GRID_WIDTH: int = 15
    TILE_GRID_HEIGHT: int = 15
    TILE_GRID_START: int = 0x0400

    # ── Creature Data (0x0500-0x05FF) ──────────────────────────────

    creature_data_region: MemoryRegion = field(
        default_factory=lambda: MemoryRegion(
            "creature_data", 0x0500, 256,
            "Creature data block (up to 16 creatures, 16 bytes each)",
            structure="block"
        )
    )

    CREATURE_SLOT_SIZE: int = 16
    MAX_CREATURES: int = 16
    CREATURE_DATA_START: int = 0x0500

    creature_fields: Dict[str, MemoryField] = field(default_factory=lambda: {
        "id": MemoryField("id", 0x00, 1, "uint8", "Creature type ID"),
        "hp": MemoryField("hp", 0x01, 1, "uint8", "Current hit points"),
        "max_hp": MemoryField("max_hp", 0x02, 1, "uint8", "Maximum hit points"),
        "x": MemoryField("x", 0x03, 1, "uint8", "X position on tile grid"),
        "y": MemoryField("y", 0x04, 1, "uint8", "Y position on tile grid"),
        "state": MemoryField("state", 0x05, 1, "uint8", "Creature state",
                              enum_values={
                                  0: "idle",
                                  1: "wandering",
                                  2: "alert",
                                  3: "attacking",
                                  4: "fleeing",
                                  5: "sleeping",
                                  6: "dead",
                                  7: "asleep",
                              }),
        "direction": MemoryField("direction", 0x06, 1, "uint8", "Facing direction",
                                  enum_values={
                                      0: "north", 1: "south",
                                      2: "east", 3: "west",
                                  }),
        "flags": MemoryField("flags", 0x07, 1, "uint8", "Creature flags",
                              enum_values={
                                  0x01: "hostile",
                                  0x02: "friendly",
                                  0x04: "boss",
                                  0x08: "unique",
                                  0x10: "invisible",
                                  0x20: "ethereal",
                                  0x40: "guarding",
                                  0x80: "quest",
                              }),
        "damage": MemoryField("damage", 0x08, 1, "uint8", "Base damage"),
        "ac": MemoryField("ac", 0x09, 1, "uint8", "Armor class"),
        "xp_value": MemoryField("xp_value", 0x0A, 1, "uint8", "XP awarded on defeat"),
        "gold_value": MemoryField("gold_value", 0x0B, 1, "uint8", "Gold carried"),
        "item_drop": MemoryField("item_drop", 0x0C, 1, "uint8", "Item index dropped on defeat"),
        "alert_range": MemoryField("alert_range", 0x0D, 1, "uint8", "Detection range in tiles"),
        "speed": MemoryField("speed", 0x0E, 1, "uint8", "Movement speed"),
        "reserved": MemoryField("reserved", 0x0F, 1, "uint8", "Reserved"),
    })

    # ── Inventory Data (0x0600-0x06FF) ─────────────────────────────

    inventory_region: MemoryRegion = field(
        default_factory=lambda: MemoryRegion(
            "inventory", 0x0600, 256,
            "Inventory data block (up to 32 items, 8 bytes each)",
            structure="block"
        )
    )

    INVENTORY_SLOT_SIZE: int = 8
    MAX_INVENTORY: int = 32
    INVENTORY_START: int = 0x0600

    inventory_fields: Dict[str, MemoryField] = field(default_factory=lambda: {
        "item_id": MemoryField("item_id", 0x00, 1, "uint8", "Item type ID"),
        "count": MemoryField("count", 0x01, 1, "uint8", "Stack count"),
        "flags": MemoryField("flags", 0x02, 1, "uint8", "Item flags",
                              enum_values={
                                  0x01: "equipped",
                                  0x02: "cursed",
                                  0x04: "blessed",
                                  0x08: "identified",
                                  0x10: "charged",
                                  0x20: "container",
                              }),
        "charges": MemoryField("charges", 0x03, 1, "uint8", "Remaining charges (for magic items)"),
        "condition": MemoryField("condition", 0x04, 1, "uint8", "Item condition (0-100)"),
        "value": MemoryField("value", 0x05, 2, "uint16", "Gold value"),
        "reserved": MemoryField("reserved", 0x07, 1, "uint8", "Reserved"),
    })

    # ── Story Flags (0x0700-0x07FF) ────────────────────────────────

    story_flags_region: MemoryRegion = field(
        default_factory=lambda: MemoryRegion(
            "story_flags", 0x0700, 256,
            "Story flags block (256 boolean flags)",
            structure="block"
        )
    )

    STORY_FLAGS_START: int = 0x0700
    STORY_FLAG_COUNT: int = 256

    # ── Room Descriptions (0x0800-0x0FFF) ──────────────────────────

    room_descriptions_region: MemoryRegion = field(
        default_factory=lambda: MemoryRegion(
            "room_descriptions", 0x0800, 2048,
            "Room description string data",
            structure="string_table"
        )
    )

    ROOM_DESCRIPTIONS_START: int = 0x0800
    ROOM_DESCRIPTIONS_SIZE: int = 2048

    # ── Tile Definitions (0x1000-0x1FFF) ───────────────────────────

    tile_definitions_region: MemoryRegion = field(
        default_factory=lambda: MemoryRegion(
            "tile_definitions", 0x1000, 4096,
            "Tile type definitions (up to 128 tiles, 32 bytes each)",
            structure="block"
        )
    )

    TILE_DEFINITION_SIZE: int = 32
    MAX_TILE_TYPES: int = 128
    TILE_DEFINITIONS_START: int = 0x1000

    # ── Creature Definitions (0x2000-0x2FFF) ───────────────────────

    creature_definitions_region: MemoryRegion = field(
        default_factory=lambda: MemoryRegion(
            "creature_definitions", 0x2000, 4096,
            "Creature type definitions (up to 64 creatures, 64 bytes each)",
            structure="block"
        )
    )

    CREATURE_DEFINITION_SIZE: int = 64
    MAX_CREATURE_TYPES: int = 64
    CREATURE_DEFINITIONS_START: int = 0x2000

    # ── Item Definitions (0x3000-0x3FFF) ───────────────────────────

    item_definitions_region: MemoryRegion = field(
        default_factory=lambda: MemoryRegion(
            "item_definitions", 0x3000, 4096,
            "Item type definitions (up to 128 items, 32 bytes each)",
            structure="block"
        )
    )

    ITEM_DEFINITION_SIZE: int = 32
    MAX_ITEM_TYPES: int = 128
    ITEM_DEFINITIONS_START: int = 0x3000

    # ── Room Definitions (0x4000-0x4FFF) ───────────────────────────

    room_definitions_region: MemoryRegion = field(
        default_factory=lambda: MemoryRegion(
            "room_definitions", 0x4000, 4096,
            "Room definitions (up to 64 rooms, 64 bytes each)",
            structure="block"
        )
    )

    ROOM_DEFINITION_SIZE: int = 64
    MAX_ROOMS: int = 64
    ROOM_DEFINITIONS_START: int = 0x4000

    # ── Message Strings (0x5000-0x5FFF) ────────────────────────────

    message_strings_region: MemoryRegion = field(
        default_factory=lambda: MemoryRegion(
            "message_strings", 0x5000, 4096,
            "Game message strings",
            structure="string_table"
        )
    )

    MESSAGE_STRINGS_START: int = 0x5000
    MESSAGE_STRINGS_SIZE: int = 4096

    # ── Tile Type Constants ────────────────────────────────────────

    TILE_TYPES: Dict[int, str] = field(default_factory=lambda: {
        0x00: "empty",
        0x01: "wall",
        0x02: "floor",
        0x03: "door",
        0x04: "locked_door",
        0x05: "secret_door",
        0x06: "stairs_up",
        0x07: "stairs_down",
        0x08: "water",
        0x09: "lava",
        0x0A: "trap",
        0x0B: "chest",
        0x0C: "altar",
        0x0D: "fountain",
        0x0E: "torch",
        0x0F: "brazier",
        0x10: "table",
        0x11: "chair",
        0x12: "bed",
        0x13: "bookshelf",
        0x14: "cabinet",
        0x15: "barrel",
        0x16: "crate",
        0x17: "pillar",
        0x18: "statue",
        0x19: "fountain",
        0x1A: "pool",
        0x1B: "bridge",
        0x1C: "chasm",
        0x1D: "web",
        0x1E: "moss",
        0x1F: "rubble",
        0x20: "grass",
        0x21: "tree",
        0x22: "bush",
        0x23: "flower",
        0x24: "path",
        0x25: "road",
        0x26: "wall_ns",
        0x27: "wall_ew",
        0x28: "wall_ne",
        0x29: "wall_nw",
        0x2A: "wall_se",
        0x2B: "wall_sw",
        0x2C: "wall_cross",
        0x2D: "wall_t_n",
        0x2E: "wall_t_s",
        0x2F: "wall_t_e",
        0x30: "wall_t_w",
        0x31: "wall_end_n",
        0x32: "wall_end_s",
        0x33: "wall_end_e",
        0x34: "wall_end_w",
        0x35: "floor_marked",
        0x36: "floor_blood",
        0x37: "floor_ash",
        0x38: "floor_water",
        0x39: "floor_ice",
        0x3A: "floor_magic",
        0x3B: "teleporter",
        0x3C: "spinner",
        0x3D: "pit",
        0x3E: "spikes",
        0x3F: "exit",
    })

    # ── Item Type Constants ────────────────────────────────────────

    ITEM_TYPES: Dict[int, str] = field(default_factory=lambda: {
        0x00: "none",
        0x01: "sword",
        0x02: "axe",
        0x03: "mace",
        0x04: "dagger",
        0x05: "spear",
        0x06: "bow",
        0x07: "arrows",
        0x08: "staff",
        0x09: "wand",
        0x0A: "shield",
        0x0B: "helm",
        0x0C: "armor_leather",
        0x0D: "armor_chain",
        0x0E: "armor_plate",
        0x0F: "ring",
        0x10: "amulet",
        0x11: "potion_healing",
        0x12: "potion_strength",
        0x13: "potion_invisibility",
        0x14: "potion_poison",
        0x15: "scroll_fire",
        0x16: "scroll_lightning",
        0x17: "scroll_teleport",
        0x18: "scroll_identify",
        0x19: "key_iron",
        0x1A: "key_gold",
        0x1B: "key_silver",
        0x1C: "key_magic",
        0x1D: "gem_ruby",
        0x1E: "gem_emerald",
        0x1F: "gem_diamond",
        0x20: "gem_sapphire",
        0x21: "coin_gold",
        0x22: "coin_silver",
        0x23: "coin_copper",
        0x24: "torch",
        0x25: "lantern",
        0x26: "food",
        0x27: "water_skin",
        0x28: "rope",
        0x29: "grappling_hook",
        0x2A: "lockpick",
        0x2B: "map",
        0x2C: "compass",
        0x2D: "crystal_ball",
        0x2E: "horn",
        0x2F: "drum",
        0x30: "flute",
        0x31: "book",
        0x32: "scroll_blank",
        0x33: "potion_blank",
        0x34: "artifact",
        0x35: "quest_item",
        0x36: "treasure",
        0x37: "container",
    })

    # ── Creature Type Constants ────────────────────────────────────

    CREATURE_TYPES: Dict[int, str] = field(default_factory=lambda: {
        0x00: "none",
        0x01: "rat",
        0x02: "bat",
        0x03: "spider",
        0x04: "snake",
        0x05: "wolf",
        0x06: "bear",
        0x07: "troll",
        0x08: "orc",
        0x09: "goblin",
        0x0A: "kobold",
        0x0B: "skeleton",
        0x0C: "zombie",
        0x0D: "ghost",
        0x0E: "wraith",
        0x0F: "vampire",
        0x10: "demon",
        0x11: "dragon",
        0x12: "giant",
        0x13: "golem",
        0x14: "elemental",
        0x15: "gargoyle",
        0x16: "harpy",
        0x17: "centaur",
        0x18: "minotaur",
        0x19: "chimera",
        0x1A: "griffin",
        0x1B: "wyvern",
        0x1C: "lich",
        0x1D: "beholder",
        0x1E: "slime",
        0x1F: "mimic",
        0x20: "bandit",
        0x21: "knight",
        0x22: "mage",
        0x23: "priest",
        0x24: "merchant",
        0x25: "peasant",
        0x26: "guard",
        0x27: "king",
        0x28: "queen",
        0x29: "princess",
        0x2A: "wizard",
        0x2B: "necromancer",
        0x2C: "druid",
        0x2D: "ranger",
        0x2E: "paladin",
        0x2F: "assassin",
        0x30: "thief",
        0x31: "bard",
        0x32: "monk",
        0x33: "barbarian",
    })

    def get_tile_name(self, tile_id: int) -> str:
        """Get the human-readable name for a tile type ID"""
        return self.TILE_TYPES.get(tile_id, f"unknown_tile_{tile_id:02X}")

    def get_item_name(self, item_id: int) -> str:
        """Get the human-readable name for an item type ID"""
        return self.ITEM_TYPES.get(item_id, f"unknown_item_{item_id:02X}")

    def get_creature_name(self, creature_id: int) -> str:
        """Get the human-readable name for a creature type ID"""
        return self.CREATURE_TYPES.get(creature_id, f"unknown_creature_{creature_id:02X}")

    def get_player_stat_address(self, field_name: str) -> Optional[int]:
        """Get the absolute memory address for a player stat field"""
        field = self.player_stats_fields.get(field_name)
        if field:
            return self.player_stats_region.start + field.offset
        return None

    def get_creature_slot_address(self, slot_index: int) -> int:
        """Get the starting address for a creature slot"""
        return self.CREATURE_DATA_START + (slot_index * self.CREATURE_SLOT_SIZE)

    def get_inventory_slot_address(self, slot_index: int) -> int:
        """Get the starting address for an inventory slot"""
        return self.INVENTORY_START + (slot_index * self.INVENTORY_SLOT_SIZE)

    def get_tile_grid_address(self, x: int, y: int) -> int:
        """Get the memory address for a specific tile in the grid"""
        return self.TILE_GRID_START + (y * self.TILE_GRID_WIDTH) + x

    def get_story_flag_address(self, flag_index: int) -> int:
        """Get the memory address for a story flag"""
        return self.STORY_FLAGS_START + flag_index

    def get_room_description_address(self, room_id: int) -> int:
        """Get the memory address for a room description string"""
        return self.ROOM_DESCRIPTIONS_START + (room_id * 32)

    def get_tile_definition_address(self, tile_type: int) -> int:
        """Get the memory address for a tile type definition"""
        return self.TILE_DEFINITIONS_START + (tile_type * self.TILE_DEFINITION_SIZE)

    def get_creature_definition_address(self, creature_type: int) -> int:
        """Get the memory address for a creature type definition"""
        return self.CREATURE_DEFINITIONS_START + (creature_type * self.CREATURE_DEFINITION_SIZE)

    def get_item_definition_address(self, item_type: int) -> int:
        """Get the memory address for an item type definition"""
        return self.ITEM_DEFINITIONS_START + (item_type * self.ITEM_DEFINITION_SIZE)

    def get_room_definition_address(self, room_id: int) -> int:
        """Get the memory address for a room definition"""
        return self.ROOM_DEFINITIONS_START + (room_id * self.ROOM_DEFINITION_SIZE)


# ── Singleton Instance ─────────────────────────────────────────────

ACS_MEMORY_MAP: ACSMemoryMap = ACSMemoryMap()


def get_acs_memory_map() -> ACSMemoryMap:
    """Get the singleton ACS memory map instance"""
    return ACS_MEMORY_MAP
