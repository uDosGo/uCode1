"""
128-Slot Character Palette Manager

Manages the 128-slot teletext character set with emoji overlays.
Provides the canonical character map used by all grid editors.

Slot Architecture:
  - 0-31:   Teletext blocks (CP437 block graphics)
  - 32-126: Printable ASCII
  - 127:    DEL / Reserved
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from enum import Enum


class SlotCategory(Enum):
    """Category of a character slot."""
    TELETEXT_BLOCK = "teletext_block"
    PRINTABLE_ASCII = "printable_ascii"
    CONTROL = "control"
    RESERVED = "reserved"


@dataclass
class SlotEntry:
    """A single slot in the 128-character map."""
    slot: int
    char: str
    name: str
    category: SlotCategory
    hex_code: str
    unicode: str
    emoji_overlay: Optional[str] = None
    word_alias: Optional[str] = None
    description: str = ""

    @property
    def display_char(self) -> str:
        """Get the display character, preferring emoji overlay if set."""
        if self.emoji_overlay:
            return self.emoji_overlay
        return self.char


class CharacterPalette:
    """
    Manages the 128-slot character palette.
    
    Provides lookup, filtering, and emoji overlay management.
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

    # Default emoji overlays for common slots
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
        self._slots: Dict[int, SlotEntry] = {}
        self._build_palette()

    def _build_palette(self) -> None:
        """Build the full 128-slot palette."""
        # Slots 0-31: Teletext blocks
        for slot, (char, name, desc) in self.TELETEXT_BLOCKS.items():
            self._slots[slot] = SlotEntry(
                slot=slot,
                char=char,
                name=name,
                category=SlotCategory.TELETEXT_BLOCK,
                hex_code=f'0x{slot:02X}',
                unicode=f'U+{ord(char):04X}',
                emoji_overlay=self.DEFAULT_EMOJI_OVERLAYS.get(slot),
                description=desc,
            )

        # Slots 32-126: Printable ASCII
        for slot in range(32, 127):
            char = chr(slot)
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
            name = name_map.get(slot, f'CHAR_{slot}')
            self._slots[slot] = SlotEntry(
                slot=slot,
                char=char,
                name=name,
                category=SlotCategory.PRINTABLE_ASCII,
                hex_code=f'0x{slot:02X}',
                unicode=f'U+{ord(char):04X}',
                description=f'ASCII {slot}: {repr(char)}',
            )

        # Slot 127: DEL / Reserved
        self._slots[127] = SlotEntry(
            slot=127,
            char='\x7f',
            name='DEL',
            category=SlotCategory.RESERVED,
            hex_code='0x7F',
            unicode='U+007F',
            description='Delete / Reserved',
        )

    def get(self, slot: int) -> Optional[SlotEntry]:
        """Get a slot entry by slot number."""
        return self._slots.get(slot)

    def get_by_char(self, char: str) -> Optional[SlotEntry]:
        """Find a slot by its character."""
        for entry in self._slots.values():
            if entry.char == char:
                return entry
        return None

    def get_by_name(self, name: str) -> Optional[SlotEntry]:
        """Find a slot by its name (case-insensitive)."""
        name_upper = name.upper()
        for entry in self._slots.values():
            if entry.name == name_upper:
                return entry
        return None

    def get_all_slots(self) -> List[SlotEntry]:
        """Get all 128 slots in order."""
        return [self._slots[i] for i in range(128)]

    def get_teletext_blocks(self) -> List[SlotEntry]:
        """Get slots 0-31 (teletext block characters)."""
        return [self._slots[i] for i in range(32)]

    def get_printable_ascii(self) -> List[SlotEntry]:
        """Get slots 32-126 (printable ASCII)."""
        return [self._slots[i] for i in range(32, 127)]

    def set_emoji_overlay(self, slot: int, emoji: Optional[str]) -> None:
        """Set or clear an emoji overlay for a slot."""
        if slot in self._slots:
            self._slots[slot].emoji_overlay = emoji

    def set_word_alias(self, slot: int, alias: Optional[str]) -> None:
        """Set or clear a word alias for a slot."""
        if slot in self._slots:
            self._slots[slot].word_alias = alias

    def search(self, query: str) -> List[SlotEntry]:
        """Search slots by name, char, or description."""
        query = query.lower()
        results = []
        for entry in self._slots.values():
            if (query in entry.name.lower() or
                query in entry.char.lower() or
                query in entry.description.lower() or
                (entry.emoji_overlay and query in entry.emoji_overlay.lower())):
                results.append(entry)
        return results

    def to_dict(self) -> Dict[str, Any]:
        """Export the full palette as a dictionary."""
        return {
            'version': '1.0',
            'total_slots': 128,
            'slots': {
                str(slot): {
                    'slot': entry.slot,
                    'char': entry.char,
                    'name': entry.name,
                    'category': entry.category.value,
                    'hex': entry.hex_code,
                    'unicode': entry.unicode,
                    'emoji': entry.emoji_overlay,
                    'alias': entry.word_alias,
                    'desc': entry.description,
                }
                for slot, entry in self._slots.items()
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterPalette':
        """Restore a palette from a dictionary."""
        palette = cls()
        slots_data = data.get('slots', {})
        if isinstance(slots_data, dict):
            for slot_str, slot_data in slots_data.items():
                slot = int(slot_str)
                if slot in palette._slots and isinstance(slot_data, dict):
                    palette._slots[slot].emoji_overlay = slot_data.get('emoji')
                    palette._slots[slot].word_alias = slot_data.get('alias')
        return palette

