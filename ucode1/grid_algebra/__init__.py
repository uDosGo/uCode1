"""
uCode1 Grid Algebra — Spatial Computing Foundation
===================================================
2D/3D grid algebra system for the uDos ecosystem.

Provides:
- GridCell: Individual cell with position, character, attributes
- GridTransform: Coordinate transformations and projections
- SpatialCodec: Encode/decode spatial data
- LocationStore: Named location registry
- ColourPalette: Colour management for grid displays
- CharacterSet: Character encoding and mapping
- FontResolver: Font resolution for grid rendering
- TeletextPage: Complete teletext page management
- CityRegistry: Named location registry for grid spaces

This is the Python port of the uConnect grid-algebra TypeScript modules.
"""

from .grid_cell import GridCell
from .grid_transform import GridTransform
from .spatial_codec import SpatialCodec
from .location_store import LocationStore
from .colour_palette import ColourPalette
from .character_set import CharacterSet
from .font_resolver import FontResolver
from .teletext_page import TeletextPage
from .city_registry import CityRegistry

__all__ = [
    'GridCell',
    'GridTransform',
    'SpatialCodec',
    'LocationStore',
    'ColourPalette',
    'CharacterSet',
    'FontResolver',
    'TeletextPage',
    'CityRegistry',
]
