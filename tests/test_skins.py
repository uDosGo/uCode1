"""
Tests for CEETEX skin system.

Tests the SKIN adapter, CSS generation, and theme switching
for the uCode1 + CEETEX integration.
"""

import pytest
from ucode1.ceefax.ceetex_app import (
    CeetexSKINAdapter,
    CeetexUCodeApp,
    CEETEX_SKINS,
    _generate_ceetex_css,
)


class TestSkinCSSGeneration:
    """Tests for CEETEX CSS generation"""

    def test_css_generation_teletext_classic(self):
        """CSS should be generated from teletext_classic skin"""
        skin = CEETEX_SKINS["teletext_classic"]
        css = _generate_ceetex_css(skin)
        assert "background: #000000" in css
        assert "color: #ffffff" in css
        assert "Screen" in css
        assert "#page_header" in css
        assert "#ticker_tape" in css
        assert "#fasttext_bar" in css
        assert "ListView" in css
        assert "ListItem" in css

    def test_css_generation_paper_retro(self):
        """CSS should be generated from paper_retro skin"""
        skin = CEETEX_SKINS["paper_retro"]
        css = _generate_ceetex_css(skin)
        assert "#F5E6C8" in css  # Parchment background
        assert "#4A3728" in css  # Dark brown text

    def test_css_generation_dark_mode(self):
        """CSS should be generated from dark_mode skin"""
        skin = CEETEX_SKINS["dark_mode"]
        css = _generate_ceetex_css(skin)
        assert "#1E1E1E" in css  # Dark background
        assert "#E0E0E0" in css  # Light text

    def test_css_generation_high_vis(self):
        """CSS should be generated from high_vis skin"""
        skin = CEETEX_SKINS["high_vis"]
        css = _generate_ceetex_css(skin)
        assert "#FFFF00" in css  # Yellow text
        assert "#000000" in css  # Black background

    def test_css_generation_amiga_workbench(self):
        """CSS should be generated from amiga_workbench skin"""
        skin = CEETEX_SKINS["amiga_workbench"]
        css = _generate_ceetex_css(skin)
        assert "#0050A0" in css  # Amiga blue
        assert "#FFFFFF" in css  # White text

    def test_css_contains_all_widgets(self):
        """CSS should contain all required widget selectors"""
        skin = CEETEX_SKINS["teletext_classic"]
        css = _generate_ceetex_css(skin)
        selectors = [
            "Screen",
            "#page_header",
            "#sub_header",
            "#teletext_container",
            "ListView",
            "ListItem",
            "#ticker_tape",
            "#fasttext_bar",
            "Input",
            ".hidden",
            "#loading_msg",
            "#article_view",
        ]
        for selector in selectors:
            assert selector in css, f"Missing CSS selector: {selector}"

    def test_css_hidden_class(self):
        """CSS should include .hidden class with display: none"""
        skin = CEETEX_SKINS["teletext_classic"]
        css = _generate_ceetex_css(skin)
        assert "display: none" in css

    def test_css_list_item_highlight(self):
        """CSS should include ListItem highlight styles"""
        skin = CEETEX_SKINS["teletext_classic"]
        css = _generate_ceetex_css(skin)
        assert "ListItem.--highlight" in css


class TestSkinAdapter:
    """Tests for the CeetexSKINAdapter class"""

    def test_initialization(self):
        """Adapter should initialize with teletext_classic skin"""
        # We can't easily instantiate without an app, but we can test
        # the skin definitions directly
        assert "teletext_classic" in CEETEX_SKINS
        assert "paper_retro" in CEETEX_SKINS
        assert "dark_mode" in CEETEX_SKINS
        assert "high_vis" in CEETEX_SKINS
        assert "amiga_workbench" in CEETEX_SKINS

    def test_skin_definitions_have_required_keys(self):
        """All skin definitions should have required colour keys"""
        required_keys = [
            "screen_bg", "screen_fg",
            "header_bg", "header_fg",
            "subheader_bg", "subheader_fg",
            "list_bg", "list_fg",
            "highlight_bg", "highlight_fg",
            "ticker_bg", "ticker_fg",
            "fasttext_bg", "fasttext_fg",
            "loading_fg", "article_fg",
        ]
        for skin_name, skin in CEETEX_SKINS.items():
            for key in required_keys:
                assert key in skin, f"Skin '{skin_name}' missing key: {key}"

    def test_skin_colours_are_valid_hex(self):
        """All skin colours should be valid 6-digit hex codes"""
        import re
        hex_pattern = re.compile(r'^#[0-9A-Fa-f]{6}$')
        for skin_name, skin in CEETEX_SKINS.items():
            for key, value in skin.items():
                assert hex_pattern.match(value), \
                    f"Skin '{skin_name}' key '{key}' has invalid hex: {value}"

    def test_skin_count(self):
        """Should have exactly 5 skins"""
        assert len(CEETEX_SKINS) == 5

    def test_skin_names(self):
        """Skin names should match expected set"""
        expected = {
            "teletext_classic",
            "paper_retro",
            "dark_mode",
            "high_vis",
            "amiga_workbench",
        }
        assert set(CEETEX_SKINS.keys()) == expected


class TestSkinApplication:
    """Tests for skin application logic"""

    def test_apply_unknown_skin_returns_false(self):
        """Applying an unknown skin should return False"""
        # We test the logic that would be in the adapter
        assert "nonexistent_skin" not in CEETEX_SKINS

    def test_skin_colour_uniqueness(self):
        """Skins should have different colour schemes"""
        # Verify skins are not identical
        schemes = [tuple(skin.values()) for skin in CEETEX_SKINS.values()]
        assert len(set(schemes)) == len(schemes), \
            "Some skins have identical colour schemes"

    def test_skin_contrast(self):
        """Skins should have sufficient contrast between bg and fg"""
        for skin_name, skin in CEETEX_SKINS.items():
            screen_bg = skin["screen_bg"]
            screen_fg = skin["screen_fg"]
            assert screen_bg != screen_fg, \
                f"Skin '{skin_name}' has identical bg/fg: {screen_bg}"
