"""
Tests for CEETEX skin system.

Tests the SKIN adapter, CSS generation, and theme switching
for the uCode1 + CEETEX integration.
"""

import pytest

try:
    from ucode1.ceefax.ceetex_app import (
        CeetexSKINAdapter,
        CeetexUCodeApp,
        CEETEX_SKINS,
        _generate_ceetex_css,
    )
    HAS_CEETEX = True
except ImportError:
    HAS_CEETEX = False

pytestmark = pytest.mark.skipif(
    not HAS_CEETEX,
    reason="ceefax module not available (requires core_py.ceefax)"
)


class TestSkinCSSGeneration:
    """Tests for CEETEX CSS generation"""

    def test_css_generation_teletext_classic(self):
        """Teletext Classic skin should generate valid CSS."""
        if not HAS_CEETEX:
            return
        css = _generate_ceetex_css("teletext_classic")
        assert css is not None
        assert len(css) > 0

    def test_css_generation_teletext_dark(self):
        """Teletext Dark skin should generate valid CSS."""
        if not HAS_CEETEX:
            return
        css = _generate_ceetex_css("teletext_dark")
        assert css is not None
        assert len(css) > 0

    def test_css_generation_invalid_skin(self):
        """Invalid skin name should raise error."""
        if not HAS_CEETEX:
            return
        with pytest.raises(ValueError):
            _generate_ceetex_css("nonexistent_skin")


class TestCeetexSKINAdapter:
    """Tests for CeetexSKINAdapter"""

    def test_adapter_initialization(self):
        """SKIN adapter should initialize with default skin."""
        if not HAS_CEETEX:
            return
        adapter = CeetexSKINAdapter()
        assert adapter is not None
        assert adapter.current_skin is not None

    def test_skin_switching(self):
        """SKIN adapter should support skin switching."""
        if not HAS_CEETEX:
            return
        adapter = CeetexSKINAdapter()
        result = adapter.set_skin("teletext_dark")
        assert result is True
        assert adapter.current_skin == "teletext_dark"

    def test_skin_list(self):
        """SKIN adapter should list available skins."""
        if not HAS_CEETEX:
            return
        adapter = CeetexSKINAdapter()
        skins = adapter.list_skins()
        assert len(skins) > 0
        assert "teletext_classic" in skins


class TestCeetexUCodeApp:
    """Tests for CeetexUCodeApp"""

    def test_app_initialization(self):
        """UCode app should initialize."""
        if not HAS_CEETEX:
            return
        app = CeetexUCodeApp()
        assert app is not None
