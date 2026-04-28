"""
Plugin Loader Module

Loads and manages plugin instances.
"""

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from .metadata import PluginManifest, PluginMetadata
from .discovery import PluginDiscovery, PluginRegistry
from .exceptions import (
    PluginError,
    PluginNotFoundError,
    PluginLoadError,
    PluginCompatibilityError,
    PluginDisabledError,
    PluginExecutionError,
)


class PluginWrapper:
    """
    Wrapper for loaded plugin instances.
    
    Provides a uniform interface for plugin interaction.
    """
    
    def __init__(self, plugin_id: str, plugin_instance: Any, manifest: PluginManifest):
        """
        Initialize plugin wrapper.
        
        Args:
            plugin_id: The ID of the plugin.
            plugin_instance: The loaded plugin module/instance.
            manifest: The plugin manifest.
        """
        self.plugin_id = plugin_id
        self._instance = plugin_instance
        self._manifest = manifest
    
    @property
    def metadata(self) -> PluginManifest:
        """Get the plugin manifest."""
        return self._manifest
    
    def __getattr__(self, name: str) -> Any:
        """Delegate attribute access to the wrapped plugin."""
        return getattr(self._instance, name)
    
    def __repr__(self) -> str:
        return f"PluginWrapper({self.plugin_id!r})"


class PluginLoader:
    """
    Loads plugins from discovered plugin directories.
    """
    
    def __init__(self, discovery: Optional[PluginDiscovery] = None,
                 registry: Optional[PluginRegistry] = None):
        """
        Initialize plugin loader.
        
        Args:
            discovery: PluginDiscovery instance for finding plugins.
            registry: PluginRegistry instance for tracking loaded plugins.
        """
        self.discovery = discovery or PluginDiscovery()
        self.registry = registry or PluginRegistry()
    
    def load(self, plugin_id: str, **kwargs) -> PluginWrapper:
        """
        Load a plugin by ID.
        
        Args:
            plugin_id: The ID of the plugin to load.
            **kwargs: Additional arguments to pass to the plugin.
        
        Returns:
            PluginWrapper containing the loaded plugin.
        
        Raises:
            PluginNotFoundError: If plugin is not found.
            PluginDisabledError: If plugin is disabled.
            PluginLoadError: If plugin fails to load.
            PluginCompatibilityError: If plugin is incompatible.
        """
        # Get plugin manifest
        manifest = self.discovery.get_plugin(plugin_id)
        metadata = manifest.metadata
        
        # Check if enabled
        if not metadata.enabled:
            raise PluginDisabledError(plugin_id)
        
        # Check compatibility
        if not metadata.is_compatible():
            raise PluginCompatibilityError(
                plugin_id,
                f"Requires uCode {metadata.ucode_version}, Python {metadata.python_version}"
            )
        
        # Load the plugin
        try:
            plugin_instance = self._load_plugin_module(manifest)
            wrapper = PluginWrapper(plugin_id, plugin_instance, manifest)
            
            # Register in registry
            self.registry.register(plugin_id, wrapper, manifest)
            
            # Call initialize if it exists
            if hasattr(plugin_instance, 'initialize'):
                plugin_instance.initialize(**kwargs)
            
            return wrapper
        
        except Exception as e:
            raise PluginLoadError(plugin_id, e)
    
    def _load_plugin_module(self, manifest: PluginManifest) -> Any:
        """
        Load the plugin module from its directory.
        
        Args:
            manifest: The plugin manifest.
        
        Returns:
            The loaded plugin module.
        
        Raises:
            PluginLoadError: If module fails to load.
        """
        plugin_path = manifest.path
        entry_point = manifest.metadata.entry_point
        
        # Add plugin directory to sys.path for imports
        plugin_dir_str = str(plugin_path)
        if plugin_dir_str not in sys.path:
            sys.path.insert(0, plugin_dir_str)
        
        # Try to import the entry point
        entry_path = plugin_path / entry_point
        
        if not entry_path.exists():
            # Try __init__.py as fallback
            init_path = plugin_path / "__init__.py"
            if init_path.exists():
                entry_path = init_path
            else:
                # Try main.py as fallback
                main_path = plugin_path / "main.py"
                if main_path.exists():
                    entry_path = main_path
                else:
                    raise PluginLoadError(
                        manifest.metadata.id,
                        Exception(f"Entry point '{entry_point}' not found in plugin directory")
                    )
        
        # Load module from file
        try:
            module_name = f"plugin_{manifest.metadata.id}"
            spec = importlib.util.spec_from_file_location(module_name, entry_path)
            if spec is None:
                raise PluginLoadError(
                    manifest.metadata.id,
                    Exception(f"Cannot create spec for {entry_path}")
                )
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            raise PluginLoadError(manifest.metadata.id, e)
    
    def unload(self, plugin_id: str) -> None:
        """
        Unload a plugin.
        
        Args:
            plugin_id: The ID of the plugin to unload.
        
        Raises:
            PluginNotFoundError: If plugin is not loaded.
        """
        if plugin_id not in self.registry:
            raise PluginNotFoundError(plugin_id)
        
        # Call cleanup if it exists
        try:
            plugin = self.registry.get(plugin_id)
            if hasattr(plugin, 'cleanup'):
                plugin.cleanup()
        except Exception:
            pass  # Ignore cleanup errors
        
        self.registry.unregister(plugin_id)
    
    def reload(self, plugin_id: str, **kwargs) -> PluginWrapper:
        """
        Reload a plugin.
        
        Args:
            plugin_id: The ID of the plugin to reload.
            **kwargs: Additional arguments to pass to the plugin.
        
        Returns:
            New PluginWrapper for the reloaded plugin.
        """
        self.unload(plugin_id)
        return self.load(plugin_id, **kwargs)
    
    def load_all(self, plugin_ids: Optional[list] = None, **kwargs) -> Dict[str, PluginWrapper]:
        """
        Load all or specified plugins.
        
        Args:
            plugin_ids: List of plugin IDs to load. If None, loads all discovered plugins.
            **kwargs: Additional arguments to pass to each plugin.
        
        Returns:
            Dictionary mapping plugin IDs to PluginWrapper instances.
        """
        if plugin_ids is None:
            plugin_ids = self.discovery.get_plugin_ids()
        
        results = {}
        for plugin_id in plugin_ids:
            try:
                results[plugin_id] = self.load(plugin_id, **kwargs)
            except PluginError as e:
                # Skip plugins that fail to load
                print(f"Warning: Failed to load plugin {plugin_id}: {e}")
                continue
        
        return results
    
    def unload_all(self) -> None:
        """Unload all loaded plugins."""
        for plugin_id in list(self.registry.list_loaded()):
            try:
                self.unload(plugin_id)
            except Exception:
                pass  # Ignore unload errors
    
    def call(self, plugin_id: str, method: str, *args, **kwargs) -> Any:
        """
        Call a method on a loaded plugin.
        
        Args:
            plugin_id: The ID of the plugin.
            method: The method name to call.
            *args: Positional arguments for the method.
            **kwargs: Keyword arguments for the method.
        
        Returns:
            The return value from the method call.
        
        Raises:
            PluginNotFoundError: If plugin is not loaded.
            PluginExecutionError: If method call fails.
        """
        plugin = self.registry.get(plugin_id)
        
        if not hasattr(plugin, method):
            raise PluginExecutionError(
                plugin_id,
                Exception(f"Plugin has no method '{method}'")
            )
        
        try:
            return getattr(plugin, method)(*args, **kwargs)
        except Exception as e:
            raise PluginExecutionError(plugin_id, e)
    
    def execute(self, plugin_id: str, command: str, *args, **kwargs) -> Any:
        """
        Execute a command on a plugin.
        
        This is an alias for call() for command-style usage.
        
        Args:
            plugin_id: The ID of the plugin.
            command: The command/method name.
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        
        Returns:
            The result of the command execution.
        """
        return self.call(plugin_id, command, *args, **kwargs)
