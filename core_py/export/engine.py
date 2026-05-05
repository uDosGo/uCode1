"""
Export Engine — core logic for static HTML generation.

Supports three export formats:
- FULL_SITE: Complete HTML page with theme, navigation, widgets
- SINGLE_PAGE: Minimal standalone HTML for a single component
- WIDGET: Embeddable HTML snippet
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import json
import os
import shutil


class ExportFormat(Enum):
    """Output format for static HTML export."""
    FULL_SITE = "full-site"
    SINGLE_PAGE = "single-page"
    WIDGET = "widget"


@dataclass
class ExportOptions:
    """Options for the export engine."""
    output_dir: str = "./dist"
    format: ExportFormat = ExportFormat.FULL_SITE
    theme: str = "bbcbasic"  # bbcbasic, nesdash, ceefax
    title: str = "uCode1 Export"
    include_widgets: bool = True
    include_nav: bool = True
    minify: bool = False
    copy_assets: bool = True
    grid_cols: int = 40
    grid_rows: int = 24


class ExportEngine:
    """
    Core export engine that generates static HTML from uCode1 data.

    Takes snacks, binders, relics, and Liquid-rendered content and
    produces standalone HTML files using the existing theme system.
    """

    def __init__(self, options: Optional[ExportOptions] = None):
        self.options = options or ExportOptions()
        self._themes_dir = self._resolve_themes_dir()

    def _resolve_themes_dir(self) -> Path:
        """Resolve the themes directory relative to uCode1."""
        # Look relative to this file's location
        here = Path(__file__).parent.parent.parent  # uCode1/
        themes = here / "themes"
        if themes.is_dir():
            return themes
        # Fallback
        return Path("./themes")

    def export_snack(
        self,
        snack_data: Dict[str, Any],
        rendered_content: Optional[str] = None,
    ) -> str:
        """
        Export a single snack as a static HTML page.

        Args:
            snack_data: Snack dictionary (from Snack.to_dict())
            rendered_content: Optional pre-rendered Liquid/HTML content

        Returns:
            Path to the generated HTML file (relative to output_dir)
        """
        content = rendered_content or snack_data.get("code", "")
        name = snack_data.get("name", snack_data.get("id", "untitled"))
        slug = name.lower().replace(" ", "-")

        html = self._build_page(
            title=f"Snack: {name}",
            body=self._snack_body(snack_data, content),
        )

        return self._write_output(slug, html)

    def export_binder(
        self,
        binder_data: Dict[str, Any],
        rendered_entries: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Export a binder as a static HTML page.

        Args:
            binder_data: Binder dictionary (from Binder.to_dict())
            rendered_entries: Optional dict of entry_id -> rendered HTML

        Returns:
            Path to the generated HTML file
        """
        metadata = binder_data.get("metadata", {})
        name = metadata.get("name", "untitled-binder")
        slug = name.lower().replace(" ", "-")

        html = self._build_page(
            title=f"Binder: {name}",
            body=self._binder_body(binder_data, rendered_entries),
        )

        return self._write_output(slug, html)

    def export_relic(
        self,
        relic_data: Dict[str, Any],
    ) -> str:
        """
        Export a relic's metadata as a static HTML page.

        Args:
            relic_data: Relic dictionary (from Relic.to_dict())

        Returns:
            Path to the generated HTML file
        """
        metadata = relic_data.get("metadata", {})
        name = metadata.get("name", "untitled-relic")
        slug = name.lower().replace(" ", "-")

        html = self._build_page(
            title=f"Relic: {name}",
            body=self._relic_body(relic_data),
        )

        return self._write_output(slug, html)

    def export_liquid(
        self,
        template_name: str,
        rendered_html: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Export Liquid-rendered content as a static HTML page.

        Args:
            template_name: Name of the template used
            rendered_html: The rendered HTML content
            context: Optional template context data (for display)

        Returns:
            Path to the generated HTML file
        """
        slug = template_name.replace(".liquid", "").lower().replace(" ", "-")

        html = self._build_page(
            title=f"Template: {template_name}",
            body=self._liquid_body(template_name, rendered_html, context),
        )

        return self._write_output(slug, html)

    def export_site(
        self,
        pages: List[Dict[str, Any]],
        site_title: str = "uCode1 Site",
    ) -> str:
        """
        Export multiple pages as a complete static site.

        Each page dict should have:
            - slug: str (filename without .html)
            - title: str
            - body: str (HTML content)

        Args:
            pages: List of page definitions
            site_title: Title for the site index

        Returns:
            Path to the generated index.html
        """
        # Write each page
        for page in pages:
            html = self._build_page(
                title=page.get("title", "Untitled"),
                body=page.get("body", ""),
                slug=page.get("slug", ""),
                is_site=True,
                site_title=site_title,
                all_pages=pages,
            )
            self._write_output(page.get("slug", "untitled"), html)

        # Write index
        index_html = self._build_site_index(site_title, pages)
        return self._write_output("index", index_html)

    # ── Internal helpers ──────────────────────────────────────────────────

    def _build_page(
        self,
        title: str,
        body: str,
        slug: str = "",
        is_site: bool = False,
        site_title: str = "",
        all_pages: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Build a complete HTML page with theme."""
        theme_css = self._get_theme_css()
        theme_js = self._get_theme_js()
        nav_html = self._build_nav(all_pages or [], slug) if self.options.include_nav and is_site else ""
        widgets_html = self._widgets_script() if self.options.include_widgets else ""

        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{self._escape_html(title)} — {site_title or "uCode1"}</title>
  <style>
{theme_css}
  </style>
  {theme_js}
  {widgets_html}
</head>
<body>
  <div class="udos-export" data-surface="{self.options.theme}">
    {nav_html}
    <main class="export-content">
      {body}
    </main>
  </div>
  <script>
    // Auto-init display if available
    if (typeof uDosWidgets !== 'undefined' && uDosWidgets.Display) {{
      var el = document.querySelector('.udos-export');
      if (el) {{
        uDosWidgets.Display.init(el, {{
          cols: {self.options.grid_cols},
          rows: {self.options.grid_rows},
          baseFont: 24
        }});
      }}
    }}
  </script>
</body>
</html>"""

    def _build_site_index(
        self,
        site_title: str,
        pages: List[Dict[str, Any]],
    ) -> str:
        """Build the site index page."""
        page_list = "\n".join(
            f'    <li><a href="{p.get("slug", "untitled")}.html">{self._escape_html(p.get("title", "Untitled"))}</a></li>'
            for p in pages
        )

        body = f"""
    <div class="site-index">
      <h1>{self._escape_html(site_title)}</h1>
      <p>Generated by uCode1 Export Engine v1.3.0</p>
      <ul class="page-list">
{page_list}
      </ul>
    </div>
"""
        return self._build_page(
            title=site_title,
            body=body,
            slug="index",
            is_site=True,
            site_title=site_title,
            all_pages=pages,
        )

    def _build_nav(
        self,
        pages: List[Dict[str, Any]],
        current_slug: str,
    ) -> str:
        """Build navigation HTML for site pages."""
        active_cls = ' class="active"'
        items = "\n".join(
            f'      <li><a href="{p.get("slug", "untitled")}.html"{active_cls if p.get("slug") == current_slug else ""}>{self._escape_html(p.get("title", "Untitled"))}</a></li>'
            for p in pages
        )
        return f"""
    <nav class="export-nav">
      <ul>
        <li><a href="index.html">Home</a></li>
{items}
      </ul>
    </nav>"""

    def _snack_body(self, snack: Dict[str, Any], content: str) -> str:
        """Build HTML body for a snack export."""
        meta = f"""
      <div class="export-meta">
        <span class="meta-badge">{snack.get("kind", "script")}</span>
        <span class="meta-badge">{snack.get("runtime", "bash")}</span>
        <span class="meta-badge">v{snack.get("version", "0")}</span>
      </div>"""

        tags = ""
        if snack.get("tags"):
            tags = '<div class="export-tags">' + "".join(
                f'<span class="tag">{t}</span>' for t in snack["tags"]
            ) + "</div>"

        return f"""
    <article class="export-snack">
      <header>
        <h2>{snack.get("emoji", "")} {self._escape_html(snack.get("name", "Untitled Snack"))}</h2>
        {meta}
        {tags}
      </header>
      <section class="export-content-body">
        <pre class="export-code"><code>{self._escape_html(content)}</code></pre>
      </section>
    </article>"""

    def _binder_body(
        self,
        binder: Dict[str, Any],
        rendered_entries: Optional[Dict[str, str]] = None,
    ) -> str:
        """Build HTML body for a binder export."""
        metadata = binder.get("metadata", {})
        root = binder.get("root", {})

        entries_html = self._render_entries(root.get("children", []), rendered_entries)

        return f"""
    <article class="export-binder">
      <header>
        <h2>\U0001F4E6 {self._escape_html(metadata.get("name", "Untitled Binder"))}</h2>
        <div class="export-meta">
          <span class="meta-badge">v{metadata.get("version", "0")}</span>
          <span class="meta-badge">{metadata.get("id", "")}</span>
        </div>
      </header>
      <section class="export-content-body">
        {entries_html}
      </section>
    </article>"""

    def _relic_body(self, relic: Dict[str, Any]) -> str:
        """Build HTML body for a relic export."""
        metadata = relic.get("metadata", {})

        resources = relic.get("resources", [])
        resources_html = ""
        if resources:
            resources_html = """
      <h3>Resources</h3>
      <table class="export-table">
        <thead><tr><th>Name</th><th>Type</th><th>Size</th></tr></thead>
        <tbody>""" + "\n".join(
                f'          <tr><td>{r.get("name", "")}</td><td>{r.get("type", "")}</td><td>{r.get("size", 0)} bytes</td></tr>'
                for r in resources
            ) + """
        </tbody>
      </table>"""

        return f"""
    <article class="export-relic">
      <header>
        <h2>\U0001F4E6 {self._escape_html(metadata.get("name", "Untitled Relic"))}</h2>
        <div class="export-meta">
          <span class="meta-badge">{metadata.get("runtime", "python")}</span>
          <span class="meta-badge">v{metadata.get("version", "0")}</span>
        </div>
      </header>
      <section class="export-content-body">
        <p><strong>ID:</strong> {metadata.get("id", "")}</p>
        <p><strong>Entry Point:</strong> {metadata.get("entry_point", "N/A")}</p>
        <p><strong>Checksum:</strong> <code>{relic.get("checksum", "")[:16]}...</code></p>
        {resources_html}
      </section>
    </article>"""

    def _liquid_body(
        self,
        template_name: str,
        rendered_html: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Build HTML body for a Liquid template export."""
        context_html = ""
        if context:
            context_html = f"""
      <details class="export-context">
        <summary>Template Context</summary>
        <pre><code>{self._escape_html(json.dumps(context, indent=2))}</code></pre>
      </details>"""

        return f"""
    <article class="export-liquid">
      <header>
        <h2>\U0001F4DD Template: {self._escape_html(template_name)}</h2>
      </header>
      <section class="export-content-body">
        {rendered_html}
      </section>
      {context_html}
    </article>"""

    def _render_entries(
        self,
        entries: List[Dict[str, Any]],
        rendered_entries: Optional[Dict[str, str]] = None,
        depth: int = 0,
    ) -> str:
        """Recursively render binder entries as HTML."""
        if not entries:
            return "<p>No entries</p>"

        items = []
        for entry in entries:
            entry_id = entry.get("id", "")
            name = entry.get("name", "entry")
            entry_type = entry.get("type", "data")
            value = entry.get("value")

            # Use pre-rendered content if available
            if rendered_entries and entry_id in rendered_entries:
                content = rendered_entries[entry_id]
            elif value:
                if isinstance(value, (dict, list)):
                    content = f'<pre><code>{self._escape_html(json.dumps(value, indent=2))}</code></pre>'
                else:
                    content = f'<p>{self._escape_html(str(value))}</p>'
            else:
                content = ""

            children_html = ""
            if entry.get("children"):
                children_html = self._render_entries(
                    entry["children"], rendered_entries, depth + 1
                )

            items.append(
                f'<li class="entry-depth-{depth}"><strong>{self._escape_html(name)}</strong> '
                f'<span class="entry-type">{entry_type}</span>'
                f'{content}{children_html}</li>'
            )

        return "<ul>" + "\n".join(items) + "</ul>"

    def _get_theme_css(self) -> str:
        """Get the CSS for the selected theme."""
        theme = self.options.theme
        css_parts = []

        # Base display CSS
        display_css = self._read_asset("display.css")
        if display_css:
            css_parts.append(display_css)

        # Tailwind sidebar CSS
        tailwind_css = self._read_asset("tailwind.css")
        if tailwind_css:
            css_parts.append(tailwind_css)

        # Theme-specific CSS
        if theme == "bbcbasic":
            theme_css = self._read_asset("bbcbasic/css.css")
            if theme_css:
                css_parts.append(theme_css)
        elif theme == "nesdash":
            pass  # NES.css loaded via CDN in template

        # Export-specific styles
        css_parts.append("""
/* Export-specific styles */
.udos-export {
  font-family: system-ui, sans-serif;
  max-width: 960px;
  margin: 0 auto;
  padding: 20px;
  color: #c0c0d0;
  background: #1a1a2e;
  min-height: 100vh;
}
.export-nav {
  background: #16213e;
  border: 1px solid #0f3460;
  border-radius: 6px;
  padding: 8px 16px;
  margin-bottom: 20px;
}
.export-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}
.export-nav a {
  color: #4a6ac0;
  text-decoration: none;
  font-size: 13px;
}
.export-nav a:hover,
.export-nav a.active {
  color: #e94560;
}
.export-meta {
  display: flex;
  gap: 8px;
  margin: 8px 0;
  flex-wrap: wrap;
}
.meta-badge {
  background: #0f3460;
  color: #b0c8ff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
}
.export-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
  margin: 8px 0;
}
.tag {
  background: rgba(74, 106, 192, 0.15);
  color: #8aa0d0;
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 10px;
}
.export-content-body {
  margin: 16px 0;
}
.export-content-body pre {
  background: #0d1117;
  border: 1px solid #0f3460;
  border-radius: 6px;
  padding: 12px;
  overflow-x: auto;
}
.export-content-body code {
  font-family: "C64 User Mono", "Courier New", monospace;
  font-size: 13px;
}
.export-table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
}
.export-table th,
.export-table td {
  border: 1px solid #0f3460;
  padding: 6px 12px;
  text-align: left;
  font-size: 12px;
}
.export-table th {
  background: #16213e;
  color: #4a6ac0;
}
.export-context {
  margin: 16px 0;
  background: #16213e;
  border: 1px solid #0f3460;
  border-radius: 6px;
  padding: 8px 12px;
}
.export-context summary {
  cursor: pointer;
  color: #4a6ac0;
  font-size: 12px;
}
.site-index h1 {
  color: #e94560;
  font-size: 24px;
}
.site-index .page-list {
  list-style: none;
  padding: 0;
}
.site-index .page-list li {
  padding: 8px 12px;
  border-bottom: 1px solid #0f3460;
}
.site-index .page-list a {
  color: #b0c8ff;
  text-decoration: none;
}
.site-index .page-list a:hover {
  color: #e94560;
}
.entry-depth-0 { padding-left: 0; }
.entry-depth-1 { padding-left: 20px; }
.entry-depth-2 { padding-left: 40px; }
.entry-depth-3 { padding-left: 60px; }
.entry-type {
  font-size: 10px;
  color: #506090;
  margin-left: 6px;
}
""")

        return "\n\n".join(css_parts)

    def _get_theme_js(self) -> str:
        """Get the JavaScript for the selected theme."""
        js = self._read_asset("udos-widgets.js")
        if js:
            return f"<script>\n{js}\n</script>"
        return ""

    def _widgets_script(self) -> str:
        """Generate widget initialization script."""
        return """
<script>
  document.addEventListener('DOMContentLoaded', function() {
    if (typeof uDosWidgets !== 'undefined') {
      uDosWidgets.refreshAll();
    }
  });
</script>"""

    def _read_asset(self, path: str) -> Optional[str]:
        """Read a theme asset file."""
        asset_path = self._themes_dir / path
        if asset_path.is_file():
            try:
                return asset_path.read_text()
            except Exception:
                return None
        return None

    def _write_output(self, slug: str, html: str) -> str:
        """Write HTML to the output directory."""
        output_dir = Path(self.options.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{slug}.html"
        filepath = output_dir / filename
        filepath.write_text(html)

        # Copy theme assets if requested
        if self.options.copy_assets:
            self._copy_assets(output_dir)

        return str(filepath)

    def _copy_assets(self, output_dir: Path) -> None:
        """Copy theme assets to the output directory."""
        assets_dir = output_dir / "assets"
        assets_dir.mkdir(exist_ok=True)

        # Copy CSS files
        for css_file in ["display.css", "tailwind.css"]:
            src = self._themes_dir / css_file
            if src.is_file():
                shutil.copy2(src, assets_dir / css_file)

        # Copy theme-specific assets
        theme = self.options.theme
        theme_dir = self._themes_dir / theme
        if theme_dir.is_dir():
            theme_assets = assets_dir / theme
            theme_assets.mkdir(exist_ok=True)
            for item in theme_dir.iterdir():
                if item.is_file() and item.suffix in (".css", ".js", ".woff", ".woff2", ".ttf", ".eot", ".png"):
                    shutil.copy2(item, theme_assets / item.name)

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace("&", "&")
            .replace("<", "<")
            .replace(">", ">")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )
