"""
uCode1 Liquid Template Engine

Provides Liquid template rendering for the uDos ecosystem.
Supports rendering templates with data from snacks, binders, relics,
and other uCode1 subsystems.

Usage:
    from core_py.liquid_engine import LiquidEngine
    engine = LiquidEngine()
    result = engine.render("Hello {{ name }}!", {"name": "World"})
"""

from .engine import LiquidEngine
from .registry import TemplateRegistry

__all__ = ["LiquidEngine", "TemplateRegistry"]
