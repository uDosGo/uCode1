"""Integration tests for Feed event archiving to Cells."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core_py.feed import (
    archive_feed_file,
    archive_feed_entries,
    search_feed_cells,
    generate_feed_report,
    FEED_BAND,
)
from core_py.cell import CellStore


class TestFeedArchiver:
    """Feed event archiving tests."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp(prefix="udox_feed_test_")
        self.store = CellStore(root_dir=os.path.join(self.tmpdir, "cells"))

    def teardown_method(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _make_feed_file(self, entries: list) -> str:
        path = os.path.join(self.tmpdir, "feed.jsonl")
        with open(path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        return path

    def test_archive_empty_file(self):
        path = self._make_feed_file([])
        count, addresses = archive_feed_file(path, self.store)
        assert count == 0
        assert len(addresses) == 0

    def test_archive_single_entry(self):
        path = self._make_feed_file([{"type": "test", "detail": "hello"}])
        count, addresses = archive_feed_file(path, self.store)
        assert count == 1
        assert len(addresses) == 1

    def test_archive_multiple_entries(self):
        entries = [
            {"type": "a", "detail": "1", "timestamp": "2026-01-01T00:00:00"},
            {"type": "b", "detail": "2", "timestamp": "2026-01-01T00:01:00"},
            {"type": "a", "detail": "3", "timestamp": "2026-01-01T00:02:00"},
        ]
        path = self._make_feed_file(entries)
        count, addresses = archive_feed_file(path, self.store)
        assert count == 3
        assert len(addresses) == 3

    def test_archive_from_list(self):
        entries = [
            {"type": "note_create", "title": "Test", "timestamp": "2026-01-01T00:00:00"},
            {"type": "snack_run", "title": "s1", "status": "done", "timestamp": "2026-01-01T00:01:00"},
        ]
        count, addresses = archive_feed_entries(entries, self.store)
        assert count == 2

    def test_skip_empty_lines(self):
        path = os.path.join(self.tmpdir, "feed.jsonl")
        with open(path, "w") as f:
            f.write('{"type":"a"}\n\n{"type":"b"}\n')
        count, addresses = archive_feed_file(path, self.store)
        assert count == 2

    def test_skip_invalid_json(self):
        path = os.path.join(self.tmpdir, "feed.jsonl")
        with open(path, "w") as f:
            f.write('{"type": "good"}\n')
            f.write('{invalid json here}\n')  # This line fails JSON parsing
            f.write('{"type": "good2"}\n')
        count, addresses = archive_feed_file(path, self.store)
        assert count == 2  # Only valid JSON lines counted

    def test_search_all(self):
        entries = [
            {"type": "a", "detail": "x", "timestamp": "2026-01-01T00:00:00"},
            {"type": "b", "detail": "y", "timestamp": "2026-01-01T00:01:00"},
        ]
        archive_feed_entries(entries, self.store)
        results = search_feed_cells(self.store)
        assert len(results) == 2

    def test_search_by_type(self):
        entries = [
            {"type": "note", "detail": "x", "timestamp": "2026-01-01T00:00:00"},
            {"type": "snack", "detail": "y", "timestamp": "2026-01-01T00:01:00"},
            {"type": "note", "detail": "z", "timestamp": "2026-01-01T00:02:00"},
        ]
        archive_feed_entries(entries, self.store)
        results = search_feed_cells(self.store, event_type="note")
        assert len(results) == 2

    def test_search_sorted_by_timestamp(self):
        entries = [
            {"type": "a", "detail": "first", "timestamp": "2026-01-01T00:00:00"},
            {"type": "a", "detail": "second", "timestamp": "2026-01-01T00:02:00"},
            {"type": "a", "detail": "third", "timestamp": "2026-01-01T00:01:00"},
        ]
        archive_feed_entries(entries, self.store)
        results = search_feed_cells(self.store)
        # Should be sorted by timestamp descending
        assert results[0]["detail"] == "second"  # 00:02:00 latest
        assert results[1]["detail"] == "third"   # 00:01:00
        assert results[2]["detail"] == "first"   # 00:00:00 earliest

    def test_report_empty(self):
        report = generate_feed_report(self.store)
        assert report["total_cells"] == 0
        assert report["event_types"] == {}

    def test_report_with_data(self):
        entries = [
            {"type": "note", "detail": "x", "timestamp": "2026-01-01T00:00:00"},
            {"type": "snack", "detail": "y", "timestamp": "2026-01-01T00:01:00"},
            {"type": "note", "detail": "z", "timestamp": "2026-01-01T00:02:00"},
        ]
        archive_feed_entries(entries, self.store)
        report = generate_feed_report(self.store)
        assert report["total_cells"] == 3
        assert report["event_types"]["note"] == 2
        assert report["event_types"]["snack"] == 1
        assert report["earliest"] == "2026-01-01T00:00:00"
        assert report["latest"] == "2026-01-01T00:02:00"
        assert report["verified"] is True

    def test_cells_verify_integrity(self):
        entries = [{"type": "test", "detail": "data", "timestamp": "2026-01-01T00:00:00"}]
        archive_feed_entries(entries, self.store)
        cells = self.store.list_cells(band=FEED_BAND)
        for addr in cells:
            cell = self.store.read(str(addr))
            assert cell is not None
            assert cell.verify() is True
