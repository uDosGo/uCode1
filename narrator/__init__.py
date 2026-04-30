"""
Narrator & Lexicon — Story generation and term mapping for uDos.

Narrator: Converts feed/snack events into human-readable stories
using the Wizard-in-a-Dungeon metaphor.

Lexicon: The 3-lane term mapping system (Dev / Story / Student)
that defines what things are called across the uDos ecosystem.

Character System: 128-slot character mapping with ANSI set, emoji
overlays, word aliases, and rendering priority (emoji > word > teletext > ANSI).
"""

from .character import (
    ANSI_CHAR_SET,
    DEFAULT_SLOTS,
    SLOT_ALIAS_END,
    SLOT_ALIAS_START,
    SLOT_COMMAND_END,
    SLOT_COMMAND_START,
    SLOT_SNACK_END,
    SLOT_SNACK_START,
    SLOT_TOTAL,
    CharacterSystem,
    SlotEntry,
    ansi_char,
    slot_range_name,
)
from .cli import main as cli_main
from .lexicon import LANE_DEV, LANE_STORY, LANE_STUDENT, Lexicon, LexiconEntry
from .narrator import NarratorEngine

__all__ = [
    "NarratorEngine", "Lexicon", "LexiconEntry",
    "LANE_DEV", "LANE_STORY", "LANE_STUDENT",
    "CharacterSystem", "SlotEntry",
    "ANSI_CHAR_SET", "DEFAULT_SLOTS",
    "ansi_char", "slot_range_name",
    "SLOT_COMMAND_START", "SLOT_COMMAND_END",
    "SLOT_SNACK_START", "SLOT_SNACK_END",
    "SLOT_ALIAS_START", "SLOT_ALIAS_END",
    "SLOT_TOTAL",
    "cli_main",
]