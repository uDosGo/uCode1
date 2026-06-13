"""
ColourPalette — Colour management for grid displays
====================================================
Standard colour palette for teletext/grid displays.
Supports 16 standard colours with names and hex values.
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class Colour:
    """A named colour with index and hex value."""
    index: int
    name: str
    hex: str
    r: int
    g: int
    b: int

    @property
    def rgb(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)

    @property
    def ansi_code(self) -> int:
        """Get ANSI escape code for this colour."""
        if self.index < 8:
            return 30 + self.index  # Dark colours
        return 90 + (self.index - 8)  # Bright colours


class ColourPalette:
    """Standard 16-colour teletext palette."""

    # Standard teletext colours (index, name, hex)
    COLOURS = [
        Colour(0, 'Black', '#000000', 0, 0, 0),
        Colour(1, 'Red', '#FF0000', 255, 0, 0),
        Colour(2, 'Green', '#00FF00', 0, 255, 0),
        Colour(3, 'Yellow', '#FFFF00', 255, 255, 0),
        Colour(4, 'Blue', '#0000FF', 0, 0, 255),
        Colour(5, 'Magenta', '#FF00FF', 255, 0, 255),
        Colour(6, 'Cyan', '#00FFFF', 0, 255, 255),
        Colour(7, 'White', '#FFFFFF', 255, 255, 255),
        Colour(8, 'Bright Black', '#555555', 85, 85, 85),
        Colour(9, 'Bright Red', '#FF5555', 255, 85, 85),
        Colour(10, 'Bright Green', '#55FF55', 85, 255, 85),
        Colour(11, 'Bright Yellow', '#FFFF55', 255, 255, 85),
        Colour(12, 'Bright Blue', '#5555FF', 85, 85, 255),
        Colour(13, 'Bright Magenta', '#FF55FF', 255, 85, 255),
        Colour(14, 'Bright Cyan', '#55FFFF', 85, 255, 255),
        Colour(15, 'Bright White', '#FFFFFF', 255, 255, 255),
    ]

    _by_index: Dict[int, Colour] = {c.index: c for c in COLOURS}
    _by_name: Dict[str, Colour] = {c.name.lower(): c for c in COLOURS}

    @classmethod
    def get(cls, index: int) -> Colour:
        """Get colour by index (0-15)."""
        return cls._by_index.get(index % 16, cls._by_index[7])

    @classmethod
    def get_by_name(cls, name: str) -> Optional[Colour]:
        """Get colour by name (case-insensitive)."""
        return cls._by_name.get(name.lower())

    @classmethod
    def hex_to_index(cls, hex_color: str) -> int:
        """Find closest colour index by hex value."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return 7
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        best = 0
        best_dist = float('inf')
        for colour in cls.COLOURS:
            dist = (r - colour.r) ** 2 + (g - colour.g) ** 2 + (b - colour.b) ** 2
            if dist < best_dist:
                best_dist = dist
                best = colour.index
        return best

    @classmethod
    def to_css(cls, index: int) -> str:
        """Get CSS colour string for index."""
        return cls.get(index).hex
