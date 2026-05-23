"""
Bitmap Grid Renderer — SVG/Font/Emoji/Icon → Character-Cell Bitmap

Converts various input formats into character-cell grid bitmaps.
Each cell in the output grid represents a pixel block in the source image.

Supports:
- SVG path rendering to grid cells
- Font glyph rendering to grid cells
- Emoji to 128-slot character mapping
- Icon set to grid bitmap
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..grid.models import Grid, GridCell, Coordinate


class RenderSource(Enum):
    """Source type for bitmap rendering."""
    SVG = "svg"
    FONT = "font"
    EMOJI = "emoji"
    ICON = "icon"
    RAW_BITMAP = "raw_bitmap"


@dataclass
class RenderOptions:
    """Options for bitmap rendering."""
    cell_width: int = 8       # Width of each character cell in pixels
    cell_height: int = 12     # Height of each character cell in pixels
    threshold: int = 128      # Brightness threshold for binarization
    invert: bool = False      # Invert the output
    dither: bool = False      # Apply dithering
    scale: float = 1.0        # Scale factor
    fg_color: str = '#ffffff'  # Foreground color
    bg_color: str = '#000000'  # Background color


@dataclass
class BitmapCell:
    """A single cell in a bitmap grid."""
    brightness: float = 0.0   # 0.0 (black) to 1.0 (white)
    r: int = 0
    g: int = 0
    b: int = 0
    is_set: bool = False      # Whether this pixel is "on"


class BitmapGrid:
    """
    A grid of bitmap cells representing pixel data.
    
    This is an intermediate representation between source images
    and character-cell grids.
    """
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cells: List[List[BitmapCell]] = [
            [BitmapCell() for _ in range(width)]
            for _ in range(height)
        ]
    
    def set_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        """Set a pixel at (x, y)."""
        if 0 <= x < self.width and 0 <= y < self.height:
            cell = self.cells[y][x]
            cell.r = r
            cell.g = g
            cell.b = b
            cell.brightness = (r + g + b) / (3 * 255)
            cell.is_set = cell.brightness > 0.5
    
    def get_region_brightness(self, x: int, y: int, w: int, h: int) -> float:
        """Get the average brightness of a region."""
        total = 0.0
        count = 0
        for dy in range(h):
            for dx in range(w):
                px, py = x + dx, y + dy
                if 0 <= px < self.width and 0 <= py < self.height:
                    total += self.cells[py][px].brightness
                    count += 1
        return total / count if count > 0 else 0.0


class BitmapRenderer:
    """
    Unified renderer that converts various sources to character-cell grids.
    
    The renderer works in two stages:
    1. Convert source to BitmapGrid (pixel data)
    2. Convert BitmapGrid to character-cell Grid
    """

    def __init__(self, options: Optional[RenderOptions] = None):
        self.options = options or RenderOptions()

    # ── BitmapGrid → Character Grid ──────────────────────────

    def bitmap_to_grid(self, bitmap: BitmapGrid) -> Grid:
        """
        Convert a BitmapGrid to a character-cell Grid.
        
        Each character cell represents a block of pixels.
        Uses block characters (█, ▄, ▀, ░, ▒, ▓) to represent
        different fill levels.
        """
        cw = self.options.cell_width
        ch = self.options.cell_height
        
        grid_width = (bitmap.width + cw - 1) // cw
        grid_height = (bitmap.height + ch - 1) // ch
        
        grid: Grid[str] = Grid(grid_width, grid_height)
        
        for gy in range(grid_height):
            for gx in range(grid_width):
                brightness = bitmap.get_region_brightness(
                    gx * cw, gy * ch, cw, ch
                )
                
                if self.options.invert:
                    brightness = 1.0 - brightness
                
                # Map brightness to character
                char = self._brightness_to_char(brightness)
                cell = grid.get(gx, gy)
                cell.char = char
                cell.fg_color = self.options.fg_color
                cell.bg_color = self.options.bg_color
        
        return grid

    def _brightness_to_char(self, brightness: float) -> str:
        """Map a brightness value (0-1) to a character."""
        if brightness < 0.1:
            return ' '          # Empty
        elif brightness < 0.25:
            return '\u2591'     # Light shade (░)
        elif brightness < 0.5:
            return '\u2592'     # Medium shade (▒)
        elif brightness < 0.75:
            return '\u2593'     # Dark shade (▓)
        else:
            return '\u2588'     # Full block (█)

    # ── SVG Rendering ────────────────────────────────────────

    def render_svg(self, svg_content: str, width: int, height: int) -> Grid:
        """
        Render SVG content to a character-cell grid.
        
        Uses a simple SVG path parser to create a bitmap,
        then converts to character cells.
        
        Note: For full SVG support, consider using cairosvg or similar.
        This provides a basic path-based renderer.
        """
        bitmap = BitmapGrid(width, height)
        
        # Simple SVG path parsing
        # Look for basic shapes: rect, circle, ellipse, line, polyline, polygon
        import re
        
        # Parse <rect> elements
        for match in re.finditer(
            r'<rect\s+[^>]*x="([^"]*)"[^>]*y="([^"]*)"[^>]*width="([^"]*)"[^>]*height="([^"]*)"[^>]*>',
            svg_content
        ):
            x = float(match.group(1))
            y = float(match.group(2))
            w = float(match.group(3))
            h = float(match.group(4))
            self._draw_rect(bitmap, int(x), int(y), int(x + w), int(y + h))
        
        # Parse <circle> elements
        for match in re.finditer(
            r'<circle\s+[^>]*cx="([^"]*)"[^>]*cy="([^"]*)"[^>]*r="([^"]*)"[^>]*>',
            svg_content
        ):
            cx = float(match.group(1))
            cy = float(match.group(2))
            r = float(match.group(3))
            self._draw_circle(bitmap, int(cx), int(cy), int(r))
        
        # Parse <line> elements
        for match in re.finditer(
            r'<line\s+[^>]*x1="([^"]*)"[^>]*y1="([^"]*)"[^>]*x2="([^"]*)"[^>]*y2="([^"]*)"[^>]*>',
            svg_content
        ):
            x1 = float(match.group(1))
            y1 = float(match.group(2))
            x2 = float(match.group(3))
            y2 = float(match.group(4))
            self._draw_line(bitmap, int(x1), int(y1), int(x2), int(y2))
        
        return self.bitmap_to_grid(bitmap)

    def _draw_rect(self, bitmap: BitmapGrid, x1: int, y1: int, x2: int, y2: int) -> None:
        """Draw a filled rectangle on the bitmap."""
        for y in range(max(0, y1), min(bitmap.height, y2 + 1)):
            for x in range(max(0, x1), min(bitmap.width, x2 + 1)):
                bitmap.set_pixel(x, y, 255, 255, 255)

    def _draw_circle(self, bitmap: BitmapGrid, cx: int, cy: int, r: int) -> None:
        """Draw a filled circle on the bitmap."""
        r2 = r * r
        for y in range(max(0, cy - r), min(bitmap.height, cy + r + 1)):
            for x in range(max(0, cx - r), min(bitmap.width, cx + r + 1)):
                dx, dy = x - cx, y - cy
                if dx * dx + dy * dy <= r2:
                    bitmap.set_pixel(x, y, 255, 255, 255)

    def _draw_line(self, bitmap: BitmapGrid, x1: int, y1: int, x2: int, y2: int) -> None:
        """Draw a line on the bitmap using Bresenham's algorithm."""
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy
        
        while True:
            if 0 <= x1 < bitmap.width and 0 <= y1 < bitmap.height:
                bitmap.set_pixel(x1, y1, 255, 255, 255)
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy

    # ── Emoji Rendering ──────────────────────────────────────

    def render_emoji(self, emoji: str, grid_width: int, grid_height: int) -> Grid:
        """
        Render an emoji to a character-cell grid.
        
        Since emoji rendering requires a font renderer,
        this creates a placeholder grid with the emoji character
        centered in the grid.
        """
        grid: Grid[str] = Grid(grid_width, grid_height)
        
        # Place the emoji character in the center cell
        cx, cy = grid_width // 2, grid_height // 2
        cell = grid.get(cx, cy)
        cell.char = emoji
        cell.fg_color = self.options.fg_color
        
        return grid

    # ── Raw Bitmap Rendering ─────────────────────────────────

    def render_raw_bitmap(self, pixels: List[List[Tuple[int, int, int]]]) -> Grid:
        """
        Render raw pixel data to a character-cell grid.
        
        Args:
            pixels: 2D list of (r, g, b) tuples
        
        Returns:
            Character-cell Grid
        """
        height = len(pixels)
        width = len(pixels[0]) if height > 0 else 0
        
        bitmap = BitmapGrid(width, height)
        for y in range(height):
            for x in range(width):
                r, g, b = pixels[y][x]
                bitmap.set_pixel(x, y, r, g, b)
        
        return self.bitmap_to_grid(bitmap)

    # ── Icon Rendering ───────────────────────────────────────

    def render_icon(self, icon_name: str, grid_width: int, grid_height: int) -> Grid:
        """
        Render a named icon to a character-cell grid.
        
        Uses a built-in set of simple icon patterns.
        """
        grid: Grid[str] = Grid(grid_width, grid_height)
        
        # Get icon pattern
        pattern = self._get_icon_pattern(icon_name, grid_width, grid_height)
        if pattern is None:
            return grid
        
        # Apply pattern to grid
        for y in range(min(len(pattern), grid_height)):
            for x in range(min(len(pattern[y]), grid_width)):
                if pattern[y][x]:
                    cell = grid.get(x, y)
                    cell.char = '\u2588'  # Full block
                    cell.fg_color = self.options.fg_color
        
        return grid

    def _get_icon_pattern(self, name: str, w: int, h: int) -> Optional[List[List[bool]]]:
        """Get a simple icon pattern by name."""
        # Arrow right
        if name == "arrow_right":
            return [
                [False, False, True, False, False],
                [False, True, True, True, False],
                [True, True, True, True, True],
                [False, True, True, True, False],
                [False, False, True, False, False],
            ]
        # Arrow left
        elif name == "arrow_left":
            return [
                [False, False, True, False, False],
                [False, True, True, True, False],
                [True, True, True, True, True],
                [False, True, True, True, False],
                [False, False, True, False, False],
            ]
        # Arrow up
        elif name == "arrow_up":
            return [
                [False, False, True, False, False],
                [False, True, True, True, False],
                [True, True, True, True, True],
                [False, False, True, False, False],
                [False, False, True, False, False],
            ]
        # Arrow down
        elif name == "arrow_down":
            return [
                [False, False, True, False, False],
                [False, False, True, False, False],
                [True, True, True, True, True],
                [False, True, True, True, False],
                [False, False, True, False, False],
            ]
        # Star
        elif name == "star":
            return [
                [False, False, True, False, False],
                [False, True, True, True, False],
                [True, True, True, True, True],
                [False, True, True, True, False],
                [False, False, True, False, False],
            ]
        # Heart
        elif name == "heart":
            return [
                [False, True, False, True, False],
                [True, True, True, True, True],
                [True, True, True, True, True],
                [False, True, True, True, False],
                [False, False, True, False, False],
            ]
        # Checkmark
        elif name == "check":
            return [
                [False, False, False, False, True],
                [False, False, False, True, True],
                [False, False, True, True, False],
                [False, True, True, False, False],
                [True, True, False, False, False],
            ]
        # Cross
        elif name == "cross":
            return [
                [True, False, False, False, True],
                [False, True, False, True, False],
                [False, False, True, False, False],
                [False, True, False, True, False],
                [True, False, False, False, True],
            ]
        return None

    # ── Utility ──────────────────────────────────────────────

    def grid_to_ascii(self, grid: Grid) -> List[str]:
        """Convert a character grid to ASCII lines."""
        lines = []
        for y in range(grid.height):
            line = ''
            for x in range(grid.width):
                cell = grid.get(x, y)
                line += cell.char if cell.char else ' '
            lines.append(line)
        return lines
