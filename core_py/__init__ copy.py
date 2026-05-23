"""
uCode1 - BASIC-inspired scripting language for uDos

Core Python implementation (no Rust dependencies)
"""

from .cli import main as cli_main
from .main import main
from .snack_cli import main as snack_cli_main

# Lazy imports for modules that may not exist yet
def _lazy_import(name):
    """Import a module lazily, returning None if not available."""
    try:
        return __import__(f"ucode1.{name}", fromlist=[name])
    except ImportError:
        return None

def get_interpreter():
    """Get the Interpreter class (lazy import)."""
    mod = _lazy_import("interpreter")
    return getattr(mod, "Interpreter", None) if mod else None

def get_parser():
    """Get the Parser class (lazy import)."""
    mod = _lazy_import("parser")
    return getattr(mod, "Parser", None) if mod else None

def get_runtime():
    """Get the Runtime class (lazy import)."""
    mod = _lazy_import("runtime")
    return getattr(mod, "Runtime", None) if mod else None

def get_teletext_renderer():
    """Get the PythonTeletextRenderer class (lazy import)."""
    mod = _lazy_import("teletext")
    return getattr(mod, "PythonTeletextRenderer", None) if mod else None

def get_vault():
    """Get the Vault class (lazy import)."""
    mod = _lazy_import("vault")
    return getattr(mod, "Vault", None) if mod else None

__version__ = "0.1.0"
__all__ = ["cli", "main", "snack_cli", "get_interpreter", "get_parser", "get_runtime", "get_teletext_renderer", "get_vault"]
