"""Tests for uCode1 CLI module."""

from ucode1.cli import main


def test_cli_imports():
    """Verify CLI module can be imported without error."""
    from ucode1 import cli
    assert cli is not None


def test_cli_has_main():
    """Verify CLI module exposes a main function."""
    from ucode1.cli import main
    assert callable(main)


def test_cli_has_get_runtime():
    """Verify CLI module exposes _get_runtime helper."""
    from ucode1.cli import _get_runtime
    runtime = _get_runtime()
    # Runtime may not exist yet, but should not crash
    assert runtime is None or hasattr(runtime, 'list_skills')

