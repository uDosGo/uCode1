"""
SKIN — State Kernel Injection
==============================
Injects state changes into BBCSDL runtime via the BBCSDLBridge.
Replaces the old interpreter-based SKIN with BBCSDL-native injection.

Usage:
    injector = SKINInjector()
    injector.set_variable("player_x", 100)
    injector.set_variable("player_y", 200)
    injector.remap_palette({"red": "blue", "green": "yellow"})
"""

from typing import Any, Dict, Optional
from .bbcsdl_bridge import BBCSDLBridge


class SKINInjector:
    """Inject state changes into BBCSDL runtime"""
    
    def __init__(self, bridge: Optional[BBCSDLBridge] = None):
        self.bridge = bridge or BBCSDLBridge()
        self._started = False
    
    def ensure_running(self) -> None:
        if not self._started:
            self.bridge.start()
            self._started = True
    
    def set_variable(self, name: str, value: Any) -> None:
        """Set a BBC BASIC variable"""
        self.ensure_running()
        self.bridge.set_variable(name, value)
    
    def set_variables(self, vars: Dict[str, Any]) -> None:
        """Set multiple variables at once"""
        self.ensure_running()
        for name, value in vars.items():
            self.bridge.set_variable(name, value)
    
    def call_procedure(self, name: str, *args) -> str:
        """Call a BBC BASIC procedure"""
        self.ensure_running()
        return self.bridge.call_procedure(name, *args)
    
    def remap_palette(self, mapping: Dict[str, str]) -> None:
        """Remap teletext palette colours"""
        self.ensure_running()
        self.bridge.install_library("mode7lib")
        for old_colour, new_colour in mapping.items():
            self.bridge.call_procedure(
                "PROC_mode7_remap",
                old_colour, new_colour
            )
    
    def inject_code(self, code: str) -> str:
        """Inject and execute arbitrary BBC BASIC code"""
        self.ensure_running()
        return self.bridge.execute(code)
    
    def close(self) -> None:
        if self._started:
            self.bridge.close()
            self._started = False
    
    def __enter__(self):
        self.ensure_running()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
