"""
uCode1 Theme System

Provides default surface themes for uCode1:
- bbcbasic: BBC BASIC Terminal Surface
- nesdash: NES.css Dashboard Surface
- ceefax: CeefaxThinUI Teletext Surface
"""

from .loader import ThemeLoader, get_theme, list_themes
from .bbcbasic import BBCBasicTheme, bbcbasic
from .nesdash import NESDashTheme, nesdash
from .ceefax import CeefaxThinUITheme, ceefax

__all__ = [
    'ThemeLoader',
    'get_theme',
    'list_themes',
    'BBCBasicTheme',
    'NESDashTheme',
    'CeefaxThinUITheme',
    'bbcbasic',
    'nesdash',
    'ceefax',
]
