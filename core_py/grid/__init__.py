# uCode1 Python Grid Core
#
# Pure Python grid manipulation and coordinate system utilities.
# Provides functionality for grid-based data structures without Rust dependencies.

"""
Grid Core - Python Implementation

Provides:
- Grid data structures (Grid, GridCell, GridRegion)
- Coordinate systems (Cartesian, Hexagonal, Isometric)
- Grid operations (slice, rotate, flip, transform)
- Spatial indexing and neighbors
- Pathfinding utilities
- Layer/stack management

This is the Python replacement for the Rust grid-core crate.
"""

from .models import (
    Grid,
    GridCell,
    GridRegion,
    GridSize,
    Coordinate,
    CoordSystem,
)
from .operations import (
    slice_grid,
    rotate_grid,
    flip_grid,
    transform_grid,
    merge_grids,
    split_grid,
    resize_grid,
)
from .neighbors import (
    get_neighbors,
    get_neighbors_4way,
    get_neighbors_8way,
    get_hex_neighbors,
    NeighborPattern,
)
from .coords import (
    cartesian_to_offset,
    offset_to_cartesian,
    cube_to_offset,
    offset_to_cube,
    axial_to_cube,
    cube_to_axial,
    CoordinateSystem,
)
from .layers import (
    GridLayer,
    GridStack,
    LayerType,
)
from .pathfinding import (
    GridPath,
    PathNode,
    find_path,
    find_shortest_path,
)
from .exceptions import (
    GridError,
    GridBoundsError,
    CoordinateError,
)

__all__ = [
    # Models
    'Grid',
    'GridCell',
    'GridRegion',
    'GridSize',
    'Coordinate',
    'CoordSystem',
    # Operations
    'slice_grid',
    'rotate_grid',
    'flip_grid',
    'transform_grid',
    'merge_grids',
    'split_grid',
    'resize_grid',
    # Neighbors
    'get_neighbors',
    'get_neighbors_4way',
    'get_neighbors_8way',
    'get_hex_neighbors',
    'NeighborPattern',
    # Coordinate systems
    'cartesian_to_offset',
    'offset_to_cartesian',
    'cube_to_offset',
    'offset_to_cube',
    'axial_to_cube',
    'cube_to_axial',
    'CoordinateSystem',
    # Layers
    'GridLayer',
    'GridStack',
    'LayerType',
    # Pathfinding
    'GridPath',
    'PathNode',
    'find_path',
    'find_shortest_path',
    # Exceptions
    'GridError',
    'GridBoundsError',
    'CoordinateError',
]

__version__ = "0.1.0"
