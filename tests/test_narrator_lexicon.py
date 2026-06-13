"""Integration tests for Narrator story generation and Lexicon term mapping."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

try:
    from narrator.lexicon import LANE_DEV, LANE_STORY, LANE_STUDENT, Lexicon, LexiconEntry
    from narrator.narrator import NarratorEngine
    HAS_NARRATOR = True
except ImportError:
    HAS_NARRATOR = False

pytestmark = pytest.mark.skipif(
    not HAS_NARRATOR,
    reason="narrator module not available (requires core_py.narrator)"
)


class TestLexicon:
    """Lexicon term mapping tests."""

    def setup_method(self):
        if not HAS_NARRATOR:
            return
        self.lex = Lexicon()

    def test_core_terms_loaded(self):
        """Core terms should be loaded on initialization."""
        if not HAS_NARRATOR:
            return
        assert len(self.lex.terms) > 0
        assert "hello" in self.lex.terms

    def test_lane_constants(self):
        """Lane constants should be defined."""
        if not HAS_NARRATOR:
            return
        assert LANE_DEV == "dev"
        assert LANE_STORY == "story"
        assert LANE_STUDENT == "student"

    def test_lexicon_entry_creation(self):
        """LexiconEntry should be creatable."""
        if not HAS_NARRATOR:
            return
        entry = LexiconEntry(
            term="test",
            definition="A test entry",
            lane=LANE_DEV,
            aliases=["tst", "demo"]
        )
        assert entry.term == "test"
        assert entry.lane == LANE_DEV

    def test_term_lookup(self):
        """Lexicon should support term lookup."""
        if not HAS_NARRATOR:
            return
        result = self.lex.lookup("hello")
        assert result is not None

    def test_term_mapping(self):
        """Lexicon should map terms to definitions."""
        if not HAS_NARRATOR:
            return
        mapping = self.lex.get_mapping("hello")
        assert mapping is not None


class TestNarratorEngine:
    """Narrator engine tests."""

    def setup_method(self):
        if not HAS_NARRATOR:
            return
        self.engine = NarratorEngine()

    def test_engine_initialization(self):
        """NarratorEngine should initialize."""
        if not HAS_NARRATOR:
            return
        assert self.engine is not None

    def test_story_generation(self):
        """Engine should generate stories from prompts."""
        if not HAS_NARRATOR:
            return
        story = self.engine.generate("A brave knight")
        assert story is not None
        assert len(story) > 0
