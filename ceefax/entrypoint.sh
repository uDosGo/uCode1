#!/bin/bash
# Ceefax Container Entrypoint
#
# Mounts the Vendor CEETEX repo and starts the Ceefax teletext service.
# The CEETEX repo is expected at /vendor/ceetex (mounted from ~/Code/Vendor/ceetex).

set -e

echo "=== Ceefax Teletext Service ==="
echo "Starting Ceefax engine..."

# Check for Vendor CEETEX
if [ -d "/vendor/ceetex" ]; then
    echo "Vendor CEETEX found at /vendor/ceetex"
    # Add to Python path so Ceefax can import from it
    export PYTHONPATH="/vendor/ceetex:${PYTHONPATH}"
else
    echo "WARNING: Vendor CEETEX not mounted at /vendor/ceetex"
    echo "Run with: -v ~/Code/Vendor/ceetex:/vendor/ceetex"
fi

# Start the Ceefax API server
echo "Starting Ceefax API on port 8080..."
exec uvicorn engine.teletext_api:app \
    --host 0.0.0.0 \
    --port 8080 \
    --log-level info
