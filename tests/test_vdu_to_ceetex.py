"""
Tests for VDU-to-CEETEX teletext conversion.

Tests the VDU bridge, teletext grid, and colour mapping components
of the uCode1 + CEETEX integration.
"""

import pytest
from ucode1.ceefax.vdu_bridge import CeefaxVDUBridge
from ucode1.ceefax.bridge import (
    TeletextGrid, TeletextCell, TeletextColour,
    GameToTeletextBridge, ColourMapper,
)


class TestTeletextGrid:
    """Tests for the TeletextGrid class"""

    def test_grid_dimensions(self):
        """Grid should be 40x25"""
        grid = TeletextGrid()
        assert grid.COLS == 40
        assert grid.ROWS == 25
        assert len(grid.cells) == 25
        assert len(grid.cells[0]) == 40

    def test_clear(self):
        """Clear should reset all cells"""
        grid = TeletextGrid()
        grid.set_cell(0, 0, "X", TeletextColour.RED, TeletextColour.WHITE)
        grid.clear()
        assert grid.cells[0][0].char == " "
        assert grid.cells[0][0].foreground == TeletextColour.WHITE
        assert grid.cells[0][0].background == TeletextColour.BLACK

    def test_set_cell(self):
        """Set cell should update character and attributes"""
        grid = TeletextGrid()
        grid.set_cell(5, 10, "A", TeletextColour.RED, TeletextColour.BLUE, True)
        cell = grid.cells[5][10]
        assert cell.char == "A"
        assert cell.foreground == TeletextColour.RED
        assert cell.background == TeletextColour.BLUE
        assert cell.bold is True

    def test_set_cell_out_of_bounds(self):
        """Setting a cell outside grid bounds should be ignored"""
        grid = TeletextGrid()
        grid.set_cell(99, 99, "X")  # Should not raise
        assert grid.cells[0][0].char == " "

    def test_write_text(self):
        """Write text should populate cells in sequence"""
        grid = TeletextGrid()
        grid.write_text("HELLO", row=0, col=0)
        assert grid.cells[0][0].char == "H"
        assert grid.cells[0][1].char == "E"
        assert grid.cells[0][2].char == "L"
        assert grid.cells[0][3].char == "L"
        assert grid.cells[0][4].char == "O"

    def test_write_text_newline(self):
        """Newline should advance to next row"""
        grid = TeletextGrid()
        grid.write_text("AB\nCD", row=0, col=0)
        assert grid.cells[0][0].char == "A"
        assert grid.cells[0][1].char == "B"
        assert grid.cells[1][0].char == "C"
        assert grid.cells[1][1].char == "D"

    def test_write_text_wraps_at_40_cols(self):
        """Text should wrap at column 40"""
        grid = TeletextGrid()
        grid.write_text("X" * 45, row=0, col=0)
        assert grid.cells[0][39].char == "X"
        assert grid.cells[1][0].char == "X"
        assert grid.cells[1][4].char == "X"

    def test_to_ansi(self):
        """to_ansi should produce valid ANSI output"""
        grid = TeletextGrid()
        grid.set_cell(0, 0, "A", TeletextColour.RED)
        ansi = grid.to_ansi()
        assert "\x1b[31m" in ansi  # Red foreground
        assert "A" in ansi

    def test_to_html(self):
        """to_html should produce valid HTML"""
        grid = TeletextGrid()
        grid.set_cell(0, 0, "A", TeletextColour.RED)
        html = grid.to_html("Test")
        assert "<!DOCTYPE html>" in html
        assert "Test" in html
        assert "#FF0000" in html  # Red


class TestColourMapper:
    """Tests for the ColourMapper class"""

    def test_from_ansi_sgr(self):
        """ANSI SGR codes should map to teletext colours"""
        assert ColourMapper.from_ansi_sgr(31) == TeletextColour.RED
        assert ColourMapper.from_ansi_sgr(32) == TeletextColour.GREEN
        assert ColourMapper.from_ansi_sgr(34) == TeletextColour.BLUE
        assert ColourMapper.from_ansi_sgr(37) == TeletextColour.WHITE

    def test_from_rgb_hex(self):
        """RGB hex should map to nearest teletext colour"""
        assert ColourMapper.from_rgb_hex("#FF0000") == TeletextColour.RED
        assert ColourMapper.from_rgb_hex("#00FF00") == TeletextColour.GREEN
        assert ColourMapper.from_rgb_hex("#0000FF") == TeletextColour.BLUE
        assert ColourMapper.from_rgb_hex("#000000") == TeletextColour.BLACK

    def test_from_rgb_hex_invalid(self):
        """Invalid hex should default to white"""
        assert ColourMapper.from_rgb_hex("not-a-color") == TeletextColour.WHITE
        assert ColourMapper.from_rgb_hex("#GGGGGG") == TeletextColour.WHITE

    def test_from_name(self):
        """Named colours should map correctly"""
        assert ColourMapper.from_name("red") == TeletextColour.RED
        assert ColourMapper.from_name("green") == TeletextColour.GREEN
        assert ColourMapper.from_name("blue") == TeletextColour.BLUE
        assert ColourMapper.from_name("orange") == TeletextColour.YELLOW
        assert ColourMapper.from_name("purple") == TeletextColour.MAGENTA

    def test_from_name_case_insensitive(self):
        """Named colour lookup should be case-insensitive"""
        assert ColourMapper.from_name("RED") == TeletextColour.RED
        assert ColourMapper.from_name("Blue") == TeletextColour.BLUE


class TestGameToTeletextBridge:
    """Tests for the GameToTeletextBridge class"""

    def test_initialization(self):
        """Bridge should initialize with empty grid"""
        bridge = GameToTeletextBridge()
        assert bridge.grid is not None
        assert bridge.grid.cells[0][0].char == " "

    def test_process_text(self):
        """Process text should render to grid"""
        bridge = GameToTeletextBridge()
        bridge.process_text("TEST", row=0, col=0)
        assert bridge.grid.cells[0][0].char == "T"
        assert bridge.grid.cells[0][1].char == "E"
        assert bridge.grid.cells[0][2].char == "S"
        assert bridge.grid.cells[0][3].char == "T"

    def test_process_text_with_colour(self):
        """Process text with colour should set attributes"""
        bridge = GameToTeletextBridge()
        bridge.process_text("RED", row=0, col=0, fg=TeletextColour.RED)
        assert bridge.grid.cells[0][0].foreground == TeletextColour.RED

    def test_process_ansi(self):
        """ANSI escape sequences should be parsed"""
        bridge = GameToTeletextBridge()
        bridge.process_ansi("\x1b[31mRED\x1b[32mGREEN")
        # After processing, grid should have coloured text
        assert bridge.grid.cells[0][0].char == "R"
        assert bridge.grid.cells[0][3].char == "G"

    def test_process_ascii_art(self):
        """ASCII art should be rendered to grid"""
        bridge = GameToTeletextBridge()
        bridge.process_ascii_art("+--+\n|  |\n+--+")
        assert bridge.grid.cells[0][0].char == "+"
        assert bridge.grid.cells[0][1].char == "-"
        assert bridge.grid.cells[1][0].char == "|"

    def test_process_box(self):
        """Box drawing should create borders"""
        bridge = GameToTeletextBridge()
        bridge.process_box(0, 0, 10, 5, title="BOX")
        assert bridge.grid.cells[0][0].char == "+"
        assert bridge.grid.cells[0][9].char == "+"
        assert bridge.grid.cells[4][0].char == "+"
        assert bridge.grid.cells[4][9].char == "+"
        assert bridge.grid.cells[1][0].char == "|"

    def test_clear(self):
        """Clear should reset the grid"""
        bridge = GameToTeletextBridge()
        bridge.process_text("SOMETHING", row=0, col=0)
        bridge.clear()
        assert bridge.grid.cells[0][0].char == " "

    def test_get_grid_data(self):
        """get_grid_data should return structured data"""
        bridge = GameToTeletextBridge()
        bridge.set_title("Test", "Subtitle")
        data = bridge.get_grid_data()
        assert data["cols"] == 40
        assert data["rows"] == 25
        assert data["title"] == "Test"
        assert data["subtitle"] == "Subtitle"
        assert len(data["cells"]) == 25
        assert len(data["cells"][0]) == 40


class TestCeefaxVDUBridge:
    """Tests for the CeefaxVDUBridge class"""

    def test_initialization(self):
        """Bridge should initialize with default page"""
        bridge = CeefaxVDUBridge()
        assert bridge.get_page_number() == 500
        assert bridge.enabled is True

    def test_set_page_number(self):
        """Setting page number should update current page"""
        bridge = CeefaxVDUBridge()
        bridge.set_page_number(600)
        assert bridge.get_page_number() == 600

    def test_write(self):
        """Write should buffer text"""
        bridge = CeefaxVDUBridge()
        bridge.write("HELLO")
        assert len(bridge._buffer) > 0

    def test_flush(self):
        """Flush should render buffered text to grid"""
        bridge = CeefaxVDUBridge()
        bridge.write("TEST")
        grid = bridge.flush()
        assert grid is not None
        assert grid.cells[0][0].char == "T"

    def test_clear(self):
        """Clear should reset grid and buffer"""
        bridge = CeefaxVDUBridge()
        bridge.write("SOMETHING")
        bridge.flush()
        bridge.clear()
        assert len(bridge._buffer) == 0

    def test_enable_disable(self):
        """Enable/disable should control capture"""
        bridge = CeefaxVDUBridge()
        assert bridge.enabled is True
        bridge.disable()
        assert bridge.enabled is False
        bridge.enable()
        assert bridge.enabled is True

    def test_list_pages(self):
        """List pages should return page info"""
        bridge = CeefaxVDUBridge()
        bridge.set_page_number(500)
        bridge.set_page_number(600)
        pages = bridge.list_pages()
        assert len(pages) >= 2
        page_nums = [p["page_number"] for p in pages]
        assert 500 in page_nums
        assert 600 in page_nums

    def test_set_title(self):
        """Set title should update page state"""
        bridge = CeefaxVDUBridge()
        bridge.set_title("My Page", page_number=500)
        state = bridge.get_page_state(500)
        assert state is not None
        assert state.title == "My Page"

    def test_to_html(self):
        """to_html should produce valid HTML"""
        bridge = CeefaxVDUBridge()
        bridge.write("TEST")
        html = bridge.to_html()
        assert "<!DOCTYPE html>" in html

    def test_to_ansi(self):
        """to_ansi should produce valid ANSI"""
        bridge = CeefaxVDUBridge()
        bridge.write("TEST")
        ansi = bridge.to_ansi()
        assert "TEST" in ansi

    def test_get_grid_data(self):
        """get_grid_data should return structured data"""
        bridge = CeefaxVDUBridge()
        bridge.write("TEST")
        data = bridge.get_grid_data()
        assert "page_number" in data
        assert "title" in data
        assert "cells" in data
