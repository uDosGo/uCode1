"""
NES Dash Theme

Provides the NES.css styled dashboard surface for uCode1.
Integrates with ThinUI and serves as the default menu/dash surface.
"""

from .loader import Theme, ThemeLoader


class NESDashTheme:
    """NES Dashboard Theme Surface."""
    
    def __init__(self):
        """Initialize the NES Dash theme."""
        self.name = "nesdash"
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
    
    def get_navigation(self) -> list:
        """Get the navigation cards."""
        return self.theme.features.get('navigation_cards', [])
    
    def get_quick_actions(self) -> list:
        """Get the quick action buttons."""
        return self.theme.features.get('quick_actions', [])
    
    def render(self) -> str:
        """Render the theme HTML."""
        if self.theme.exists():
            with open(self.theme.full_path, 'r') as f:
                return f.read()
        return "<html><body><h1>NES Dash Theme Not Found</h1></body></html>"
    
    def get_assets(self) -> list:
        """Get list of asset files required by this theme."""
        assets = [
            'fonts/press-start-2p.woff2',
            'nes.css',
        ]
        return assets


# Singleton instance
nesdash = NESDashTheme()
