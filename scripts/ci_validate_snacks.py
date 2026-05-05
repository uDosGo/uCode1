#!/usr/bin/env python3
"""
CI script: Find and validate all snack.yaml files in the repository.
Exits with code 1 if any snack manifest is invalid.
"""
import os
import sys
import yaml

REQUIRED_FIELDS = ["name", "version"]
errors = 0
found = 0

for root, dirs, files in os.walk("."):
    # Skip common non-project directories
    dirs[:] = [d for d in dirs if d not in ("__pycache__", ".venv", "node_modules", "dist", "build", ".git")]
    for f in files:
        if f == "snack.yaml":
            path = os.path.join(root, f)
            found += 1
            print(f"Validating: {path}")
            try:
                with open(path) as fh:
                    data = yaml.safe_load(fh)
                if data is None:
                    print(f"  FAIL: Empty YAML file")
                    errors += 1
                    continue
                missing = [r for r in REQUIRED_FIELDS if r not in data]
                if missing:
                    print(f"  FAIL: Missing required fields: {missing}")
                    errors += 1
                    continue
                print(f"  OK: {data['name']} v{data['version']}")
            except yaml.YAMLError as e:
                print(f"  FAIL: YAML parse error: {e}")
                errors += 1
            except Exception as e:
                print(f"  FAIL: {e}")
                errors += 1

print(f"\nFound {found} snack manifest(s)")
if errors:
    print(f"{errors} validation error(s) found")
    sys.exit(1)
else:
    print("All snack manifests valid")
