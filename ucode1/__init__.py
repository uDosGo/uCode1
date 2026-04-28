"""
uCode1 - BASIC-inspired scripting language for uDos

Core Python implementation (no Rust dependencies)
"""

from .interpreter import Interpreter
from .parser import Parser
from .runtime import Runtime
from .teletext import PythonTeletextRenderer
from .vault import Vault

__version__ = "0.1.0"
__all__ = ["Interpreter", "Parser", "Runtime", "PythonTeletextRenderer", "Vault"]