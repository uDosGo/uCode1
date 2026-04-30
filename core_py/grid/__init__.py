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

from .coords import (
    CoordinateSystem,
    axial_to_cube,
    cartesian_to_offset,
    cube_to_axial,
    cube_to_offset,
    offset_to_cartesian,
    offset_to_cube,
)
from .exceptions import (
    CoordinateError,
    GridBoundsError,
    GridError,
    GridSizeError,
    GridTypeError,
    LayerError,
    PathNotFoundError,
)
from .layers import (
    GridLayer,
    GridStack,
    LayerType,
)
from .models import (
    Coordinate,
    CoordSystem,
    Grid,
    GridCell,
    GridRegion,
    GridSize,
)
from .monodraw import (
    edit_grid_interactive,
    export_grid_to_monopic,
    install_symlink,
    is_monopic_file,
    monopic_to_ascii,
    monopic_to_json,
    open_in_monodraw,
)
from .monodraw import (
    get_cli_path as monodraw_path,
)
from .monodraw import (
    is_available as monodraw_available,
)
from .neighbors import (
    NeighborPattern,
    count_neighbors,
    get_centered_neighbors,
    get_corner_neighbors,
    get_edge_neighbors,
    get_hex_neighbors,
    get_moore_neighborhood,
    get_neighbors,
    get_neighbors_4way,
    get_neighbors_8way,
    get_neighbors_in_grid,
    get_von_neumann_neighborhood,
)
from .operations import (
    flip_grid,
    merge_grids,
    resize_grid,
    rotate_grid,
    slice_grid,
    split_grid,
    transform_grid,
)
from .pathfinding import (
    GridPath,
    PathfindingAlgorithm,
    PathNode,
    find_path,
    find_shortest_path,
    heuristic,
    heuristic_euclidean,
)

__all__ = [
    # Models
    'Grid',
    'GridCell',
    'GridRegion',
    'GridSize',
    'Coordinate',
    'CoordSystem',
    # Monodraw Integration
    'monodraw_available',
    'monodraw_path',
    'is_monopic_file',
    'monopic_to_ascii',
    'monopic_to_json',
    'export_grid_to_monopic',
    'open_in_monodraw',
    'edit_grid_interactive',
    'install_symlink',
    # Operations
    'slice_grid',
    'rotate_grid',
    'rotate_grid_90',
    'rotate_grid_180',
    'flip_grid',
    'flip_grid_horizontal',
    'flip_grid_vertical',
    'transform_grid',
    'merge_grids',
    'split_grid',
    'resize_grid',
    'crop_grid',
    'expand_grid',
    'transpose_grid',
    'map_cells',
    'filter_cells',
    'get_bounds',
    'trim_grid',
    # Neighbors
    'get_neighbors',
    'get_neighbors_4way',
    'get_neighbors_8way',
    'get_hex_neighbors',
    'get_centered_neighbors',
    'get_neighbors_in_grid',
    'get_edge_neighbors',
    'get_corner_neighbors',
    'count_neighbors',
    'get_moore_neighborhood',
    'get_von_neumann_neighborhood',
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
    'PathfindingAlgorithm',
    'heuristic',
    'heuristic_euclidean',
    # Exceptions
    'GridError',
    'GridBoundsError',
    'CoordinateError',
    'GridSizeError',
    'GridTypeError',
    'LayerError',
    'PathNotFoundError',
]

__version__ = "0.1.0"
