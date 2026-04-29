"""
OK Agent — Local AI assistant for uDos.

A friendly, unassuming helper that runs entirely offline, prioritises user
privacy, and understands the Ceefax library format. Built on TinyLlama first,
phi3:mini for extended stability.
"""

from .cli import main as cli_main
from .orchestrate import OKOrchestrator

__all__ = ["OKOrchestrator", "cli_main"]
