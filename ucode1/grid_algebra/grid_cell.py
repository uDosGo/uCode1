"""
GridCell — Individual cell in the grid algebra system
======================================================
Represents a single cell at position (x, y, z) with character,
foreground/background colour, and display attributes.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class GridCell:
    """A single cell in the grid."""
    x: int = 0
    y: int = 0
    z: int = 0
    char: str = ' '
    fg: int = 7   # Default foreground (white)
    bg: int = 0   # Default background (black)
    bold: bool = False
    italic: bool = False
    underline: bool = False
    blink: bool = False
    reverse: bool = False
    meta: dict = field(default_factory=dict)

    def __post_init__(self):
        if len(self.char) != 1:
            raise ValueError(f"GridCell char must be a single character, got '{self.char}'")

    @property
    def position(self) -> tuple:
        """Return (x, y, z) position."""
        return (self.x, self.y, self.z)

    @property
    def is_empty(self) -> bool:
        """Check if cell is empty (space character)."""
        return self.char == ' '

    def clone(self) -> 'GridCell':
        """Create a deep copy of this cell."""
        return GridCell(
            x=self.x, y=self.y, z=self.z,
            char=self.char, fg=self.fg, bg=self.bg,
            bold=self.bold, italic=self.italic,
            underline=self.underline, blink=self.blink,
            reverse=self.reverse,
            meta=dict(self.meta),
        )

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            'x': self.x, 'y': self.y, 'z': self.z,
            'char': self.char, 'fg': self.fg, 'bg': self.bg,
            'bold': self.bold, 'italic': self.italic,
            'underline': self.underline, 'blink': self.blink,
            'reverse': self.reverse,
            'meta': self.meta,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'GridCell':
        """Deserialize from dictionary."""
        return cls(
            x=data.get('x', 0), y=data.get('y', 0), z=data.get('z', 0),
            char=data.get('char', ' '),
            fg=data.get('fg', 7), bg=data.get('bg', 0),
            bold=data.get('bold', False),
            italic=data.get('italic', False),
            underline=data.get('underline', False),
            blink=data.get('blink', False),
            reverse=data.get('reverse', False),
            meta=data.get('meta', {}),
        )

    def __repr__(self) -> str:
        attrs = []
        if self.bold: attrs.append('B')
        if self.italic: attrs.append('I')
        if self.underline: attrs.append('U')
        if self.blink: attrs.append('K')
        if self.reverse: attrs.append('R')
        attr_str = f" [{''.join(attrs)}]" if attrs else ''
        return f"Cell({self.x},{self.y},{self.z}) '{self.char}' fg={self.fg} bg={self.bg}{attr_str}"
