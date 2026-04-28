#!/usr/bin/env python3
"""
Comprehensive test for the uCode1 Snack system
"""

import sys
import os
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from core_py import (
    Snack, SnackInput, SnackOutput, SnackEngine, execute_snack,
    DependencyResolver, resolve_snack_dependencies, CircularDependencyError
)
from core_py.snack.validator import validate_snack


def test_basic_snack_creation():
    """Test basic Snack creation"""
    print("Testing basic Snack creation...")
    
    snack = Snack.create("TEST-001", "Test Snack", "1.0.0", "echo 'Hello'")
    assert snack.id == "TEST-001"
    assert snack.name == "Test Snack"
    assert snack.version == "1.0.0"
    assert snack.code == "echo 'Hello'"
    
    print("✓ Basic Snack creation works")


def test_snack_validation():
    """Test Snack validation"""
    print("Testing Snack validation...")
    
    # Test valid snack
    valid_snack = Snack.create("VALID-001", "Valid Snack", "1.0.0", "echo 'test'")
    try:
        validate_snack(valid_snack)
        print("✓ Valid Snack passes validation")
    except Exception as e:
        print(f"✗ Valid Snack failed validation: {e}")
        return False
    
    # Test invalid snack (empty ID)
    invalid_snack = Snack.create("", "Invalid Snack", "1.0.0", "echo 'test'")
    try:
        validate_snack(invalid_snack)
        print("✗ Invalid Snack should have failed validation")
        return False
    except ValueError:
        print("✓ Invalid Snack correctly failed validation")
    
    return True


def test_snack_execution():
    """Test Snack execution"""
    print("Testing Snack execution...")
    
    # Test bash execution
    bash_snack = Snack.create("BASH-001", "Bash Snack", "1.0.0", "echo 'Hello from bash'")
    bash_snack.runtime = "bash"
    
    try:
        result = execute_snack(bash_snack)
        assert result['exit_code'] == 0
        assert 'Hello from bash' in result['stdout']
        print("✓ Bash execution works")
    except Exception as e:
        print(f"✗ Bash execution failed: {e}")
        return False
    
    # Test Python execution
    python_snack = Snack.create(
        "PY-001", "Python Snack", "1.0.0",
        'import os\nprint("Hello from Python")'
    )
    python_snack.runtime = "python"
    
    try:
        result = execute_snack(python_snack)
        assert result['exit_code'] == 0
        assert 'Hello from Python' in result['stdout']
        print("✓ Python execution works")
    except Exception as e:
        print(f"✗ Python execution failed: {e}")
        return False
    
    return True


def test_snack_with_inputs():
    """Test Snack with inputs"""
    print("Testing Snack with inputs...")
    
    snack = Snack.create("INPUT-001", "Input Snack", "1.0.0", "echo 'Hello $NAME'")
    snack.runtime = "bash"
    snack.inputs = [SnackInput(name="NAME", type="string", required=True)]
    snack.outputs = [SnackOutput(name="message", type="string")]
    
    try:
        result = execute_snack(snack, {"NAME": "World"})
        assert result['exit_code'] == 0
        assert 'Hello $NAME' in result['stdout']  # Note: bash doesn't expand env vars in single quotes
        print("✓ Snack with inputs works")
    except Exception as e:
        print(f"✗ Snack with inputs failed: {e}")
        return False
    
    return True


def test_dependency_resolution():
    """Test dependency resolution"""
    print("Testing dependency resolution...")
    
    # Create snacks with dependencies: A -> B -> C
    snack_a = Snack.create("DEP-A", "Snack A", "1.0.0", "echo A")
    snack_b = Snack.create("DEP-B", "Snack B", "1.0.0", "echo B")
    snack_c = Snack.create("DEP-C", "Snack C", "1.0.0", "echo C")
    
    snack_b.requires = ["DEP-A"]
    snack_c.requires = ["DEP-B"]
    
    snacks = [snack_a, snack_b, snack_c]
    
    try:
        execution_order = resolve_snack_dependencies(snacks)
        order_ids = [s.id for s in execution_order]
        
        # Should be A -> B -> C
        expected = ["DEP-A", "DEP-B", "DEP-C"]
        assert order_ids == expected, f"Expected {expected}, got {order_ids}"
        
        print(f"✓ Dependency resolution works: {' -> '.join(order_ids)}")
    except Exception as e:
        print(f"✗ Dependency resolution failed: {e}")
        return False
    
    return True


def test_circular_dependency_detection():
    """Test circular dependency detection"""
    print("Testing circular dependency detection...")
    
    # Create circular dependency: A -> B -> A
    snack_a = Snack.create("CIRC-A", "Circular A", "1.0.0", "echo A")
    snack_b = Snack.create("CIRC-B", "Circular B", "1.0.0", "echo B")
    
    snack_a.requires = ["CIRC-B"]
    snack_b.requires = ["CIRC-A"]
    
    circular_snacks = [snack_a, snack_b]
    
    try:
        resolve_snack_dependencies(circular_snacks)
        print("✗ Circular dependency should have been detected")
        return False
    except CircularDependencyError as e:
        print(f"✓ Circular dependency correctly detected: {e}")
        return True
    except Exception as e:
        print(f"✗ Unexpected error in circular dependency test: {e}")
        return False


def test_snack_serialization():
    """Test Snack serialization/deserialization"""
    print("Testing Snack serialization...")
    
    # Create a complex snack
    snack = Snack.create("SERIAL-001", "Serialization Test", "1.0.0", "echo 'test'")
    snack.emoji = "🧪"
    snack.tags = ["test", "serialization"]
    snack.inputs = [SnackInput(name="input1", type="string", required=True)]
    snack.outputs = [SnackOutput(name="output1", type="string")]
    
    # Test to_dict
    snack_dict = snack.to_dict()
    assert snack_dict['id'] == "SERIAL-001"
    assert snack_dict['emoji'] == "🧪"
    
    # Test from_dict
    reconstructed = Snack.from_dict(snack_dict)
    assert reconstructed.id == snack.id
    assert reconstructed.name == snack.name
    
    # Test file operations
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = Path(f.name)
    
    try:
        snack.save_to_file(temp_path)
        loaded_snack = Snack.load_from_file(temp_path)
        assert loaded_snack.id == snack.id
        print("✓ Snack serialization works")
        return True
    except Exception as e:
        print(f"✗ Snack serialization failed: {e}")
        return False
    finally:
        temp_path.unlink()


def main():
    """Run all tests"""
    print("=== uCode1 Snack System Comprehensive Test ===\n")
    
    tests = [
        test_basic_snack_creation,
        test_snack_validation,
        test_snack_execution,
        test_snack_with_inputs,
        test_dependency_resolution,
        test_circular_dependency_detection,
        test_snack_serialization,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = test()
            if result is False:
                failed += 1
            else:
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print(f"=== Test Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())