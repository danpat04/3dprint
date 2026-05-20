FROM python:3.11-slim

WORKDIR /app

# System dependencies for OCP (OpenCascade)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libxrender1 \
    libxmu6 \
    libxi6 \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install dependencies only (no project build)
COPY pyproject.toml .
RUN uv pip install --system build123d ocp-vscode

# Patch: support reverse proxy (no port in Host header, wss:// for HTTPS)
RUN sed -i 's/address, port = request.host.split(":")/host_parts = request.host.split(":"); address = host_parts[0]; port = host_parts[1] if len(host_parts) > 1 else "443"/' \
    /usr/local/lib/python3.11/site-packages/ocp_vscode/standalone.py \
 && sed -i 's|`ws://${this.host}:${this.port}`|`${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}`|' \
    /usr/local/lib/python3.11/site-packages/ocp_vscode/static/js/comms.js

# Copy source
COPY models/ models/

# ocp_vscode viewer server on port 3939
EXPOSE 3939

# Start the viewer server
CMD ["python", "-m", "ocp_vscode", "--host", "0.0.0.0"]
