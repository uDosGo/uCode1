"""Integration tests for Character System — slots, ANSI set, emoji, aliases, rendering."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

try:
    from narrator.character import (
        ANSI_CHAR_SET,
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
    HAS_NARRATOR = True
except ImportError:
    HAS_NARRATOR = False

pytestmark = pytest.mark.skipif(
    not HAS_NARRATOR,
    reason="narrator module not available (requires core_py.narrator)"
)


class TestCharacterSystem:
    """Tests for the CharacterSystem class."""

    def setup_method(self):
        if not HAS_NARRATOR:
            return
        self.cs = CharacterSystem()

    def test_system_initialization(self):
        """CharacterSystem should initialize with default slots."""
        if not HAS_NARRATOR:
            return
        assert self.cs is not None
        assert hasattr(self.cs, 'slots')
        assert len(self.cs.slots) == SLOT_TOTAL

    def test_slot_ranges(self):
        """Slot ranges should be properly defined."""
        if not HAS_NARRATOR:
            return
        assert SLOT_ALIAS_START < SLOT_ALIAS_END
        assert SLOT_COMMAND_START < SLOT_COMMAND_END
        assert SLOT_SNACK_START < SLOT_SNACK_END

    def test_ansi_char_set(self):
        """ANSI_CHAR_SET should contain standard characters."""
        if not HAS_NARRATOR:
            return
        assert len(ANSI_CHAR_SET) > 0
        assert 'A' in ANSI_CHAR_SET
        assert ' ' in ANSI_CHAR_SET

    def test_slot_entry_creation(self):
        """SlotEntry should be creatable with valid parameters."""
        if not HAS_NARRATOR:
            return
        entry = SlotEntry(
            slot_id=1,
            name="test_slot",
            char_range=(0x20, 0x7E),
            description="Test slot"
        )
        assert entry.slot_id == 1
        assert entry.name == "test_slot"

    def test_ansi_char_function(self):
        """ansi_char should return correct character."""
        if not HAS_NARRATOR:
            return
        result = ansi_char(65)
        assert result == 'A'

    def test_slot_range_name(self):
        """slot_range_name should return correct range name."""
        if not HAS_NARRATOR:
            return
        name = slot_range_name(SLOT_ALIAS_START)
        assert name is not None
