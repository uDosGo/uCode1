"""
Grid Neighbors Module

Provides neighbor finding utilities for different grid types.
"""

from enum import Enum
from typing import List, Optional, Tuple
from .models import Coordinate, CoordSystem, Grid


class NeighborPattern(Enum):
    """Neighborhood patterns for different grid types."""
    FOUR_WAY = "4way"        # Cartesian: up, down, left, right
    EIGHT_WAY = "8way"       # Cartesian: includes diagonals
    SIX_WAY = "6way"        # Hexagonal: six neighbors
    

# Direction vectors for different neighbor patterns
FOUR_WAY_DIRS = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # N, E, S, W
EIGHT_WAY_DIRS = [
    (0, -1), (1, -1), (1, 0), (1, 1),
    (0, 1), (-1, 1), (-1, 0), (-1, -1)
]  # N, NE, E, SE, S, SW, W, NW

# Hexagonal directions (cube coordinates)
HEX_CUBE_DIRS = [
    (1, -1, 0), (1, 0, -1), (0, 1, -1),
    (-1, 1, 0), (-1, 0, 1), (0, -1, 1)
]


def get_neighbors_4way(coord: Coordinate) -> List[Coordinate]:
    """Get 4-way neighbors (cartesian grid).
    
    Returns neighbors: North, East, South, West
    
    Args:
        coord: The origin coordinate
    
    Returns:
        List of neighboring coordinates
    """
    result = []
    for dx, dy in FOUR_WAY_DIRS:
        result.append(Coordinate(coord.x + dx, coord.y + dy, coord.system))
    return result


def get_neighbors_8way(coord: Coordinate) -> List[Coordinate]:
    """Get 8-way neighbors (cartesian grid with diagonals).
    
    Returns neighbors in all 8 directions.
    
    Args:
        coord: The origin coordinate
    
    Returns:
        List of neighboring coordinates
    """
    result = []
    for dx, dy in EIGHT_WAY_DIRS:
        result.append(Coordinate(coord.x + dx, coord.y + dy, coord.system))
    return result


def get_neighbors(coord: Coordinate, pattern: NeighborPattern = NeighborPattern.FOUR_WAY) -> List[Coordinate]:
    """Get neighbors based on pattern.
    
    Args:
        coord: The origin coordinate
        pattern: The neighbor pattern to use
    
    Returns:
        List of neighboring coordinates
    """
    if pattern == NeighborPattern.FOUR_WAY:
        return get_neighbors_4way(coord)
    elif pattern == NeighborPattern.EIGHT_WAY:
        return get_neighbors_8way(coord)
    elif pattern == NeighborPattern.SIX_WAY:
        return get_hex_neighbors(coord)
    else:
        raise ValueError(f"Unknown neighbor pattern: {pattern}")


def get_hex_neighbors(coord: Coordinate) -> List[Coordinate]:
    """Get hexagonal neighbors (6-way).
    
    Assumes cube coordinate system. If coord is not in cube system,
    first converts it.
    
    Args:
        coord: The origin coordinate
    
    Returns:
        List of 6 hexagonal neighboring coordinates
    """
    # Ensure we're working with cube coordinates
    if coord.system != CoordSystem.CUBE:
        # Convert to cube
        cube = coord.to_cube()
        orig_x, orig_y, orig_z = cube
    else:
        orig_x, orig_y, orig_z = coord.x, coord.y, coord.z or 0
    
    result = []
    for dx, dy, dz in HEX_CUBE_DIRS:
        new_x = orig_x + dx
        new_y = orig_y + dy
        new_z = orig_z + dz
        result.append(Coordinate(new_x, new_y, CoordSystem.CUBE, new_z))
    
    return result


def get_centered_neighbors(coord: Coordinate, pattern: NeighborPattern = NeighborPattern.FOUR_WAY) -> List[Coordinate]:
    """Get neighbors including the center coordinate.
    
    Args:
        coord: The origin coordinate
        pattern: The neighbor pattern to use
    
    Returns:
        List of coordinates including center and all neighbors
    """
    neighbors = get_neighbors(coord, pattern)
    return [coord] + neighbors


def get_neighbors_in_grid(grid: Grid, x: int, y: int, 
                           pattern: NeighborPattern = NeighborPattern.FOUR_WAY) -> List[Tuple[int, int]]:
    """Get neighboring coordinates within grid bounds.
    
    Args:
        grid: The grid
        x: X coordinate
        y: Y coordinate
        pattern: The neighbor pattern to use
    
    Returns:
        List of (x, y) tuples for valid neighbors
    """
    coord = Coordinate(x, y)
    neighbors = get_neighbors(coord, pattern)
    
    result = []
    for n in neighbors:
        if 0 <= n.x < grid.width and 0 <= n.y < grid.height:
            result.append((n.x, n.y))
    
    return result


def get_edge_neighbors(grid: Grid, x: int, y: int) -> List[Tuple[int, int]]:
    """Get neighbors that are on the edge of the grid.
    
    Args:
        grid: The grid
        x: X coordinate
        y: Y coordinate
    
    Returns:
        List of (x, y) tuples for edge neighbors
    """
    all_neighbors = get_neighbors_in_grid(grid, x, y, NeighborPattern.EIGHT_WAY)
    edge_neighbors = []
    
    for nx, ny in all_neighbors:
        if nx == 0 or nx == grid.width - 1 or ny == 0 or ny == grid.height - 1:
            edge_neighbors.append((nx, ny))
    
    return edge_neighbors


def get_corner_neighbors(grid: Grid, x: int, y: int) -> List[Tuple[int, int]]:
    """Get neighbors that are in the corners of the grid.
    
    Args:
        grid: The grid
        x: X coordinate
        y: Y coordinate
    
    Returns:
        List of (x, y) tuples for corner neighbors
    """
    all_neighbors = get_neighbors_in_grid(grid, x, y, NeighborPattern.EIGHT_WAY)
    corners = [(0, 0), (grid.width - 1, 0), (0, grid.height - 1), (grid.width - 1, grid.height - 1)]
    
    return [(nx, ny) for nx, ny in all_neighbors if (nx, ny) in corners]


def count_neighbors(grid: Grid, x: int, y: int, 
                     pattern: NeighborPattern = NeighborPattern.FOUR_WAY) -> int:
    """Count valid neighbors for a cell.
    
    Args:
        grid: The grid
        x: X coordinate
        y: Y coordinate
        pattern: The neighbor pattern to use
    
    Returns:
        Number of valid neighbors
    """
    return len(get_neighbors_in_grid(grid, x, y, pattern))


def get_moore_neighborhood(grid: Grid, x: int, y: int, radius: int = 1) -> List[Tuple[int, int]]:
    """Get Moore neighborhood (all cells in square around center).
    
    Moore neighborhood includes all cells within a given radius.
    
    Args:
        grid: The grid
        x: X coordinate
        y: Y coordinate
        radius: Distance from center
    
    Returns:
        List of (x, y) tuples for all cells in the neighborhood
    """
    result = []
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid.width and 0 <= ny < grid.height:
                result.append((nx, ny))
    return result


def get_von_neumann_neighborhood(grid: Grid, x: int, y: int, radius: int = 1) -> List[Tuple[int, int]]:
    """Get von Neumann neighborhood (Manhattan distance <= radius).
    
    Args:
        grid: The grid
        x: X coordinate
        y: Y coordinate
        radius: Maximum Manhattan distance
    
    Returns:
        List of (x, y) tuples for cells within Manhattan distance
    """
    result = []
    for dy in range(-radius, radius + 1):
        remaining = radius - abs(dy)
        for dx in range(-remaining, remaining + 1):
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid.width and 0 <= ny < grid.height:
                result.append((nx, ny))
    return result
