"""
Grid Core Exceptions

Custom exceptions for grid operations.
"""


class GridError(Exception):
    """Base exception for grid operations."""
    pass


class GridBoundsError(GridError):
    """Raised when coordinates are outside grid bounds."""
    
    def __init__(self, x, y, width, height, message=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.message = message or f"Coordinate ({x}, {y}) outside grid bounds ({width}x{height})"
        super().__init__(self.message)


class CoordinateError(GridError):
    """Raised for invalid coordinate operations."""
    
    def __init__(self, coordinate, reason):
        self.coordinate = coordinate
        self.reason = reason
        self.message = f"Invalid coordinate {coordinate}: {reason}"
        super().__init__(self.message)


class GridSizeError(GridError):
    """Raised for invalid grid size operations."""
    pass


class GridTypeError(GridError):
    """Raised for type mismatches in grid operations."""
    pass


class LayerError(GridError):
    """Raised for layer-related errors."""
    pass


class PathNotFoundError(GridError):
    """Raised when pathfinding fails."""
    pass
