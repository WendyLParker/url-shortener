# Start from a lightweight official Python 3.12 image
FROM python:3.12-slim AS base

# Set environment variables for better Python & pip behavior
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set the working directory inside the container
WORKDIR /app

# Install system packages needed at runtime (curl is used for the healthcheck)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# -------------------------------------------------------
# Install Python dependencies first (better Docker layer caching)
# If only application code changes later, this layer is reused
# -------------------------------------------------------
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# Copy the application source code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
COPY docker/entrypoint.sh ./docker/entrypoint.sh

# Make the entrypoint script executable
RUN chmod +x ./docker/entrypoint.sh

# -------------------------------------------------------
# Security best practice: run the app as a non-root user
# -------------------------------------------------------
RUN useradd --create-home --shell /bin/bash appuser \
    && chown -R appuser:appuser /app
USER appuser

# Document that the container listens on port 8000
EXPOSE 8000

# Healthcheck so Docker/orchestrators know if the app is healthy
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Start the application using the entrypoint script
ENTRYPOINT ["./docker/entrypoint.sh"]