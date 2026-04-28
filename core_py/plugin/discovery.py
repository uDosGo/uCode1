"""
Plugin Discovery Module

Discovers and manages plugins from multiple directories.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from .metadata import PluginManifest, PluginMetadata
from .exceptions import (
    PluginError,
    PluginNotFoundError,
    PluginLoadError,
    PluginCompatibilityError,
)


class PluginDiscovery:
    """
    Discovers plugins from configured directories.
    
    Plugin directories are searched in order:
    1. User plugins directory (~/.uDos/plugins or similar)
    2. Project plugins directory (./plugins)
    3. System plugins directory
    4. Built-in plugins directory
    """
    
    def __init__(self, plugin_dirs: Optional[List[Path]] = None):
        """
        Initialize plugin discovery.
        
        Args:
            plugin_dirs: List of directories to search for plugins.
                         If None, uses default directories.
        """
        if plugin_dirs is None:
            plugin_dirs = self._get_default_plugin_dirs()
        
        self.plugin_dirs = plugin_dirs
        self._plugins: Optional[Dict[str, PluginManifest]] = None
        self._enabled_plugins: Optional[Set[str]] = None
        self._disabled_plugins: Optional[Set[str]] = None
    
    def _get_default_plugin_dirs(self) -> List[Path]:
        """Get default plugin directories."""
        dirs = []
        
        # User plugins directory
        if "UCODE_PLUGINS" in os.environ:
            user_dir = Path(os.environ["UCODE_PLUGINS"])
        else:
            home = Path.home()
            user_dir = home / ".uDos" / "plugins"
        dirs.append(user_dir)
        
        # Project plugins directory (relative to current working directory)
        project_dir = Path.cwd() / "plugins"
        dirs.append(project_dir)
        
        # System plugins directory
        system_dir = Path("/usr/local/share/uDos/plugins")
        if system_dir.exists():
            dirs.append(system_dir)
        
        # Built-in plugins directory (relative to uCode1)
        builtin_dir = Path(__file__).parent.parent.parent / "plugins"
        dirs.append(builtin_dir)
        
        return dirs
    
    def discover(self, force_refresh: bool = False) -> Dict[str, PluginManifest]:
        """
        Discover all available plugins.
        
        Args:
            force_refresh: If True, re-scan all directories.
        
        Returns:
            Dictionary mapping plugin IDs to PluginManifest objects.
        """
        if self._plugins is not None and not force_refresh:
            return self._plugins
        
        plugins = {}
        seen_ids = set()
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
            
            for plugin_path in plugin_dir.iterdir():
                if not plugin_path.is_dir():
                    continue
                
                manifest = PluginManifest.from_directory(plugin_path)
                if manifest is None or not manifest.is_valid:
                    continue
                
                plugin_id = manifest.metadata.id
                if plugin_id in seen_ids:
                    # Plugin with same ID already found, skip duplicate
                    continue
                
                seen_ids.add(plugin_id)
                plugins[plugin_id] = manifest
        
        self._plugins = plugins
        return plugins
    
    def get_plugin_paths(self) -> List[Path]:
        """
        Get list of all plugin directory paths.
        
        Returns:
            List of Path objects pointing to plugin directories.
        """
        plugins = self.discover()
        return [manifest.path for manifest in plugins.values()]
    
    def get_plugin_ids(self) -> List[str]:
        """
        Get list of all discovered plugin IDs.
        
        Returns:
            List of plugin IDs (strings).
        """
        plugins = self.discover()
        return list(plugins.keys())
    
    def get_plugin(self, plugin_id: str) -> PluginManifest:
        """
        Get a specific plugin by ID.
        
        Args:
            plugin_id: The ID of the plugin to retrieve.
        
        Returns:
            PluginManifest for the requested plugin.
        
        Raises:
            PluginNotFoundError: If plugin is not found.
        """
        plugins = self.discover()
        if plugin_id not in plugins:
            raise PluginNotFoundError(plugin_id)
        return plugins[plugin_id]
    
    def is_plugin_enabled(self, plugin_id: str) -> bool:
        """
        Check if a plugin is enabled.
        
        Args:
            plugin_id: The ID of the plugin to check.
        
        Returns:
            True if plugin is enabled, False otherwise.
        """
        try:
            plugin = self.get_plugin(plugin_id)
            return plugin.metadata.enabled
        except PluginNotFoundError:
            return False
    
    def get_enabled_plugins(self) -> List[str]:
        """
        Get list of enabled plugin IDs.
        
        Returns:
            List of enabled plugin IDs.
        """
        plugins = self.discover()
        return [
            plugin_id for plugin_id, manifest in plugins.items()
            if manifest.metadata.enabled
        ]
    
    def get_disabled_plugins(self) -> List[str]:
        """
        Get list of disabled plugin IDs.
        
        Returns:
            List of disabled plugin IDs.
        """
        plugins = self.discover()
        return [
            plugin_id for plugin_id, manifest in plugins.items()
            if not manifest.metadata.enabled
        ]


class PluginRegistry:
    """
    Registry for loaded plugins.
    
    Maintains a mapping of plugin IDs to loaded plugin instances.
    """
    
    def __init__(self):
        self._registry: Dict[str, Any] = {}
        self._metadata: Dict[str, PluginManifest] = {}
    
    def register(self, plugin_id: str, plugin_instance: Any, manifest: PluginManifest) -> None:
        """
        Register a plugin instance.
        
        Args:
            plugin_id: The ID of the plugin.
            plugin_instance: The loaded plugin instance.
            manifest: The plugin manifest.
        """
        self._registry[plugin_id] = plugin_instance
        self._metadata[plugin_id] = manifest
    
    def unregister(self, plugin_id: str) -> None:
        """
        Unregister a plugin.
        
        Args:
            plugin_id: The ID of the plugin to unregister.
        """
        self._registry.pop(plugin_id, None)
        self._metadata.pop(plugin_id, None)
    
    def get(self, plugin_id: str) -> Any:
        """
        Get a loaded plugin instance.
        
        Args:
            plugin_id: The ID of the plugin.
        
        Returns:
            The plugin instance.
        
        Raises:
            PluginNotFoundError: If plugin is not loaded.
        """
        if plugin_id not in self._registry:
            raise PluginNotFoundError(plugin_id)
        return self._registry[plugin_id]
    
    def get_metadata(self, plugin_id: str) -> PluginManifest:
        """
        Get metadata for a loaded plugin.
        
        Args:
            plugin_id: The ID of the plugin.
        
        Returns:
            The plugin manifest.
        
        Raises:
            PluginNotFoundError: If plugin is not loaded.
        """
        if plugin_id not in self._metadata:
            raise PluginNotFoundError(plugin_id)
        return self._metadata[plugin_id]
    
    def list_loaded(self) -> List[str]:
        """
        List all loaded plugin IDs.
        
        Returns:
            List of loaded plugin IDs.
        """
        return list(self._registry.keys())
    
    def clear(self) -> None:
        """Clear all loaded plugins."""
        self._registry.clear()
        self._metadata.clear()
    
    def __contains__(self, plugin_id: str) -> bool:
        """Check if a plugin is loaded."""
        return plugin_id in self._registry
