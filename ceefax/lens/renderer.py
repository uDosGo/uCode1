"""Ceefax LENS Renderer — transforms teletext frames into display formats.

Supports:
  - HTML rendering (with Teletext50 font)
  - ANSI terminal rendering
  - Raw teletext frame data
  - GridUI cell mapping (for uCode1 grid display)
"""

import html
from typing import List, Optional


class TeletextRenderer:
    """Renders teletext frames into various output formats."""

    # Teletext colour palette (ANSI)
    COLORS = {
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "reset": "\033[0m",
    }

    # Teletext colour palette (CSS)
    CSS_COLORS = {
        "black": "#000000",
        "red": "#ff0000",
        "green": "#00ff00",
        "yellow": "#ffff00",
        "blue": "#0000ff",
        "magenta": "#ff00ff",
        "cyan": "#00ffff",
        "white": "#ffffff",
    }

    def __init__(self, font_family: str = "Teletext50, monospace"):
        self.font_family = font_family

    def to_html(self, rows: List[str], page_number: int = 0) -> str:
        """Render teletext rows as HTML using teletext-spec.css classes."""
        html_rows = []
        for row in rows:
            escaped = html.escape(row)
            html_rows.append(
                '<div class="tt-row">%s</div>' % escaped
            )
        return "\n".join(html_rows)

    def to_full_page(self, rows: List[str], title: str = "Ceefax") -> str:
        """Render a full teletext page with teletext-spec.css."""
        body = self.to_html(rows)
        return """<!DOCTYPE html>
<html>
<head>
    <title>%s</title>
    <link rel="stylesheet" href="/teletext-spec.css">
</head>
<body class="tt-theme-green">
    <div class="tt-frame">
        <div class="tt-header-row">═══ %s ═══</div>
        <div class="tt-body">
            %s
        </div>
    </div>
</body>
</html>""" % (title, title, body)

    def to_ansi(self, rows: List[str], color: str = "green") -> str:
        """Render teletext rows as ANSI text for terminal display."""
        color_code = self.COLORS.get(color, self.COLORS["green"])
        reset = self.COLORS["reset"]
        lines = [f"{color_code}{row}{reset}" for row in rows]
        return "\n".join(lines)

    def to_grid_cells(self, rows: List[str]) -> List[List[dict]]:
        """Map teletext rows to GridUI cell format.

        Each cell is a dict with:
          - char: the character
          - fg: foreground colour
          - bg: background colour
          - flash: whether the cell should flash
        """
        grid = []
        for row in rows:
            cells = []
            for char in row:
                cells.append({
                    "char": char,
                    "fg": "green",
                    "bg": "black",
                    "flash": False,
                })
            grid.append(cells)
        return grid

    def to_raw(self, rows: List[str]) -> bytes:
        """Render teletext rows as raw teletext frame bytes."""
        frame = bytearray()
        for row in rows:
            frame.extend(row.encode("ascii", errors="replace"))
            frame.extend(b"\r\n")
        return bytes(frame)
