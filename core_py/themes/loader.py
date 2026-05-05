"""
Theme Loader Module

Loads and manages uCode1 theme surfaces from the themes directory.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class Theme:
    """Represents a uCode1 theme surface."""
    name: str
    path: str
    theme_type: str
    description: str
    default: bool = False
    features: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def full_path(self) -> Path:
        """Get the full filesystem path to the theme."""
        theme_dir = Path(__file__).parent.parent.parent.parent / "themes"
        return theme_dir / self.path
    
    def exists(self) -> bool:
        """Check if the theme file exists."""
        return self.full_path.exists()


class ThemeLoader:
    """Loads and manages uCode1 themes."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the theme loader."""
        self.config_path = config_path
        self.themes: Dict[str, Theme] = {}
        self._load_config()
    
    def _load_config(self):
        """Load theme configuration from YAML file."""
        if self.config_path:
            config_file = Path(self.config_path)
        else:
            # Default config location: uCode1/themes/config.yaml
            # From uCode1/core_py/themes/loader.py:
            # parent.parent = uCode1/core_py
            # parent.parent.parent = uCode1
            config_file = Path(__file__).parent.parent.parent / "themes" / "config.yaml"
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                
            priority_list = config.get('priority', [])
            if isinstance(priority_list, list):
                for theme_name in priority_list:
                    theme_data = config.get(theme_name, {})
                    if theme_data:
                        self._load_theme(theme_name, theme_data)
            elif isinstance(priority_list, dict):
                for theme_name, theme_data in priority_list.items():
                    self._load_theme(theme_name, theme_data)
            
            # Also load from main themes section
            for theme_name, theme_data in config.items():
                if theme_name not in ['priority', 'assets', 'integration']:
                    self._load_theme(theme_name, theme_data)
    
    def _load_theme(self, name: str, data: dict):
        """Load a single theme from config data."""
        theme = Theme(
            name=name,
            path=data.get('path', f'themes/{name}/index.html'),
            theme_type=data.get('type', 'surface'),
            description=data.get('description', ''),
            default=data.get('default', False),
            features=data.get('features', {})
        )
        self.themes[name] = theme
    
    def get(self, name: str) -> Optional[Theme]:
        """Get a theme by name."""
        return self.themes.get(name)
    
    def list_all(self) -> List[Theme]:
        """List all available themes."""
        return list(self.themes.values())
    
    def get_default(self, theme_type: Optional[str] = None) -> Optional[Theme]:
        """Get the default theme, optionally filtered by type."""
        defaults = [t for t in self.themes.values() if t.default]
        if theme_type:
            defaults = [t for t in defaults if t.theme_type == theme_type]
        return defaults[0] if defaults else None


def get_theme(name: str) -> Optional[Theme]:
    """Get a theme by name using the default loader."""
    loader = ThemeLoader()
    return loader.get(name)


def list_themes() -> List[Theme]:
    """List all available themes."""
    loader = ThemeLoader()
    return loader.list_all()


# Initialize default loader
_default_loader = ThemeLoader()
