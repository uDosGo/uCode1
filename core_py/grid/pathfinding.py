"""
Grid Pathfinding

Provides pathfinding algorithms for grids (A*, Dijkstra, BFS).
"""

import heapq
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Generic, List, Optional, Set, Tuple, TypeVar
from enum import Enum
from .models import Grid, Coordinate, GridSize
from .neighbors import get_neighbors_4way, get_neighbors_8way, get_neighbors_in_grid, NeighborPattern

T = TypeVar('T')


class PathfindingAlgorithm(Enum):
    """Available pathfinding algorithms."""
    BFS = "bfs"           # Breadth-First Search
    DIJKSTRA = "dijkstra" # Dijkstra's algorithm
    ASTAR = "astar"       # A* algorithm


@dataclass
class PathNode:
    """A node in a path."""
    coordinate: Coordinate
    g_score: float = 0.0    # Cost from start
    h_score: float = 0.0    # Heuristic to goal
    f_score: float = 0.0    # g + h (for A*)
    parent: Optional['PathNode'] = None
    visited: bool = False
    
    @property
    def total_score(self) -> float:
        return self.g_score + self.h_score
    
    def __repr__(self) -> str:
        return f"PathNode({self.coordinate}, g={self.g_score}, h={self.h_score})"
    
    def __lt__(self, other: 'PathNode') -> bool:
        # For priority queue ordering
        return self.f_score < other.f_score


@dataclass
class GridPath:
    """A path through a grid."""
    nodes: List[Coordinate] = field(default_factory=list)
    cost: float = 0.0
    found: bool = False
    
    def __len__(self) -> int:
        return len(self.nodes)
    
    def __iter__(self):
        return iter(self.nodes)
    
    def __getitem__(self, index: int) -> Coordinate:
        return self.nodes[index]
    
    def __repr__(self) -> str:
        return f"GridPath({len(self.nodes)} steps, cost={self.cost}, found={self.found})"
    
    def get_coordinates(self) -> List[Tuple[int, int]]:
        """Get path as list of (x, y) tuples."""
        return [(c.x, c.y) for c in self.nodes]
    
    def get_first(self) -> Optional[Coordinate]:
        """Get the first coordinate."""
        return self.nodes[0] if self.nodes else None
    
    def get_last(self) -> Optional[Coordinate]:
        """Get the last coordinate."""
        return self.nodes[-1] if self.nodes else None


def reconstruct_path(end_node: PathNode) -> List[Coordinate]:
    """Reconstruct path from end node to start.
    
    Args:
        end_node: The end node of the path
    
    Returns:
        List of coordinates from start to end
    """
    path = []
    current = end_node
    while current:
        path.append(current.coordinate)
        current = current.parent
    return path[::-1]  # Reverse to get start -> end


def heuristic(a: Coordinate, b: Coordinate) -> float:
    """Manhattan distance heuristic.
    
    Args:
        a: First coordinate
        b: Second coordinate
    
    Returns:
        Manhattan distance between coordinates
    """
    return abs(a.x - b.x) + abs(a.y - b.y)


def heuristic_euclidean(a: Coordinate, b: Coordinate) -> float:
    """Euclidean distance heuristic.
    
    Args:
        a: First coordinate
        b: Second coordinate
    
    Returns:
        Euclidean distance between coordinates
    """
    import math
    dx = a.x - b.x
    dy = a.y - b.y
    return math.sqrt(dx*dx + dy*dy)


def find_path(grid: Grid[T],
               start: Coordinate,
               goal: Coordinate,
               algorithm: PathfindingAlgorithm = PathfindingAlgorithm.ASTAR,
               neighbor_pattern: NeighborPattern = NeighborPattern.FOUR_WAY,
               cost_func: Callable[[Grid[T], int, int], float] = lambda g, x, y: 1.0,
               heuristic_func: Callable[[Coordinate, Coordinate], float] = heuristic) -> GridPath:
    """Find a path from start to goal on a grid.
    
    Args:
        grid: The grid to search
        start: Starting coordinate
        goal: Goal coordinate
        algorithm: Pathfinding algorithm to use
        neighbor_pattern: Which neighbors to consider
        cost_func: Function to calculate movement cost (grid, x, y) -> cost
        heuristic_func: Heuristic function for A* (a, b) -> estimated cost
    
    Returns:
        GridPath containing the path (or empty if no path found)
    """
    if algorithm == PathfindingAlgorithm.BFS:
        return _find_path_bfs(grid, start, goal, neighbor_pattern, cost_func)
    elif algorithm == PathfindingAlgorithm.DIJKSTRA:
        return _find_path_dijkstra(grid, start, goal, neighbor_pattern, cost_func)
    elif algorithm == PathfindingAlgorithm.ASTAR:
        return _find_path_astar(grid, start, goal, neighbor_pattern, cost_func, heuristic_func)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")


def find_shortest_path(grid: Grid[T],
                        start: Coordinate,
                        goal: Coordinate,
                        **kwargs) -> GridPath:
    """Find the shortest path (alias for find_path with A*).
    
    This is the recommended function for most use cases.
    
    Args:
        grid: The grid to search
        start: Starting coordinate
        goal: Goal coordinate
        **kwargs: Additional arguments for find_path
    
    Returns:
        GridPath containing the shortest path
    """
    return find_path(grid, start, goal, PathfindingAlgorithm.ASTAR, **kwargs)


def _find_path_bfs(grid: Grid[T],
                   start: Coordinate,
                   goal: Coordinate,
                   neighbor_pattern: NeighborPattern,
                   cost_func: Callable[[Grid[T], int, int], float]) -> GridPath:
    """Breadth-First Search pathfinding.
    
    Finds the shortest path in unweighted grids.
    """
    # Check if start or goal are out of bounds
    if not (0 <= start.x < grid.width and 0 <= start.y < grid.height):
        return GridPath(found=False)
    if not (0 <= goal.x < grid.width and 0 <= goal.y < grid.height):
        return GridPath(found=False)
    
    # If start is goal
    if start.x == goal.x and start.y == goal.y:
        return GridPath(nodes=[start], cost=0, found=True)
    
    # BFS queue
    from collections import deque
    queue = deque()
    
    # Create start node
    start_node = PathNode(start, g_score=0, h_score=0)
    queue.append(start_node)
    
    # Visited tracking
    visited: Set[Tuple[int, int]] = set()
    visited.add((start.x, start.y))
    
    # parent tracking for path reconstruction
    parent: Dict[Tuple[int, int], PathNode] = {(start.x, start.y): start_node}
    
    # Direction multipliers for different patterns
    if neighbor_pattern == NeighborPattern.FOUR_WAY:
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    else:  # EIGHT_WAY
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    
    while queue:
        current = queue.popleft()
        
        # Found goal
        if current.coordinate.x == goal.x and current.coordinate.y == goal.y:
            path = reconstruct_path(current)
            return GridPath(nodes=path, cost=current.g_score, found=True)
        
        # Explore neighbors
        for dx, dy in directions:
            nx, ny = current.coordinate.x + dx, current.coordinate.y + dy
            
            # Check bounds
            if not (0 <= nx < grid.width and 0 <= ny < grid.height):
                continue
            
            # Check if visited
            if (nx, ny) in visited:
                continue
            
            # Mark visited
            visited.add((nx, ny))
            
            # Create neighbor node
            cost = cost_func(grid, nx, ny)
            neighbor_node = PathNode(
                coordinate=Coordinate(nx, ny),
                g_score=current.g_score + cost,
                parent=current
            )
            
            parent[(nx, ny)] = neighbor_node
            queue.append(neighbor_node)
    
    # No path found
    return GridPath(found=False)


def _find_path_dijkstra(grid: Grid[T],
                         start: Coordinate,
                         goal: Coordinate,
                         neighbor_pattern: NeighborPattern,
                         cost_func: Callable[[Grid[T], int, int], float]) -> GridPath:
    """Dijkstra's algorithm pathfinding.
    
    Finds shortest path in weighted grids.
    """
    # Check bounds
    if not (0 <= start.x < grid.width and 0 <= start.y < grid.height):
        return GridPath(found=False)
    if not (0 <= goal.x < grid.width and 0 <= goal.y < grid.height):
        return GridPath(found=False)
    
    if start.x == goal.x and start.y == goal.y:
        return GridPath(nodes=[start], cost=0, found=True)
    
    # Priority queue
    open_set = []
    
    # Create start node
    start_node = PathNode(start, g_score=0)
    heapq.heappush(open_set, (start_node.g_score, start_node))
    
    # Visited tracking
    visited: Set[Tuple[int, int]] = set()
    
    # Best scores tracking
    g_scores: Dict[Tuple[int, int], float] = {(start.x, start.y): 0}
    
    # Parent tracking
    parent: Dict[Tuple[int, int], PathNode] = {(start.x, start.y): start_node}
    
    if neighbor_pattern == NeighborPattern.FOUR_WAY:
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    else:
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        # Skip if already visited
        if (current.coordinate.x, current.coordinate.y) in visited:
            continue
        
        # Found goal
        if current.coordinate.x == goal.x and current.coordinate.y == goal.y:
            path = reconstruct_path(current)
            return GridPath(nodes=path, cost=current.g_score, found=True)
        
        visited.add((current.coordinate.x, current.coordinate.y))
        
        # Explore neighbors
        for dx, dy in directions:
            nx, ny = current.coordinate.x + dx, current.coordinate.y + dy
            
            if not (0 <= nx < grid.width and 0 <= ny < grid.height):
                continue
            
            # Calculate tentative g-score
            cost = cost_func(grid, nx, ny)
            tentative_g = current.g_score + cost
            
            # If this path is better
            if (nx, ny) not in g_scores or tentative_g < g_scores[(nx, ny)]:
                g_scores[(nx, ny)] = tentative_g
                
                neighbor_node = PathNode(
                    coordinate=Coordinate(nx, ny),
                    g_score=tentative_g,
                    parent=current
                )
                
                parent[(nx, ny)] = neighbor_node
                heapq.heappush(open_set, (tentative_g, neighbor_node))
    
    return GridPath(found=False)


def _find_path_astar(grid: Grid[T],
                     start: Coordinate,
                     goal: Coordinate,
                     neighbor_pattern: NeighborPattern,
                     cost_func: Callable[[Grid[T], int, int], float],
                     heuristic_func: Callable[[Coordinate, Coordinate], float]) -> GridPath:
    """A* pathfinding algorithm.
    
    Finds shortest path in weighted grids using heuristic.
    """
    # Check bounds
    if not (0 <= start.x < grid.width and 0 <= start.y < grid.height):
        return GridPath(found=False)
    if not (0 <= goal.x < grid.width and 0 <= goal.y < grid.height):
        return GridPath(found=False)
    
    if start.x == goal.x and start.y == goal.y:
        return GridPath(nodes=[start], cost=0, found=True)
    
    # Priority queue
    open_set = []
    
    # Create start node
    start_h = heuristic_func(start, goal)
    start_node = PathNode(start, g_score=0, h_score=start_h, f_score=start_h)
    heapq.heappush(open_set, (start_node.f_score, start_node))
    
    # Tracking dictionaries
    g_scores: Dict[Tuple[int, int], float] = {(start.x, start.y): 0}
    f_scores: Dict[Tuple[int, int], float] = {(start.x, start.y): start_h}
    parent: Dict[Tuple[int, int], PathNode] = {(start.x, start.y): start_node}
    visited: Set[Tuple[int, int]] = set()
    
    if neighbor_pattern == NeighborPattern.FOUR_WAY:
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    else:
        directions = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        # Skip if already visited
        if (current.coordinate.x, current.coordinate.y) in visited:
            continue
        
        # Found goal
        if current.coordinate.x == goal.x and current.coordinate.y == goal.y:
            path = reconstruct_path(current)
            return GridPath(nodes=path, cost=current.g_score, found=True)
        
        visited.add((current.coordinate.x, current.coordinate.y))
        
        # Explore neighbors
        for dx, dy in directions:
            nx, ny = current.coordinate.x + dx, current.coordinate.y + dy
            
            if not (0 <= nx < grid.width and 0 <= ny < grid.height):
                continue
            
            cost = cost_func(grid, nx, ny)
            tentative_g = current.g_score + cost
            
            if (nx, ny) not in g_scores or tentative_g < g_scores[(nx, ny)]:
                g_scores[(nx, ny)] = tentative_g
                
                neighbor_coord = Coordinate(nx, ny)
                neighbor_h = heuristic_func(neighbor_coord, goal)
                neighbor_f = tentative_g + neighbor_h
                
                # Use f_score for priority
                f_scores[(nx, ny)] = neighbor_f
                
                neighbor_node = PathNode(
                    coordinate=neighbor_coord,
                    g_score=tentative_g,
                    h_score=neighbor_h,
                    f_score=neighbor_f,
                    parent=current
                )
                
                parent[(nx, ny)] = neighbor_node
                heapq.heappush(open_set, (neighbor_f, neighbor_node))
    
    return GridPath(found=False)
