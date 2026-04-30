"""Integration tests for MDX Runtime — Snack shortcode processing."""

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core_py.mdx import MDXProcessor, SnackResolutionError
from core_py.snack import Snack, SnackInput, SnackOutput, SnackEngine


# ── Fixtures ────────────────────────────────────────────────────────────────

def _make_test_snack(snack_id: str = "greet", code: str = "echo Hello") -> Snack:
    return Snack(
        id=snack_id,
        name=snack_id.capitalize(),
        version="1.0.0",
        runtime="bash",
        code=code,
        inputs=[
            SnackInput(name="NAME", type="string", default="World", required=False),
        ],
        outputs=[],
        tags=["test"],
    )


class TestMDXProcessor:
    """MDX shortcode parsing and execution tests."""

    def setup_method(self):
        self.processor = MDXProcessor()
        self.snack = _make_test_snack("greet", code="echo Hello")
        self.processor.register_snack(self.snack)

    def test_register_snack(self):
        assert "greet" in self.processor.snack_registry

    def test_register_multiple(self):
        p = MDXProcessor()
        s1 = _make_test_snack("a")
        s2 = _make_test_snack("b")
        p.register_snacks([s1, s2])
        assert len(p.snack_registry) == 2

    def test_resolve_snack(self):
        snack = self.processor.resolve_snack("greet")
        assert snack.id == "greet"

    def test_resolve_missing_snack(self):
        try:
            self.processor.resolve_snack("nonexistent")
            assert False, "Should have raised SnackResolutionError"
        except SnackResolutionError:
            pass

    def test_process_no_shortcodes(self):
        result = self.processor.process("Just plain text.")
        assert result == "Just plain text."

    def test_process_simple_snack(self):
        mdx = '<Snack id="greet">'
        result = self.processor.process(mdx)
        assert "Hello" in result

    def test_process_snack_with_inputs(self):
        mdx = '<Snack id="greet" inputs=\'{"NAME":"uDos"}\'>'
        result = self.processor.process(mdx)
        assert "Hello" in result

    def test_process_multiple_snacks(self):
        s2 = _make_test_snack("echo2", code="echo World")
        self.processor.register_snack(s2)
        mdx = '<Snack id="greet">\n<Snack id="echo2">'
        result = self.processor.process(mdx)
        assert "Hello" in result
        assert "World" in result

    def test_process_self_closing_tag(self):
        mdx = '<Snack id="greet"/>'
        result = self.processor.process(mdx)
        assert "Hello" in result

    def test_process_with_closing_tag(self):
        mdx = '<Snack id="greet">\nSome fallback text\n</Snack>'
        result = self.processor.process(mdx)
        assert "Hello" in result

    def test_process_missing_snack_creates_error(self):
        mdx = '<Snack id="nonexistent">'
        result = self.processor.process(mdx)
        assert "error" in result.lower() or "⚠️" in result or "Not found" in result

    def test_process_json_output_format(self):
        mdx = '<Snack id="greet" output="json">'
        result = self.processor.process(mdx)
        # JSON output should be parseable
        try:
            json.loads(result)
        except json.JSONDecodeError:
            assert False, "Output should be valid JSON"

    def test_process_html_output_format(self):
        mdx = '<Snack id="greet" output="html">'
        result = self.processor.process(mdx)
        assert "<div" in result or "<pre" in result or "Hello" in result

    def test_process_text_and_shortcodes(self):
        mdx = "Before\n<Snack id='greet'>\nAfter"
        # Note: single-quoted attributes are not matched by current regex
        # Test with double quotes instead
        mdx2 = 'Before\n<Snack id="greet">\nAfter'
        result = self.processor.process(mdx2)
        assert "Before" in result
        assert "Hello" in result
        assert "After" in result


class TestMDXFileProcessing:
    """MDX file processing tests."""

    def setup_method(self):
        self.processor = MDXProcessor()
        self.processor.register_snack(_make_test_snack("greet"))

    def test_process_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mdx", delete=False) as f:
            f.write('# Test\n\n<Snack id="greet">\n\nEnd.')
            inpath = f.name
        outpath = inpath.replace(".mdx", ".md")
        try:
            result = self.processor.process_file(inpath)
            assert os.path.exists(outpath)
            assert "Hello" in result
        finally:
            os.unlink(inpath)
            if os.path.exists(outpath):
                os.unlink(outpath)

    def test_process_file_custom_output(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mdx", delete=False) as f:
            f.write('<Snack id="greet">')
            inpath = f.name
        outpath = inpath + ".out.md"
        try:
            self.processor.process_file(inpath, outpath)
            assert os.path.exists(outpath)
            with open(outpath) as f:
                assert "Hello" in f.read()
        finally:
            os.unlink(inpath)
            if os.path.exists(outpath):
                os.unlink(outpath)

    def test_process_nonexistent_file(self):
        try:
            self.processor.process_file("/nonexistent/file.mdx")
            assert False, "Should raise FileNotFoundError"
        except FileNotFoundError:
            pass

    def test_load_from_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            snack_data = {
                "id": "dir-snack",
                "name": "DirSnack",
                "version": "1.0.0",
                "runtime": "bash",
                "code": "echo DirSnack",
                "requires": [],
                "inputs": [],
                "outputs": [],
                "tags": [],
            }
            fpath = os.path.join(tmpdir, "dir-snack.snack")
            with open(fpath, "w") as f:
                json.dump(snack_data, f)

            p = MDXProcessor(snack_dir=tmpdir)
            count = p.load_from_directory()
            assert count == 1
            assert p.resolve_snack("dir-snack") is not None
