"""
Grid Editor — Interactive Grid Painting and Editing

Provides cursor-based grid editing with:
- Cursor movement and painting
- Flood fill and selection
- Copy/paste regions
- Multi-layer editing support
- Undo/redo via EditHistory
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from ..grid.models import Grid, GridCell, Coordinate, GridRegion, GridSize
from ..grid.layers import GridLayer, GridStack, LayerType
from .history import EditHistory
from .palette import CharacterPalette, SlotEntry


class EditTool(Enum):
    """Available editing tools."""
    PENCIL = "pencil"          # Paint individual cells
    ERASER = "eraser"          # Clear individual cells
    FILL = "fill"              # Flood fill
    SELECT = "select"          # Rectangle selection
    LINE = "line"              # Draw lines
    RECT = "rect"              # Draw rectangles
    EYEDROPPER = "eyedropper"  # Pick character from cell


class SelectionMode(Enum):
    """Selection behavior."""
    REPLACE = "replace"  # Replace selection
    ADD = "add"          # Add to selection
    SUBTRACT = "subtract"  # Remove from selection


@dataclass
class CursorState:
    """State of the editing cursor."""
    x: int = 0
    y: int = 0
    visible: bool = True
    blink: bool = True

    def move(self, dx: int, dy: int, bounds: GridSize) -> None:
        """Move cursor within grid bounds."""
        self.x = max(0, min(bounds.width - 1, self.x + dx))
        self.y = max(0, min(bounds.height - 1, self.y + dy))

    def to_coordinate(self) -> Coordinate:
        """Convert to a Coordinate."""
        return Coordinate(self.x, self.y)


@dataclass
class SelectionState:
    """State of the current selection."""
    active: bool = False
    start_x: int = 0
    start_y: int = 0
    end_x: int = 0
    end_y: int = 0
    mode: SelectionMode = SelectionMode.REPLACE

    @property
    def region(self) -> GridRegion:
        """Get the selection as a GridRegion."""
        x1 = min(self.start_x, self.end_x)
        y1 = min(self.start_y, self.end_y)
        x2 = max(self.start_x, self.end_x)
        y2 = max(self.start_y, self.end_y)
        return GridRegion(x1, y1, x2 - x1 + 1, y2 - y1 + 1)

    @property
    def is_empty(self) -> bool:
        """Check if selection is empty (single point)."""
        return (self.start_x == self.end_x and
                self.start_y == self.end_y)

    def contains(self, x: int, y: int) -> bool:
        """Check if a point is within the selection."""
        return self.region.contains_xy(x, y)

    def clear(self) -> None:
        """Clear the selection."""
        self.active = False
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0


@dataclass
class ClipboardState:
    """Clipboard for copy/paste operations."""
    cells: List[List[Dict[str, Any]]] = field(default_factory=list)
    width: int = 0
    height: int = 0

    @property
    def is_empty(self) -> bool:
        """Check if clipboard has content."""
        return len(self.cells) == 0

    def clear(self) -> None:
        """Clear the clipboard."""
        self.cells.clear()
        self.width = 0
        self.height = 0


class GridEditor:
    """
    Interactive grid editor with cursor, tools, and history.
    
    Operates on a GridStack (multi-layer) and provides:
    - Cursor-based painting with various tools
    - Flood fill
    - Selection and copy/paste
    - Undo/redo
    - Layer management
    """

    def __init__(
        self,
        width: int = 40,
        height: int = 25,
        palette: Optional[CharacterPalette] = None,
    ):
        self.palette = palette or CharacterPalette()
        self.history = EditHistory[Grid](max_depth=100)

        # Create default grid stack with a base layer
        base_grid: Grid[Any] = Grid(width, height)
        self.stack: GridStack[Any] = GridStack()
        self.stack.add_layer(GridLayer(
            name="base",
            grid=base_grid,
            layer_type=LayerType.BASE,
            z_index=0,
        ))

        # Editor state
        self.cursor = CursorState()
        self.selection = SelectionState()
        self.clipboard = ClipboardState()
        self.tool: EditTool = EditTool.PENCIL
        self.current_slot: int = 22  # Default: full block (█)
        self.current_fg: str = '#ffffff'
        self.current_bg: str = '#000000'
        self._is_dragging: bool = False
        self._drag_start: Optional[Coordinate] = None

        # Active layer (default: first layer)
        self._active_layer_index: int = 0

    # ── Layer Management ──────────────────────────────────────

    @property
    def active_layer(self) -> Optional[GridLayer]:
        """Get the currently active layer."""
        if 0 <= self._active_layer_index < len(self.stack.layers):
            return self.stack.layers[self._active_layer_index]
        return None

    @property
    def active_grid(self) -> Optional[Grid]:
        """Get the grid of the active layer."""
        layer = self.active_layer
        return layer.grid if layer else None

    def set_active_layer(self, index: int) -> bool:
        """Set the active layer by index."""
        if 0 <= index < len(self.stack.layers):
            self._active_layer_index = index
            return True
        return False

    def set_active_layer_by_name(self, name: str) -> bool:
        """Set the active layer by name."""
        for i, layer in enumerate(self.stack.layers):
            if layer.name == name:
                self._active_layer_index = i
                return True
        return False

    def add_layer(self, name: str, layer_type: LayerType = LayerType.OBJECT,
                  z_index: Optional[int] = None) -> GridLayer:
        """Add a new layer to the stack."""
        grid = self.active_grid
        if grid is None:
            grid = Grid(40, 25)
        new_grid: Grid[Any] = Grid(grid.width, grid.height)
        z = z_index if z_index is not None else len(self.stack.layers)
        layer = GridLayer(name=name, grid=new_grid, layer_type=layer_type, z_index=z)
        self.stack.add_layer(layer)
        return layer

    def remove_active_layer(self) -> bool:
        """Remove the active layer (cannot remove the last layer)."""
        if len(self.stack.layers) <= 1:
            return False
        layer = self.active_layer
        if layer:
            self.stack.remove_layer(layer.name)
            self._active_layer_index = max(0, self._active_layer_index - 1)
            return True
        return False

    # ── Snapshot / History ────────────────────────────────────

    def _snapshot(self) -> Grid:
        """Take a snapshot of the active grid for undo."""
        grid = self.active_grid
        if grid is None:
            return Grid(40, 25)
        return grid.clone()

    def _push_history(self, description: str) -> None:
        """Push current state to undo history."""
        self.history.push(description, self._snapshot())

    def undo(self) -> bool:
        """Undo the last edit. Returns True if successful."""
        snapshot = self.history.undo()
        if snapshot is not None:
            grid = self.active_grid
            if grid:
                # Restore cells from snapshot
                for y in range(min(grid.height, snapshot.height)):
                    for x in range(min(grid.width, snapshot.width)):
                        grid.cells[y][x] = snapshot.cells[y][x].clone()
            return True
        return False

    def redo(self) -> bool:
        """Redo the last undone edit. Returns True if successful."""
        snapshot = self.history.redo()
        if snapshot is not None:
            grid = self.active_grid
            if grid:
                for y in range(min(grid.height, snapshot.height)):
                    for x in range(min(grid.width, snapshot.width)):
                        grid.cells[y][x] = snapshot.cells[y][x].clone()
            return True
        return False

    # ── Cell Operations ───────────────────────────────────────

    def _get_cell(self, x: int, y: int) -> Optional[GridCell]:
        """Get a cell from the active grid."""
        grid = self.active_grid
        if grid is None:
            return None
        try:
            return grid.get(x, y)
        except Exception:
            return None

    def _set_cell(self, x: int, y: int, char: str,
                  fg: Optional[str] = None, bg: Optional[str] = None) -> bool:
        """Set a cell in the active grid."""
        grid = self.active_grid
        if grid is None:
            return False
        try:
            cell = grid.get(x, y)
            cell.char = char
            if fg is not None:
                cell.fg_color = fg
            if bg is not None:
                cell.bg_color = bg
            return True
        except Exception:
            return False

    def paint(self, x: int, y: int) -> bool:
        """Paint a cell with the current slot character."""
        slot = self.palette.get(self.current_slot)
        if slot is None:
            return False
        return self._set_cell(x, y, slot.char, self.current_fg, self.current_bg)

    def erase(self, x: int, y: int) -> bool:
        """Erase a cell (set to space)."""
        return self._set_cell(x, y, ' ', '#ffffff', '#000000')

    # ── Flood Fill ────────────────────────────────────────────

    def flood_fill(self, start_x: int, start_y: int) -> int:
        """
        Flood fill from the starting position.
        Replaces all connected cells with the same character.
        Returns the number of cells filled.
        """
        grid = self.active_grid
        if grid is None:
            return 0

        start_cell = self._get_cell(start_x, start_y)
        if start_cell is None:
            return 0

        target_char = start_cell.char or ' '
        slot = self.palette.get(self.current_slot)
        if slot is None:
            return 0
        fill_char = slot.char

        # Don't fill if target and fill are the same
        if target_char == fill_char:
            return 0

        self._push_history(f"Flood fill at ({start_x}, {start_y})")

        filled = 0
        visited: Set[Tuple[int, int]] = set()
        stack = [(start_x, start_y)]

        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if not (0 <= x < grid.width and 0 <= y < grid.height):
                continue

            cell = grid.get(x, y)
            if (cell.char or ' ') != target_char:
                continue

            visited.add((x, y))
            cell.char = fill_char
            cell.fg_color = self.current_fg
            cell.bg_color = self.current_bg
            filled += 1

            # Add neighbors
            stack.extend([(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)])

        return filled

    # ── Line Drawing ──────────────────────────────────────────

    def draw_line(self, x1: int, y1: int, x2: int, y2: int) -> int:
        """
        Draw a line using Bresenham's algorithm.
        Returns the number of cells drawn.
        """
        self._push_history(f"Line from ({x1},{y1}) to ({x2},{y2})")
        return self._bresenham_line(x1, y1, x2, y2)

    def _bresenham_line(self, x1: int, y1: int, x2: int, y2: int) -> int:
        """Bresenham line algorithm."""
        drawn = 0
        dx = abs(x2 - x1)
        dy = -abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx + dy

        while True:
            if self.paint(x1, y1):
                drawn += 1
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x1 += sx
            if e2 <= dx:
                err += dx
                y1 += sy

        return drawn

    # ── Rectangle Drawing ─────────────────────────────────────

    def draw_rect(self, x1: int, y1: int, x2: int, y2: int,
                  filled: bool = False) -> int:
        """
        Draw a rectangle outline or filled rectangle.
        Returns the number of cells drawn.
        """
        self._push_history(f"Rect ({x1},{y1})-({x2},{y2}) {'filled' if filled else 'outline'}")

        drawn = 0
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)

        if filled:
            for y in range(y_min, y_max + 1):
                for x in range(x_min, x_max + 1):
                    if self.paint(x, y):
                        drawn += 1
        else:
            # Top and bottom edges
            for x in range(x_min, x_max + 1):
                if self.paint(x, y_min):
                    drawn += 1
                if y_min != y_max and self.paint(x, y_max):
                    drawn += 1
            # Left and right edges (excluding corners)
            for y in range(y_min + 1, y_max):
                if self.paint(x_min, y):
                    drawn += 1
                if x_min != x_max and self.paint(x_max, y):
                    drawn += 1

        return drawn

    # ── Selection ─────────────────────────────────────────────

    def start_selection(self, x: int, y: int,
                        mode: SelectionMode = SelectionMode.REPLACE) -> None:
        """Start a new selection at the given position."""
        self.selection.active = True
        self.selection.start_x = x
        self.selection.start_y = y
        self.selection.end_x = x
        self.selection.end_y = y
        self.selection.mode = mode

    def update_selection(self, x: int, y: int) -> None:
        """Update the selection end point."""
        if self.selection.active:
            self.selection.end_x = x
            self.selection.end_y = y

    def finish_selection(self) -> None:
        """Finalize the current selection."""
        pass  # Selection remains active until cleared

    def clear_selection(self) -> None:
        """Clear the current selection."""
        self.selection.clear()

    def copy_selection(self) -> bool:
        """Copy the selected region to clipboard."""
        if not self.selection.active:
            return False

        region = self.selection.region
        grid = self.active_grid
        if grid is None:
            return False

        self.clipboard.cells.clear()
        for y in range(region.y, region.y + region.height):
            row = []
            for x in range(region.x, region.x + region.width):
                cell = grid.get_safe(x, y)
                if cell:
                    row.append({
                        'char': cell.char,
                        'fg_color': cell.fg_color,
                        'bg_color': cell.bg_color,
                    })
                else:
                    row.append({'char': ' ', 'fg_color': '#ffffff', 'bg_color': '#000000'})
            self.clipboard.cells.append(row)

        self.clipboard.width = region.width
        self.clipboard.height = region.height
        return True

    def cut_selection(self) -> bool:
        """Cut the selected region (copy + clear)."""
        if not self.copy_selection():
            return False

        self._push_history("Cut selection")
        region = self.selection.region
        for y in range(region.y, region.y + region.height):
            for x in range(region.x, region.x + region.width):
                self.erase(x, y)
        return True

    def paste_clipboard(self, x: int, y: int) -> bool:
        """Paste clipboard contents at the given position."""
        if self.clipboard.is_empty:
            return False

        self._push_history(f"Paste at ({x}, {y})")
        for cy, row in enumerate(self.clipboard.cells):
            for cx, cell_data in enumerate(row):
                self._set_cell(
                    x + cx, y + cy,
                    cell_data.get('char', ' '),
                    cell_data.get('fg_color'),
                    cell_data.get('bg_color'),
                )
        return True

    # ── Cursor Movement ───────────────────────────────────────

    def move_cursor(self, dx: int, dy: int) -> None:
        """Move the cursor by delta."""
        grid = self.active_grid
        if grid is None:
            return
        self.cursor.move(dx, dy, grid.size())

    def move_cursor_to(self, x: int, y: int) -> None:
        """Move cursor to absolute position."""
        grid = self.active_grid
        if grid is None:
            return
        self.cursor.x = max(0, min(grid.width - 1, x))
        self.cursor.y = max(0, min(grid.height - 1, y))

    # ── Tool Execution ────────────────────────────────────────

    def apply_tool_at(self, x: int, y: int) -> bool:
        """Apply the current tool at the given position."""
        if self.tool == EditTool.PENCIL:
            self._push_history(f"Paint at ({x}, {y})")
            return self.paint(x, y)
        elif self.tool == EditTool.ERASER:
            self._push_history(f"Erase at ({x}, {y})")
            return self.erase(x, y)
        elif self.tool == EditTool.EYEDROPPER:
            return self._eyedropper(x, y)
        elif self.tool == EditTool.FILL:
            count = self.flood_fill(x, y)
            return count > 0
        return False

    def _eyedropper(self, x: int, y: int) -> bool:
        """Pick character and colors from a cell."""
        cell = self._get_cell(x, y)
        if cell is None or not cell.char:
            return False

        slot = self.palette.get_by_char(cell.char)
        if slot:
            self.current_slot = slot.slot
        if cell.fg_color:
            self.current_fg = cell.fg_color
        if cell.bg_color:
            self.current_bg = cell.bg_color
        return True

    def start_drag(self, x: int, y: int) -> None:
        """Start a drag operation."""
        self._is_dragging = True
        self._drag_start = Coordinate(x, y)

        if self.tool in (EditTool.SELECT,):
            self.start_selection(x, y)
        elif self.tool in (EditTool.LINE, EditTool.RECT):
            self._push_history(f"{self.tool.value} start")

    def update_drag(self, x: int, y: int) -> None:
        """Update an ongoing drag operation."""
        if not self._is_dragging:
            return

        if self.tool == EditTool.SELECT:
            self.update_selection(x, y)
        elif self.tool == EditTool.PENCIL:
            self.paint(x, y)

    def finish_drag(self, x: int, y: int) -> None:
        """Finish a drag operation."""
        if not self._is_dragging:
            return

        if self.tool == EditTool.LINE and self._drag_start:
            self.draw_line(self._drag_start.x, self._drag_start.y, x, y)
        elif self.tool == EditTool.RECT and self._drag_start:
            self.draw_rect(self._drag_start.x, self._drag_start.y, x, y)
        elif self.tool == EditTool.SELECT:
            self.update_selection(x, y)
            self.finish_selection()

        self._is_dragging = False
        self._drag_start = None

    def cancel_drag(self) -> None:
        """Cancel the current drag operation."""
        self._is_dragging = False
        self._drag_start = None

    # ── Grid Operations ───────────────────────────────────────

    def resize_grid(self, new_width: int, new_height: int) -> bool:
        """Resize the active grid."""
        grid = self.active_grid
        if grid is None:
            return False

        self._push_history(f"Resize to {new_width}x{new_height}")

        # Create new grid and copy cells
        new_grid: Grid[Any] = Grid(new_width, new_height)
        for y in range(min(grid.height, new_height)):
            for x in range(min(grid.width, new_width)):
                new_grid.cells[y][x] = grid.cells[y][x].clone()

        # Update the layer's grid
        layer = self.active_layer
        if layer:
            layer.grid = new_grid
        return True

    def clear_grid(self) -> bool:
        """Clear all cells in the active grid."""
        grid = self.active_grid
        if grid is None:
            return False

        self._push_history("Clear grid")
        for y in range(grid.height):
            for x in range(grid.width):
                grid.cells[y][x].char = ' '
                grid.cells[y][x].fg_color = '#ffffff'
                grid.cells[y][x].bg_color = '#000000'
        return True

    def merge_visible_layers(self) -> Optional[Grid]:
        """Merge all visible layers into a single grid."""
        return self.stack.merge_visible()

    # ── Export ────────────────────────────────────────────────

    def to_ascii(self) -> List[str]:
        """Export the active grid as ASCII lines."""
        grid = self.active_grid
        if grid is None:
            return []
        lines = []
        for y in range(grid.height):
            line = ''
            for x in range(grid.width):
                cell = grid.get(x, y)
                line += cell.char if cell.char else ' '
            lines.append(line)
        return lines

    def to_dict(self) -> Dict[str, Any]:
        """Export editor state as a dictionary."""
        grid = self.active_grid
        return {
            'tool': self.tool.value,
            'cursor': {'x': self.cursor.x, 'y': self.cursor.y},
            'current_slot': self.current_slot,
            'current_fg': self.current_fg,
            'current_bg': self.current_bg,
            'selection': {
                'active': self.selection.active,
                'region': {
                    'x': self.selection.region.x,
                    'y': self.selection.region.y,
                    'width': self.selection.region.width,
                    'height': self.selection.region.height,
                } if self.selection.active else None,
            },
            'active_layer': self._active_layer_index,
            'layers': [
                {
                    'name': l.name,
                    'type': l.layer_type.value,
                    'visible': l.visible,
                    'z_index': l.z_index,
                }
                for l in self.stack.layers
            ],
            'history': self.history.to_dict(),
            'grid': grid.to_dict() if grid else None,
        }
