#!/usr/bin/env python3
"""
ThinUI Integration Tests

Tests for the CAD▶ThinUI bridge functionality.
"""

import sys
import os
import json
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core_py.thinui import (
    ThinUIGridBridge, ThinUIGridData,
    ThinUILayout, ThinUIComponent, ThinUIComponentType, ThinUIColor, ThinUIFormat
)
from core_py.usxd import ASCIIGridParser, ParsedGrid


def test_thinui_bridge_creation():
    """Test ThinUIGridBridge can be created"""
    bridge = ThinUIGridBridge()
    assert bridge is not None
    assert bridge.parser is not None
    assert bridge.mapper is not None
    assert bridge.renderer is not None
    print("✓ ThinUIGridBridge creation test passed")


def test_thinui_color_conversion():
    """Test color conversion between formats"""
    # Test hex color
    color = ThinUIColor(hex="#FF0000")
    assert color.to_css() == "#FF0000"
    
    # Test ANSI color conversion
    color = ThinUIColor.from_ansi_code(9)  # Red
    assert color.to_css() == "#FF0000"
    
    # Test named color
    color = ThinUIColor(name="red")
    assert color.to_css() == "red"
    
    # Test RGB color
    color = ThinUIColor(rgb="rgb(255,0,0)")
    assert color.to_css() == "rgb(255,0,0)"
    
    print("✓ ThinUI color conversion test passed")


def test_parse_to_thinui():
    """Test parsing ASCII grid to ThinUI format"""
    bridge = ThinUIGridBridge()
    
    grid_text = """┌───┐
│ A │
└───┘"""
    
    result = bridge.parse_to_thinui(grid_text, "Test Grid")
    
    assert result is not None
    assert isinstance(result, ThinUIGridData)
    assert result.rows == 3
    assert result.cols == 5
    assert result.title == "Test Grid"
    assert result.format == "box"
    assert len(result.cells) == 3
    assert result.layout is not None
    
    print("✓ Parse to ThinUI test passed")


def test_parsed_grid_to_thinui():
    """Test converting ParsedGrid to ThinUI format"""
    bridge = ThinUIGridBridge()
    parser = ASCIIGridParser()
    
    grid_text = """ABC
DEF
GHI"""
    parsed = parser.parse_grid(grid_text, "Simple Grid")
    
    result = bridge.parsed_grid_to_thinui(parsed)
    
    assert result.rows == 3
    assert result.cols == 3
    assert result.title == "Simple Grid"
    assert len(result.cells) == 3
    assert len(result.cells[0]) == 3  # Row 0 has 3 columns
    
    # Check cell data
    assert result.cells[0][0]['char'] == 'A'
    assert result.cells[0][0]['row'] == 0
    assert result.cells[0][0]['col'] == 0
    
    print("✓ ParsedGrid to ThinUI test passed")


def test_thinui_component_tree():
    """Test creating ThinUI component tree from parsed grid"""
    bridge = ThinUIGridBridge()
    parser = ASCIIGridParser()
    
    grid_text = """┌───┐
│ OK │
└───┘"""
    parsed = parser.parse_grid(grid_text, "Component Test")
    
    tree = bridge.create_thinui_component_tree(parsed)
    
    assert tree is not None
    assert isinstance(tree, ThinUIComponent)
    assert tree.component_type == ThinUIComponentType.CONTAINER
    assert tree.width == parsed.cols
    assert tree.height == parsed.rows
    assert len(tree.children) > 0
    
    # Check that we have children components
    assert len(tree.children) > 0
    
    print("✓ ThinUI component tree test passed")


def test_thinui_layout_from_parsed_grid():
    """Test ThinUILayout creation from ParsedGrid"""
    parser = ASCIIGridParser()
    
    grid_text = """A|B
-+-
C|D"""
    parsed = parser.parse_grid(grid_text, "Layout Test")
    
    layout = ThinUILayout.from_parsed_grid(parsed)
    
    assert layout is not None
    assert isinstance(layout, ThinUILayout)
    assert layout.title == "Layout Test"
    assert layout.format.type == "grid-layout"
    assert layout.root is not None
    assert layout.grid is not None
    assert layout.grid['rows'] == 3
    assert layout.grid['cols'] == 3
    
    # Test JSON serialization
    json_str = layout.to_json()
    assert json_str is not None
    
    # Parse back to verify
    parsed_json = json.loads(json_str)
    assert parsed_json['title'] == "Layout Test"
    assert parsed_json['grid']['rows'] == 3
    
    print("✓ ThinUILayout from ParsedGrid test passed")


def test_thinui_with_colors():
    """Test ThinUI handling of colored grids"""
    bridge = ThinUIGridBridge()
    parser = ASCIIGridParser()
    
    grid_text = """R
G
B"""
    parsed = parser.parse_grid(grid_text, "Color Test")
    
    # Add colors to cells
    parsed.get_cell(0, 0).fg_color = '#FF0000'
    parsed.get_cell(1, 0).fg_color = '#00FF00'
    parsed.get_cell(2, 0).fg_color = '#0000FF'
    
    result = bridge.parsed_grid_to_thinui(parsed)
    
    assert result.cells[0][0]['fgColor'] == '#FF0000'
    assert result.cells[1][0]['fgColor'] == '#00FF00'
    assert result.cells[2][0]['fgColor'] == '#0000FF'
    
    print("✓ ThinUI with colors test passed")


def test_thinui_json_serialization():
    """Test JSON serialization of ThinUI data structures"""
    # Test ThinUIGridData
    grid_data = ThinUIGridData(
        rows=2,
        cols=2,
        cells=[
            [{'char': 'A', 'row': 0, 'col': 0}, {'char': 'B', 'row': 0, 'col': 1}],
            [{'char': 'C', 'row': 1, 'col': 0}, {'char': 'D', 'row': 1, 'col': 1}]
        ],
        title="JSON Test"
    )
    
    json_str = grid_data.to_json()
    assert json_str is not None
    
    # Parse back
    parsed = json.loads(json_str)
    assert parsed['rows'] == 2
    assert parsed['cols'] == 2
    assert parsed['title'] == "JSON Test"
    
    # Test ThinUIColor
    color = ThinUIColor(hex="#123456", name="test-color")
    color_dict = color.to_dict()
    assert color_dict['hex'] == "#123456"
    assert color_dict['name'] == "test-color"
    
    print("✓ ThinUI JSON serialization test passed")


def test_threshold_box_drawing_detection():
    """Test box drawing character detection in component tree"""
    bridge = ThinUIGridBridge()
    parser = ASCIIGridParser()
    
    grid_text = """┌─┐
│ │
└─┘"""
    parsed = parser.parse_grid(grid_text, "Box Drawing Test")
    
    # Create component tree with box drawing detection
    tree = bridge.create_thinui_component_tree(parsed, include_box_drawing=True)
    
    # Check that we have box components
    box_components = [
        c for c in flatten_components(tree) 
        if c.component_type == ThinUIComponentType.BOX
    ]
    assert len(box_components) >= 2, f"Expected at least 2 box components, got {len(box_components)}"
    
    # Check that we have line components
    line_components = [
        c for c in flatten_components(tree) 
        if c.component_type == ThinUIComponentType.LINE
    ]
    assert len(line_components) >= 2, f"Expected at least 2 line components, got {len(line_components)}"
    
    print("✓ Box drawing detection test passed")


def flatten_components(component: ThinUIComponent) -> List[ThinUIComponent]:
    """Flatten a component tree into a list"""
    result = [component]
    for child in component.children:
        result.extend(flatten_components(child))
    return result


def run_all_tests():
    """Run all ThinUI integration tests"""
    print("🧪 Running ThinUI Integration Tests...")
    print("=" * 60)
    
    test_functions = [
        test_thinui_bridge_creation,
        test_thinui_color_conversion,
        test_parse_to_thinui,
        test_parsed_grid_to_thinui,
        test_thinui_component_tree,
        test_thinui_layout_from_parsed_grid,
        test_thinui_with_colors,
        test_thinui_json_serialization,
        test_threshold_box_drawing_detection,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        test_name = test_func.__name__
        print(f"\n📋 {test_name}")
        
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: {e}")
            import traceback
            traceback.print_exc()
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
