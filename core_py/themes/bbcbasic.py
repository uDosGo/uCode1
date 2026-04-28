"""
BBC BASIC Theme

Provides the C64-style BBC BASIC terminal surface integration.
Integrates with the uCode1 BBC BASIC interpreter.
"""

from .loader import Theme, ThemeLoader


class BBCBasicTheme:
    """BBC BASIC Terminal Theme Surface."""
    
    def __init__(self):
        """Initialize the BBC BASIC theme."""
        self.name = "bbcbasic"
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
    
    def get_default_commands(self) -> list:
        """Get the default BBC BASIC commands supported."""
        return self.theme.features.get('interactive_commands', [])
    
    def render(self) -> str:
        """Render the theme HTML."""
        if self.theme.exists():
            with open(self.theme.full_path, 'r') as f:
                return f.read()
        return "<html><body><h1>BBC BASIC Theme Not Found</h1></body></html>"
    
    def get_assets(self) -> list:
        """Get list of asset files required by this theme."""
        # Assets from the theme config
        assets = [
            'C64_User_Mono_v1.0-STYLE.eot',
            'C64_User_Mono_v1.0-STYLE.ttf',
            'C64_User_Mono_v1.0-STYLE.woff',
            'giana.eot',
            'giana.ttf',
            'giana.woff',
            'css.css',
            'prefixfree.min.js',
            'pixelambacht-logo.png',
        ]
        return assets


# Singleton instance
bbcbasic = BBCBasicTheme()
