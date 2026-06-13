"""
SpatialCodec — Encode/decode spatial data
==========================================
Serialization and deserialization of grid spatial data
for storage, transmission, and interop with uConnect.
"""

import json
import base64
from typing import List, Dict, Any, Optional
from .grid_cell import GridCell


class SpatialCodec:
    """Encode/decode spatial grid data."""

    @staticmethod
    def encode_cells(cells: List[GridCell]) -> str:
        """Encode a list of GridCells to a JSON string."""
        return json.dumps([c.to_dict() for c in cells])

    @staticmethod
    def decode_cells(data: str) -> List[GridCell]:
        """Decode a JSON string to a list of GridCells."""
        raw = json.loads(data)
        return [GridCell.from_dict(item) for item in raw]

    @staticmethod
    def encode_grid(grid: Dict[tuple, GridCell]) -> str:
        """Encode a grid (dict of position -> cell) to JSON."""
        cells = []
        for pos, cell in grid.items():
            d = cell.to_dict()
            d['x'], d['y'], d['z'] = pos
            cells.append(d)
        return json.dumps(cells)

    @staticmethod
    def decode_grid(data: str) -> Dict[tuple, GridCell]:
        """Decode JSON to a grid dict."""
        raw = json.loads(data)
        grid = {}
        for item in raw:
            cell = GridCell.from_dict(item)
            grid[(cell.x, cell.y, cell.z)] = cell
        return grid

    @staticmethod
    def encode_compact(cells: List[GridCell]) -> str:
        """Encode cells in a compact binary-like format (base64)."""
        # Simple compact format: x,y,z,char,fg,bg for each cell
        parts = []
        for c in cells:
            parts.append(f"{c.x},{c.y},{c.z},{ord(c.char)},{c.fg},{c.bg}")
        return base64.b64encode('|'.join(parts).encode()).decode()

    @staticmethod
    def decode_compact(data: str) -> List[GridCell]:
        """Decode compact format back to cells."""
        decoded = base64.b64decode(data).decode()
        cells = []
        for part in decoded.split('|'):
            if not part.strip():
                continue
            x, y, z, char_code, fg, bg = part.split(',')
            cells.append(GridCell(
                x=int(x), y=int(y), z=int(z),
                char=chr(int(char_code)),
                fg=int(fg), bg=int(bg),
            ))
        return cells
