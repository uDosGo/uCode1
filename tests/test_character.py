"""Integration tests for Character System — slots, ANSI set, emoji, aliases, rendering."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narrator.character import (
    CharacterSystem,
    SlotEntry,
    ansi_char,
    slot_range_name,
    ANSI_CHAR_SET,
    SLOT_COMMAND_START,
    SLOT_COMMAND_END,
    SLOT_SNACK_START,
    SLOT_SNACK_END,
    SLOT_ALIAS_START,
    SLOT_ALIAS_END,
    SLOT_TOTAL,
)


class TestSlotRanges:
    """Slot range classification tests."""

    def test_command_range(self):
        assert slot_range_name(0) == "command"
        assert slot_range_name(15) == "command"
        assert slot_range_name(31) == "command"

    def test_snack_range(self):
        assert slot_range_name(32) == "snack"
        assert slot_range_name(50) == "snack"
        assert slot_range_name(63) == "snack"

    def test_reserved_range(self):
        assert slot_range_name(64) == "reserved"
        assert slot_range_name(80) == "reserved"
        assert slot_range_name(95) == "reserved"

    def test_alias_range(self):
        assert slot_range_name(96) == "alias"
        assert slot_range_name(110) == "alias"
        assert slot_range_name(127) == "alias"

    def test_out_of_range(self):
        assert slot_range_name(200) == "unknown"
        assert slot_range_name(-1) == "unknown"


class TestANSICharSet:
    """128-character ANSI set tests."""

    def test_all_128_slots_have_chars(self):
        for slot in range(SLOT_TOTAL):
            ch = ansi_char(slot)
            assert len(ch) == 1, f"Slot {slot} has empty char"

    def test_command_slot_chars(self):
        assert ansi_char(0) == "@"
        assert ansi_char(1) == "#"
        assert ansi_char(7) == "!"

    def test_snack_slot_letters(self):
        assert ansi_char(32) == "A"
        assert ansi_char(57) == "Z"
        assert ansi_char(58) == "0"

    def test_reserved_lowercase(self):
        assert ansi_char(64) == "a"
        assert ansi_char(89) == "z"

    def test_alias_extended(self):
        assert ansi_char(96) == "¡"
        assert ansi_char(127) == "÷"


class TestSlotEntry:
    """Individual slot entry tests."""

    def test_default_ansi_from_set(self):
        entry = SlotEntry(slot=0)
        assert entry.ansi_char == "@"

    def test_custom_ansi_override(self):
        entry = SlotEntry(slot=5, ansi_char="X")
        assert entry.ansi_char == "X"

    def test_range_name(self):
        entry = SlotEntry(slot=32)
        assert entry.range_name == "snack"

    def test_render_emoji_priority(self):
        entry = SlotEntry(slot=0, emoji="💾", word_alias="vault", ansi_char="@")
        assert entry.render("emoji") == "💾"

    def test_render_word_priority(self):
        entry = SlotEntry(slot=0, emoji="💾", word_alias="vault", ansi_char="@")
        assert entry.render("word") == "vault"

    def test_render_teletext_priority(self):
        entry = SlotEntry(slot=0, emoji="💾", word_alias="vault", ansi_char="@")
        assert entry.render("teletext") == "@"

    def test_render_ansi_priority(self):
        entry = SlotEntry(slot=0, emoji="💾", word_alias="vault", ansi_char="@")
        assert entry.render("ansi") == "@"

    def test_render_fallback_no_emoji(self):
        entry = SlotEntry(slot=0, word_alias="vault", ansi_char="@")
        assert entry.render("emoji") == "vault"  # Falls back to word

    def test_render_fallback_no_word(self):
        entry = SlotEntry(slot=0, ansi_char="@")
        assert entry.render("emoji") == "@"  # Falls back to ANSI

    def test_to_dict(self):
        entry = SlotEntry(slot=5, term_id="test", label="Test", emoji="🎯")
        d = entry.to_dict()
        assert d["slot"] == 5
        assert d["term_id"] == "test"
        assert d["range"] == "command"
        assert d["emoji"] == "🎯"


class TestCharacterSystem:
    """CharacterSystem integration tests."""

    def setup_method(self):
        self.cs = CharacterSystem()

    def test_defaults_loaded(self):
        entries = self.cs.list_slots()
        assert len(entries) >= 12

    def test_get_by_slot(self):
        entry = self.cs.get(0)
        assert entry is not None
        assert entry.term_id == "vault"

    def test_get_unassigned_slot(self):
        entry = self.cs.get(99)
        assert entry is None

    def test_get_by_term(self):
        entry = self.cs.get_by_term("snack")
        assert entry is not None
        assert entry.slot == 32

    def test_get_by_term_missing(self):
        assert self.cs.get_by_term("bogus") is None

    def test_assign_new_slot(self):
        entry = SlotEntry(slot=10, term_id="custom", label="Custom")
        self.cs.assign(entry)
        assert self.cs.get(10) is not None
        assert self.cs.get_by_term("custom").slot == 10

    def test_assign_alias(self):
        self.cs.assign_alias(32, "spell")
        assert self.cs.get(32).word_alias == "spell"

    def test_assign_emoji(self):
        self.cs.assign_emoji(0, "🆕")
        assert self.cs.get(0).emoji == "🆕"

    def test_render_line(self):
        rendered = self.cs.render_line([0, 1, 2], priority="emoji")
        assert "💾" in rendered
        assert "📝" in rendered or "🏷" in rendered

    def test_render_line_fallback(self):
        rendered = self.cs.render_line([0, 1, 2], priority="ansi")
        # Slot 0=@, 1=#, 2=$ (but SlotEntry 2 overrides with emoji)
        assert len(rendered) == 3

    def test_render_grid(self):
        grid = self.cs.render_grid([[0, 1], [32, 33]], priority="emoji")
        lines = grid.split("\n")
        assert len(lines) == 2

    def test_list_slots_by_range(self):
        cmds = self.cs.list_slots(range_name="command")
        assert all(e.range_name == "command" for e in cmds)

    def test_list_slots_sorted(self):
        entries = self.cs.list_slots()
        slots = [e.slot for e in entries]
        assert slots == sorted(slots)

    def test_unassigned_slots(self):
        unassigned = self.cs.unassigned_slots()
        assert len(unassigned) == SLOT_TOTAL - len(self.cs.list_slots())

    def test_to_dict(self):
        d = self.cs.to_dict()
        assert d["total"] == SLOT_TOTAL
        assert d["assigned"] >= 12
        assert d["unassigned"] > 0
