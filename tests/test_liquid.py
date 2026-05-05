"""
Tests for the Liquid template engine.
"""

import os
import sys
import tempfile
import json

# Add parent dir so we can import core_py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core_py.liquid_engine import LiquidEngine, TemplateRegistry


class TestLiquidEngine:
    """Tests for LiquidEngine."""

    def test_render_simple(self):
        """Test basic variable substitution."""
        engine = LiquidEngine(template_dirs=[])
        result = engine.render("Hello {{ name }}!", {"name": "World"})
        assert result == "Hello World!"

    def test_render_with_object(self):
        """Test rendering with nested objects."""
        engine = LiquidEngine(template_dirs=[])
        result = engine.render(
            "{{ snack.name }}: {{ snack.output }}",
            {"snack": {"name": "hello", "output": "Hello, World!"}},
        )
        assert result == "hello: Hello, World!"

    def test_render_with_list(self):
        """Test rendering with lists."""
        engine = LiquidEngine(template_dirs=[])
        result = engine.render(
            "{% for item in items %}{{ item }},{% endfor %}",
            {"items": ["a", "b", "c"]},
        )
        assert result == "a,b,c,"

    def test_render_with_condition(self):
        """Test rendering with conditionals."""
        engine = LiquidEngine(template_dirs=[])
        result = engine.render(
            "{% if active %}ACTIVE{% else %}INACTIVE{% endif %}",
            {"active": True},
        )
        assert result == "ACTIVE"

        result = engine.render(
            "{% if active %}ACTIVE{% else %}INACTIVE{% endif %}",
            {"active": False},
        )
        assert result == "INACTIVE"

    def test_render_empty_data(self):
        """Test rendering with no data."""
        engine = LiquidEngine(template_dirs=[])
        result = engine.render("Hello {{ name }}!", {})
        assert result == "Hello !"

    def test_render_snack(self):
        """Test render_snack convenience method."""
        engine = LiquidEngine(template_dirs=[])
        result = engine.render_snack(
            "{{ snack.name }}: {{ snack.status }}",
            {"name": "test", "output": "ok", "status": "success",
             "duration": 0.5, "metadata": {}},
        )
        assert result == "test: success"

    def test_render_binder(self):
        """Test render_binder convenience method."""
        engine = LiquidEngine(template_dirs=[])
        result = engine.render_binder(
            "Binder: {{ binder.name }}",
            {"name": "my-binder", "state": {}, "variables": {}},
        )
        assert result == "Binder: my-binder"

    def test_render_relic(self):
        """Test render_relic convenience method."""
        engine = LiquidEngine(template_dirs=[])
        result = engine.render_relic(
            "Relic: {{ relic.name }}",
            {"name": "my-relic", "data": "test"},
        )
        assert result == "Relic: my-relic"

    def test_render_file(self):
        """Test rendering a template file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a template file
            template_path = os.path.join(tmpdir, "greeting.liquid")
            with open(template_path, "w") as f:
                f.write("Hello {{ name }}!")

            engine = LiquidEngine(template_dirs=[tmpdir])
            result = engine.render_file("greeting.liquid", {"name": "World"})
            assert result == "Hello World!"

    def test_render_file_not_found(self):
        """Test rendering a non-existent template file."""
        engine = LiquidEngine(template_dirs=[])
        try:
            engine.render_file("nonexistent.liquid", {})
            assert False, "Should have raised an exception"
        except Exception:
            pass  # Expected


class TestTemplateRegistry:
    """Tests for TemplateRegistry."""

    def test_scan_empty(self):
        """Test scanning with no template directories."""
        registry = TemplateRegistry(directories=[])
        templates = registry.scan()
        assert templates == {}

    def test_scan_with_templates(self):
        """Test scanning a directory with template files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create some template files
            for name in ["hello", "world", "test"]:
                with open(os.path.join(tmpdir, f"{name}.liquid"), "w") as f:
                    f.write(f"Template: {name}")

            registry = TemplateRegistry(directories=[tmpdir])
            templates = registry.scan()
            assert len(templates) == 3
            assert "hello" in templates
            assert "world" in templates
            assert "test" in templates

    def test_list_templates(self):
        """Test listing templates with metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "hello.liquid"), "w") as f:
                f.write("Hello!")

            registry = TemplateRegistry(directories=[tmpdir])
            listing = registry.list_templates()
            assert len(listing) == 1
            assert listing[0]["name"] == "hello"
            assert listing[0]["size"] == 6  # "Hello!" is 6 bytes

    def test_get_template(self):
        """Test getting template content by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(os.path.join(tmpdir, "hello.liquid"), "w") as f:
                f.write("Hello {{ name }}!")

            registry = TemplateRegistry(directories=[tmpdir])
            content = registry.get_template("hello")
            assert content == "Hello {{ name }}!"

    def test_get_template_not_found(self):
        """Test getting a non-existent template."""
        registry = TemplateRegistry(directories=[])
        content = registry.get_template("nonexistent")
        assert content is None

    def test_get_path(self):
        """Test getting template file path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            template_path = os.path.join(tmpdir, "hello.liquid")
            with open(template_path, "w") as f:
                f.write("Hello!")

            registry = TemplateRegistry(directories=[tmpdir])
            path = registry.get_path("hello")
            assert path == template_path

    def test_get_path_not_found(self):
        """Test getting path for non-existent template."""
        registry = TemplateRegistry(directories=[])
        path = registry.get_path("nonexistent")
        assert path is None


class TestLiquidCLI:
    """Tests for the liquid CLI commands."""

    def test_render_command(self, capsys):
        """Test the render command."""
        from liquid_cli import cmd_render

        class Args:
            template = "Hello {{ name }}!"
            data = ["name=World"]

        result = cmd_render(Args())
        captured = capsys.readouterr()
        assert result == 0
        assert captured.out.strip() == "Hello World!"

    def test_render_command_with_json_data(self, capsys):
        """Test render with JSON data values."""
        from liquid_cli import cmd_render

        class Args:
            template = "{{ items | join: ', ' }}"
            data = ['items=["a","b","c"]']

        result = cmd_render(Args())
        captured = capsys.readouterr()
        assert result == 0
        assert captured.out.strip() == "a, b, c"

    def test_list_command_empty(self, capsys):
        """Test list command with no templates."""
        from liquid_cli import cmd_list

        class Args:
            json = False

        result = cmd_list(Args())
        captured = capsys.readouterr()
        assert result == 0
        assert "No templates found" in captured.out

    def test_list_command_json(self, capsys):
        """Test list command with JSON output."""
        from liquid_cli import cmd_list

        class Args:
            json = True

        result = cmd_list(Args())
        captured = capsys.readouterr()
        assert result == 0
        # Should output valid JSON (empty array)
        data = json.loads(captured.out)
        assert data == []

    def test_render_snack_command(self, capsys):
        """Test the render-snack command."""
        from liquid_cli import cmd_render_snack

        class Args:
            template = "{{ snack.name }}: {{ snack.status }}"
            snack_name = "test-snack"

        result = cmd_render_snack(Args())
        captured = capsys.readouterr()
        assert result == 0
        assert "test-snack: success" in captured.out

    def test_render_binder_command(self, capsys):
        """Test the render-binder command."""
        from liquid_cli import cmd_render_binder

        class Args:
            template = "Binder: {{ binder.name }}"
            binder_name = "my-binder"

        result = cmd_render_binder(Args())
        captured = capsys.readouterr()
        assert result == 0
        assert "Binder: my-binder" in captured.out
