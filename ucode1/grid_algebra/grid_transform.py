"""
GridTransform — Coordinate transformations and projections
===========================================================
Handles 2D/3D coordinate transformations, projections,
and spatial calculations for the grid algebra system.
"""

from typing import Tuple, List, Optional
import math


class GridTransform:
    """Coordinate transformations for grid algebra."""

    @staticmethod
    def project_3d_to_2d(x: int, y: int, z: int, viewer_angle: float = 30.0) -> Tuple[float, float]:
        """
        Project a 3D coordinate (x, y, z) to 2D screen space.
        Uses a simple isometric-like projection.
        
        Args:
            x, y, z: 3D coordinates
            viewer_angle: Viewing angle in degrees (default: 30)
            
        Returns:
            (screen_x, screen_y) projected coordinates
        """
        angle_rad = math.radians(viewer_angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)
        
        # Isometric projection
        sx = x - y
        sy = (x + y) * sin_a - z * cos_a
        
        return (sx, sy)

    @staticmethod
    def cube_to_axial(q: int, r: int, s: int) -> Tuple[int, int]:
        """
        Convert cube coordinates (q, r, s) to axial coordinates (q, r).
        Cube constraint: q + r + s = 0
        """
        return (q, r)

    @staticmethod
    def axial_to_cube(q: int, r: int) -> Tuple[int, int, int]:
        """Convert axial coordinates (q, r) to cube coordinates (q, r, s)."""
        s = -q - r
        return (q, r, s)

    @staticmethod
    def hex_distance(a: Tuple[int, int, int], b: Tuple[int, int, int]) -> int:
        """Calculate hex distance between two cube coordinates."""
        return max(
            abs(a[0] - b[0]),
            abs(a[1] - b[1]),
            abs(a[2] - b[2]),
        )

    @staticmethod
    def hex_neighbors(q: int, r: int, s: int) -> List[Tuple[int, int, int]]:
        """Get the 6 neighbors of a hex in cube coordinates."""
        directions = [
            (1, 0, -1), (0, 1, -1), (-1, 1, 0),
            (-1, 0, 1), (0, -1, 1), (1, -1, 0),
        ]
        return [(q + dq, r + dr, s + ds) for dq, dr, ds in directions]

    @staticmethod
    def manhattan_distance(a: Tuple[int, int], b: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two 2D points."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def euclidean_distance(a: Tuple[float, float, float], b: Tuple[float, float, float]) -> float:
        """Calculate Euclidean distance between two 3D points."""
        return math.sqrt(
            (a[0] - b[0]) ** 2 +
            (a[1] - b[1]) ** 2 +
            (a[2] - b[2]) ** 2
        )

    @staticmethod
    def rotate_2d(x: int, y: int, center_x: int, center_y: int, degrees: float) -> Tuple[float, float]:
        """Rotate a 2D point around a center point."""
        rad = math.radians(degrees)
        dx = x - center_x
        dy = y - center_y
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        return (
            center_x + dx * cos_a - dy * sin_a,
            center_y + dx * sin_a + dy * cos_a,
        )

    @staticmethod
    def scale(x: int, y: int, z: int, factor: float) -> Tuple[float, float, float]:
        """Scale coordinates by a factor."""
        return (x * factor, y * factor, z * factor)

    @staticmethod
    def translate(x: int, y: int, z: int, dx: int, dy: int, dz: int) -> Tuple[int, int, int]:
        """Translate coordinates by an offset."""
        return (x + dx, y + dy, z + dz)
