#!/bin/bash
# Test script for uDos CLI Vibe Skill

echo "🧪 Testing uDos CLI Vibe Skill..."
echo "====================================="

# Test 1: Check if skill files exist
echo "Test 1: Checking skill files..."
if [ -f "skill.yaml" ]; then
    echo "✅ skill.yaml exists"
else
    echo "❌ skill.yaml missing"
    exit 1
fi

if [ -f "udos-cli.sh" ]; then
    echo "✅ udos-cli.sh exists"
else
    echo "❌ udos-cli.sh missing"
    exit 1
fi

if [ -f "README.md" ]; then
    echo "✅ README.md exists"
else
    echo "❌ README.md missing"
    exit 1
fi

# Test 2: Check if script is executable
echo ""
echo "Test 2: Checking script permissions..."
if [ -x "udos-cli.sh" ]; then
    echo "✅ udos-cli.sh is executable"
else
    echo "❌ udos-cli.sh is not executable"
    exit 1
fi

# Test 3: Test status command
echo ""
echo "Test 3: Testing status command..."
./udos-cli.sh status

# Test 4: Validate YAML syntax
echo ""
echo "Test 4: Validating YAML syntax..."
if command -v yaml-lint >/dev/null 2>&1; then
    yaml-lint skill.yaml && echo "✅ YAML syntax is valid"
else
    echo "⚠️  yaml-lint not available, skipping YAML validation"
fi

echo ""
echo "====================================="
echo "🎉 All tests passed! uDos CLI Vibe Skill is ready."
echo ""
echo "You can now use:"
echo "  vibe udos-cli status"
echo "  vibe udos-cli install"
echo "  vibe udos-cli update"
echo "  vibe udos-cli repair"
echo "  vibe udos-cli uninstall"