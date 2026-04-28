"""
CeefaxThinUI Theme

Provides the Teletext Mode 7 renderer surface for uCode1.
Integrates with MCP and provides NES-style teletext interface.
"""

from .loader import Theme, ThemeLoader


class CeefaxThinUITheme:
    """Ceefax ThinUI Teletext Theme Surface."""
    
    def __init__(self):
        """Initialize the CeefaxThinUI theme."""
        self.name = "ceefax"
        self.loader = ThemeLoader()
        self.theme: Theme = self.loader.get(self.name)
        
        if not self.theme:
            raise RuntimeError(f"Theme '{self.name}' not found in configuration")
    
    def get_path(self) -> str:
        """Get the filesystem path to the theme."""
        return str(self.theme.full_path)
    
    def get_features(self) -> dict:
        """Get the theme features."""
        return self.theme.features
    
    def get_mcp_commands(self) -> list:
        """Get the MCP commands supported by this surface."""
        return self.theme.features.get('mcp_commands', [])
    
    def get_grid_layout(self) -> str:
        """Get the grid layout (e.g., '40x25')."""
        return self.theme.features.get('grid_layout', '40x25')
    
    def render(self) -> str:
        """Render the theme HTML."""
        if self.theme.exists():
            with open(self.theme.full_path, 'r') as f:
                return f.read()
        return "<html><body><h1>CeefaxThinUI Theme Not Found</h1></body></html>"
    
    def get_assets(self) -> list:
        """Get list of asset files required by this theme."""
        # CeefaxThinUI uses pure CSS, minimal assets
        return []


# Singleton instance
ceefax = CeefaxThinUITheme()
