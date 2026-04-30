"""
Character System — Slot mapping, ANSI set, emoji overlays, and rendering priority.

Architecture:
  Slot Range    | Purpose       | Example
  --------------|---------------|-----------------------
  0-31          | Command Slots | System operations
  32-63         | Snack Slots   | Executable snacks
  64-95         | (reserved)    | Future use
  96-127        | Alias Slots   | Word aliases per term

Rendering Priority (highest wins):
  emoji > word alias > teletext char > ANSI char
"""

from dataclasses import dataclass, field
from typing import Optional

# ── Slot Ranges ─────────────────────────────────────────────────────────────

SLOT_COMMAND_START = 0
SLOT_COMMAND_END = 31
SLOT_SNACK_START = 32
SLOT_SNACK_END = 63
SLOT_RESERVED_START = 64
SLOT_RESERVED_END = 95
SLOT_ALIAS_START = 96
SLOT_ALIAS_END = 127

SLOT_TOTAL = 128


def slot_range_name(slot: int) -> str:
    """Get the human-readable range name for a slot number."""
    if SLOT_COMMAND_START <= slot <= SLOT_COMMAND_END:
        return "command"
    elif SLOT_SNACK_START <= slot <= SLOT_SNACK_END:
        return "snack"
    elif SLOT_RESERVED_START <= slot <= SLOT_RESERVED_END:
        return "reserved"
    elif SLOT_ALIAS_START <= slot <= SLOT_ALIAS_END:
        return "alias"
    return "unknown"


# ── 128-Character ANSI Set ─────────────────────────────────────────────────

ANSI_CHAR_SET: dict[int, str] = {
    # Command Slots 0-31 — system control characters / symbols
    0:  "@",   1:  "#",   2:  "$",   3:  "%",   4:  "^",
    5:  "&",   6:  "*",   7:  "!",   8:  "?",   9:  "+",
    10: "=",   11: "<",   12: ">",   13: "~",   14: "|",
    15: "\\",  16: "/",   17: "[",   18: "]",   19: "{",
    20: "}",   21: "(",   22: ")",   23: "'",   24: '"',
    25: ":",   26: ";",   27: ",",   28: ".",   29: "-",
    30: "_",   31: "`",
    # Snack Slots 32-63 — letters A-Z (upper), then 0-9
    32: "A",   33: "B",   34: "C",   35: "D",   36: "E",
    37: "F",   38: "G",   39: "H",   40: "I",   41: "J",
    42: "K",   43: "L",   44: "M",   45: "N",   46: "O",
    47: "P",   48: "Q",   49: "R",   50: "S",   51: "T",
    52: "U",   53: "V",   54: "W",   55: "X",   56: "Y",
    57: "Z",   58: "0",   59: "1",   60: "2",   61: "3",
    62: "4",   63: "5",
    # Reserved 64-95 — lowercase letters
    64: "a",   65: "b",   66: "c",   67: "d",   68: "e",
    69: "f",   70: "g",   71: "h",   72: "i",   73: "j",
    74: "k",   75: "l",   76: "m",   77: "n",   78: "o",
    79: "p",   80: "q",   81: "r",   82: "s",   83: "t",
    84: "u",   85: "v",   86: "w",   87: "x",   88: "y",
    89: "z",   90: "6",   91: "7",   92: "8",   93: "9",
    94: " ",   95: ".",
    # Alias Slots 96-127 — extended symbols
    96: "¡",   97: "¢",   98: "£",   99: "¤",   100: "¥",
    101: "¦",  102: "§",  103: "¨",  104: "©",  105: "ª",
    106: "«",  107: "¬",  108: "®",  109: "¯",  110: "°",
    111: "±",  112: "²",  113: "³",  114: "´",  115: "µ",
    116: "¶",  117: "·",  118: "¸",  119: "¹",  120: "º",
    121: "»",  122: "¼",  123: "½",  124: "¾",  125: "¿",
    126: "×",  127: "÷",
}


def ansi_char(slot: int) -> str:
    """Get the ANSI character for a slot number (0-127)."""
    return ANSI_CHAR_SET.get(slot, "?")


# ── Slot Entry ──────────────────────────────────────────────────────────────

@dataclass
class SlotEntry:
    """A single slot in the 128-slot character system."""
    slot: int
    term_id: str = ""           # Linked lexicon term ID
    label: str = ""             # Human-readable label
    ansi_char: str = ""         # Override ANSI character (defaults from ANSI_CHAR_SET)
    emoji: str = ""             # Emoji overlay
    word_alias: str = ""        # Word alias for this slot
    description: str = ""       # Description

    def __post_init__(self):
        if not self.ansi_char:
            self.ansi_char = ANSI_CHAR_SET.get(self.slot, "?")

    @property
    def range_name(self) -> str:
        return slot_range_name(self.slot)

    def render(self, priority: str = "emoji") -> str:
        """Render this slot's character at the given priority level.

        Priority levels (highest first):
          - emoji:     emoji > word_alias > ansi_char
          - word:      word_alias > ansi_char
          - teletext:  ansi_char only
          - ansi:      ansi_char only
        """
        if priority == "emoji" and self.emoji:
            return self.emoji
        if priority in ("emoji", "word") and self.word_alias:
            return self.word_alias
        return self.ansi_char

    def to_dict(self) -> dict:
        return {
            "slot": self.slot,
            "range": self.range_name,
            "term_id": self.term_id,
            "label": self.label,
            "ansi_char": self.ansi_char,
            "emoji": self.emoji,
            "word_alias": self.word_alias,
            "description": self.description,
        }


# ── Default Slot Mappings (from core lexicon terms) ────────────────────────

DEFAULT_SLOTS: dict[int, SlotEntry] = {
    # Command Slots 0-4 — vault operations
    0: SlotEntry(0, "vault", "Vault", emoji="💾", word_alias="vault", description="Core data storage"),
    1: SlotEntry(1, "note", "Note", emoji="📝", word_alias="note", description="Markdown document"),
    2: SlotEntry(2, "tag", "Tag", emoji="🏷️", word_alias="tag", description="Metadata label"),
    3: SlotEntry(3, "feed", "Feed", emoji="📡", word_alias="feed", description="Activity log"),
    4: SlotEntry(4, "task", "Task", emoji="✅", word_alias="task", description="Action item"),
    # Snack Slots 32-37 — core snacks
    32: SlotEntry(32, "snack", "Snack", emoji="🍱", word_alias="snack", description="Executable container"),
    33: SlotEntry(33, "ok", "OK Agent", emoji="🤖", word_alias="oracle", description="AI Assistant"),
    34: SlotEntry(34, "grid", "Grid", emoji="🧩", word_alias="grid", description="ASCII grid layout"),
    35: SlotEntry(35, "cell", "Cell", emoji="🔲", word_alias="cell", description="Storage unit"),
    36: SlotEntry(36, "spatial", "Spatial", emoji="🗺️", word_alias="map", description="Coordinate system"),
    37: SlotEntry(37, "skill", "Skill", emoji="🎯", word_alias="skill", description="Function template"),
    # Reserved 64 — link
    64: SlotEntry(64, "link", "Link", emoji="🔗", word_alias="thread", description="Bidirectional reference"),
    # Alias Slots 96+ extend with custom aliases
}


# ── Character System ────────────────────────────────────────────────────────

class CharacterSystem:
    """The 128-slot character system with emoji overlays and aliases."""

    def __init__(self):
        self._slots: dict[int, SlotEntry] = {}
        self._term_map: dict[str, int] = {}  # term_id → slot number
        self.load_defaults()

    def load_defaults(self):
        """Load default slot mappings from DEFAULT_SLOTS."""
        for slot, entry in DEFAULT_SLOTS.items():
            # Deep-copy to avoid mutation across instances
            self._slots[slot] = SlotEntry(
                slot=entry.slot, term_id=entry.term_id, label=entry.label,
                ansi_char=entry.ansi_char, emoji=entry.emoji,
                word_alias=entry.word_alias, description=entry.description,
            )
            if entry.term_id:
                self._term_map[entry.term_id] = slot

    def get(self, slot: int) -> Optional[SlotEntry]:
        """Get a slot entry by slot number."""
        return self._slots.get(slot)

    def get_by_term(self, term_id: str) -> Optional[SlotEntry]:
        """Find a slot by lexicon term ID."""
        slot = self._term_map.get(term_id)
        if slot is not None:
            return self._slots.get(slot)
        return None

    def assign(self, entry: SlotEntry):
        """Assign a slot entry (overrides defaults)."""
        self._slots[entry.slot] = entry
        if entry.term_id:
            self._term_map[entry.term_id] = entry.slot

    def assign_alias(self, slot: int, alias: str):
        """Assign a word alias to an existing slot."""
        if slot in self._slots:
            self._slots[slot].word_alias = alias

    def assign_emoji(self, slot: int, emoji: str):
        """Assign an emoji overlay to an existing slot."""
        if slot in self._slots:
            self._slots[slot].emoji = emoji

    def render_line(self, slots: list[int], priority: str = "emoji") -> str:
        """Render a line from a list of slot numbers.

        Args:
            slots: List of slot numbers to render.
            priority: Rendering priority ('emoji', 'word', 'teletext', 'ansi').

        Returns:
            Rendered string.
        """
        chars = []
        for s in slots:
            if s in self._slots:
                chars.append(self._slots[s].render(priority))
            else:
                chars.append(ansi_char(s))
        return "".join(chars)

    def render_grid(self, rows: list[list[int]], priority: str = "emoji") -> str:
        """Render a grid of slot numbers.

        Args:
            rows: List of rows, each a list of slot numbers.
            priority: Rendering priority.

        Returns:
            Multi-line rendered string.
        """
        return "\n".join(self.render_line(r, priority) for r in rows)

    def list_slots(self, range_name: Optional[str] = None) -> list[SlotEntry]:
        """List all slots, optionally filtered by range name."""
        entries = list(self._slots.values())
        if range_name:
            entries = [e for e in entries if e.range_name == range_name]
        return sorted(entries, key=lambda e: e.slot)

    def unassigned_slots(self) -> list[int]:
        """List all unassigned slots (empty slots)."""
        return [s for s in range(SLOT_TOTAL) if s not in self._slots]

    def to_dict(self) -> dict:
        return {
            "slots": {str(k): v.to_dict() for k, v in self._slots.items()},
            "total": SLOT_TOTAL,
            "assigned": len(self._slots),
            "unassigned": len(self.unassigned_slots()),
        }
