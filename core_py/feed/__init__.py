#!/usr/bin/env python3
"""
Feed Archiver — Converts feed events into Cells for archival storage.

Feed events are JSONL entries (one JSON object per line) representing
activity in the uDos system. This module archives them as Cells in
.state/cells/ with the 'feed' layer type, enabling time-based queries,
search, and bulk export.

Layer band mapping:
  L300 → Feed events (band 300, layer=LAYER_FEED)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..cell import (
    LAYER_FEED,
    Cell,
    CellAddress,
    CellStore,
)

FEED_BAND = 300       # Layer band dedicated to feed events
FEED_CELL_EXT = ".cell.json"


def _make_feed_cell(
    entry: Dict[str, Any],
    index: int,
    store: CellStore,
    band: int = FEED_BAND,
) -> Cell:
    """Convert a single feed entry into a Cell and write it to the store.

    The cell address is derived deterministically from the event type,
    timestamp, and index for unique yet queryable addresses.

    Args:
        entry: Feed entry dict (must have at least 'type' key).
        index: Sequential index within the feed batch.
        store: CellStore to write to.
        band: Layer band.

    Returns:
        The created Cell.
    """
    if not isinstance(entry, dict):
        # Skip non-dict entries (e.g. invalid JSON lines parsed as strings)
        entry = {"type": "invalid", "detail": str(entry)}
    event_type = entry.get("type", "unknown")
    timestamp = entry.get("timestamp", entry.get("time", datetime.now().isoformat()))
    detail = entry.get("detail", entry.get("content", entry.get("title", "")))

    # Deterministic address components
    col = (hash(event_type) & 0x7FFFFFFF) % 26
    row = index % 26
    sub = (hash(timestamp) & 0x7FFFFFFF) % 100
    slot = index % 128
    version = 0

    addr = CellAddress(
        band=band,
        col=col,
        row=row,
        sub=sub,
        layer=LAYER_FEED,
        slot=slot,
        version=version,
    )

    data = {
        "event_type": event_type,
        "timestamp": timestamp,
        "detail": detail,
        "index": index,
        "_raw": entry,
    }

    cell = Cell(address=addr, data=data)
    store.write(cell)
    return cell


def archive_feed_file(
    path: str,
    store: Optional[CellStore] = None,
    band: int = FEED_BAND,
) -> Tuple[int, List[str]]:
    """Archive all entries from a JSONL feed file as Cells.

    Args:
        path: Path to JSONL feed file (one JSON object per line).
        store: CellStore instance (creates default if omitted).
        band: Layer band.

    Returns:
        Tuple of (entry_count, cell_addresses).
    """
    store = store or CellStore()
    count = 0
    addresses = []

    if not os.path.isfile(path):
        raise FileNotFoundError(f"Feed file not found: {path}")

    with open(path) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            cell = _make_feed_cell(entry, i, store, band)
            count += 1
            addresses.append(str(cell.address))

    return count, addresses


def archive_feed_entries(
    entries: List[Dict[str, Any]],
    store: Optional[CellStore] = None,
    band: int = FEED_BAND,
) -> Tuple[int, List[str]]:
    """Archive a list of feed entries as Cells.

    Args:
        entries: List of feed entry dicts.
        store: CellStore instance.
        band: Layer band.

    Returns:
        Tuple of (entry_count, cell_addresses).
    """
    store = store or CellStore()
    addresses = []

    for i, entry in enumerate(entries):
        cell = _make_feed_cell(entry, i, store, band)
        addresses.append(str(cell.address))

    return len(addresses), addresses


def search_feed_cells(
    store: Optional[CellStore] = None,
    band: int = FEED_BAND,
    event_type: Optional[str] = None,
    limit: int = 100,
) -> List[Dict[str, Any]]:
    """Search archived feed cells, optionally filtered by event type.

    Args:
        store: CellStore instance.
        band: Layer band.
        event_type: Optional event type filter.
        limit: Maximum results.

    Returns:
        List of cell data dicts sorted by timestamp.
    """
    store = store or CellStore()
    results = []

    for addr in store.list_cells(band=band):
        cell = store.read(str(addr))
        if not cell:
            continue
        data = cell.data
        if event_type and data.get("event_type") != event_type:
            continue
        results.append({
            "address": str(addr),
            "event_type": data.get("event_type", "?"),
            "timestamp": data.get("timestamp", ""),
            "detail": data.get("detail", ""),
            "checksum": cell.checksum,
            "verified": cell.verify(),
        })

    # Sort by timestamp
    results.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
    return results[:limit]


def generate_feed_report(
    store: Optional[CellStore] = None,
    band: int = FEED_BAND,
) -> Dict[str, Any]:
    """Generate a summary report of archived feed cells.

    Args:
        store: CellStore instance.
        band: Layer band.

    Returns:
        Dict with report stats.
    """
    store = store or CellStore()
    cells = store.list_cells(band=band)
    total = len(cells)

    # Count by event type
    type_counts: Dict[str, int] = {}
    for addr in cells:
        cell = store.read(str(addr))
        if cell:
            et = cell.data.get("event_type", "unknown")
            type_counts[et] = type_counts.get(et, 0) + 1

    # Time range
    timestamps = []
    for addr in cells:
        cell = store.read(str(addr))
        if cell:
            ts = cell.data.get("timestamp", "")
            if ts:
                timestamps.append(ts)

    return {
        "total_cells": total,
        "band": band,
        "event_types": type_counts,
        "earliest": min(timestamps) if timestamps else None,
        "latest": max(timestamps) if timestamps else None,
        "verified": all(
            store.read(str(addr)).verify()
            for addr in cells[:10]  # Check first 10
        ),
    }
