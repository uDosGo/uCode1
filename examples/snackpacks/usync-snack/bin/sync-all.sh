#!/bin/bash
# Comprehensive Sync Management Script for uDosGo Ecosystem

set -e

echo "🔄 Starting uDosGo Ecosystem Sync..."
echo "Timestamp: $(date)"
echo "=================================="

# Function to sync a repository
sync_repo() {
    local repo_path=$1
    local repo_name=$2
    
    echo ""
    echo "Syncing $repo_name..."
    
    if [ -d "$repo_path" ]; then
        cd "$repo_path"
        
        # Check if it's a git repository
        if [ -d ".git" ]; then
            # Get current branch
            local branch=$(git branch --show-current 2>/dev/null || echo "main")
            
            echo "  Branch: $branch"
            
            # Check for changes
            if [ -n "$(git status --porcelain)" ]; then
                echo "  ✓ Changes detected, committing..."
                git add .
                git commit -m "Auto-sync: $(date)"
            else
                echo "  ✓ No changes"
            fi
            
            # Pull and push
            git pull --rebase
            git push origin "$branch"
            
            echo "  ✅ $repo_name synced successfully"
        else
            echo "  ⚠️  Not a git repository: $repo_path"
        fi
    else
        echo "  ❌ Repository not found: $repo_path"
    fi
}

# @uDosGo Repositories
echo ""
echo "Syncing @uDosGo repositories..."
sync_repo "~/uDos/Go/Connect" "Connect"
sync_repo "~/uDos/Dev/Framework" "Framework"
sync_repo "~/uDos/Home" "Home"
sync_repo "~/uDos/Go/3dWorld" "World"
sync_repo "~/Code/Apps/GrooveBox888" "Groovebox"
sync_repo "~/uDos/inbox" "inbox"
sync_repo "~/uDos/outbox" "outbox"

# @AgentDigitalCo Repositories
echo ""
echo "Syncing @AgentDigitalCo repositories..."
sync_repo "~/Code/AgentDigitalCoFramework" "AgentDigitalCo Framework"
sync_repo "~/Code/Apps/Marksmith" "Marksmith"
sync_repo "~/Code/Apps/McSnackbar" "McSnackbar"
sync_repo "~/Code/Apps/AppStoreDocs" "AppStoreDocs"

# Personal Vault
echo ""
echo "Syncing Vault..."
sync_repo "~/Vault" "Vault"

echo ""
echo "=================================="
echo "✅ All repositories synced!"
echo "Completed: $(date)"

# Return to original directory
cd - > /dev/null