"""Integration tests for Narrator story generation and Lexicon term mapping."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from narrator.lexicon import LANE_DEV, LANE_STORY, LANE_STUDENT, Lexicon, LexiconEntry
from narrator.narrator import NarratorEngine


class TestLexicon:
    """Lexicon term mapping tests."""

    def setup_method(self):
        self.lex = Lexicon()

    def test_core_terms_loaded(self):
        """All 12 core lexicon terms are loaded by default."""
        assert len(self.lex) >= 12, f"Expected >=12 terms, got {len(self.lex)}"

    def test_get_term(self):
        """Lexicon.get returns correct entry."""
        entry = self.lex.get("vault")
        assert entry is not None
        assert entry.term_id == "vault"
        assert entry.emoji == "💾"

    def test_get_missing_term(self):
        assert self.lex.get("nonexistent") is None

    def test_translate_dev(self):
        assert self.lex.translate("vault", LANE_DEV) == "Vault"

    def test_translate_story(self):
        assert "Dungeon" in self.lex.translate("vault", LANE_STORY)

    def test_translate_student(self):
        assert "notebook" in self.lex.translate("vault", LANE_STUDENT).lower()

    def test_translate_missing_term(self):
        assert self.lex.translate("bogus", LANE_DEV) == "bogus"

    def test_add_custom_term(self):
        entry = LexiconEntry(
            term_id="custom",
            dev="Custom",
            story="Legendary Artifact",
            student="Custom thing",
            emoji="🌟",
            description="A test custom term",
        )
        self.lex.add(entry)
        assert self.lex.get("custom") is not None
        assert self.lex.translate("custom", LANE_STORY) == "Legendary Artifact"

    def test_remove_term(self):
        self.lex.remove("spatial")
        assert self.lex.get("spatial") is None

    def test_search_by_term_id(self):
        results = self.lex.search("vault")
        assert any(r.term_id == "vault" for r in results)

    def test_search_by_lane(self):
        results = self.lex.search("oracle", lane=LANE_STORY)
        assert len(results) > 0

    def test_list_terms(self):
        terms = self.lex.list_terms()
        assert len(terms) >= 12

    def test_list_terms_by_tag(self):
        terms = self.lex.list_terms(tag="core")
        assert len(terms) >= 10  # Most terms have tag "core"

    def test_list_terms_by_lane(self):
        terms = self.lex.list_terms(lane=LANE_STORY)
        # All terms should be returned (lane filters only in search, list returns all)
        assert len(terms) >= 12

    def test_to_dict(self):
        d = self.lex.to_dict()
        assert "vault" in d
        assert d["vault"]["term_id"] == "vault"

    def test_roundtrip_from_dict(self):
        d = self.lex.to_dict()
        lex2 = Lexicon.from_dict(d)
        assert lex2.get("vault") is not None
        assert lex2.translate("vault", LANE_DEV) == "Vault"


class TestNarrator:
    """Narrator story generation tests."""

    def setup_method(self):
        self.narrator = NarratorEngine()

    def test_vault_init_story(self):
        story = self.narrator.vault_init("/test/path")
        assert "Dungeon of Knowledge" in story or "awakens" in story
        assert len(story) > 20

    def test_note_create_story(self):
        story = self.narrator.note_create("Test Note")
        assert "Test Note" in story
        assert len(story) > 20

    def test_note_create_with_tags(self):
        story = self.narrator.note_create("Tagged Note", tags=["core", "test"])
        assert "Tagged Note" in story

    def test_snack_completed(self):
        story = self.narrator.snack_run("test-snack", status="completed")
        assert "test-snack" in story
        assert "completes" in story or "complet" in story

    def test_snack_failed(self):
        story = self.narrator.snack_run("fail-snack", status="failed")
        assert "fail-snack" in story
        assert "fizzles" in story or "fail" in story.lower()

    def test_task_create(self):
        story = self.narrator.task_create("Write docs")
        assert "Write docs" in story
        assert "quest" in story.lower() or "task" in story.lower()

    def test_ok_response(self):
        story = self.narrator.ok_response("What is the vault?")
        assert "What is the vault?" in story or "vault" in story

    def test_generate_story_vault_init(self):
        story = self.narrator.generate_story("vault_init", title="/vault")
        assert story["type"] == "story"
        assert story["event"] == "vault_init"
        assert len(story["content"]) > 20

    def test_generate_story_note_create(self):
        story = self.narrator.generate_story("note_create", title="Meeting")
        assert story["event"] == "note_create"
        assert "Meeting" in story["content"]

    def test_generate_story_unknown_event(self):
        story = self.narrator.generate_story("unknown_event")
        assert "unknown" in story["content"].lower()

    def test_story_to_markdown(self):
        story = self.narrator.generate_story("vault_init", title="/vault")
        md = self.narrator.story_to_markdown(story)
        assert md.startswith("##")
        assert "Dungeon of Knowledge" in md or "The" in md

    def test_story_to_ceefax(self):
        story = self.narrator.generate_story("note_create", title="Hi")
        cf = self.narrator.story_to_ceefax(story)
        assert cf.startswith("┌")
        assert cf.endswith("┘\n")

    def test_feed_line_processing(self):
        line = json.dumps({"type": "note_create", "detail": "test"})
        story = self.narrator.process_feed_line(line)
        assert story is not None
        assert story["event"] == "note_create"  # Keeps original event type
        assert len(story["content"]) > 0

    def test_process_feed_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps({"type": "note_create", "title": "F1", "detail": ""}) + "\n")
            f.write(json.dumps({"type": "snack_run", "title": "s1", "status": "completed", "detail": ""}) + "\n")
            fpath = f.name
        try:
            stories = self.narrator.process_feed_file(fpath)
            assert len(stories) >= 2
        finally:
            os.unlink(fpath)

    def test_empty_feed_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            fpath = f.name
        try:
            stories = self.narrator.process_feed_file(fpath)
            assert len(stories) == 0
        finally:
            os.unlink(fpath)
