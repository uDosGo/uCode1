#!/usr/bin/env python3
# ~/Code/Dev/Usync/update-vault-structure.py

import os
import shutil
from pathlib import Path

def scan_and_update_vault(vault_path: Path):
    """Scan and update the Vault structure to align with new rules."""
    
    # Define the expected structure
    expected_structure = {
        "Binders": "750",
        "Data": "750",
        "@inbox": "700",
        "@outbox": "700",
        "@compost-inbox": "700",
        "@feeds": "700",
        "@sandbox": "700",
        "@toybox": "700",
        "@user": "700",
        "Assets": "700",
        "content": "700",
        "documents": "700",
        "feeds": "700",
        "handoff": "700",
        "learning": "700",
        "Notepad": "700",
        "notes": "700",
        "personal": "700",
        "Private": "700",
        "repos": "700",
        "spatial": "700",
        "spools": "700",
        "surfaces": "700",
        "system": "700",
        "Templates": "700",
        "tools": "700",
        "ucode": "700",
        "vault": "700"
    }
    
    # Scan the Vault directory
    for item in vault_path.iterdir():
        if item.name in expected_structure:
            # Check and update permissions
            expected_permissions = expected_structure[item.name]
            current_permissions = oct(os.stat(item).st_mode)[-3:]
            
            if current_permissions != expected_permissions:
                print(f"Updating permissions for {item.name}: {current_permissions} -> {expected_permissions}")
                os.chmod(item, int(expected_permissions, 8))
        else:
            print(f"Unexpected item in Vault: {item.name}")
    
    print("Vault structure scan and update complete.")

if __name__ == "__main__":
    vault_path = Path("/Users/fredbook/Vault")
    scan_and_update_vault(vault_path)