"""
GameToTeletextBridge — Convert game output to teletext grid format

This module provides the bridge between game output (ANSI/ASCII)
and the CeefaxThinUI teletext grid format (40x25 characters).

Features:
    - ANSI escape sequence parsing and colour mapping
    - ASCII art to teletext grid conversion
    - 40x25 character grid with per-cell colour attributes
    - SKIN style application to teletext output
    - Export to CeefaxThinUI format, HTML, and PNG
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
from enum import Enum
import re


class TeletextColour(Enum):
    """Teletext colour palette (Mode 7)"""
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7


# ANSI colour to teletext colour mapping
ANSI_TO_TELETEXT: Dict[int, TeletextColour] = {
    30: TeletextColour.BLACK,    # Black
    31: TeletextColour.RED,      # Red
    32: TeletextColour.GREEN,    # Green
    33: TeletextColour.YELLOW,   # Yellow
    34: TeletextColour.BLUE,     # Blue
    35: TeletextColour.MAGENTA,  # Magenta
    36: TeletextColour.CYAN,     # Cyan
    37: TeletextColour.WHITE,    # White
    90: TeletextColour.BLACK,    # Bright Black (Dark Grey)
    91: TeletextColour.RED,      # Bright Red
    92: TeletextColour.GREEN,    # Bright Green
    93: TeletextColour.YELLOW,   # Bright Yellow
    94: TeletextColour.BLUE,     # Bright Blue
    95: TeletextColour.MAGENTA,  # Bright Magenta
    96: TeletextColour.CYAN,     # Bright Cyan
    97: TeletextColour.WHITE,    # Bright White
}


@dataclass
class TeletextCell:
    """A single cell in the teletext grid"""
    char: str = " "
    foreground: TeletextColour = TeletextColour.WHITE
    background: TeletextColour = TeletextColour.BLACK
    bold: bool = False
    flash: bool = False
    double_height: bool = False
    double_width: bool = False


class TeletextGrid:
    """
    40x25 teletext character grid.
    
    The grid represents a standard Mode 7 teletext screen with
    40 columns and 25 rows. Each cell has a character and colour
    attributes.
    """
    
    COLS = 40
    ROWS = 25
    
    def __init__(self):
        """Initialize an empty teletext grid"""
        self.cells: List[List[TeletextCell]] = [
            [TeletextCell() for _ in range(self.COLS)]
            for _ in range(self.ROWS)
        ]
        self._current_fg: TeletextColour = TeletextColour.WHITE
        self._current_bg: TeletextColour = TeletextColour.BLACK
        self._current_bold: bool = False
        self._cursor_row: int = 0
        self._cursor_col: int = 0
    
    def clear(self):
        """Clear the entire grid"""
        for row in range(self.ROWS):
            for col in range(self.COLS):
                self.cells[row][col] = TeletextCell()
        self._cursor_row = 0
        self._cursor_col = 0
    
    def set_cell(self, row: int, col: int, char: str,
                 fg: Optional[TeletextColour] = None,
                 bg: Optional[TeletextColour] = None,
                 bold: Optional[bool] = None):
        """Set a cell's character and attributes"""
        if 0 <= row < self.ROWS and 0 <= col < self.COLS:
            cell = self.cells[row][col]
            cell.char = char if char else " "
            if fg is not None:
                cell.foreground = fg
            if bg is not None:
                cell.background = bg
            if bold is not None:
                cell.bold = bold
    
    def write_text(self, text: str, row: Optional[int] = None,
                   col: Optional[int] = None):
        """Write text to the grid at the given position"""
        if row is not None:
            self._cursor_row = row
        if col is not None:
            self._cursor_col = col
        
        for ch in text:
            if ch == '\n':
                self._cursor_row += 1
                self._cursor_col = 0
            elif ch == '\r':
                self._cursor_col = 0
            else:
                self.set_cell(
                    self._cursor_row, self._cursor_col, ch,
                    self._current_fg, self._current_bg, self._current_bold
                )
                self._cursor_col += 1
                if self._cursor_col >= self.COLS:
                    self._cursor_row += 1
                    self._cursor_col = 0
    
    def set_foreground(self, colour: TeletextColour):
        """Set current foreground colour"""
        self._current_fg = colour
    
    def set_background(self, colour: TeletextColour):
        """Set current background colour"""
        self._current_bg = colour
    
    def set_bold(self, bold: bool):
        """Set bold attribute"""
        self._current_bold = bold
    
    def to_ceefax_format(self) -> List[str]:
        """
        Convert grid to CeefaxThinUI format.
        
        Returns a list of strings, one per row, with teletext
        control codes embedded.
        """
        lines = []
        for row in range(self.ROWS):
            line = ""
            current_fg = None
            current_bg = None
            
            for col in range(self.COLS):
                cell = self.cells[row][col]
                
                # Add colour change codes when needed
                if cell.foreground != current_fg:
                    current_fg = cell.foreground
                    line += f"\x1b[{31 + current_fg.value}m"
                
                if cell.background != current_bg:
                    current_bg = cell.background
                    line += f"\x1b[{41 + current_bg.value}m"
                
                line += cell.char
            
            lines.append(line)
        
        return lines
    
    def to_html(self, title: str = "Teletext Output") -> str:
        """
        Export grid to HTML with inline styles.
        
        Args:
            title: Page title
            
        Returns:
            HTML string
        """
        colour_map = {
            TeletextColour.BLACK: "#000000",
            TeletextColour.RED: "#FF0000",
            TeletextColour.GREEN: "#00FF00",
            TeletextColour.YELLOW: "#FFFF00",
            TeletextColour.BLUE: "#0000FF",
            TeletextColour.MAGENTA: "#FF00FF",
            TeletextColour.CYAN: "#00FFFF",
            TeletextColour.WHITE: "#FFFFFF",
        }
        
        html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  body {{ background: #000; font-family: 'Courier New', monospace; font-size: 14px; line-height: 1.2; }}
  pre {{ margin: 0; padding: 0; }}
</style>
</head>
<body>
<pre>
"""
        for row in range(self.ROWS):
            line = ""
            for col in range(self.COLS):
                cell = self.cells[row][col]
                fg = colour_map.get(cell.foreground, "#FFFFFF")
                bg = colour_map.get(cell.background, "#000000")
                weight = "bold" if cell.bold else "normal"
                escaped = cell.char.replace("&", "&").replace("<", "<").replace(">", ">")
                line += f'<span style="color:{fg};background:{bg};font-weight:{weight}">{escaped}</span>'
            html += line + "\n"
        
        html += """</pre>
</body>
</html>"""
        return html
    
    def to_ansi(self) -> str:
        """
        Export grid to ANSI escape sequence string.
        
        Returns:
            ANSI-formatted string
        """
        result = ""
        for row in range(self.ROWS):
            current_fg = None
            current_bg = None
            
            for col in range(self.COLS):
                cell = self.cells[row][col]
                
                if cell.foreground != current_fg:
                    current_fg = cell.foreground
                    result += f"\x1b[{30 + current_fg.value}m"
                
                if cell.background != current_bg:
                    current_bg = cell.background
                    result += f"\x1b[{40 + current_bg.value}m"
                
                if cell.bold:
                    result += "\x1b[1m"
                
                result += cell.char
                
                if cell.bold:
                    result += "\x1b[22m"
            
            result += "\x1b[0m\n"
        
        return result


class ColourMapper:
    """
    Maps game colours to teletext palette.
    
    Handles conversion from various colour formats:
    - ANSI escape sequences (SGR codes)
    - RGB hex colours
    - Named colours
    - Game-specific colour indices
    """
    
    # Named colour to teletext mapping
    NAMED_COLOURS: Dict[str, TeletextColour] = {
        "black": TeletextColour.BLACK,
        "red": TeletextColour.RED,
        "green": TeletextColour.GREEN,
        "yellow": TeletextColour.YELLOW,
        "blue": TeletextColour.BLUE,
        "magenta": TeletextColour.MAGENTA,
        "cyan": TeletextColour.CYAN,
        "white": TeletextColour.WHITE,
        "grey": TeletextColour.BLACK,
        "gray": TeletextColour.BLACK,
        "orange": TeletextColour.YELLOW,
        "purple": TeletextColour.MAGENTA,
        "pink": TeletextColour.MAGENTA,
        "brown": TeletextColour.RED,
        "gold": TeletextColour.YELLOW,
        "silver": TeletextColour.WHITE,
    }
    
    @classmethod
    def from_ansi_sgr(cls, sgr_code: int) -> TeletextColour:
        """Map ANSI SGR colour code to teletext colour"""
        return ANSI_TO_TELETEXT.get(sgr_code, TeletextColour.WHITE)
    
    @classmethod
    def from_rgb_hex(cls, hex_colour: str) -> TeletextColour:
        """
        Map RGB hex colour to nearest teletext colour.
        
        Args:
            hex_colour: Hex colour string (e.g. "#FF0000")
            
        Returns:
            Nearest teletext colour
        """
        hex_colour = hex_colour.lstrip('#')
        if len(hex_colour) != 6:
            return TeletextColour.WHITE
        
        try:
            r = int(hex_colour[0:2], 16)
            g = int(hex_colour[2:4], 16)
            b = int(hex_colour[4:6], 16)
        except ValueError:
            return TeletextColour.WHITE
        
        # Find nearest teletext colour
        teletext_rgb = [
            (0, 0, 0),      # Black
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (255, 255, 0),  # Yellow
            (0, 0, 255),    # Blue
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 255, 255),# White
        ]
        
        min_dist = float('inf')
        best = TeletextColour.WHITE
        
        for i, (tr, tg, tb) in enumerate(teletext_rgb):
            dist = (r - tr) ** 2 + (g - tg) ** 2 + (b - tb) ** 2
            if dist < min_dist:
                min_dist = dist
                best = TeletextColour(i)
        
        return best
    
    @classmethod
    def from_name(cls, name: str) -> TeletextColour:
        """Map named colour to teletext colour"""
        return cls.NAMED_COLOURS.get(name.lower(), TeletextColour.WHITE)


class GameToTeletextBridge:
    """
    Converts game output to teletext grid format.
    
    This bridge takes raw game output (ANSI text, ASCII art, or
    structured data) and converts it to a 40x25 teletext grid
    suitable for display via CeefaxThinUI.
    
    Features:
    - ANSI escape sequence parsing
    - ASCII art to teletext conversion
    - SKIN style application
    - Colour mapping
    - Export to multiple formats
    """
    
    def __init__(self, skin_engine=None):
        """
        Initialize the bridge.
        
        Args:
            skin_engine: Optional SkinEngine for style application
        """
        self.grid = TeletextGrid()
        self.skin_engine = skin_engine
        self._ansi_pattern = re.compile(r'\x1b\[([0-9;]*)m')
        self._title: str = ""
        self._subtitle: str = ""
    
    def clear(self):
        """Clear the grid"""
        self.grid.clear()
    
    def set_title(self, title: str, subtitle: str = ""):
        """Set the title and subtitle for display"""
        self._title = title
        self._subtitle = subtitle
    
    def process_ansi(self, ansi_text: str) -> None:
        """
        Process ANSI-encoded text and render to teletext grid.
        
        Parses ANSI escape sequences and maps colours to the
        teletext palette.
        
        Args:
            ansi_text: ANSI-encoded text string
        """
        # Split text by ANSI sequences
        parts = self._ansi_pattern.split(ansi_text)
        
        current_fg = TeletextColour.WHITE
        current_bg = TeletextColour.BLACK
        current_bold = False
        
        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Text content
                self.grid.write_text(part)
            else:
                # ANSI escape sequence
                if part:
                    codes = [int(c) for c in part.split(';') if c]
                    for code in codes:
                        if code == 0:
                            # Reset
                            current_fg = TeletextColour.WHITE
                            current_bg = TeletextColour.BLACK
                            current_bold = False
                        elif code == 1:
                            current_bold = True
                        elif code == 22:
                            current_bold = False
                        elif 30 <= code <= 37:
                            current_fg = ColourMapper.from_ansi_sgr(code)
                        elif 40 <= code <= 47:
                            current_bg = ColourMapper.from_ansi_sgr(code - 10)
                        elif code == 90:
                            current_fg = TeletextColour.BLACK
                        elif 91 <= code <= 97:
                            current_fg = ColourMapper.from_ansi_sgr(code)
                
                self.grid.set_foreground(current_fg)
                self.grid.set_background(current_bg)
                self.grid.set_bold(current_bold)
    
    def process_ascii_art(self, ascii_text: str) -> None:
        """
        Process ASCII art text and render to teletext grid.
        
        Handles box-drawing characters, borders, and simple
        ASCII art layouts.
        
        Args:
            ascii_text: ASCII art text
        """
        lines = ascii_text.split('\n')
        for row, line in enumerate(lines):
            if row >= TeletextGrid.ROWS:
                break
            for col, ch in enumerate(line):
                if col >= TeletextGrid.COLS:
                    break
                self.grid.set_cell(row, col, ch)
    
    def process_text(self, text: str, row: int = 0, col: int = 0,
                     fg: Optional[TeletextColour] = None,
                     bg: Optional[TeletextColour] = None,
                     bold: bool = False) -> None:
        """
        Process plain text and render to teletext grid.
        
        Args:
            text: Text to render
            row: Starting row
            col: Starting column
            fg: Foreground colour
            bg: Background colour
            bold: Bold attribute
        """
        if fg is not None:
            self.grid.set_foreground(fg)
        if bg is not None:
            self.grid.set_background(bg)
        self.grid.set_bold(bold)
        self.grid.write_text(text, row, col)
    
    def process_box(self, x: int, y: int, width: int, height: int,
                    title: str = "", fg: TeletextColour = TeletextColour.WHITE,
                    bg: TeletextColour = TeletextColour.BLACK) -> None:
        """
        Draw a box on the teletext grid.
        
        Args:
            x: Left column
            y: Top row
            width: Box width (including borders)
            height: Box height (including borders)
            title: Optional title text
            fg: Foreground colour
            bg: Background colour
        """
        self.grid.set_foreground(fg)
        self.grid.set_background(bg)
        
        # Top border
        self.grid.set_cell(y, x, '+', fg, bg)
        for cx in range(x + 1, x + width - 1):
            self.grid.set_cell(y, cx, '-', fg, bg)
        self.grid.set_cell(y, x + width - 1, '+', fg, bg)
        
        # Title
        if title and len(title) < width - 2:
            title_x = x + 2
            for i, ch in enumerate(title):
                self.grid.set_cell(y, title_x + i, ch, fg, bg)
        
        # Bottom border
        by = y + height - 1
        self.grid.set_cell(by, x, '+', fg, bg)
        for cx in range(x + 1, x + width - 1):
            self.grid.set_cell(by, cx, '-', fg, bg)
        self.grid.set_cell(by, x + width - 1, '+', fg, bg)
        
        # Side borders
        for ry in range(y + 1, y + height - 1):
            self.grid.set_cell(ry, x, '|', fg, bg)
            self.grid.set_cell(ry, x + width - 1, '|', fg, bg)
    
    def apply_skin(self) -> None:
        """Apply SKIN styles to the current grid"""
        if self.skin_engine is None:
            return
        
        skin = self.skin_engine.active_skin
        if skin is None:
            return
        
        # Apply skin colours to the grid
        fg = ColourMapper.from_rgb_hex(skin.foreground_color)
        bg = ColourMapper.from_rgb_hex(skin.background_color)
        
        self.grid.set_foreground(fg)
        self.grid.set_background(bg)
    
    def to_ceefax_format(self) -> List[str]:
        """Export grid to CeefaxThinUI format"""
        return self.grid.to_ceefax_format()
    
    def to_html(self, title: str = "Teletext Output") -> str:
        """Export grid to HTML"""
        return self.grid.to_html(title)
    
    def to_ansi(self) -> str:
        """Export grid to ANSI string"""
        return self.grid.to_ansi()
    
    def get_grid_data(self) -> Dict[str, Any]:
        """
        Get grid data as a dictionary for API export.
        
        Returns:
            Dict with grid dimensions and cell data
        """
        return {
            "cols": TeletextGrid.COLS,
            "rows": TeletextGrid.ROWS,
            "title": self._title,
            "subtitle": self._subtitle,
            "cells": [
                [
                    {
                        "char": self.grid.cells[r][c].char,
                        "fg": self.grid.cells[r][c].foreground.value,
                        "bg": self.grid.cells[r][c].background.value,
                        "bold": self.grid.cells[r][c].bold,
                    }
                    for c in range(TeletextGrid.COLS)
                ]
                for r in range(TeletextGrid.ROWS)
            ],
        }


def create_bridge(skin_engine=None) -> GameToTeletextBridge:
    """Create and return a GameToTeletextBridge instance"""
    return GameToTeletextBridge(skin_engine)
