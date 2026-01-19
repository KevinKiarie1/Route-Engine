# =============================================================================
# Farmer's Choice Logistics System - Production Dockerfile
# Multi-stage build for optimized, secure container
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Compile dependencies and create wheels
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    python3-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create wheels directory
WORKDIR /wheels

# Copy requirements and build wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir=/wheels -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Final - Production image
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS final

# Labels for container metadata
LABEL maintainer="Farmer's Choice DevOps <devops@farmerschoice.co.ke>" \
      version="1.0.0" \
      description="Farmer's Choice Logistics Route Engine API"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    APP_HOME=/app \
    APP_USER=appuser \
    APP_GROUP=appgroup \
    PORT=8000

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid 1000 ${APP_GROUP} \
    && useradd --uid 1000 --gid ${APP_GROUP} --shell /bin/bash --create-home ${APP_USER}

# Set working directory
WORKDIR ${APP_HOME}

# Copy wheels from builder stage and install
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl \
    && rm -rf /wheels

# Copy application source code
COPY --chown=${APP_USER}:${APP_GROUP} ./app ${APP_HOME}/app
COPY --chown=${APP_USER}:${APP_GROUP} ./requirements.txt ${APP_HOME}/

# Create necessary directories
RUN mkdir -p ${APP_HOME}/logs ${APP_HOME}/static \
    && chown -R ${APP_USER}:${APP_GROUP} ${APP_HOME}

# Switch to non-root user
USER ${APP_USER}

# Expose port 8000 (Railway will override via PORT env var)
EXPOSE 8000

# No HEALTHCHECK in Dockerfile - Railway handles this via railway.toml

# Production entrypoint - Railway injects PORT at runtime
# Using exec form with sh -c to ensure proper variable expansion
CMD ["/bin/sh", "-c", "exec gunicorn app.main:app --bind 0.0.0.0:${PORT:-8000} --worker-class uvicorn.workers.UvicornWorker --workers 2 --timeout 120 --keep-alive 5 --access-logfile - --error-logfile -"]
