#!/usr/bin/env python3
"""
End-to-End Tests for USXD Pipeline

This module contains comprehensive end-to-end tests for the complete USXD pipeline:
- ASCII Grid Parser
- Component Mapping
- Grid Rendering
- USXD Document Integration
- CLI Integration

Run with: python3 tests/test_usxd_pipeline.py
"""

import sys
import os
import json
import tempfile
import subprocess
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test imports
TEST_IMPORTS = True
try:
    from core_py.usxd import (
        USXDDocument, USXDMetadata, USXDSection, USXDRegistry, USXDFormat,
        ASCIIGridParser, ParsedGrid, GridCell, GridComponent, GridFormat,
        ComponentMapper, ComponentMapping, ComponentType, ThinUIProperties,
        GridRenderer, Style, ColorMode, TerminalUI
    )
    CORE_PY_USXD_AVAILABLE = True
except ImportError as e:
    print(f"Warning: USXD modules not available: {e}")
    CORE_PY_USXD_AVAILABLE = False
    TEST_IMPORTS = False

try:
    from core_py import Binder, BinderMetadata, BinderEntry
    CORE_PY_BINDER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Binder modules not available: {e}")
    CORE_PY_BINDER_AVAILABLE = False


def run_test(test_func):
    """Run a test function and return result"""
    try:
        test_func()
        return True, None
    except Exception as e:
        return False, str(e)
    except AssertionError as e:
        return False, str(e)


# ============================================================================
# ASCII Grid Parser Tests
# ============================================================================

def test_simple_grid_parsing():
    """Test simple ASCII grid parsing"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    grid_text = """ABC
DEF
GHI"""
    parsed = parser.parse_grid(grid_text, "Simple Test")
    
    assert parsed.rows == 3
    assert parsed.cols == 3
    assert parsed.title == "Simple Test"
    assert parsed.get_cell(0, 0).char == 'A'
    assert parsed.get_cell(2, 2).char == 'I'
    print("✓ Simple grid parsing test passed")


def test_box_drawing_parsing():
    """Test box drawing character parsing"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    grid_text = """┌───┐
│ABC│
└───┘"""
    parsed = parser.parse_grid(grid_text, "Box Drawing Test")
    
    assert parsed.rows == 3
    assert parsed.cols == 5
    assert parsed.get_cell(0, 0).char == '┌'
    assert parsed.get_cell(0, 0).metadata['type'] == 'TL'
    assert parsed.get_cell(1, 0).char == '│'
    assert parsed.get_cell(1, 0).metadata['type'] == 'V'
    print("✓ Box drawing parsing test passed")


def test_markdown_table_parsing():
    """Test markdown table parsing"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    md_table = """| A | B | C |
|---|---|---|
| D | E | F |
| G | H | I |"""
    parsed = parser.parse_grid(md_table, "Markdown Test")
    
    assert parsed.rows == 3
    assert parsed.cols == 3
    assert parsed.get_cell(1, 0).char == 'D'
    print("✓ Markdown table parsing test passed")


def test_csv_parsing():
    """Test CSV parsing"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    csv_data = """A,B,C
D,E,F
G,H,I"""
    parsed = parser.parse_grid(csv_data, "CSV Test")
    
    assert parsed.rows == 3
    assert parsed.cols == 3
    assert parsed.get_cell(0, 0).char == 'A'
    assert parsed.get_cell(0, 1).char == 'B'
    print("✓ CSV parsing test passed")


def test_json_serialization():
    """Test JSON serialization/deserialization"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    grid_text = """ABC
DEF"""
    parsed = parser.parse_grid(grid_text, "JSON Test")
    
    # Serialize to JSON
    json_str = parsed.to_json()
    assert json_str is not None
    
    # Deserialize from JSON
    parsed_back = ParsedGrid.from_json(json_str)
    assert parsed_back.rows == 2
    assert parsed_back.cols == 3
    assert parsed_back.get_cell(0, 0).char == 'A'
    print("✓ JSON serialization test passed")


def test_component_detection():
    """Test automatic component detection"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    grid_text = """AAA
BBB
CCC"""
    parsed = parser.parse_grid(grid_text, "Component Test")
    
    components = parser.split_into_components(grid_text)
    assert len(components) == 3
    assert components[0]['size'] == 3
    assert components[1]['size'] == 3
    assert components[2]['size'] == 3
    print("✓ Component detection test passed")


# ============================================================================
# Component Mapper Tests
# ============================================================================

def test_basic_mapping():
    """Test basic component mapping"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    mapper = ComponentMapper()
    
    grid_text = """┌───┐
│ A │
└───┘"""
    parsed = parser.parse_grid(grid_text, "Mapping Test")
    
    # Add a component
    component = GridComponent(
        id="button1",
        name="Test Button",
        component_type="widget",
        cells=[(1, 1)]
    )
    parsed.add_component(component)
    
    # Map to ThinUI
    thinui_tree = mapper.map_grid(parsed)
    
    assert thinui_tree is not None
    assert thinui_tree.component_type == ComponentType.CONTAINER
    assert len(thinui_tree.children) > 0
    print("✓ Basic mapping test passed")


def test_custom_mapping():
    """Test custom component mapping rules"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    mapper = ComponentMapper()
    
    grid_text = """ABC"""
    parsed = parser.parse_grid(grid_text, "Custom Mapping Test")
    
    # Add component
    component = GridComponent(
        id="custom_btn",
        name="Custom",
        component_type="widget",
        cells=[(0, 0)]
    )
    parsed.add_component(component)
    
    # Add custom mapping
    mapper.add_mapping(
        grid_component_id="custom_btn",
        thinui_type=ComponentType.BUTTON,
        properties=ThinUIProperties(
            component_type=ComponentType.BUTTON,
            text="Click Me",
            fg_color="#FFFFFF",
            bg_color="#0000FF"
        )
    )
    
    thinui_tree = mapper.map_grid(parsed)
    
    # Check if custom mapping was applied
    button_found = False
    for child in thinui_tree.children:
        if child.component_type == ComponentType.BUTTON:
            button_found = True
            assert child.text == "Click Me"
            assert child.bg_color == "#0000FF"
            break
    
    assert button_found, "Custom button mapping not applied"
    print("✓ Custom mapping test passed")


def test_layout_creation():
    """Test layout creation"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    mapper = ComponentMapper()
    
    grid_text = """┌───┐
│ A │
└───┘"""
    parsed = parser.parse_grid(grid_text, "Layout Test")
    
    # Create grid layout
    layout = mapper.create_grid_layout(parsed)
    assert layout['type'] == 'grid'
    assert 'components' in layout
    assert len(layout['components']) > 0
    print("✓ Grid layout creation test passed")


def test_teletext_layout():
    """Test teletext layout creation"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    mapper = ComponentMapper()
    
    grid_text = """┌───┐
│ A │
└───┘"""
    parsed = parser.parse_grid(grid_text, "Teletext Test")
    
    layout = mapper.create_teletext_layout(parsed)
    assert layout['mode7'] == True
    assert layout['character_set'] == 'teletext'
    assert 'cells' in layout
    print("✓ Teletext layout test passed")


def test_html_generation():
    """Test HTML generation"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    mapper = ComponentMapper()
    
    grid_text = """A|B
-+-
C|D"""
    parsed = parser.parse_grid(grid_text, "HTML Test")
    
    html = mapper.map_to_html(parsed, "simple")
    assert '<table' in html
    assert '<td' in html
    print("✓ HTML generation test passed")


# ============================================================================
# Grid Renderer Tests
# ============================================================================

def test_simple_rendering():
    """Test simple grid rendering"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    renderer = GridRenderer()
    
    grid_text = """ABC
DEF"""
    parsed = parser.parse_grid(grid_text, "Render Test")
    
    rendered = renderer.render(parsed)
    assert rendered is not None
    assert len(rendered) > 0
    # Remove ANSI codes for assertion
    import re
    clean = re.sub(r'\033\[[0-9;]*m', '', rendered)
    assert 'ABC' in clean
    print("✓ Simple rendering test passed")


def test_color_rendering():
    """Test colored rendering"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    renderer = GridRenderer()
    
    grid_text = """A"""
    parsed = parser.parse_grid(grid_text, "Color Test")
    
    # Create a colored cell
    cell = parsed.get_cell(0, 0)
    cell.fg_color = '#FF0000'
    cell.bg_color = '#0000FF'
    
    rendered = renderer.render(parsed)
    assert '\033[' in rendered  # ANSI escape code
    print("✓ Color rendering test passed")


def test_focus_rendering():
    """Test focus rendering"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    renderer = GridRenderer()
    
    grid_text = """AB
CD"""
    parsed = parser.parse_grid(grid_text, "Focus Test")
    
    rendered = renderer.render(parsed, focused_cell=(0, 0))
    assert rendered is not None
    print("✓ Focus rendering test passed")


def test_style_generator():
    """Test style ANSI code generation"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    style = Style(fg_color='#FF0000', bold=True, underline=True)
    ansi = style.to_ansi(ColorMode.FULL)
    
    assert ansi is not None
    assert '38;5;196' in ansi  # Red color
    assert '1' in ansi  # Bold
    assert '4' in ansi  # Underline
    print("✓ Style generator test passed")


# ============================================================================
# USXD Integration Tests
# ============================================================================

def test_grid_to_usxd():
    """Test converting ASCII grid to USXD document"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    registry = USXDRegistry()
    
    grid_text = """┌───┐
│ A │
└───┘"""
    parsed = parser.parse_grid(grid_text, "Grid to USXD Test")
    
    # Create USXD document
    metadata = USXDMetadata(
        id="test-grid-usxd",
        title="Grid Test Document",
        version="1.0.0",
        description="Test converting grid to USXD"
    )
    
    doc = USXDDocument(metadata=metadata)
    
    # Add parsed grid as section
    structured = parser.to_structured(parsed)
    grid_section = USXDSection(
        id="grid_section",
        name="ASCII Grid",
        section_type="data",
        content=structured,
        format="application/x-usxd-grid"
    )
    doc.add_section(grid_section)
    
    # Verify document
    assert doc.verify_integrity()
    assert len(doc.sections) == 1
    print("✓ Grid to USXD test passed")


def test_usxd_json_roundtrip():
    """Test USXD JSON serialization/deserialization"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    registry = USXDRegistry()
    
    metadata = USXDMetadata(
        id="test-roundtrip",
        title="Roundtrip Test",
        version="1.0.0"
    )
    
    doc = USXDDocument(metadata=metadata)
    doc.add_section(USXDSection(
        id="section1",
        name="Test Section",
        section_type="content",
        content="Test content"
    ))
    
    # Serialize
    json_str = doc.to_json()
    assert json_str is not None
    
    # Deserialize
    doc_back = USXDDocument.from_json(json_str)
    assert doc_back.metadata.id == "test-roundtrip"
    assert doc_back.verify_integrity()
    assert len(doc_back.sections) == 1
    print("✓ USXD JSON roundtrip test passed")


def test_usxd_registry():
    """Test USXD registry operations"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    registry = USXDRegistry()
    
    metadata = USXDMetadata(
        id="test-registry-e2e",
        title="Registry Test E2E",
        version="1.0.0"
    )
    
    doc = USXDDocument(metadata=metadata)
    
    # Save to registry
    filepath = registry.save_document(doc)
    assert filepath.exists()
    
    # List documents
    docs = registry.list_documents()
    assert len(docs) > 0
    
    # Find our document
    found = False
    for doc_info in docs:
        if doc_info.get('id') == 'test-registry-e2e':
            found = True
            break
    
    assert found, "Document not found in registry"
    
    # Load document
    loaded = registry.load_document(filepath.name)
    assert loaded.metadata.id == 'test-registry-e2e'
    
    print("✓ USXD registry test passed")


# ============================================================================
# End-to-End Pipeline Tests
# ============================================================================

def test_full_pipeline_ascii_to_rendered():
    """Test complete pipeline: ASCII → Parsed → Mapped → Rendered"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    mapper = ComponentMapper()
    renderer = GridRenderer()
    
    # Step 1: Parse ASCII grid
    grid_text = """┌───┬───┐
│ A │ B │
├───┼───┤
│ C │ D │
└───┴───┘"""
    
    parsed = parser.parse_grid(grid_text, "Full Pipeline Test")
    assert parsed.rows == 5
    assert parsed.cols == 9
    
    # Step 2: Add components
    button_a = GridComponent(
        id="button_a",
        name="Button A",
        component_type="widget",
        cells=[(1, 1)]
    )
    button_b = GridComponent(
        id="button_b",
        name="Button B",
        component_type="widget",
        cells=[(1, 4)]
    )
    parsed.add_component(button_a)
    parsed.add_component(button_b)
    
    # Step 3: Map to ThinUI components
    thinui_tree = mapper.map_grid(parsed)
    assert thinui_tree is not None
    assert len(thinui_tree.children) > 0
    
    # Step 4: Create layout
    layout = mapper.create_grid_layout(parsed)
    assert layout['type'] == 'grid'
    
    # Step 5: Render to terminal
    rendered = renderer.render(parsed)
    assert rendered is not None
    assert len(rendered) > 0
    
    print("✓ Full pipeline (ASCII → Parsed → Mapped → Rendered) test passed")


def test_full_pipeline_to_usxd_document():
    """Test complete pipeline: ASCII → Parsed → USXD Document"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    mapper = ComponentMapper()
    registry = USXDRegistry()
    
    # Step 1: Parse grid
    grid_text = """┌───┐
│ OK │
└───┘"""
    
    parsed = parser.parse_grid(grid_text, "CLI Test Grid")
    assert parsed.rows == 3
    
    # Step 2: Add component with action
    button = GridComponent(
        id="ok_button",
        name="OK Button",
        component_type="widget",
        properties={"action": "submit"},
        cells=[(1, 1), (1, 2), (1, 3)]
    )
    parsed.add_component(button)
    
    # Step 3: Map to layout
    layout = mapper.create_grid_layout(parsed)
    
    # Step 4: Create USXD document
    metadata = USXDMetadata(
        id="pipeline-test-e2e",
        title="Pipeline Test Document",
        version="1.0.0",
        description="End-to-end pipeline test"
    )
    
    doc = USXDDocument(metadata=metadata)
    
    # Add grid as section
    grid_section = USXDSection(
        id="grid_data",
        name="Parsed Grid",
        section_type="data",
        content=layout,
        format="application/x-usxd-grid-layout"
    )
    doc.add_section(grid_section)
    
    # Add raw text as section
    raw_section = USXDSection(
        id="raw_text",
        name="Raw Text",
        section_type="content",
        content=grid_text
    )
    doc.add_section(raw_section)
    
    # Verify
    assert doc.verify_integrity()
    assert len(doc.sections) == 2
    
    # Save to registry
    filepath = registry.save_document(doc)
    assert filepath.exists()
    
    # Load and verify
    loaded = registry.load_document(filepath.name)
    assert loaded.metadata.id == "pipeline-test-e2e"
    assert loaded.verify_integrity()
    
    print("✓ Full pipeline to USXD document test passed")


def test_pipeline_with_colors():
    """Test pipeline with colored components"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    mapper = ComponentMapper()
    renderer = GridRenderer()
    
    grid_text = """RED
GRN
BLU"""
    
    parsed = parser.parse_grid(grid_text, "Color Test")
    
    # Add components with colors
    red_comp = GridComponent(
        id="red",
        name="Red",
        component_type="label",
        cells=[(0, 0), (0, 1), (0, 2)]
    )
    green_comp = GridComponent(
        id="green",
        name="Green",
        component_type="label",
        cells=[(1, 0), (1, 1), (1, 2)]
    )
    blue_comp = GridComponent(
        id="blue",
        name="Blue",
        component_type="label",
        cells=[(2, 0), (2, 1), (2, 2)]
    )
    
    parsed.add_component(red_comp)
    parsed.add_component(green_comp)
    parsed.add_component(blue_comp)
    
    # Map with custom colors
    mapper.add_mapping(
        grid_component_id="red",
        properties=ThinUIProperties(
            component_type=ComponentType.LABEL,
            fg_color="#FF0000"
        )
    )
    mapper.add_mapping(
        grid_component_id="green",
        properties=ThinUIProperties(
            component_type=ComponentType.LABEL,
            fg_color="#00FF00"
        )
    )
    mapper.add_mapping(
        grid_component_id="blue",
        properties=ThinUIProperties(
            component_type=ComponentType.LABEL,
            fg_color="#0000FF"
        )
    )
    
    # Render
    rendered = renderer.render(parsed)
    assert rendered is not None
    
    print("✓ Pipeline with colors test passed")


# ============================================================================
# CLI Integration Tests
# ============================================================================

def test_usxd_cli_help():
    """Test USXD CLI help command"""
    cwd = str(Path(__file__).parent.parent)
    result = subprocess.run(
        [sys.executable, "usxd_cli.py", "--help"],
        cwd=cwd,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    # Remove ANSI codes
    import re
    clean = re.sub(r'\033\[[0-9;]*[JHjh]', '', result.stdout)
    clean = re.sub(r'\033\[[0-9;]*m', '', clean)
    assert "USXD CLI" in clean
    assert "parse" in clean
    assert "render" in clean
    print("✓ USXD CLI help test passed")


def test_binder_cli_help():
    """Test Binder CLI help command"""
    import re
    cwd = str(Path(__file__).parent.parent)
    result = subprocess.run(
        [sys.executable, "binder_cli.py", "--help"],
        cwd=cwd,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    clean = re.sub(r'\033\[[0-9;]*[JHjh]', '', result.stdout)
    clean = re.sub(r'\033\[[0-9;]*m', '', clean)
    assert "Binder CLI" in clean
    assert "list" in clean
    assert "create" in clean
    print("✓ Binder CLI help test passed")


def test_usxd_cli_list():
    """Test USXD CLI list command"""
    import re
    cwd = str(Path(__file__).parent.parent)
    result = subprocess.run(
        [sys.executable, "usxd_cli.py", "list"],
        cwd=cwd,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    clean = re.sub(r'\033\[[0-9;]*[JHjh]', '', result.stdout)
    clean = re.sub(r'\033\[[0-9;]*m', '', clean)
    assert "Available USXD Documents" in clean
    print("✓ USXD CLI list test passed")


def test_binder_cli_list():
    """Test Binder CLI list command"""
    import re
    cwd = str(Path(__file__).parent.parent)
    result = subprocess.run(
        [sys.executable, "binder_cli.py", "list"],
        cwd=cwd,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0
    clean = re.sub(r'\033\[[0-9;]*[JHjh]', '', result.stdout)
    clean = re.sub(r'\033\[[0-9;]*m', '', clean)
    assert "Available Binders" in clean
    print("✓ Binder CLI list test passed")


def test_usxd_cli_grid_parse():
    """Test USXD CLI grid parse command"""
    import re
    cwd = str(Path(__file__).parent.parent)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("┌───┐\n│ A │\n└───┘\n")
        temp_file = f.name
    
    try:
        result = subprocess.run(
            [sys.executable, "usxd_cli.py", "grid", "parse", "--file", temp_file, "--title", "CLI Test"],
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        clean = re.sub(r'\033\[[0-9;]*[JHjh]', '', result.stdout)
        clean = re.sub(r'\033\[[0-9;]*m', '', clean)
        assert "Parsed grid" in clean
        assert "3x5" in clean
        print("✓ USXD CLI grid parse test passed")
    finally:
        os.unlink(temp_file)


# ============================================================================
# Performance Tests
# ============================================================================

def test_large_grid_parsing():
    """Test parsing large grid"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    
    # Create 100x100 grid
    rows = []
    for i in range(100):
        row = ''.join(chr(65 + (j % 26)) for j in range(100))
        rows.append(row)
    grid_text = '\n'.join(rows)
    
    start = time.time()
    parsed = parser.parse_grid(grid_text, "Performance Test")
    end = time.time()
    
    duration = end - start
    assert parsed.rows == 100
    assert parsed.cols == 100
    assert duration < 5.0, f"Large grid parsing too slow: {duration}s"
    print(f"✓ Large grid parsing test passed ({duration:.3f}s)")


def test_auto_component_detection_performance():
    """Test performance of component detection"""
    if not CORE_PY_USXD_AVAILABLE:
        return
    
    parser = ASCIIGridParser()
    
    # Grid with many components
    grid_text = '\n'.join([f"{chr(65 + i)*10}" for i in range(26)])
    
    start = time.time()
    components = parser.split_into_components(grid_text)
    end = time.time()
    
    duration = end - start
    assert len(components) == 26
    assert duration < 2.0, f"Component detection too slow: {duration}s"
    print(f"✓ Auto component detection performance test passed ({duration:.3f}s)")


# ============================================================================
# Test Runner
# ============================================================================

def run_all_tests():
    """Run all tests"""
    if not TEST_IMPORTS:
        print("❌ Required modules not available. Skipping tests.")
        return False
    
    print("🧪 Running End-to-End USXD Pipeline Tests...")
    print("=" * 60)
    
    # Define all test functions
    test_functions = [
        # ASCII Grid Parser Tests
        test_simple_grid_parsing,
        test_box_drawing_parsing,
        test_markdown_table_parsing,
        test_csv_parsing,
        test_json_serialization,
        test_component_detection,
        
        # Component Mapper Tests
        test_basic_mapping,
        test_custom_mapping,
        test_layout_creation,
        test_teletext_layout,
        test_html_generation,
        
        # Grid Renderer Tests
        test_simple_rendering,
        test_color_rendering,
        test_focus_rendering,
        test_style_generator,
        
        # USXD Integration Tests
        test_grid_to_usxd,
        test_usxd_json_roundtrip,
        test_usxd_registry,
        
        # End-to-End Pipeline Tests
        test_full_pipeline_ascii_to_rendered,
        test_full_pipeline_to_usxd_document,
        test_pipeline_with_colors,
        
        # CLI Integration Tests
        test_usxd_cli_help,
        test_binder_cli_help,
        test_usxd_cli_list,
        test_binder_cli_list,
        test_usxd_cli_grid_parse,
        
        # Performance Tests
        test_large_grid_parsing,
        test_auto_component_detection_performance,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        test_name = test_func.__name__
        print(f"\n📋 {test_name}")
        
        success, error = run_test(test_func)
        if success:
            passed += 1
        else:
            print(f"❌ {test_name}: {error}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed > 0:
        print("❌ Some tests failed")
        return False
    else:
        print("✅ All tests passed!")
        return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
