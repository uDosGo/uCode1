"""
Plugin System Exceptions

Defines custom exceptions for the plugin system.
"""


class PluginError(Exception):
    """Base exception for plugin system errors."""
    pass


class PluginNotFoundError(PluginError):
    """Raised when a plugin cannot be found."""
    
    def __init__(self, plugin_id: str, message: str = None):
        self.plugin_id = plugin_id
        self.message = message or f"Plugin '{plugin_id}' not found"
        super().__init__(self.message)


class PluginLoadError(PluginError):
    """Raised when a plugin fails to load."""
    
    def __init__(self, plugin_id: str, error: Exception, message: str = None):
        self.plugin_id = plugin_id
        self.original_error = error
        self.message = message or f"Failed to load plugin '{plugin_id}': {error}"
        super().__init__(self.message)


class PluginCompatibilityError(PluginError):
    """Raised when a plugin is incompatible."""
    
    def __init__(self, plugin_id: str, reason: str):
        self.plugin_id = plugin_id
        self.reason = reason
        self.message = f"Plugin '{plugin_id}' is incompatible: {reason}"
        super().__init__(self.message)


class PluginDisabledError(PluginError):
    """Raised when trying to access a disabled plugin."""
    
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.message = f"Plugin '{plugin_id}' is disabled"
        super().__init__(self.message)


class PluginRegistrationError(PluginError):
    """Raised when plugin registration fails."""
    
    def __init__(self, plugin_id: str, reason: str):
        self.plugin_id = plugin_id
        self.reason = reason
        self.message = f"Failed to register plugin '{plugin_id}': {reason}"
        super().__init__(self.message)


class PluginExecutionError(PluginError):
    """Raised when plugin execution fails."""
    
    def __init__(self, plugin_id: str, error: Exception):
        self.plugin_id = plugin_id
        self.original_error = error
        self.message = f"Plugin '{plugin_id}' execution failed: {error}"
        super().__init__(self.message)
