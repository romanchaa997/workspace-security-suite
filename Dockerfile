# Workspace Security Suite - Deployment Docker Image

FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY scripts/ ./scripts/
COPY configs/ ./configs/
COPY requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "-m", "scripts.google_workspace_api_monitor"]

# Build stage for documentation
FROM base as production
COPY docs/ ./docs/
LABEL maintainer="romanchaa997" \
      description="Workspace Security Suite - Enterprise-grade security audit tool" \
      version="1.0.0"
