"""
Ceefax Spool — Save/Load teletext page collections

Spool files store collections of teletext pages for import/export.
Each spool is a JSON file containing multiple pages with their
grid data, metadata, and timestamps.

Usage:
    spool = CeefaxSpool()
    spool.save_page(page_number, grid, title="News")
    spool.export("my_spool.json")
    spool.import_file("my_spool.json")
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict

from .bridge import TeletextGrid, TeletextCell, TeletextColour


@dataclass
class SpoolPageEntry:
    """A single page entry in a spool file"""
    page_number: int
    title: str = ""
    subtitle: str = ""
    timestamp: float = 0.0
    source: str = "manual"
    cells: List[List[Dict[str, Any]]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SpoolManifest:
    """Spool file manifest/metadata"""
    version: str = "1.0"
    created: float = 0.0
    updated: float = 0.0
    page_count: int = 0
    description: str = ""
    tags: List[str] = field(default_factory=list)
    source: str = "ceefax"


@dataclass
class CeefaxSpoolFile:
    """Complete spool file containing multiple teletext pages"""
    manifest: SpoolManifest = field(default_factory=SpoolManifest)
    pages: List[SpoolPageEntry] = field(default_factory=list)


class CeefaxSpool:
    """
    Manages teletext page spool files for import/export.

    Features:
        - Save individual pages to spool
        - Export entire spool to JSON file
        - Import spool from JSON file
        - List pages in spool
        - Convert between TeletextGrid and spool format
        - Merge multiple spools
    """

    def __init__(self, spool_dir: Optional[str] = None):
        """
        Initialize the spool manager.

        Args:
            spool_dir: Directory for spool files (default: ~/.udos/spools/)
        """
        self._spool_dir = spool_dir or os.path.expanduser("~/.udos/spools")
        self._current: CeefaxSpoolFile = CeefaxSpoolFile(
            manifest=SpoolManifest(created=time.time(), updated=time.time())
        )
        os.makedirs(self._spool_dir, exist_ok=True)

    # ── Page Management ────────────────────────────────────────────

    def save_page(self, page_number: int, grid: TeletextGrid,
                  title: str = "", subtitle: str = "",
                  metadata: Optional[Dict[str, Any]] = None) -> SpoolPageEntry:
        """
        Save a teletext grid as a page entry in the current spool.

        Args:
            page_number: Teletext page number
            grid: TeletextGrid to save
            title: Page title
            subtitle: Page subtitle
            metadata: Optional additional metadata

        Returns:
            The created SpoolPageEntry
        """
        cells = []
        for row in range(TeletextGrid.ROWS):
            row_data = []
            for col in range(TeletextGrid.COLS):
                cell = grid.cells[row][col]
                row_data.append({
                    "char": cell.char,
                    "fg": cell.foreground.value,
                    "bg": cell.background.value,
                    "bold": cell.bold,
                    "flash": cell.flash,
                })
            cells.append(row_data)

        entry = SpoolPageEntry(
            page_number=page_number,
            title=title,
            subtitle=subtitle,
            timestamp=time.time(),
            source="manual",
            cells=cells,
            metadata=metadata or {},
        )

        # Replace or append
        for i, existing in enumerate(self._current.pages):
            if existing.page_number == page_number:
                self._current.pages[i] = entry
                break
        else:
            self._current.pages.append(entry)

        self._current.manifest.page_count = len(self._current.pages)
        self._current.manifest.updated = time.time()
        return entry

    def remove_page(self, page_number: int) -> bool:
        """Remove a page from the current spool"""
        for i, entry in enumerate(self._current.pages):
            if entry.page_number == page_number:
                self._current.pages.pop(i)
                self._current.manifest.page_count = len(self._current.pages)
                self._current.manifest.updated = time.time()
                return True
        return False

    def get_page(self, page_number: int) -> Optional[SpoolPageEntry]:
        """Get a page entry by page number"""
        for entry in self._current.pages:
            if entry.page_number == page_number:
                return entry
        return None

    def list_pages(self) -> List[Dict[str, Any]]:
        """List all pages in the current spool"""
        return [
            {
                "page_number": p.page_number,
                "title": p.title,
                "subtitle": p.subtitle,
                "timestamp": p.timestamp,
                "source": p.source,
                "metadata": p.metadata,
            }
            for p in self._current.pages
        ]

    def clear(self) -> None:
        """Clear all pages from the current spool"""
        self._current.pages.clear()
        self._current.manifest.page_count = 0
        self._current.manifest.updated = time.time()

    # ── Grid Conversion ────────────────────────────────────────────

    def to_grid(self, entry: SpoolPageEntry) -> TeletextGrid:
        """
        Convert a spool page entry back to a TeletextGrid.

        Args:
            entry: SpoolPageEntry to convert

        Returns:
            TeletextGrid
        """
        grid = TeletextGrid()
        for row_idx, row_data in enumerate(entry.cells):
            if row_idx >= TeletextGrid.ROWS:
                break
            for col_idx, cell_data in enumerate(row_data):
                if col_idx >= TeletextGrid.COLS:
                    break
                grid.cells[row_idx][col_idx] = TeletextCell(
                    char=cell_data.get("char", " "),
                    foreground=TeletextColour(cell_data.get("fg", 7)),
                    background=TeletextColour(cell_data.get("bg", 0)),
                    bold=cell_data.get("bold", False),
                    flash=cell_data.get("flash", False),
                )
        return grid

    # ── Export / Import ────────────────────────────────────────────

    def export(self, filename: str) -> str:
        """
        Export the current spool to a JSON file.

        Args:
            filename: Output filename (without extension)

        Returns:
            Path to the exported file
        """
        if not filename.endswith(".spool"):
            filename += ".spool"

        filepath = os.path.join(self._spool_dir, filename)

        # Build export data
        data = {
            "manifest": asdict(self._current.manifest),
            "pages": [
                {
                    "page_number": p.page_number,
                    "title": p.title,
                    "subtitle": p.subtitle,
                    "timestamp": p.timestamp,
                    "source": p.source,
                    "cells": p.cells,
                    "metadata": p.metadata,
                }
                for p in self._current.pages
            ],
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        return filepath

    def import_file(self, filepath: str) -> int:
        """
        Import pages from a spool JSON file.

        Args:
            filepath: Path to spool file

        Returns:
            Number of pages imported

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a valid spool
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Spool file not found: {filepath}")

        with open(filepath, 'r') as f:
            data = json.load(f)

        if "manifest" not in data or "pages" not in data:
            raise ValueError(f"Invalid spool file: {filepath}")

        imported = 0
        for page_data in data["pages"]:
            entry = SpoolPageEntry(
                page_number=page_data.get("page_number", 0),
                title=page_data.get("title", ""),
                subtitle=page_data.get("subtitle", ""),
                timestamp=page_data.get("timestamp", time.time()),
                source=page_data.get("source", "imported"),
                cells=page_data.get("cells", []),
                metadata=page_data.get("metadata", {}),
            )

            # Replace or append
            for i, existing in enumerate(self._current.pages):
                if existing.page_number == entry.page_number:
                    self._current.pages[i] = entry
                    break
            else:
                self._current.pages.append(entry)

            imported += 1

        self._current.manifest.page_count = len(self._current.pages)
        self._current.manifest.updated = time.time()
        return imported

    def merge(self, other: 'CeefaxSpool') -> int:
        """
        Merge pages from another spool into this one.

        Args:
            other: Another CeefaxSpool instance

        Returns:
            Number of pages merged
        """
        merged = 0
        for entry in other._current.pages:
            # Only add if page number doesn't exist
            exists = any(
                p.page_number == entry.page_number
                for p in self._current.pages
            )
            if not exists:
                self._current.pages.append(entry)
                merged += 1

        self._current.manifest.page_count = len(self._current.pages)
        self._current.manifest.updated = time.time()
        return merged

    # ── File Management ────────────────────────────────────────────

    def list_spool_files(self) -> List[Dict[str, Any]]:
        """List all spool files in the spool directory"""
        files = []
        spool_dir = Path(self._spool_dir)
        for f in sorted(spool_dir.glob("*.spool")):
            try:
                with open(f, 'r') as fh:
                    data = json.load(fh)
                manifest = data.get("manifest", {})
                files.append({
                    "filename": f.stem,
                    "path": str(f),
                    "page_count": manifest.get("page_count", 0),
                    "created": manifest.get("created", 0),
                    "updated": manifest.get("updated", 0),
                    "description": manifest.get("description", ""),
                    "size": f.stat().st_size,
                })
            except Exception:
                files.append({
                    "filename": f.stem,
                    "path": str(f),
                    "error": "invalid spool",
                })
        return files

    def delete_spool_file(self, filename: str) -> bool:
        """Delete a spool file"""
        if not filename.endswith(".spool"):
            filename += ".spool"
        filepath = os.path.join(self._spool_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
        return False

    # ── Properties ─────────────────────────────────────────────────

    @property
    def page_count(self) -> int:
        """Number of pages in the current spool"""
        return len(self._current.pages)

    @property
    def spool_dir(self) -> str:
        """Spool directory path"""
        return self._spool_dir

    @property
    def manifest(self) -> SpoolManifest:
        """Current spool manifest"""
        return self._current.manifest


# Convenience function
def create_ceefax_spool(spool_dir: Optional[str] = None) -> CeefaxSpool:
    """Create and return a CeefaxSpool"""
    return CeefaxSpool(spool_dir)
