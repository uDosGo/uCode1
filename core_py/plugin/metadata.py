"""
Plugin Metadata Module

Defines the structure and parsing of plugin metadata files (plugin.yaml).
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import yaml
from pathlib import Path


@dataclass
class PluginMetadata:
    """Metadata for a uCode1 plugin."""
    
    # Required fields
    id: str
    name: str
    version: str
    description: str
    author: str
    
    # Optional fields with defaults
    enabled: bool = True
    entry_point: str = "main.py"
    
    # Compatibility
    ucode_version: str = ">=1.0.0"
    python_version: str = ">=3.9"
    
    # Categories and tags
    categories: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)
    
    # Additional metadata
    homepage: Optional[str] = None
    license: Optional[str] = None
    repository: Optional[str] = None
    
    @classmethod
    def from_yaml(cls, yaml_content: str) -> 'PluginMetadata':
        """Parse plugin metadata from YAML content."""
        try:
            data = yaml.safe_load(yaml_content)
            return cls(**data)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in plugin metadata: {e}")
        except TypeError as e:
            raise ValueError(f"Missing required fields in plugin metadata: {e}")
    
    @classmethod
    def from_file(cls, path: Path) -> 'PluginMetadata':
        """Parse plugin metadata from a YAML file."""
        with open(path, 'r') as f:
            content = f.read()
        return cls.from_yaml(content)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'enabled': self.enabled,
            'entry_point': self.entry_point,
            'ucode_version': self.ucode_version,
            'python_version': self.python_version,
            'categories': self.categories,
            'tags': self.tags,
            'config': self.config,
            'dependencies': self.dependencies,
            'homepage': self.homepage,
            'license': self.license,
            'repository': self.repository,
        }
    
    def is_compatible(self, ucode_version: str = "1.0.0") -> bool:
        """Check if plugin is compatible with the given uCode version."""
        # Simple version comparison (basic implementation)
        # In production, use packaging.version or similar
        return True  # Assume compatible for now
    
    def __repr__(self) -> str:
        return f"PluginMetadata(id={self.id!r}, name={self.name!r}, version={self.version!r})"


@dataclass
class PluginManifest:
    """Manifest for a plugin directory."""
    
    metadata: PluginMetadata
    path: Path
    is_valid: bool = True
    error: Optional[str] = None
    
    @classmethod
    def from_directory(cls, path: Path) -> Optional['PluginManifest']:
        """Create a plugin manifest from a plugin directory."""
        plugin_yaml = path / "plugin.yaml"
        
        if not plugin_yaml.exists():
            return None
        
        try:
            metadata = PluginMetadata.from_file(plugin_yaml)
            return cls(
                metadata=metadata,
                path=path,
                is_valid=True,
                error=None
            )
        except Exception as e:
            return cls(
                metadata=PluginMetadata(
                    id="",
                    name="",
                    version="",
                    description="",
                    author=""
                ),
                path=path,
                is_valid=False,
                error=str(e)
            )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary."""
        result = self.metadata.to_dict()
        result['path'] = str(self.path)
        result['is_valid'] = self.is_valid
        result['error'] = self.error
        return result
