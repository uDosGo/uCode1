#!/usr/bin/env python3
"""
Cell System — Atomic storage units with UDX addressing.

Cells are 24×24 pixel atomic storage units referenced by a
UDX-style address: L<band>-<x><y>-<layer><slot>-<version>

Address format:  L100-BB45-1010-2
  L<band>        Layer band (100, 200, ... 899)
  <x><y>         Grid coordinate (BB45 = column B, row 45)
  <layer><slot>  Layer type + slot number
  <version>      Cell version/revision
"""

import hashlib
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── Constants ───────────────────────────────────────────────────────────────

CELL_DIR = ".state/cells"
CELL_EXT = ".cell.json"
CELL_ADDRESS_RE = re.compile(
    r"^L(\d{3})-([A-Z])([A-Z])(\d{2})-(\d)(\d{3})-(\d)$"
)

# Layer types
LAYER_GRID = 0     # Grid data
LAYER_SPATIAL = 1  # Spatial index
LAYER_SNACK = 2    # Snack execution
LAYER_FEED = 3     # Feed/event log
LAYER_META = 4     # Metadata
LAYER_CHAR = 5     # Character slot
LAYER_BINDER = 6   # Binder snapshot
LAYER_USXD = 7     # USXD document
LAYER_CUBE = 8     # Cube (SnackBox packaging)
LAYER_USER = 9     # User-defined


def layer_name(layer: int) -> str:
    return {
        LAYER_GRID: "grid",
        LAYER_SPATIAL: "spatial",
        LAYER_SNACK: "snack",
        LAYER_FEED: "feed",
        LAYER_META: "meta",
        LAYER_CHAR: "char",
        LAYER_BINDER: "binder",
        LAYER_USXD: "usxd",
        LAYER_CUBE: "cube",
        LAYER_USER: "user",
    }.get(layer, "unknown")


# ── Cell Address ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class CellAddress:
    """A UDX-style cell address: L<band>-<col><row><sub>-<layer><slot>-<version>

    Example: L100-BB01-1001-0
      band=100, col=B(1), row=B(1), sub=01, layer=1, slot=001, ver=0
    """
    band: int          # Layer band (100-899)
    col: int           # Column letter (0-25, A=0)
    row: int           # Row letter (0-25, A=0)
    sub: int           # Sub-position (0-99)
    layer: int         # Layer type (0-9)
    slot: int          # Slot number (0-127)
    version: int       # Version/revision

    @property
    def x(self) -> int:
        """Alias for col."""
        return self.col

    @property
    def y(self) -> int:
        """Alias for row."""
        return self.row

    @classmethod
    def parse(cls, address: str) -> Optional["CellAddress"]:
        """Parse a UDX address string into a CellAddress.

        Format: L<band>-<col><row><sub>-<layer><slot>-<version>
          col:  1 letter A-Z
          row:  1 letter A-Z
          sub:  2-digit sub-position (00-99)
          layer: 1 digit (0-9)
          slot:  3 digits (000-127)
          version: 1 digit (0-9)

        Example: L100-BB01-1001-0
          band=100, col=B, row=B, sub=01, layer=1, slot=001, ver=0
        """
        m = CELL_ADDRESS_RE.match(address.upper())
        if not m:
            return None
        return cls(
            band=int(m.group(1)),
            col=ord(m.group(2)) - ord("A"),
            row=ord(m.group(3)) - ord("A"),
            sub=int(m.group(4)),
            layer=int(m.group(5)),
            slot=int(m.group(6)),
            version=int(m.group(7)),
        )

    def __str__(self) -> str:
        col = chr(ord("A") + self.col)
        row = chr(ord("A") + self.row)
        return f"L{self.band:03d}-{col}{row}{self.sub:02d}-{self.layer}{self.slot:03d}-{self.version}"

    @property
    def path_segment(self) -> str:
        """Get filesystem path segment for this address."""
        return f"L{self.band:03d}/{self.layer}{self.slot:03d}"


# ── Cell Data ───────────────────────────────────────────────────────────────

@dataclass
class Cell:
    """A single cell — atomic storage unit."""
    address: CellAddress
    data: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""
    created: str = ""
    updated: str = ""

    def __post_init__(self):
        now = datetime.now().isoformat()
        if not self.created:
            self.created = now
        if not self.updated:
            self.updated = now
        if not self.checksum:
            self.checksum = self._calc_checksum()

    def _calc_checksum(self) -> str:
        content = str(self.address) + json.dumps(self.data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def verify(self) -> bool:
        return self.checksum == self._calc_checksum()

    def to_dict(self) -> dict:
        return {
            "address": str(self.address),
            "data": self.data,
            "checksum": self.checksum,
            "created": self.created,
            "updated": self.updated,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Cell":
        addr = CellAddress.parse(d["address"])
        if not addr:
            raise ValueError(f"Invalid cell address: {d['address']}")
        return cls(
            address=addr,
            data=d.get("data", {}),
            checksum=d.get("checksum", ""),
            created=d.get("created", ""),
            updated=d.get("updated", ""),
        )


# ── Cube (SnackBox packaging — groups of cells) ────────────────────────────

@dataclass
class Cube:
    """A Cube bundles multiple cells into a SnackBox package for transport."""
    id: str
    cells: List[Cell] = field(default_factory=list)
    created: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.created:
            self.created = datetime.now().isoformat()

    def add(self, cell: Cell):
        self.cells.append(cell)

    def remove(self, address: str):
        self.cells = [c for c in self.cells if str(c.address) != address]

    def get(self, address: str) -> Optional[Cell]:
        for c in self.cells:
            if str(c.address) == address:
                return c
        return None

    def size(self) -> int:
        return len(self.cells)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "cells": [c.to_dict() for c in self.cells],
            "created": self.created,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Cube":
        cells = [Cell.from_dict(c) for c in d.get("cells", [])]
        return cls(
            id=d["id"],
            cells=cells,
            created=d.get("created", ""),
            metadata=d.get("metadata", {}),
        )


# ── Cell Store (filesystem-backed registry) ────────────────────────────────

class CellStore:
    """Filesystem-backed cell storage. Uses .state/cells/ as root.

    Directory structure:
      .state/cells/
        L100/
          00000/
            L100-AA00-0000-0.cell.json
            L100-AA00-0000-1.cell.json
          10001/
            L100-BB01-1001-0.cell.json
        L200/
          ...
    """

    def __init__(self, root_dir: Optional[str] = None):
        self.root = Path(root_dir or CELL_DIR)
        self.root.mkdir(parents=True, exist_ok=True)

    def _cell_path(self, addr: CellAddress) -> Path:
        """Get filesystem path for a cell address."""
        return self.root / f"L{addr.band:03d}" / f"{addr.layer}{addr.slot:05d}" / f"{addr}.cell.json"

    def write(self, cell: Cell) -> None:
        """Write a cell to disk."""
        path = self._cell_path(cell.address)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(cell.to_dict(), f, indent=2)

    def read(self, address: str) -> Optional[Cell]:
        """Read a cell by address string."""
        addr = CellAddress.parse(address)
        if not addr:
            return None
        path = self._cell_path(addr)
        if not path.exists():
            return None
        with open(path) as f:
            return Cell.from_dict(json.load(f))

    def delete(self, address: str) -> bool:
        """Delete a cell by address. Returns True if deleted."""
        addr = CellAddress.parse(address)
        if not addr:
            return False
        path = self._cell_path(addr)
        if path.exists():
            path.unlink()
            return True
        return False

    def list_cells(self, band: Optional[int] = None) -> List[CellAddress]:
        """List all stored cell addresses, optionally filtered by band."""
        addresses = []
        scan_root = self.root / f"L{band:03d}" if band else self.root
        if not scan_root.exists():
            return addresses

        # Use rglob to find all .cell.json files (3 levels deep)
        for cell_file in scan_root.rglob("*.cell.json"):
            addr_str = cell_file.name.replace(".cell.json", "")
            addr = CellAddress.parse(addr_str)
            if addr:
                addresses.append(addr)
        return sorted(addresses, key=lambda a: (a.band, a.col, a.row, a.layer, a.slot))

    def count(self, band: Optional[int] = None) -> int:
        """Count cells, optionally filtered by band."""
        return len(self.list_cells(band))

    def purge_band(self, band: int) -> int:
        """Delete all cells in a layer band. Returns count deleted."""
        count = 0
        band_dir = self.root / f"L{band:03d}"
        if band_dir.exists():
            for f in band_dir.rglob("*.json"):
                f.unlink()
                count += 1
        return count
