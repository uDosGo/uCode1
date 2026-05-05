"""
Page Exporter — single-page and widget export from uCode1 data.

Provides PageExporter for generating standalone HTML pages and
embeddable widget snippets from individual uCode1 components.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .engine import ExportEngine, ExportFormat, ExportOptions


@dataclass
class PageConfig:
    """Configuration for single-page export."""
    output_dir: str = "./dist"
    theme: str = "bbcbasic"
    title: str = "uCode1 Page"
    include_widgets: bool = True
    minify: bool = False
    grid_cols: int = 40
    grid_rows: int = 24


class PageExporter:
    """
    Exports individual uCode1 components as standalone HTML pages
    or embeddable widget snippets.
    """

    def __init__(self, config: Optional[PageConfig] = None):
        self.config = config or PageConfig()

    def export_snack_page(
        self,
        snack_data: Dict[str, Any],
        rendered_content: Optional[str] = None,
    ) -> str:
        """
        Export a single snack as a standalone HTML page.

        Args:
            snack_data: Snack dictionary
            rendered_content: Optional pre-rendered content

        Returns:
            Path to the generated HTML file
        """
        engine = ExportEngine(ExportOptions(
            output_dir=self.config.output_dir,
            format=ExportFormat.SINGLE_PAGE,
            theme=self.config.theme,
            title=f"Snack: {snack_data.get('name', 'Untitled')}",
            include_widgets=self.config.include_widgets,
            include_nav=False,
            minify=self.config.minify,
            grid_cols=self.config.grid_cols,
            grid_rows=self.config.grid_rows,
        ))
        return engine.export_snack(snack_data, rendered_content)

    def export_binder_page(
        self,
        binder_data: Dict[str, Any],
        rendered_entries: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Export a single binder as a standalone HTML page.

        Args:
            binder_data: Binder dictionary
            rendered_entries: Optional dict of entry_id -> rendered HTML

        Returns:
            Path to the generated HTML file
        """
        meta = binder_data.get("metadata", {})
        engine = ExportEngine(ExportOptions(
            output_dir=self.config.output_dir,
            format=ExportFormat.SINGLE_PAGE,
            theme=self.config.theme,
            title=f"Binder: {meta.get('name', 'Untitled')}",
            include_widgets=self.config.include_widgets,
            include_nav=False,
            minify=self.config.minify,
            grid_cols=self.config.grid_cols,
            grid_rows=self.config.grid_rows,
        ))
        return engine.export_binder(binder_data, rendered_entries)

    def export_relic_page(
        self,
        relic_data: Dict[str, Any],
    ) -> str:
        """
        Export a single relic as a standalone HTML page.

        Args:
            relic_data: Relic dictionary

        Returns:
            Path to the generated HTML file
        """
        meta = relic_data.get("metadata", {})
        engine = ExportEngine(ExportOptions(
            output_dir=self.config.output_dir,
            format=ExportFormat.SINGLE_PAGE,
            theme=self.config.theme,
            title=f"Relic: {meta.get('name', 'Untitled')}",
            include_widgets=self.config.include_widgets,
            include_nav=False,
            minify=self.config.minify,
            grid_cols=self.config.grid_cols,
            grid_rows=self.config.grid_rows,
        ))
        return engine.export_relic(relic_data)

    def export_liquid_page(
        self,
        template_name: str,
        rendered_html: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Export Liquid-rendered content as a standalone HTML page.

        Args:
            template_name: Name of the template used
            rendered_html: The rendered HTML content
            context: Optional template context data

        Returns:
            Path to the generated HTML file
        """
        engine = ExportEngine(ExportOptions(
            output_dir=self.config.output_dir,
            format=ExportFormat.SINGLE_PAGE,
            theme=self.config.theme,
            title=f"Template: {template_name}",
            include_widgets=self.config.include_widgets,
            include_nav=False,
            minify=self.config.minify,
            grid_cols=self.config.grid_cols,
            grid_rows=self.config.grid_rows,
        ))
        return engine.export_liquid(template_name, rendered_html, context)

    def export_widget(
        self,
        widget_name: str,
        widget_html: str,
    ) -> str:
        """
        Export an embeddable HTML widget snippet.

        Args:
            widget_name: Name for the widget
            widget_html: The HTML content

        Returns:
            Path to the generated HTML file
        """
        slug = widget_name.lower().replace(" ", "-")
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filepath = output_dir / f"{slug}.html"
        filepath.write_text(f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{widget_name}</title>
</head>
<body>
  <div class="udos-widget" data-widget="{widget_name}">
    {widget_html}
  </div>
</body>
</html>""")
        return str(filepath)
