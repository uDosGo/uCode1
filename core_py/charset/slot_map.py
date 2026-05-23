"""
128-Slot Character Map — Full Character Mapping System

Provides the complete 128-slot character map with metadata,
emoji overlays, CP437 teletext block mapping, and utilities
for character transformation and lookup.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class SlotRange(Enum):
    """Named ranges within the 128-slot map."""
    TELETEXT_BLOCKS = (0, 31, "Teletext Block Graphics")
    PRINTABLE_ASCII = (32, 126, "Printable ASCII")
    CONTROL = (0, 31, "Control Characters")
    RESERVED = (127, 127, "Reserved / DEL")
    ALL = (0, 127, "Full 128-Slot Map")

    def __init__(self, start: int, end: int, description: str):
        self.start = start
        self.end = end
        self.description = description


@dataclass
class SlotMapping:
    """A mapping between a slot and its character representation."""
    slot: int
    char: str
    unicode: str
    name: str
    category: str
    hex_code: str
    emoji_overlay: Optional[str] = None
    word_alias: Optional[str] = None
    description: str = ""

    @property
    def display_char(self) -> str:
        """Get the display character, preferring emoji overlay."""
        return self.emoji_overlay or self.char


class SlotMap:
    """
    Complete 128-slot character map.
    
    Provides:
    - Full slot metadata
    - Emoji overlay management
    - CP437 teletext block mapping
    - Character lookup and search
    - Batch transformation utilities
    """

    # CP437 teletext block characters (slots 0-31)
    TELETEXT_BLOCKS: Dict[int, Tuple[str, str, str]] = {
        0:  ('\u0000', 'NULL', 'Null character'),
        1:  ('\u263A', 'SMILE', 'White smiling face'),
        2:  ('\u263B', 'INV_SMILE', 'Black smiling face'),
        3:  ('\u2665', 'HEART', 'Black heart suit'),
        4:  ('\u2666', 'DIAMOND', 'Black diamond suit'),
        5:  ('\u2663', 'CLUB', 'Black club suit'),
        6:  ('\u2660', 'SPADE', 'Black spade suit'),
        7:  ('\u2022', 'BULLET', 'Bullet'),
        8:  ('\u25D8', 'INV_BULLET', 'Inverse bullet'),
        9:  ('\u25CB', 'CIRCLE', 'White circle'),
        10: ('\u25D9', 'INV_CIRCLE', 'Inverse circle'),
        11: ('\u2642', 'MALE', 'Male sign'),
        12: ('\u2640', 'FEMALE', 'Female sign'),
        13: ('\u266A', 'NOTE', 'Eighth note'),
        14: ('\u266B', 'DBL_NOTE', 'Beamed eighth notes'),
        15: ('\u263C', 'SUN', 'White sun with rays'),
        16: ('\u25BA', 'RARROW', 'Black right-pointing pointer'),
        17: ('\u25C4', 'LARROW', 'Black left-pointing pointer'),
        18: ('\u2195', 'UDARROW', 'Up down arrow'),
        19: ('\u203C', 'DBL_EXCLAM', 'Double exclamation mark'),
        20: ('\u00B6', 'PILCROW', 'Pilcrow sign'),
        21: ('\u00A7', 'SECTION', 'Section sign'),
        22: ('\u2588', 'FULL_BLOCK', 'Full block'),
        23: ('\u2584', 'LOWER_HALF', 'Lower half block'),
        24: ('\u2580', 'UPPER_HALF', 'Upper half block'),
        25: ('\u258C', 'LEFT_HALF', 'Left half block'),
        26: ('\u2590', 'RIGHT_HALF', 'Right half block'),
        27: ('\u2591', 'QUARTER', 'Light shade / quarter block'),
        28: ('\u2592', 'MID', 'Medium shade / mid block'),
        29: ('\u2593', 'DARK', 'Dark shade / dark block'),
        30: ('\u2588', 'LIGHT_BLOCK', 'Full block (alias)'),
        31: (' ', 'RESERVED', 'Reserved'),
    }

    # Default emoji overlays
    DEFAULT_EMOJI_OVERLAYS: Dict[int, str] = {
        1:  '😊',   # Smile
        3:  '❤️',   # Heart
        13: '🎵',   # Music note
        14: '🎶',   # Double note
        15: '☀️',   # Sun
        16: '➡️',   # Right arrow
        17: '⬅️',   # Left arrow
        22: '⬛',   # Full block
    }

    def __init__(self):
        self._mappings: Dict[int, SlotMapping] = {}
        self._build_map()

    def _build_map(self) -> None:
        """Build the full 128-slot map."""
        # Slots 0-31: Teletext blocks
        for slot, (char, name, desc) in self.TELETEXT_BLOCKS.items():
            self._mappings[slot] = SlotMapping(
                slot=slot,
                char=char,
                unicode=f'U+{ord(char):04X}',
                name=name,
                category='teletext_block',
                hex_code=f'0x{slot:02X}',
                emoji_overlay=self.DEFAULT_EMOJI_OVERLAYS.get(slot),
                description=desc,
            )

        # Slots 32-126: Printable ASCII
        name_map = {
            32: 'SPACE', 33: 'EXCLAM', 34: 'QUOTE', 35: 'HASH',
            36: 'DOLLAR', 37: 'PERCENT', 38: 'AMPERSAND', 39: 'APOS',
            40: 'LPAREN', 41: 'RPAREN', 42: 'STAR', 43: 'PLUS',
            44: 'COMMA', 45: 'MINUS', 46: 'DOT', 47: 'SLASH',
            48: 'ZERO', 49: 'ONE', 50: 'TWO', 51: 'THREE',
            52: 'FOUR', 53: 'FIVE', 54: 'SIX', 55: 'SEVEN',
            56: 'EIGHT', 57: 'NINE', 58: 'COLON', 59: 'SEMICOLON',
            60: 'LT', 61: 'EQ', 62: 'GT', 63: 'QUESTION',
            64: 'AT', 65: 'A', 66: 'B', 67: 'C', 68: 'D', 69: 'E',
            70: 'F', 71: 'G', 72: 'H', 73: 'I', 74: 'J', 75: 'K',
            76: 'L', 77: 'M', 78: 'N', 79: 'O', 80: 'P', 81: 'Q',
            82: 'R', 83: 'S', 84: 'T', 85: 'U', 86: 'V', 87: 'W',
            88: 'X', 89: 'Y', 90: 'Z', 91: 'LBRACKET', 92: 'BACKSLASH',
            93: 'RBRACKET', 94: 'CARET', 95: 'UNDERSCORE',
            96: 'BACKTICK', 97: 'a', 98: 'b', 99: 'c', 100: 'd',
            101: 'e', 102: 'f', 103: 'g', 104: 'h', 105: 'i', 106: 'j',
            107: 'k', 108: 'l', 109: 'm', 110: 'n', 111: 'o', 112: 'p',
            113: 'q', 114: 'r', 115: 's', 116: 't', 117: 'u', 118: 'v',
            119: 'w', 120: 'x', 121: 'y', 122: 'z', 123: 'LBRACE',
            124: 'PIPE', 125: 'RBRACE', 126: 'TILDE',
        }
        for slot in range(32, 127):
            char = chr(slot)
            name = name_map.get(slot, f'CHAR_{slot}')
            self._mappings[slot] = SlotMapping(
                slot=slot,
                char=char,
                unicode=f'U+{ord(char):04X}',
                name=name,
                category='printable_ascii',
                hex_code=f'0x{slot:02X}',
                description=f'ASCII {slot}: {repr(char)}',
            )

        # Slot 127: DEL / Reserved
        self._mappings[127] = SlotMapping(
            slot=127,
            char='\x7f',
            unicode='U+007F',
            name='DEL',
            category='reserved',
            hex_code='0x7F',
            description='Delete / Reserved',
        )

    # ── Lookup ───────────────────────────────────────────────

    def get(self, slot: int) -> Optional[SlotMapping]:
        """Get a slot mapping by slot number."""
        return self._mappings.get(slot)

    def get_by_char(self, char: str) -> Optional[SlotMapping]:
        """Find a slot by its character."""
        for mapping in self._mappings.values():
            if mapping.char == char:
                return mapping
        return None

    def get_by_name(self, name: str) -> Optional[SlotMapping]:
        """Find a slot by its name (case-insensitive)."""
        name_upper = name.upper()
        for mapping in self._mappings.values():
            if mapping.name == name_upper:
                return mapping
        return None

    def get_range(self, start: int, end: int) -> List[SlotMapping]:
        """Get all slots in a range."""
        return [self._mappings[i] for i in range(start, end + 1) if i in self._mappings]

    def get_teletext_blocks(self) -> List[SlotMapping]:
        """Get slots 0-31."""
        return self.get_range(0, 31)

    def get_printable_ascii(self) -> List[SlotMapping]:
        """Get slots 32-126."""
        return self.get_range(32, 126)

    def get_all(self) -> List[SlotMapping]:
        """Get all 128 slots."""
        return self.get_range(0, 127)

    # ── Emoji Overlay Management ─────────────────────────────

    def set_emoji_overlay(self, slot: int, emoji: Optional[str]) -> None:
        """Set or clear an emoji overlay for a slot."""
        if slot in self._mappings:
            self._mappings[slot].emoji_overlay = emoji

    def get_emoji_overlay(self, slot: int) -> Optional[str]:
        """Get the emoji overlay for a slot."""
        mapping = self._mappings.get(slot)
        return mapping.emoji_overlay if mapping else None

    def clear_emoji_overlay(self, slot: int) -> None:
        """Clear the emoji overlay for a slot."""
        self.set_emoji_overlay(slot, None)

    def get_slots_with_emoji(self) -> List[SlotMapping]:
        """Get all slots that have emoji overlays."""
        return [m for m in self._mappings.values() if m.emoji_overlay is not None]

    # ── Word Alias Management ────────────────────────────────

    def set_word_alias(self, slot: int, alias: Optional[str]) -> None:
        """Set or clear a word alias for a slot."""
        if slot in self._mappings:
            self._mappings[slot].word_alias = alias

    def get_word_alias(self, slot: int) -> Optional[str]:
        """Get the word alias for a slot."""
        mapping = self._mappings.get(slot)
        return mapping.word_alias if mapping else None

    # ── Search ───────────────────────────────────────────────

    def search(self, query: str) -> List[SlotMapping]:
        """Search slots by name, char, or description."""
        query = query.lower()
        results = []
        for mapping in self._mappings.values():
            if (query in mapping.name.lower() or
                query in mapping.char.lower() or
                query in mapping.description.lower() or
                (mapping.emoji_overlay and query in mapping.emoji_overlay.lower()) or
                (mapping.word_alias and query in mapping.word_alias.lower())):
                results.append(mapping)
        return results

    # ── Transformation Utilities ─────────────────────────────

    def remap_char(self, grid_text: str, old_char: str, new_char: str) -> str:
        """Replace all occurrences of a character in text."""
        return grid_text.replace(old_char, new_char)

    def remap_slot(self, grid_text: str, old_slot: int, new_slot: int) -> str:
        """Replace all occurrences of a slot's character with another slot's character."""
        old_mapping = self._mappings.get(old_slot)
        new_mapping = self._mappings.get(new_slot)
        if old_mapping is None or new_mapping is None:
            return grid_text
        return grid_text.replace(old_mapping.char, new_mapping.char)

    def to_upper(self, grid_text: str) -> str:
        """Convert lowercase ASCII to uppercase in grid text."""
        result = []
        for char in grid_text:
            if 'a' <= char <= 'z':
                result.append(chr(ord(char) - 32))
            else:
                result.append(char)
        return ''.join(result)

    def to_lower(self, grid_text: str) -> str:
        """Convert uppercase ASCII to lowercase in grid text."""
        result = []
        for char in grid_text:
            if 'A' <= char <= 'Z':
                result.append(chr(ord(char) + 32))
            else:
                result.append(char)
        return ''.join(result)

    def invert_case(self, grid_text: str) -> str:
        """Invert the case of ASCII letters in grid text."""
        result = []
        for char in grid_text:
            if 'a' <= char <= 'z':
                result.append(chr(ord(char) - 32))
            elif 'A' <= char <= 'Z':
                result.append(chr(ord(char) + 32))
            else:
                result.append(char)
        return ''.join(result)

    # ── Export ───────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Export the full slot map as a dictionary."""
        return {
            'version': '1.0',
            'total_slots': 128,
            'slots': {
                str(slot): {
                    'slot': m.slot,
                    'char': m.char,
                    'name': m.name,
                    'category': m.category,
                    'hex': m.hex_code,
                    'unicode': m.unicode,
                    'emoji': m.emoji_overlay,
                    'alias': m.word_alias,
                    'desc': m.description,
                }
                for slot, m in self._mappings.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SlotMap':
        """Restore a slot map from a dictionary."""
        slot_map = cls()
        slots_data = data.get('slots', {})
        if isinstance(slots_data, dict):
            for slot_str, slot_data in slots_data.items():
                slot = int(slot_str)
                if slot in slot_map._mappings and isinstance(slot_data, dict):
                    slot_map._mappings[slot].emoji_overlay = slot_data.get('emoji')
                    slot_map._mappings[slot].word_alias = slot_data.get('alias')
        return slot_map
