"""Tests for uCode1 package initialization."""

from ucode1 import __version__


def test_version_exists():
    """Verify package exposes a version string."""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_version_format():
    """Verify version follows semver format."""
    import re
    assert re.match(r'^\d+\.\d+\.\d+', __version__)
