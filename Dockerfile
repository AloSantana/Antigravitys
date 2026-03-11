# Multi-stage build for optimized Antigravity Workspace
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt backend/requirements.txt* ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    if [ -f backend/requirements.txt ]; then \
        pip install --no-cache-dir -r backend/requirements.txt; \
    fi

# Final stage
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create necessary directories with artifact subdirectories pre-created
WORKDIR /app
RUN mkdir -p /app/logs /app/drop_zone \
             /app/artifacts/code /app/artifacts/diffs /app/artifacts/tests \
             /app/artifacts/screenshots /app/artifacts/reports /app/artifacts/other \
             /app/data && \
    chown -R appuser:appuser /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set up entrypoint (runs as root to fix bind-mount ownership, then drops to appuser)
RUN chmod +x /app/scripts/docker-entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Entrypoint fixes permissions on bind-mounted volumes then drops to appuser via gosu
ENTRYPOINT ["/app/scripts/docker-entrypoint.sh"]

# Run the backend from its own directory so module imports are unambiguous
CMD ["sh", "-c", "cd /app/backend && exec python main.py"]
