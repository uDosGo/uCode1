# uCode1 Plugin System
#
# This module provides plugin discovery, loading, and management for uCode1.

"""
Plugin System for uCode1

Provides:
- Plugin discovery from multiple directories
- Plugin metadata parsing (plugin.yaml)
- Plugin version compatibility checking
- Plugin enable/disable functionality
- Plugin registration API

Plugin Structure:
    plugins/
        plugin_name/
            plugin.yaml      # Plugin metadata
            __init__.py      # Plugin entry point
            main.py         # Plugin implementation
            ...
"""

from .discovery import PluginDiscovery, PluginRegistry
from .loader import PluginLoader, PluginWrapper
from .metadata import PluginMetadata, PluginManifest
from .exceptions import (
    PluginError,
    PluginNotFoundError,
    PluginLoadError,
    PluginCompatibilityError,
    PluginDisabledError,
)

__all__ = [
    # Discovery
    'PluginDiscovery',
    'PluginRegistry',
    # Loader
    'PluginLoader',
    'PluginWrapper',
    # Metadata
    'PluginMetadata',
    'PluginManifest',
    # Exceptions
    'PluginError',
    'PluginNotFoundError',
    'PluginLoadError',
    'PluginCompatibilityError',
    'PluginDisabledError',
]

__version__ = "0.1.0"
