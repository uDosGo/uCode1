#!/usr/bin/env python3
"""
Nugget System - Python Implementation

This module provides the core functionality for managing Nuggets,
which are binary executable units in the uDos ecosystem.
"""
from .models import Nugget, NuggetMetadata, NuggetResource, NuggetBinaryFormat, NuggetRegistry

__all__ = [
    "Nugget",
    "NuggetMetadata",
    "NuggetResource",
    "NuggetBinaryFormat",
    "NuggetRegistry"
]
