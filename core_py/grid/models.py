"""
Grid Core Models

Defines the fundamental data structures for grid operations.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar, Union
from enum import Enum
from .exceptions import GridBoundsError

T = TypeVar('T')


class CoordSystem(Enum):
    """Coordinate system types."""
    CARTESIAN = "cartesian"      # Standard (x, y) with y-down
    CARTESIAN_UP = "cartesian_up"  # Standard (x, y) with y-up
    OFFSET_EVEN = "offset_even"  # Offset coordinates (even rows)
    OFFSET_ODD = "offset_odd"    # Offset coordinates (odd rows)
    CUBE = "cube"                # Cube coordinates (hex grids)
    AXIAL = "axial"              # Axial coordinates (hex grids)


@dataclass
class Coordinate:
    """Represents a coordinate in a grid.
    
    Supports multiple coordinate systems via conversion methods.
    """
    x: int
    y: int
    system: CoordSystem = CoordSystem.CARTESIAN
    z: Optional[int] = None  # For cube coordinates
    
    def __post_init__(self):
        # If using cube coordinates and z is not provided, calculate it
        if self.system == CoordSystem.CUBE and self.z is None:
            self.z = 0
        elif self.system == CoordSystem.CUBE:
            # For cube coordinates: x + y + z = 0
            self.z = -self.x - self.y
    
    @classmethod
    def from_tuple(cls, coords: Tuple[int, int], system: CoordSystem = CoordSystem.CARTESIAN) -> 'Coordinate':
        """Create a coordinate from a tuple."""
        return cls(coords[0], coords[1], system)
    
    @classmethod
    def from_cube(cls, x: int, y: int, z: int) -> 'Coordinate':
        """Create a cube coordinate."""
        return cls(x, y, CoordSystem.CUBE, z)
    
    def to_tuple(self) -> Tuple[int, int]:
        """Convert to (x, y) tuple."""
        return (self.x, self.y)
    
    def to_cube(self) -> Tuple[int, int, int]:
        """Convert to cube coordinates."""
        if self.system == CoordSystem.CUBE:
            return (self.x, self.y, self.z or 0)
        # Convert from other systems to cube
        return self.to_axial().to_cube()
    
    def to_axial(self) -> 'Coordinate':
        """Convert to axial coordinates (for hex grids)."""
        if self.system == CoordSystem.AXIAL:
            return self
        # We'll implement proper conversion in coords module
        return Coordinate(self.x, self.y, CoordSystem.AXIAL)
    
    def __add__(self, other: 'Coordinate') -> 'Coordinate':
        """Add two coordinates."""
        return Coordinate(self.x + other.x, self.y + other.y, self.system)
    
    def __sub__(self, other: 'Coordinate') -> 'Coordinate':
        """Subtract two coordinates."""
        return Coordinate(self.x - other.x, self.y - other.y, self.system)
    
    def __mul__(self, scalar: int) -> 'Coordinate':
        """Multiply coordinate by scalar."""
        return Coordinate(self.x * scalar, self.y * scalar, self.system)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Coordinate):
            return False
        return self.x == other.x and self.y == other.y and self.system == other.system
    
    def __hash__(self) -> int:
        return hash((self.x, self.y, self.system))
    
    def __repr__(self) -> str:
        return f"Coordinate({self.x}, {self.y}, system={self.system.value})"
    
    def distance_to(self, other: 'Coordinate') -> float:
        """Calculate distance to another coordinate."""
        if self.system == CoordSystem.CUBE or other.system == CoordSystem.CUBE:
            # Cube distance for hex grids
            dx = self.x - other.x
            dy = self.y - other.y
            dz = (self.z or 0) - (other.z or 0)
            return (abs(dx) + abs(dy) + abs(dz)) / 2
        else:
            # Euclidean distance for cartesian
            dx = self.x - other.x
            dy = self.y - other.y
            return (dx**2 + dy**2) ** 0.5


@dataclass
class GridSize:
    """Represents the size/dimensions of a grid."""
    width: int
    height: int
    
    @classmethod
    def from_tuple(cls, size: Tuple[int, int]) -> 'GridSize':
        """Create from a (width, height) tuple."""
        return cls(size[0], size[1])
    
    def to_tuple(self) -> Tuple[int, int]:
        """Convert to tuple."""
        return (self.width, self.height)
    
    def area(self) -> int:
        """Calculate total number of cells."""
        return self.width * self.height
    
    def __mul__(self, scalar: int) -> 'GridSize':
        """Scale the size."""
        return GridSize(self.width * scalar, self.height * scalar)
    
    def __repr__(self) -> str:
        return f"GridSize({self.width}, {self.height})"


@dataclass
class GridCell(Generic[T]):
    """A single cell in a grid.
    
    Can hold any data type and has metadata for rendering.
    """
    data: Optional[T] = None
    x: int = 0
    y: int = 0
    
    # Rendering metadata
    fg_color: Optional[str] = None
    bg_color: Optional[str] = None
    char: Optional[str] = None
    bold: bool = False
    underline: bool = False
    blink: bool = False
    
    # Semantic metadata
    cell_type: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_empty(self) -> bool:
        """Check if cell has no data."""
        return self.data is None and self.char is None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'data': self.data,
            'x': self.x,
            'y': self.y,
            'fg_color': self.fg_color,
            'bg_color': self.bg_color,
            'char': self.char,
            'bold': self.bold,
            'underline': self.underline,
            'blink': self.blink,
            'cell_type': self.cell_type,
            'tags': self.tags,
            'metadata': self.metadata,
        }
    
    def __repr__(self) -> str:
        data_repr = repr(self.data) if self.data is not None else 'None'
        return f"GridCell({data_repr}, {self.x}, {self.y})"


@dataclass
class GridRegion:
    """A rectangular region within a grid."""
    x: int
    y: int
    width: int
    height: int
    
    @property
    def size(self) -> GridSize:
        """Get the size of this region."""
        return GridSize(self.width, self.height)
    
    @property
    def area(self) -> int:
        """Get the area of this region."""
        return self.width * self.height
    
    def contains(self, coord: Coordinate) -> bool:
        """Check if a coordinate is inside this region."""
        return (self.x <= coord.x < self.x + self.width and
                self.y <= coord.y < self.y + self.height)
    
    def contains_xy(self, x: int, y: int) -> bool:
        """Check if (x, y) is inside this region."""
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)
    
    def iterate(self) -> List[Coordinate]:
        """Iterate over all coordinates in this region."""
        coords = []
        for y in range(self.y, self.y + self.height):
            for x in range(self.x, self.x + self.width):
                coords.append(Coordinate(x, y))
        return coords
    
    def __repr__(self) -> str:
        return f"GridRegion({self.x}, {self.y}, {self.width}x{self.height})"


@dataclass
class Grid(Generic[T]):
    """A 2D grid data structure.
    
    Stores cells in a 2D array with arbitrary data.
    Supports various coordinate systems and operations.
    """
    width: int
    height: int
    cells: List[List[GridCell[T]]] = field(default_factory=list)
    default_cell: Optional[GridCell[T]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize cells if not provided."""
        if not self.cells:
            self.cells = [[self._create_default_cell(x, y) for x in range(self.width)] 
                         for y in range(self.height)]
    
    def _create_default_cell(self, x: int, y: int) -> GridCell[T]:
        """Create a default cell at (x, y)."""
        if self.default_cell:
            return GridCell(
                data=self.default_cell.data,
                x=x,
                y=y,
                fg_color=self.default_cell.fg_color,
                bg_color=self.default_cell.bg_color,
                char=self.default_cell.char,
            )
        return GridCell(x=x, y=y)
    
    def get(self, x: int, y: int) -> GridCell[T]:
        """Get cell at coordinates, raising error if out of bounds."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise GridBoundsError(x, y, self.width, self.height)
        return self.cells[y][x]
    
    def get_safe(self, x: int, y: int, default: Optional[GridCell[T]] = None) -> Optional[GridCell[T]]:
        """Get cell at coordinates, returning None/def if out of bounds."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.cells[y][x]
        return default
    
    def set(self, x: int, y: int, cell: GridCell[T]) -> None:
        """Set cell at coordinates."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise GridBoundsError(x, y, self.width, self.height)
        self.cells[y][x] = cell
        self.cells[y][x].x = x
        self.cells[y][x].y = y
    
    def set_data(self, x: int, y: int, data: T) -> None:
        """Set data at coordinates."""
        cell = self.get(x, y)
        cell.data = data
    
    def __getitem__(self, coord: Union[Coordinate, Tuple[int, int]]) -> GridCell[T]:
        """Get cell using coordinate or tuple."""
        if isinstance(coord, Coordinate):
            return self.get(coord.x, coord.y)
        return self.get(coord[0], coord[1])
    
    def __setitem__(self, coord: Union[Coordinate, Tuple[int, int]], value: T) -> None:
        """Set cell data using coordinate or tuple."""
        if isinstance(coord, Coordinate):
            return self.set_data(coord.x, coord.y, value)
        return self.set_data(coord[0], coord[1], value)
    
    def size(self) -> GridSize:
        """Get the size of this grid."""
        return GridSize(self.width, self.height)
    
    def region(self, x: int, y: int, width: int, height: int) -> 'Grid[T]':
        """Extract a sub-grid region."""
        return slice_grid(self, x, y, width, height)
    
    def iterate(self) -> List[Tuple[int, int, GridCell[T]]]:
        """Iterate over all cells with coordinates."""
        result = []
        for y in range(self.height):
            for x in range(self.width):
                result.append((x, y, self.cells[y][x]))
        return result
    
    def iterate_coords(self) -> List[Coordinate]:
        """Iterate over all coordinates."""
        return [Coordinate(x, y) for y in range(self.height) for x in range(self.width)]
    
    def clear(self, data: Optional[T] = None) -> None:
        """Clear all cells, optionally setting a default data value."""
        for y in range(self.height):
            for x in range(self.width):
                self.cells[y][x].data = data
    
    def clone(self) -> 'Grid[T]':
        """Create a deep copy of this grid."""
        import copy
        return copy.deepcopy(self)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert grid to dictionary."""
        return {
            'width': self.width,
            'height': self.height,
            'cells': [[cell.to_dict() for cell in row] for row in self.cells],
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Grid[Any]':
        """Create grid from dictionary."""
        grid = cls(data['width'], data['height'])
        for y, row in enumerate(data.get('cells', [])):
            for x, cell_data in enumerate(row):
                cell = GridCell(
                    data=cell_data.get('data'),
                    x=x,
                    y=y,
                    fg_color=cell_data.get('fg_color'),
                    bg_color=cell_data.get('bg_color'),
                    char=cell_data.get('char'),
                )
                grid.cells[y][x] = cell
        grid.metadata = data.get('metadata', {})
        return grid
    
    @classmethod
    def from_grid_parser(cls, parsed_grid: Any) -> 'Grid[Any]':
        """Create grid from USXD ASCIIGridParser output."""
        # Import here to avoid circular dependency
        try:
            from ..usxd.grid_parser import ParsedGrid, GridCell as USXDGridCell
            if isinstance(parsed_grid, type(ParsedGrid)):
                # Convert USXD parsed grid to our grid format
                grid = cls(parsed_grid.width, parsed_grid.height)
                for y, row in enumerate(parsed_grid.cells):
                    for x, usxd_cell in enumerate(row):
                        cell = GridCell(
                            data=usxd_cell.char,
                            x=x,
                            y=y,
                            fg_color=getattr(usxd_cell, 'fg_color', None),
                            bg_color=getattr(usxd_cell, 'bg_color', None),
                            char=usxd_cell.char,
                        )
                        grid.cells[y][x] = cell
                return grid
        except ImportError:
            pass
        raise ValueError("Cannot import from grid_parser")
    
    def __repr__(self) -> str:
        return f"Grid({self.width}x{self.height}, cells={self.width * self.height})"
    
    def __len__(self) -> int:
        return self.width * self.height
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Grid):
            return False
        if self.width != other.width or self.height != other.height:
            return False
        for y in range(self.height):
            for x in range(self.width):
                if self.cells[y][x] != other.cells[y][x]:
                    return False
        return True
