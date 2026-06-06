"""Ceefax GridUI Surface — maps teletext pages onto uCode1 grid cells.

The uCode1 grid system renders content as a grid of cells, each with
a character, foreground colour, and background colour. This module
converts teletext pages (24 rows x 40 cols) into grid cell arrays.
"""

from typing import List, Dict, Any, Optional


class TeletextSurface:
    """Maps teletext pages onto the uCode1 grid cell system.

    The grid is 24 rows x 40 columns, matching the teletext standard.
    Each cell contains a character and colour information.
    """

    GRID_ROWS = 24
    GRID_COLS = 40

    def __init__(self):
        self.cells: List[List[Dict[str, Any]]] = [
            [{"char": " ", "fg": "green", "bg": "black"} for _ in range(self.GRID_COLS)]
            for _ in range(self.GRID_ROWS)
        ]

    def load_page(self, rows: List[str]) -> None:
        """Load teletext page rows into the grid surface."""
        for y, row in enumerate(rows[: self.GRID_ROWS]):
            for x, char in enumerate(row[: self.GRID_COLS]):
                if y < self.GRID_ROWS and x < self.GRID_COLS:
                    self.cells[y][x]["char"] = char

    def get_cells(self) -> List[List[Dict[str, Any]]]:
        """Get the current grid cell state."""
        return self.cells

    def get_row(self, y: int) -> List[Dict[str, Any]]:
        """Get a single row of grid cells."""
        if 0 <= y < self.GRID_ROWS:
            return self.cells[y]
        return []

    def set_cell(self, y: int, x: int, char: str, fg: str = "green", bg: str = "black") -> None:
        """Set a single grid cell."""
        if 0 <= y < self.GRID_ROWS and 0 <= x < self.GRID_COLS:
            self.cells[y][x] = {"char": char, "fg": fg, "bg": bg}

    def clear(self) -> None:
        """Clear the grid surface."""
        for y in range(self.GRID_ROWS):
            for x in range(self.GRID_COLS):
                self.cells[y][x] = {"char": " ", "fg": "green", "bg": "black"}

    def to_text(self) -> str:
        """Render the grid surface as plain text."""
        lines = []
        for row in self.cells:
            line = "".join(cell["char"] for cell in row)
            lines.append(line)
        return "\n".join(lines)

    def to_teletext_frame(self) -> List[str]:
        """Export the grid surface as a teletext frame (list of rows)."""
        return [self.to_text().split("\n")[i] for i in range(self.GRID_ROWS)]
