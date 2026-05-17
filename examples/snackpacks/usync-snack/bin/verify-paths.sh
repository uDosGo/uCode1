#!/bin/bash
# Final Path Verification Script

echo "🔍 Verifying uDosGo Path Structure"
echo "=================================="

ISSUES=0

# Test 1: Check lowercase inbox/outbox
echo ""
echo "1. Checking inbox/outbox (should be lowercase)..."
if [ -d "$HOME/uDos/inbox" ]; then
  echo "✅ inbox exists (lowercase)"
else
  echo "❌ inbox missing or wrong case"
  ISSUES=$((ISSUES+1))
fi

if [ -d "$HOME/uDos/outbox" ]; then
  echo "✅ outbox exists (lowercase)"
else
  echo "❌ outbox missing or wrong case"
  ISSUES=$((ISSUES+1))
fi

# Test 2: Check TitleCase system paths
echo ""
echo "2. Checking system paths (should be TitleCase)..."
if [ -d "$HOME/uDosGo/Memory/State" ]; then
  echo "✅ Memory/State/ exists"
else
  echo "❌ Memory/State/ missing"
  ISSUES=$((ISSUES+1))
fi

if [ -d "$HOME/uDosGo/Core/Connect" ]; then
  echo "✅ Core/Connect/ exists"
else
  echo "❌ Core/Connect/ missing"
  ISSUES=$((ISSUES+1))
fi

if [ -d "$HOME/uDosGo/Dev/Framework" ]; then
  echo "✅ Dev/Framework/ exists"
else
  echo "❌ Dev/Framework/ missing"
  ISSUES=$((ISSUES+1))
fi

# Test 3: Check Vault structure
echo ""
echo "3. Checking Vault structure (should be lowercase)..."
if [ -d "$HOME/Vault/documents" ]; then
  echo "✅ Vault/documents/ exists"
else
  echo "❌ Vault/documents/ missing"
  ISSUES=$((ISSUES+1))
fi

if [ -d "$HOME/Vault/notes" ]; then
  echo "✅ Vault/notes/ exists"
else
  echo "❌ Vault/notes/ missing"
  ISSUES=$((ISSUES+1))
fi

# Test 4: Check for old TitleCase paths
echo ""
echo "4. Checking for deprecated TitleCase paths..."
if [ -d "$HOME/uDos/Inbox" ]; then
  echo "❌ Old Inbox/ still exists (should be inbox/)"
  ISSUES=$((ISSUES+1))
fi

if [ -d "$HOME/uDos/Outbox" ]; then
  echo "❌ Old Outbox/ still exists (should be outbox/)"
  ISSUES=$((ISSUES+1))
fi

# Test 5: Check workspace CLI
echo ""
echo "5. Checking workspace management..."
if [ -f "$HOME/Code/Dev/Usync/bin/workspace" ]; then
  echo "✅ workspace CLI exists"
else
  echo "❌ workspace CLI missing"
  ISSUES=$((ISSUES+1))
fi

# Test 6: Check configuration files
echo ""
echo "6. Checking configuration files..."
if [ -f "$HOME/uDos/inbox/.rules.yaml" ]; then
  echo "✅ inbox/.rules.yaml exists"
else
  echo "❌ inbox/.rules.yaml missing"
  ISSUES=$((ISSUES+1))
fi

if [ -f "$HOME/uDos/outbox/.queue.yaml" ]; then
  echo "✅ outbox/.queue.yaml exists"
else
  echo "❌ outbox/.queue.yaml missing"
  ISSUES=$((ISSUES+1))
fi

# Final summary
echo ""
echo "=================================="
if [ $ISSUES -eq 0 ]; then
  echo "✅ All paths correct!"
  echo "🎯 uDosGo path structure is properly configured."
  exit 0
else
  echo "⚠️  Found $ISSUES issues that need attention."
  echo "Run: verify-paths.sh --fix to attempt automatic fixes."
  exit 1
fi