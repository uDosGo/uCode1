"""Tests for uCode1 Snack CLI module."""

from ucode1.snack_cli import main


def test_snack_cli_imports():
    """Verify Snack CLI module can be imported without error."""
    from ucode1 import snack_cli
    assert snack_cli is not None


def test_snack_cli_has_main():
    """Verify Snack CLI module exposes a main function."""
    from ucode1.snack_cli import main
    assert callable(main)
