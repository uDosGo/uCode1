"""
Grid Core Operations

Provides grid manipulation operations (slice, rotate, flip, transform, etc.).
"""

from typing import Callable, List, Optional, Tuple, TypeVar, Any, Dict
from .models import Grid, GridCell, GridSize, Coordinate, GridRegion
from .exceptions import GridBoundsError, GridError

T = TypeVar('T')


def slice_grid(grid: Grid[T], x: int, y: int, width: int, height: int) -> Grid[T]:
    """Extract a rectangular region from a grid.
    
    Args:
        grid: The source grid
        x: Starting x coordinate
        y: Starting y coordinate
        width: Width of the region
        height: Height of the region
    
    Returns:
        A new grid containing the sliced region
    
    Raises:
        GridBoundsError: If the region is outside grid bounds
    """
    if x < 0 or y < 0:
        raise GridBoundsError(x, y, grid.width, grid.height)
    if x + width > grid.width or y + height > grid.height:
        raise GridBoundsError(x + width - 1, y + height - 1, grid.width, grid.height)
    
    new_grid = Grid(width, height)
    for sy in range(height):
        for sx in range(width):
            new_grid.cells[sy][sx] = grid.cells[y + sy][x + sx].clone() if hasattr(grid.cells[y + sy][x + sx], 'clone') else grid.cells[y + sy][x + sx]
            new_grid.cells[sy][sx].x = sx
            new_grid.cells[sy][sx].y = sy
    
    return new_grid


def rotate_grid_90(grid: Grid[T], clockwise: bool = True) -> Grid[T]:
    """Rotate grid 90 degrees.
    
    Args:
        grid: The grid to rotate
        clockwise: If True, rotate clockwise; otherwise counter-clockwise
    
    Returns:
        A new rotated grid
    """
    new_width = grid.height
    new_height = grid.width
    new_grid = Grid(new_width, new_height)
    
    for y in range(grid.height):
        for x in range(grid.width):
            if clockwise:
                # (x, y) -> (y, width - 1 - x)
                new_x = y
                new_y = grid.width - 1 - x
            else:
                # (x, y) -> (height - 1 - y, x)
                new_x = grid.height - 1 - y
                new_y = x
            
            new_grid.cells[new_y][new_x] = grid.cells[y][x]
            new_grid.cells[new_y][new_x].x = new_x
            new_grid.cells[new_y][new_x].y = new_y
    
    return new_grid


def rotate_grid_180(grid: Grid[T]) -> Grid[T]:
    """Rotate grid 180 degrees.
    
    Args:
        grid: The grid to rotate
    
    Returns:
        A new rotated grid
    """
    new_grid = Grid(grid.width, grid.height)
    
    for y in range(grid.height):
        for x in range(grid.width):
            new_x = grid.width - 1 - x
            new_y = grid.height - 1 - y
            
            new_grid.cells[new_y][new_x] = grid.cells[y][x]
            new_grid.cells[new_y][new_x].x = new_x
            new_grid.cells[new_y][new_x].y = new_y
    
    return new_grid


def rotate_grid(grid: Grid[T], degrees: int) -> Grid[T]:
    """Rotate grid by specified degrees (90, 180, 270).
    
    Args:
        grid: The grid to rotate
        degrees: Rotation degrees (90, 180, 270)
    
    Returns:
        A new rotated grid
    
    Raises:
        GridError: If degrees is not 90, 180, or 270
    """
    if degrees == 90:
        return rotate_grid_90(grid, clockwise=True)
    elif degrees == 180:
        return rotate_grid_180(grid)
    elif degrees == 270:
        return rotate_grid_90(grid, clockwise=False)
    else:
        raise GridError(f"Unsupported rotation: {degrees} degrees. Use 90, 180, or 270.")


def flip_grid_horizontal(grid: Grid[T]) -> Grid[T]:
    """Flip grid horizontally (mirror left-right).
    
    Args:
        grid: The grid to flip
    
    Returns:
        A new flipped grid
    """
    new_grid = Grid(grid.width, grid.height)
    
    for y in range(grid.height):
        for x in range(grid.width):
            new_x = grid.width - 1 - x
            new_grid.cells[y][new_x] = grid.cells[y][x]
            new_grid.cells[y][new_x].x = new_x
            new_grid.cells[y][new_x].y = y
    
    return new_grid


def flip_grid_vertical(grid: Grid[T]) -> Grid[T]:
    """Flip grid vertically (mirror top-bottom).
    
    Args:
        grid: The grid to flip
    
    Returns:
        A new flipped grid
    """
    new_grid = Grid(grid.width, grid.height)
    
    for y in range(grid.height):
        for x in range(grid.width):
            new_y = grid.height - 1 - y
            new_grid.cells[new_y][x] = grid.cells[y][x]
            new_grid.cells[new_y][x].x = x
            new_grid.cells[new_y][x].y = new_y
    
    return new_grid


def flip_grid(grid: Grid[T], axis: str = 'x') -> Grid[T]:
    """Flip grid along specified axis.
    
    Args:
        grid: The grid to flip
        axis: Axis to flip along ('x' for horizontal, 'y' for vertical)
    
    Returns:
        A new flipped grid
    """
    if axis == 'x':
        return flip_grid_horizontal(grid)
    elif axis == 'y':
        return flip_grid_vertical(grid)
    else:
        raise GridError(f"Unknown flip axis: {axis}. Use 'x' or 'y'.")


def transform_grid(grid: Grid[T], 
                   translation: Tuple[int, int] = (0, 0),
                   scale: Tuple[float, float] = (1.0, 1.0)) -> Grid[T]:
    """Apply geometric transformation to grid.
    
    Note: This is a simplified transformation that may change grid dimensions.
    
    Args:
        grid: The grid to transform
        translation: (tx, ty) to translate origins
        scale: (sx, sy) to scale dimensions
    
    Returns:
        A new transformed grid
    """
    import math
    
    new_width = max(1, math.floor(grid.width * scale[0]))
    new_height = max(1, math.floor(grid.height * scale[1]))
    new_grid = Grid(new_width, new_height)
    
    for y in range(new_height):
        for x in range(new_width):
            # Map back to original coordinates
            orig_x = int(x / scale[0]) + translation[0]
            orig_y = int(y / scale[1]) + translation[1]
            
            if 0 <= orig_x < grid.width and 0 <= orig_y < grid.height:
                new_grid.cells[y][x] = grid.cells[orig_y][orig_x]
                new_grid.cells[y][x].x = x
                new_grid.cells[y][x].y = y
    
    return new_grid


def merge_grids(grid1: Grid[T], grid2: Grid[T], 
                offset_x: int = 0, offset_y: int = 0,
                conflict_resolver: Callable[[GridCell[T], GridCell[T]], GridCell[T]] = lambda a, b: b) -> Grid[T]:
    """Merge two grids together, placing grid2 at an offset relative to grid1.
    
    Args:
        grid1: Base grid
        grid2: Grid to merge on top
        offset_x: X offset for grid2
        offset_y: Y offset for grid2
        conflict_resolver: Function to resolve cell conflicts (gets grid1 cell, grid2 cell)
    
    Returns:
        A new merged grid
    """
    new_width = max(grid1.width, offset_x + grid2.width)
    new_height = max(grid1.height, offset_y + grid2.height)
    new_grid = Grid(new_width, new_height)
    
    # Copy grid1
    for y in range(grid1.height):
        for x in range(grid1.width):
            new_grid.cells[y][x] = grid1.cells[y][x]
            new_grid.cells[y][x].x = x
            new_grid.cells[y][x].y = y
    
    # Copy grid2 at offset
    for y in range(grid2.height):
        for x in range(grid2.width):
            nx, ny = offset_x + x, offset_y + y
            if 0 <= nx < new_width and 0 <= ny < new_height:
                if new_grid.cells[ny][nx].data is not None:
                    # Conflict - use resolver
                    new_grid.cells[ny][nx] = conflict_resolver(new_grid.cells[ny][nx], grid2.cells[y][x])
                else:
                    new_grid.cells[ny][nx] = grid2.cells[y][x]
                new_grid.cells[ny][nx].x = nx
                new_grid.cells[ny][nx].y = ny
    
    return new_grid


def split_grid(grid: Grid[T], regions: List[GridRegion]) -> List[Grid[T]]:
    """Split grid into multiple regions.
    
    Args:
        grid: The grid to split
        regions: List of regions to extract
    
    Returns:
        List of grids, one for each region
    """
    return [slice_grid(grid, r.x, r.y, r.width, r.height) for r in regions]


def resize_grid(grid: Grid[T], new_width: int, new_height: int,
                fill: Optional[GridCell[T]] = None) -> Grid[T]:
    """Resize a grid to new dimensions.
    
    Args:
        grid: The grid to resize
        new_width: New width
        new_height: New height
        fill: Cell to fill new areas with (default: empty cell)
    
    Returns:
        A new resized grid
    """
    new_grid = Grid(new_width, new_height)
    
    for y in range(min(grid.height, new_height)):
        for x in range(min(grid.width, new_width)):
            new_grid.cells[y][x] = grid.cells[y][x]
            new_grid.cells[y][x].x = x
            new_grid.cells[y][x].y = y
    
    return new_grid


def crop_grid(grid: Grid[T], region: GridRegion) -> Grid[T]:
    """Crop grid to a region.
    
    Convenience wrapper for slice_grid using GridRegion.
    """
    return slice_grid(grid, region.x, region.y, region.width, region.height)


def expand_grid(grid: Grid[T], padding: int, fill: Optional[GridCell[T]] = None) -> Grid[T]:
    """Expand grid with padding on all sides.
    
    Args:
        grid: The grid to expand
        padding: Number of cells to add on each side
        fill: Cell to fill padding with
    
    Returns:
        A new expanded grid
    """
    new_width = grid.width + 2 * padding
    new_height = grid.height + 2 * padding
    new_grid = Grid(new_width, new_height, default_cell=fill)
    
    for y in range(grid.height):
        for x in range(grid.width):
            new_grid.cells[y + padding][x + padding] = grid.cells[y][x]
            new_grid.cells[y + padding][x + padding].x = x + padding
            new_grid.cells[y + padding][x + padding].y = y + padding
    
    return new_grid


def transpose_grid(grid: Grid[T]) -> Grid[T]:
    """Transpose grid (swap dimensions).
    
    Args:
        grid: The grid to transpose
    
    Returns:
        A new transposed grid
    """
    new_grid = Grid(grid.height, grid.width)
    
    for y in range(grid.height):
        for x in range(grid.width):
            new_grid.cells[x][y] = grid.cells[y][x]
            new_grid.cells[x][y].x = x
            new_grid.cells[x][y].y = y
    
    return new_grid


def map_cells(grid: Grid[T], func: Callable[[GridCell[T]], Any]) -> Grid[Any]:
    """Apply a function to each cell in the grid.
    
    Args:
        grid: The grid to map
        func: Function to apply to each cell
    
    Returns:
        A new grid with transformed cells
    """
    new_grid = Grid(grid.width, grid.height)
    
    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.cells[y][x]
            new_data = func(cell)
            new_grid.cells[y][x] = GridCell(
                data=new_data,
                x=x,
                y=y,
                fg_color=cell.fg_color,
                bg_color=cell.bg_color,
                char=cell.char,
            )
    
    return new_grid


def filter_cells(grid: Grid[T], predicate: Callable[[GridCell[T]], bool]) -> Grid[T]:
    """Filter cells, keeping only those that match the predicate.
    
    Note: This maintain grid structure, setting non-matching cells to empty.
    
    Args:
        grid: The grid to filter
        predicate: Function to test each cell
    
    Returns:
        A new grid with filtered cells
    """
    new_grid = Grid(grid.width, grid.height)
    
    for y in range(grid.height):
        for x in range(grid.width):
            cell = grid.cells[y][x]
            if predicate(cell):
                new_grid.cells[y][x] = cell
                new_grid.cells[y][x].x = x
                new_grid.cells[y][x].y = y
            else:
                new_grid.cells[y][x] = GridCell(x=x, y=y)
    
    return new_grid


def get_bounds(grid: Grid[T]) -> GridRegion:
    """Get the bounds of non-empty cells in the grid.
    
    Args:
        grid: The grid to analyze
    
    Returns:
        GridRegion containing all non-empty cells
    """
    min_x, min_y = grid.width, grid.height
    max_x, max_y = -1, -1
    
    for y in range(grid.height):
        for x in range(grid.width):
            if not grid.cells[y][x].is_empty():
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
    
    if max_x < min_x or max_y < min_y:
        # Empty grid
        return GridRegion(0, 0, 0, 0)
    
    return GridRegion(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)


def trim_grid(grid: Grid[T]) -> Grid[T]:
    """Trim empty borders from grid.
    
    Args:
        grid: The grid to trim
    
    Returns:
        A new trimmed grid
    """
    bounds = get_bounds(grid)
    return slice_grid(grid, bounds.x, bounds.y, bounds.width, bounds.height)
