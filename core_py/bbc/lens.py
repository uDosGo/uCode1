"""
LENS — Live Extraction of Native State
=======================================
Extracts game state from BBCSDL runtime via the BBCSDLBridge.
Replaces the old interpreter-based LENS with BBCSDL-native extraction.

Usage:
    extractor = Lensextractor()
    state = extractor.capture_full_state()
    print(state["teletext"])
    print(state["sprites"])
"""

import time
from typing import Any, Dict, List, Optional
from .bbcsdl_bridge import BBCSDLBridge, BBCSDLError


class Lensextractor:
    """Extract game state from BBCSDL runtime"""
    
    def __init__(self, bridge: Optional[BBCSDLBridge] = None):
        self.bridge = bridge or BBCSDLBridge()
        self._started = False
    
    def ensure_running(self) -> None:
        """Start BBCSDL if not already running"""
        if not self._started:
            self.bridge.start()
            self._started = True
    
    def capture_teletext_grid(self) -> Dict[str, Any]:
        """Extract MODE 7 teletext screen"""
        self.ensure_running()
        self.bridge.install_library("mode7lib")
        grid = self.bridge.call_function("FN_mode7_get_grid")
        return {
            "type": "teletext",
            "data": grid,
            "timestamp": time.time()
        }
    
    def capture_sprites(self, max_sprites: int = 8) -> List[Dict[str, Any]]:
        """Extract sprite positions (max 8 per layer)"""
        self.ensure_running()
        sprites = []
        for i in range(max_sprites):
            visible = self.bridge.get_variable(f"sprite_visible_{i}")
            if visible:
                sprites.append({
                    "id": i,
                    "x": self.bridge.get_variable(f"sprite_x_{i}"),
                    "y": self.bridge.get_variable(f"sprite_y_{i}"),
                    "frame": self.bridge.get_variable(f"sprite_frame_{i}")
                })
        return sprites
    
    def capture_variables(self, var_names: List[str]) -> Dict[str, Any]:
        """Extract specific variables by name"""
        self.ensure_running()
        result = {}
        for name in var_names:
            try:
                result[name] = self.bridge.get_variable(name)
            except BBCSDLError:
                result[name] = None
        return result
    
    def capture_full_state(self) -> Dict[str, Any]:
        """Capture everything: teletext + sprites + variables"""
        return {
            "teletext": self.capture_teletext_grid(),
            "sprites": self.capture_sprites(),
            "timestamp": time.time()
        }
    
    def close(self) -> None:
        """Shutdown BBCSDL"""
        if self._started:
            self.bridge.close()
            self._started = False
    
    def __enter__(self):
        self.ensure_running()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
