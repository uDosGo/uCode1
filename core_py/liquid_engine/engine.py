"""
Liquid template engine wrapper.

Provides a unified interface for rendering Liquid templates
with data from uCode1 subsystems.

Uses liquidpy (https://github.com/sauljabin/liquidpy) under the hood.
"""

import os
from typing import Any, Dict, List, Optional

try:
    from liquid import Liquid
    HAS_LIQUID = True
except ImportError:
    HAS_LIQUID = False


class LiquidEngine:
    """Liquid template engine for uCode1."""

    def __init__(self, template_dirs: Optional[List[str]] = None):
        """
        Initialize the Liquid engine.

        Args:
            template_dirs: List of directories to search for templates.
                          Defaults to ~/.udos/templates/ and ./templates/
        """
        self.template_dirs = template_dirs or self._default_dirs()

    def _default_dirs(self) -> List[str]:
        """Get default template directories."""
        dirs = []
        # User-level templates
        user_dir = os.path.expanduser("~/.udos/templates")
        if os.path.isdir(user_dir):
            dirs.append(user_dir)
        # Project-level templates
        local_dir = os.path.join(os.getcwd(), "templates")
        if os.path.isdir(local_dir):
            dirs.append(local_dir)
        return dirs

    def render(
        self,
        template_source: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render a Liquid template string with the given data.

        Args:
            template_source: Liquid template string.
            data: Dictionary of variables to inject.

        Returns:
            Rendered string output.

        Raises:
            RuntimeError: If liquidpy is not installed or rendering fails.
        """
        if not HAS_LIQUID:
            raise ImportError(
                "liquidpy is not installed. "
                "Run: pip install liquidpy"
            )
        try:
            engine = Liquid(template_source, from_file=False)
            return engine.render(**(data or {}))
        except Exception as e:
            raise RuntimeError(f"Liquid render failed: {e}") from e

    def render_file(
        self,
        template_name: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Render a template file with the given data.

        Searches template_dirs for the named file.

        Args:
            template_name: Name of the template file (e.g. "greeting.liquid").
            data: Dictionary of variables to inject.

        Returns:
            Rendered string output.
        """
        if not HAS_LIQUID:
            raise ImportError(
                "liquidpy is not installed. "
                "Run: pip install liquidpy"
            )
        # Search template directories for the file
        for directory in self.template_dirs:
            path = os.path.join(directory, template_name)
            if os.path.isfile(path):
                try:
                    engine = Liquid(path, from_file=True)
                    return engine.render(**(data or {}))
                except Exception as e:
                    raise RuntimeError(
                        f"Liquid render failed for {path}: {e}"
                    ) from e
        raise FileNotFoundError(
            f"Template '{template_name}' not found in {self.template_dirs}"
        )

    def render_snack(
        self,
        template_source: str,
        snack_data: Dict[str, Any],
    ) -> str:
        """
        Render a Liquid template with snack execution data.

        The snack_data dict should contain:
            - name: Snack name
            - output: Snack execution output
            - status: Execution status (success/error)
            - duration: Execution time in seconds
            - metadata: Any additional snack metadata

        Args:
            template_source: Liquid template string.
            snack_data: Snack execution data.

        Returns:
            Rendered string output.
        """
        return self.render(template_source, {"snack": snack_data})

    def render_binder(
        self,
        template_source: str,
        binder_data: Dict[str, Any],
    ) -> str:
        """
        Render a Liquid template with binder state data.

        Args:
            template_source: Liquid template string.
            binder_data: Binder state data.

        Returns:
            Rendered string output.
        """
        return self.render(template_source, {"binder": binder_data})

    def render_relic(
        self,
        template_source: str,
        relic_data: Dict[str, Any],
    ) -> str:
        """
        Render a Liquid template with relic data.

        Args:
            template_source: Liquid template string.
            relic_data: Relic data.

        Returns:
            Rendered string output.
        """
        return self.render(template_source, {"relic": relic_data})
