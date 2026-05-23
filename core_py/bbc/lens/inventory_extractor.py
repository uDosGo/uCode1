"""
Inventory Extractor — ACS Inventory Data Extraction

Extracts inventory data from ACS game memory, including equipped items,
carried items, and item properties.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import time

from .acs_memory_map import ACSMemoryMap, get_acs_memory_map


@dataclass
class InventoryItem:
    """A single item in the inventory"""
    slot_index: int
    item_id: int
    item_name: str
    count: int = 1
    is_equipped: bool = False
    is_cursed: bool = False
    is_blessed: bool = False
    is_identified: bool = False
    is_charged: bool = False
    is_container: bool = False
    charges: int = 0
    condition: int = 100
    value: int = 0
    category: str = "misc"

    def to_dict(self) -> Dict[str, Any]:
        """Serialize inventory item to dictionary"""
        return {
            "slot_index": self.slot_index,
            "item_id": self.item_id,
            "item_name": self.item_name,
            "count": self.count,
            "is_equipped": self.is_equipped,
            "is_cursed": self.is_cursed,
            "is_blessed": self.is_blessed,
            "is_identified": self.is_identified,
            "is_charged": self.is_charged,
            "is_container": self.is_container,
            "charges": self.charges,
            "condition": self.condition,
            "value": self.value,
            "category": self.category,
        }


@dataclass
class InventorySlot:
    """An equipment slot on the character"""
    slot_name: str
    item: Optional[InventoryItem] = None
    slot_index: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize inventory slot to dictionary"""
        return {
            "slot_name": self.slot_name,
            "item": self.item.to_dict() if self.item else None,
            "slot_index": self.slot_index,
        }


class InventoryExtractor:
    """
    Extracts inventory data from ACS game memory.

    Reads inventory slots from memory and produces structured
    InventoryItem objects with properties, categories, and
    equipment status.
    """

    ITEM_CATEGORIES: Dict[int, str] = {
        0x01: "weapon", 0x02: "weapon", 0x03: "weapon", 0x04: "weapon",
        0x05: "weapon", 0x06: "weapon", 0x07: "ammo", 0x08: "weapon",
        0x09: "weapon", 0x0A: "armor", 0x0B: "armor", 0x0C: "armor",
        0x0D: "armor", 0x0E: "armor", 0x0F: "jewelry", 0x10: "jewelry",
        0x11: "potion", 0x12: "potion", 0x13: "potion", 0x14: "potion",
        0x15: "scroll", 0x16: "scroll", 0x17: "scroll", 0x18: "scroll",
        0x19: "key", 0x1A: "key", 0x1B: "key", 0x1C: "key",
        0x1D: "gem", 0x1E: "gem", 0x1F: "gem", 0x20: "gem",
        0x21: "money", 0x22: "money", 0x23: "money",
        0x24: "tool", 0x25: "tool", 0x26: "food", 0x27: "tool",
        0x28: "tool", 0x29: "tool", 0x2A: "tool", 0x2B: "tool",
        0x2C: "tool", 0x2D: "tool", 0x2E: "tool", 0x2F: "tool",
        0x30: "tool", 0x31: "book", 0x32: "scroll", 0x33: "potion",
        0x34: "artifact", 0x35: "quest", 0x36: "treasure", 0x37: "container",
    }

    EQUIPMENT_SLOTS: Dict[str, str] = {
        "weapon": "weapon_idx",
        "armor": "armor_idx",
        "shield": "shield_idx",
        "helm": "helm_idx",
        "ring": "ring_idx",
    }

    def __init__(self, memory_map: Optional[ACSMemoryMap] = None):
        self.memory_map = memory_map or get_acs_memory_map()
        self._last_inventory: List[InventoryItem] = []
        self._inventory_history: List[List[InventoryItem]] = []

    def extract_inventory(self, memory_reader) -> List[InventoryItem]:
        """
        Extract inventory from ACS memory.

        Args:
            memory_reader: Object with read_byte(address) method

        Returns:
            List of InventoryItem objects
        """
        mm = self.memory_map
        inventory: List[InventoryItem] = []

        for slot in range(mm.MAX_INVENTORY):
            addr = mm.get_inventory_slot_address(slot)
            item_id = memory_reader.read_byte(addr)

            if item_id == 0x00:
                continue

            count = memory_reader.read_byte(addr + 0x01)
            flags = memory_reader.read_byte(addr + 0x02)
            charges = memory_reader.read_byte(addr + 0x03)
            condition = memory_reader.read_byte(addr + 0x04)
            value_low = memory_reader.read_byte(addr + 0x05)
            value_high = memory_reader.read_byte(addr + 0x06)
            value = (value_high << 8) | value_low

            item = InventoryItem(
                slot_index=slot,
                item_id=item_id,
                item_name=mm.get_item_name(item_id),
                count=count,
                is_equipped=bool(flags & 0x01),
                is_cursed=bool(flags & 0x02),
                is_blessed=bool(flags & 0x04),
                is_identified=bool(flags & 0x08),
                is_charged=bool(flags & 0x10),
                is_container=bool(flags & 0x20),
                charges=charges,
                condition=condition,
                value=value,
                category=self.ITEM_CATEGORIES.get(item_id, "misc"),
            )
            inventory.append(item)

        self._last_inventory = inventory
        self._inventory_history.append(list(inventory))
        if len(self._inventory_history) > 100:
            self._inventory_history.pop(0)

        return inventory

    def extract_equipment_slots(self, memory_reader) -> Dict[str, InventorySlot]:
        """
        Extract currently equipped items.

        Args:
            memory_reader: Object with read_byte(address) method

        Returns:
            Dict mapping slot names to InventorySlot objects
        """
        mm = self.memory_map
        slots: Dict[str, InventorySlot] = {}

        for slot_name, stat_field in self.EQUIPMENT_SLOTS.items():
            addr = mm.get_player_stat_address(stat_field)
            if addr is not None:
                item_idx = memory_reader.read_byte(addr)
                if item_idx > 0:
                    item_addr = mm.get_inventory_slot_address(item_idx - 1)
                    item_id = memory_reader.read_byte(item_addr)
                    if item_id > 0:
                        item = InventoryItem(
                            slot_index=item_idx - 1,
                            item_id=item_id,
                            item_name=mm.get_item_name(item_id),
                            is_equipped=True,
                            category=self.ITEM_CATEGORIES.get(item_id, "misc"),
                        )
                        slots[slot_name] = InventorySlot(
                            slot_name=slot_name,
                            item=item,
                            slot_index=item_idx - 1,
                        )

        return slots

    def detect_inventory_changes(self, new_inventory: List[InventoryItem]) -> Dict[str, Any]:
        """
        Detect changes between the last extracted inventory and a new one.

        Args:
            new_inventory: Recently extracted inventory list

        Returns:
            Dict with 'added', 'removed', 'changed' lists and 'summary' string
        """
        if not self._last_inventory:
            return {"added": [], "removed": [], "changed": [], "summary": "initial capture"}

        old_map = {item.slot_index: item for item in self._last_inventory}
        new_map = {item.slot_index: item for item in new_inventory}

        added = []
        removed = []
        changed = []

        for slot_idx, item in new_map.items():
            if slot_idx not in old_map:
                added.append(item.to_dict())
            elif (old_map[slot_idx].item_id != item.item_id or
                  old_map[slot_idx].count != item.count):
                changed.append({
                    "slot": slot_idx,
                    "old": old_map[slot_idx].item_name,
                    "new": item.item_name,
                })

        for slot_idx, item in old_map.items():
            if slot_idx not in new_map:
                removed.append(item.to_dict())

        parts = []
        if added:
            parts.append(f"{len(added)} item(s) gained")
        if removed:
            parts.append(f"{len(removed)} item(s) lost")
        if changed:
            parts.append(f"{len(changed)} item(s) changed")

        return {
            "added": added,
            "removed": removed,
            "changed": changed,
            "summary": ", ".join(parts) if parts else "no changes",
        }

    def get_inventory_value(self, inventory: List[InventoryItem]) -> int:
        """Calculate total gold value of inventory"""
        return sum(item.value * item.count for item in inventory)

    def get_inventory_by_category(self, inventory: List[InventoryItem]) -> Dict[str, List[InventoryItem]]:
        """Group inventory items by category"""
        by_category: Dict[str, List[InventoryItem]] = {}
        for item in inventory:
            if item.category not in by_category:
                by_category[item.category] = []
            by_category[item.category].append(item)
        return by_category
