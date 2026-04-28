#!/usr/bin/env python3
"""
Relic System - Python Implementation

This module provides the core functionality for managing Relics,
which are binary executable units in the uDos ecosystem.
"""

from .models import Relic, RelicMetadata, RelicResource, RelicBinaryFormat, RelicRegistry

__all__ = [
    "Relic",
    "RelicMetadata",
    "RelicResource",
    "RelicBinaryFormat",
    "RelicRegistry"
]