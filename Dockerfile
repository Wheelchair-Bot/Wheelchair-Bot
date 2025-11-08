# Wheelchair-Bot Developer Container
# Multi-stage Dockerfile for development environment

FROM python:3.11-slim-bookworm AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials
    build-essential \
    gcc \
    g++ \
    make \
    # Git for version control
    git \
    # Required for some Python packages
    libffi-dev \
    libssl-dev \
    # Optional: Video/camera tools (for testing, not functional in container)
    # Note: GPIO and camera won't work in container, but libraries can be installed
    python3-dev \
    # Cleanup
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for development
RUN useradd -m -s /bin/bash -u 1000 developer && \
    mkdir -p /workspace && \
    chown -R developer:developer /workspace

# Switch to non-root user
USER developer
WORKDIR /workspace

# Add local bin to PATH for pip-installed executables
ENV PATH="/home/developer/.local/bin:${PATH}"

# Development stage - includes all dev dependencies
FROM base AS development

# Copy requirements files first (for better caching)
COPY --chown=developer:developer requirements-docker.txt requirements-dev.txt pyproject.toml ./

# Install Python dependencies
# Use requirements-docker.txt which excludes hardware-specific packages like RPi.GPIO
# Configure pip to handle SSL cert issues in some environments
RUN pip install --user --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-docker.txt && \
    pip install --user --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-dev.txt

# Copy the entire project
COPY --chown=developer:developer . .

# Install the package in editable mode
RUN pip install --user --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -e ".[dev]"

# Set the default command to bash for interactive development
CMD ["/bin/bash"]

# Testing stage - optimized for running tests
FROM development AS testing

# Run tests by default in this stage
CMD ["pytest", "tests/", "-v", "--cov=wheelchair_bot", "--cov=wheelchair_controller", "--cov-report=term-missing"]

# Production-ready stage (minimal, for running the application)
FROM base AS production

# Copy only necessary files
COPY --chown=developer:developer requirements-docker.txt ./
RUN pip install --user --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements-docker.txt

# Copy source code
COPY --chown=developer:developer wheelchair_bot wheelchair_bot/
COPY --chown=developer:developer wheelchair_controller wheelchair_controller/
COPY --chown=developer:developer src src/
COPY --chown=developer:developer main.py demo.py README.md ./
COPY --chown=developer:developer config config/
COPY --chown=developer:developer pyproject.toml setup.py ./

# Install the package
RUN pip install --user --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org .

# Expose ports for web interface and API
EXPOSE 8000 8080

# Run in mock mode by default (since hardware won't be available in container)
CMD ["python", "main.py", "--mock", "--verbose"]
