"""
Coordinate System Conversions

Provides conversion functions between different coordinate systems.
"""

from typing import Tuple
from .models import Coordinate, CoordSystem


def cartesian_to_offset(coord: Coordinate, even_offset: bool = True) -> Coordinate:
    """Convert Cartesian coordinates to offset coordinates.
    
    Offset coordinates are used for hex grids laid out in rows.
    
    Args:
        coord: Cartesian coordinate
        even_offset: If True, use even-row offset; otherwise odd-row
    
    Returns:
        Offset coordinate
    """
    if coord.system == CoordSystem.OFFSET_EVEN or coord.system == CoordSystem.OFFSET_ODD:
        return coord
    
    if coord.system != CoordSystem.CARTESIAN and coord.system != CoordSystem.CARTESIAN_UP:
        raise ValueError(f"Cannot convert from {coord.system} to offset")
    
    # Default to even offset
    system = CoordSystem.OFFSET_EVEN if even_offset else CoordSystem.OFFSET_ODD
    return Coordinate(coord.x, coord.y, system)


def offset_to_cartesian(coord: Coordinate) -> Coordinate:
    """Convert offset coordinates to Cartesian.
    
    Args:
        coord: Offset coordinate
    
    Returns:
        Cartesian coordinate (y-up)
    """
    if coord.system != CoordSystem.OFFSET_EVEN and coord.system != CoordSystem.OFFSET_ODD:
        if coord.system == CoordSystem.CARTESIAN or coord.system == CoordSystem.CARTESIAN_UP:
            return coord
        raise ValueError(f"Cannot convert from {coord.system} to cartesian")
    
    return Coordinate(coord.x, coord.y, CoordSystem.CARTESIAN_UP)


def cube_to_offset(cube: Coordinate) -> Tuple[Coordinate, Coordinate]:
    """Convert cube coordinates to offset coordinates.
    
    Returns both even and odd offset variants.
    
    Args:
        cube: Cube coordinate (x + y + z = 0)
    
    Returns:
        Tuple of (even_offset, odd_offset) coordinates
    """
    if cube.system != CoordSystem.CUBE:
        raise ValueError(f"Expected cube coordinate, got {cube.system}")
    
    x, y, z = cube.x, cube.y, cube.z or 0
    
    # Even offset: r = x, q = z + (y - (y & 1)) / 2
    even_q = x
    even_r = z + (y + (y & 1)) // 2  # Modified for even offset
    
    # Odd offset: r = x, q = z + (y - (y & 1)) / 2
    odd_q = x
    odd_r = z + (y - (y & 1)) // 2
    
    return (
        Coordinate(even_q, even_r, CoordSystem.OFFSET_EVEN),
        Coordinate(odd_q, odd_r, CoordSystem.OFFSET_ODD)
    )


def offset_to_cube(coord: Coordinate) -> Coordinate:
    """Convert offset coordinates to cube coordinates.
    
    Args:
        coord: Offset coordinate (even or odd)
    
    Returns:
        Cube coordinate
    """
    if coord.system == CoordSystem.CUBE:
        return coord
    
    if coord.system not in [CoordSystem.OFFSET_EVEN, CoordSystem.OFFSET_ODD]:
        raise ValueError(f"Expected offset coordinate, got {coord.system}")
    
    q = coord.x
    r = coord.y
    
    if coord.system == CoordSystem.OFFSET_EVEN:
        # even: s = -q - r, x = q, z = r
        # Basically: x = q, z = r, y = -x - z
        x = q
        z = r - (q + (q & 1)) // 2  # Adjustment for even offset
        y = -x - z
    else:  # OFFSET_ODD
        x = q
        z = r - (q - (q & 1)) // 2  # Adjustment for odd offset
        y = -x - z
    
    return Coordinate(x, y, CoordSystem.CUBE, z)


def axial_to_cube(axial: Coordinate) -> Coordinate:
    """Convert axial coordinates to cube coordinates.
    
    Args:
        axial: Axial coordinate (q, r)
    
    Returns:
        Cube coordinate (q, r, s) where q + r + s = 0
    """
    if axial.system != CoordSystem.AXIAL:
        raise ValueError(f"Expected axial coordinate, got {axial.system}")
    
    q, r = axial.x, axial.y
    s = -q - r
    return Coordinate(q, r, CoordSystem.CUBE, s)


def cube_to_axial(cube: Coordinate) -> Coordinate:
    """Convert cube coordinates to axial coordinates.
    
    Args:
        cube: Cube coordinate
    
    Returns:
        Axial coordinate
    """
    if cube.system != CoordSystem.CUBE:
        return axial_to_cube(cube).to_axial()  # Convert via cube if needed
    
    return Coordinate(cube.x, cube.y, CoordSystem.AXIAL)


class CoordinateSystem:
    """Utility class for coordinate system operations."""
    
    @staticmethod
    def convert(coord: Coordinate, target: CoordSystem) -> Coordinate:
        """Convert a coordinate to a target coordinate system.
        
        Args:
            coord: Source coordinate
            target: Target coordinate system
        
        Returns:
            Converted coordinate
        """
        if coord.system == target:
            return coord
        
        # Conversion chain: Cube is the universal intermediate
        if coord.system == CoordSystem.CUBE:
            if target == CoordSystem.AXIAL:
                return cube_to_axial(coord)
            elif target in [CoordSystem.OFFSET_EVEN, CoordSystem.OFFSET_ODD]:
                result = cube_to_offset(coord)
                if target == CoordSystem.OFFSET_EVEN:
                    return result[0]
                return result[1]
            else:
                return Coordinate(coord.x, coord.y, target)
        
        elif coord.system == CoordSystem.AXIAL:
            cube = axial_to_cube(coord)
            return CoordinateSystem.convert(cube, target)
        
        elif coord.system in [CoordSystem.OFFSET_EVEN, CoordSystem.OFFSET_ODD]:
            cube = offset_to_cube(coord)
            return CoordinateSystem.convert(cube, target)
        
        else:  # Cartesian variants
            if target in [CoordSystem.CARTESIAN, CoordSystem.CARTESIAN_UP]:
                # Keep x the same, flip y if needed
                if (coord.system == CoordSystem.CARTESIAN_UP and target == CoordSystem.CARTESIAN) or \
                   (coord.system == CoordSystem.CARTESIAN and target == CoordSystem.CARTESIAN_UP):
                    return Coordinate(coord.x, -coord.y, target)
                return Coordinate(coord.x, coord.y, target)
            # Convert via cartesian
            cart = Coordinate(coord.x, coord.y, CoordSystem.CARTESIAN_UP)
            return CoordinateSystem.convert(cart, target)
        
        raise ValueError(f"Cannot convert from {coord.system} to {target}")
    
    @staticmethod
    def distance(a: Coordinate, b: Coordinate) -> float:
        """Calculate distance between two coordinates in any system.
        
        Distance is calculated in cube space for hex coordinates,
        or Euclidean for cartesian.
        
        Args:
            a: First coordinate
            b: Second coordinate
        
        Returns:
            Distance between coordinates
        """
        # Convert both to cube for consistent distance calculation
        a_cube = CoordinateSystem.convert(a, CoordSystem.CUBE)
        b_cube = CoordinateSystem.convert(b, CoordSystem.CUBE)
        
        return a_cube.distance_to(b_cube)
