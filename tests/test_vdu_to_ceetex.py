"""
Tests for VDU-to-CEETEX teletext conversion.

Tests the VDU bridge, teletext grid, and colour mapping components
of the uCode1 + CEETEX integration.
"""

import pytest

try:
    from ucode1.ceefax.vdu_bridge import CeefaxVDUBridge
    from ucode1.ceefax.bridge import (
        TeletextGrid, TeletextCell, TeletextColour,
        GameToTeletextBridge, ColourMapper,
    )
    HAS_CEETEX = True
except ImportError:
    HAS_CEETEX = False

pytestmark = pytest.mark.skipif(
    not HAS_CEETEX,
    reason="ceefax module not available (requires core_py.ceefax)"
)


class TestTeletextGrid:
    """Tests for the TeletextGrid class"""

    def test_grid_dimensions(self):
        """Grid should be 40x25"""
        if not HAS_CEETEX:
            return
        grid = TeletextGrid()
        assert grid.width == 40
        assert grid.height == 25

    def test_grid_clear(self):
        """Grid should clear all cells"""
        if not HAS_CEETEX:
            return
        grid = TeletextGrid()
        grid.set_cell(0, 0, 'A')
        grid.clear()
        cell = grid.get_cell(0, 0)
        assert cell.char == ' '

    def test_set_get_cell(self):
        """Should set and get cell characters"""
        if not HAS_CEETEX:
            return
        grid = TeletextGrid()
        grid.set_cell(10, 5, 'X')
        cell = grid.get_cell(10, 5)
        assert cell.char == 'X'


class TestTeletextCell:
    """Tests for the TeletextCell class"""

    def test_cell_creation(self):
        """Cell should initialize with default values"""
        if not HAS_CEETEX:
            return
        cell = TeletextCell()
        assert cell.char == ' '
        assert cell.fg == TeletextColour.WHITE
        assert cell.bg == TeletextColour.BLACK

    def test_cell_with_char(self):
        """Cell should accept character"""
        if not HAS_CEETEX:
            return
        cell = TeletextCell(char='A')
        assert cell.char == 'A'


class TestColourMapper:
    """Tests for the ColourMapper class"""

    def test_colour_mapping(self):
        """Should map colours correctly"""
        if not HAS_CEETEX:
            return
        mapper = ColourMapper()
        result = mapper.map_colour(0, 0)
        assert result is not None


class TestGameToTeletextBridge:
    """Tests for the GameToTeletextBridge class"""

    def test_bridge_creation(self):
        """Bridge should initialize"""
        if not HAS_CEETEX:
            return
        bridge = GameToTeletextBridge()
        assert bridge is not None
