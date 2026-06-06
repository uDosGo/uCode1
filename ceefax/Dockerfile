# Ceefax Container — Teletext RSS Reader Service
#
# Wraps the CEETEX engine (from ~/Code/Vendor/ceetex/) as a Docker service
# with LENS/SKIN/MCP adapters and GridUI surface mapping.
#
# Build:
#   docker build -t ceefax:latest .
#
# Run:
#   docker run -p 8080:8080 -v ~/Code/Vendor/ceetex:/vendor/ceetex ceefax:latest

FROM python:3.12-slim

LABEL org.udos.component="ceefax"
LABEL org.udos.description="Ceefax Teletext RSS Reader — containerised CEETEX engine"
LABEL org.udos.vendor-source="~/Code/Vendor/ceetex"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy Ceefax engine, adapters, and surface modules
COPY engine/ ./engine/
COPY lens/ ./lens/
COPY skin/ ./skin/
COPY mcp/ ./mcp/
COPY gridui/ ./gridui/
COPY spec/ ./spec/
COPY entrypoint.sh /entrypoint.sh

# Install Python dependencies
RUN pip install --no-cache-dir \
    textual \
    feedparser \
    rich \
    fastapi \
    uvicorn \
    httpx \
    websockets

# Make entrypoint executable
RUN chmod +x /entrypoint.sh

# Expose Ceefax API port
EXPOSE 8080

# Entrypoint mounts Vendor CEETEX and starts the service
ENTRYPOINT ["/entrypoint.sh"]
