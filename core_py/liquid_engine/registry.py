"""
Template registry for discovering and managing Liquid templates.

Scans configured directories for .liquid template files
and provides listing and lookup functionality.
"""

import os
from typing import Dict, List, Optional


class TemplateRegistry:
    """Registry for discovering and managing Liquid templates."""

    def __init__(self, directories: Optional[List[str]] = None):
        """
        Initialize the template registry.

        Args:
            directories: List of directories to scan for templates.
                        Defaults to ~/.udos/templates/ and ./templates/
        """
        self.directories = directories or self._default_dirs()
        self._cache: Optional[Dict[str, str]] = None

    def _default_dirs(self) -> List[str]:
        """Get default template directories."""
        dirs = []
        user_dir = os.path.expanduser("~/.udos/templates")
        if os.path.isdir(user_dir):
            dirs.append(user_dir)
        local_dir = os.path.join(os.getcwd(), "templates")
        if os.path.isdir(local_dir):
            dirs.append(local_dir)
        return dirs

    def scan(self) -> Dict[str, str]:
        """
        Scan all template directories and return a mapping of
        template names to their file paths.

        Returns:
            Dict mapping template names (without extension) to file paths.
        """
        templates: Dict[str, str] = {}
        for directory in self.directories:
            if not os.path.isdir(directory):
                continue
            for filename in os.listdir(directory):
                if filename.endswith(".liquid"):
                    name = filename[:-7]  # Remove .liquid suffix
                    templates[name] = os.path.join(directory, filename)
        self._cache = templates
        return templates

    def list_templates(self) -> List[Dict[str, str]]:
        """
        List all available templates with metadata.

        Returns:
            List of dicts with 'name', 'path', and 'size' keys.
        """
        templates = self.scan()
        result = []
        for name, path in sorted(templates.items()):
            size = os.path.getsize(path) if os.path.isfile(path) else 0
            result.append({
                "name": name,
                "path": path,
                "size": size,
            })
        return result

    def get_template(self, name: str) -> Optional[str]:
        """
        Get the content of a template by name.

        Args:
            name: Template name (without .liquid extension).

        Returns:
            Template content as string, or None if not found.
        """
        templates = self.scan()
        path = templates.get(name)
        if path and os.path.isfile(path):
            with open(path, "r") as f:
                return f.read()
        return None

    def get_path(self, name: str) -> Optional[str]:
        """
        Get the file path of a template by name.

        Args:
            name: Template name (without .liquid extension).

        Returns:
            Full file path, or None if not found.
        """
        templates = self.scan()
        return templates.get(name)
