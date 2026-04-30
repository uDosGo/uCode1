#!/usr/bin/env python3
"""
MDX Runtime — Snack shortcode resolution and execution in MDX documents.

Parses MDX content for `<Snack>` shortcodes, resolves them to actual
Snack objects, executes them, and renders output inline.

Features:
  - `<Snack id="..." inputs='{...}'>` shortcode support
  - Snack resolution from registry or inline definition
  - Snack execution with input passing
  - Output rendering (plain text, JSON, HTML)
  - Error handling with fallback content
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

from ..snack.engine import SnackEngine, execute_snack
from ..snack.exceptions import SnackExecutionError
from ..snack.models import Snack, SnackInput, SnackOutput
from ..snack.validator import validate_snack

# Regex to match <Snack> shortcodes in MDX content
# Supports:
#   <Snack id="my-snack">
#   <Snack id="my-snack" inputs='{"key":"value"}'>
#   <Snack id="my-snack" inputs='{"key":"value"}' />
SNACK_SHORTCODE_RE = re.compile(
    r'<Snack\s+'
    r'id="([^"]+)"'                           # id attribute
    r'(?:\s+inputs=\'([^\']+)\')?'            # optional inputs as JSON string
    r'(?:\s+output="([^"]+)")?'               # optional output format
    r'\s*(?:/>|>)',                           # self-closing or open tag
    re.IGNORECASE,
)

# Regex to match closing </Snack> tag
SNACK_CLOSE_RE = re.compile(r'</Snack\s*>', re.IGNORECASE)


class SnackResolutionError(Exception):
    """Raised when a Snack cannot be resolved."""
    pass


class MDXRuntimeError(Exception):
    """Raised when MDX processing fails."""
    pass


class MDXProcessor:
    """Processes MDX content, resolving and executing Snack shortcodes.

    The processor walks through MDX text, finds `<Snack>` shortcodes,
    resolves them to Snack objects (from a provided registry or inline),
    executes them, and replaces the shortcode with rendered output.

    Args:
        snack_registry: Optional dict of {snack_id: Snack} for resolution.
        snack_dir: Optional directory path to scan for .snack files.
        engine: Optional SnackEngine instance (created fresh if omitted).
    """

    def __init__(
        self,
        snack_registry: Optional[Dict[str, Snack]] = None,
        snack_dir: Optional[str] = None,
        engine: Optional[SnackEngine] = None,
    ):
        self.snack_registry = snack_registry or {}
        self.snack_dir = snack_dir
        self.engine = engine or SnackEngine()
        self._loaded = False

    def register_snack(self, snack: Snack) -> None:
        """Register a Snack for resolution by ID."""
        self.snack_registry[snack.id] = snack

    def register_snacks(self, snacks: List[Snack]) -> None:
        """Register multiple Snacks at once."""
        for snack in snacks:
            self.register_snack(snack)

    def load_from_directory(self, directory: Optional[str] = None) -> int:
        """Load .snack files from a directory into the registry.

        Args:
            directory: Path to scan. Defaults to self.snack_dir.

        Returns:
            Number of snacks loaded.
        """
        from ..snack.models import Snack
        from ..snack.schema import validate_snack_schema

        d = directory or self.snack_dir
        if not d or not os.path.isdir(d):
            return 0

        count = 0
        for fname in os.listdir(d):
            if fname.endswith(".snack"):
                fpath = os.path.join(d, fname)
                try:
                    with open(fpath) as f:
                        data = json.load(f)
                    snack = Snack.from_dict(data)
                    self.register_snack(snack)
                    count += 1
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    print(f"  ⚠️  Skipped {fname}: {e}")
        self._loaded = True
        return count

    def resolve_snack(self, snack_id: str) -> Snack:
        """Resolve a Snack by ID from the registry.

        Raises SnackResolutionError if not found.
        """
        # Try registry first
        if snack_id in self.snack_registry:
            return self.snack_registry[snack_id]

        # Try snack_dir if not yet loaded
        if not self._loaded and self.snack_dir:
            self.load_from_directory()
            if snack_id in self.snack_registry:
                return self.snack_registry[snack_id]

        raise SnackResolutionError(
            f"Snack '{snack_id}' not found. "
            f"Available: {list(self.snack_registry.keys())}"
        )

    def process(self, mdx_content: str) -> str:
        """Process MDX content, resolving and executing all Snack shortcodes.

        Args:
            mdx_content: Raw MDX text containing <Snack> shortcodes.

        Returns:
            MDX content with shortcodes replaced by execution output.
        """
        result_parts = []
        pos = 0
        errors = []

        while pos < len(mdx_content):
            match = SNACK_SHORTCODE_RE.search(mdx_content, pos)
            if not match:
                result_parts.append(mdx_content[pos:])
                break

            # Add text before the shortcode
            result_parts.append(mdx_content[pos:match.start()])

            # Extract shortcode attributes
            snack_id = match.group(1)
            inputs_json = match.group(2)
            output_format = match.group(3) or "text"

            # Parse inputs
            inputs = {}
            if inputs_json:
                try:
                    inputs = json.loads(inputs_json)
                except json.JSONDecodeError as e:
                    errors.append(f"Invalid inputs for '{snack_id}': {e}")
                    result_parts.append(
                        _error_block(snack_id, f"Invalid inputs JSON: {e}")
                    )
                    pos = match.end()
                    continue

            # Execute the snack
            try:
                snack = self.resolve_snack(snack_id)
            except SnackResolutionError as e:
                errors.append(str(e))
                result_parts.append(_error_block(snack_id, f"Not found: {e}"))
                pos = match.end()
                continue

            try:
                result = self.engine.execute(snack, inputs)
                output = _format_output(snack, result, output_format)
                result_parts.append(output)
            except SnackExecutionError as e:
                errors.append(f"Execution failed for '{snack_id}': {e}")
                result_parts.append(_error_block(snack_id, str(e)))

            pos = match.end()

            # If not self-closing, skip optional closing tag
            if mdx_content[match.end() - 2:match.end()] != "/>":
                close_match = SNACK_CLOSE_RE.search(mdx_content, pos)
                if close_match:
                    pos = close_match.end()

        result = "".join(result_parts)

        if errors:
            result += "\n\n<!-- MDX Runtime Errors:\n"
            for err in errors:
                result += f"  - {err}\n"
            result += "-->"

        return result

    def process_file(self, input_path: str, output_path: Optional[str] = None) -> str:
        """Process an MDX file, writing output if output_path is given.

        Args:
            input_path: Path to input .mdx file.
            output_path: Optional output path. If omitted, derived from input.

        Returns:
            Processed content.
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"MDX file not found: {input_path}")

        with open(input_path) as f:
            content = f.read()

        processed = self.process(content)

        out = output_path or input_path.replace(".mdx", ".md")
        with open(out, "w") as f:
            f.write(processed)

        return processed

    def list_registered(self) -> List[Dict[str, Any]]:
        """List all registered snacks with metadata."""
        return [
            {
                "id": s.id,
                "name": s.name,
                "runtime": s.runtime,
                "kind": s.kind,
                "inputs": [i.name for i in s.inputs],
            }
            for s in self.snack_registry.values()
        ]


def _format_output(snack: Snack, result: Dict[str, Any], fmt: str = "text") -> str:
    """Format snack execution output for MDX embedding."""
    stdout = result.get("stdout", "").strip()
    stderr = result.get("stderr", "").strip()
    exit_code = result.get("exit_code", 0)

    if fmt == "json":
        return json.dumps(result, indent=2)

    if fmt == "html":
        parts = [f'<div class="snack-output snack-{snack.id}">']
        if stdout:
            parts.append(f"<pre><code>{_escape_html(stdout)}</code></pre>")
        if stderr:
            parts.append(
                f'<pre class="snack-error"><code>{_escape_html(stderr)}</code></pre>'
            )
        parts.append("</div>")
        return "\n".join(parts)

    # Default: plain text, inline
    return stdout if stdout else ""


def _error_block(snack_id: str, message: str) -> str:
    """Generate an error placeholder block."""
    return (
        f'\n<div class="snack-error snack-error-{snack_id}">\n'
        f"  ⚠️ **Snack '{snack_id}' error:** {message}\n"
        f"</div>\n"
    )


def _escape_html(text: str) -> str:
    """Escape HTML entities."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
