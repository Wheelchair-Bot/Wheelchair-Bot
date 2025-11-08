# Docker Developer Environment

This directory contains a Docker-based development environment for Wheelchair-Bot. The containerized setup provides a consistent development environment across different platforms without requiring local installation of dependencies.

## Quick Start

### Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 1.29 or higher)

### Option 1: Interactive Development (Recommended)

Start an interactive development container with your code mounted for live editing:

```bash
# Start the development container
docker compose up -d dev

# Enter the container
docker compose exec dev bash

# Inside the container, you can:
# - Run the application in mock mode
python main.py --mock --verbose

# - Run tests
pytest tests/ -v

# - Run code formatting
black wheelchair_bot/ wheelchair_controller/ tests/

# - Run linting
ruff check wheelchair_bot/ wheelchair_controller/

# - Run type checking
mypy wheelchair_bot/

# Exit the container
exit

# Stop the container
docker compose down
```

### Option 2: Run Tests

Run the test suite in a container:

```bash
# Run all tests with coverage
docker compose run --rm test

# Run specific tests
docker compose run --rm test pytest tests/test_controller.py -v

# Run tests with custom options
docker compose run --rm test pytest tests/ -v --cov-report=html
```

### Option 3: Run Application

Run the application in mock mode (no hardware required):

```bash
# Start the application service
docker compose up app

# The web interface will be available at:
# http://localhost:8080

# Stop with Ctrl+C or:
docker compose down
```

## Development Workflow

### 1. Building the Images

Build all Docker images:

```bash
# Build all images
docker compose build

# Build specific service
docker compose build dev

# Build with no cache (fresh build)
docker compose build --no-cache
```

### 2. Code Editing

Your local code is mounted into the container, so you can:

1. Edit files in your favorite IDE on your host machine
2. Changes are immediately reflected in the container
3. Run and test your changes inside the container

```bash
# Start development container in background
docker compose up -d dev

# Execute commands in the running container
docker compose exec dev python main.py --mock
docker compose exec dev pytest tests/
docker compose exec dev black .

# Or start an interactive shell
docker compose exec dev bash
```

### 3. Running Code Quality Tools

```bash
# Format code with Black
docker compose exec dev black wheelchair_bot/ wheelchair_controller/ tests/

# Check code style with Ruff
docker compose exec dev ruff check wheelchair_bot/ wheelchair_controller/

# Auto-fix issues with Ruff
docker compose exec dev ruff check --fix wheelchair_bot/ wheelchair_controller/

# Type checking with mypy
docker compose exec dev mypy wheelchair_bot/

# Run all quality checks
docker compose exec dev bash -c "black . && ruff check --fix . && mypy wheelchair_bot/"
```

### 4. Testing

```bash
# Run all tests
docker compose run --rm test

# Run with verbose output
docker compose run --rm test pytest tests/ -v

# Run specific test file
docker compose run --rm test pytest tests/test_controller.py

# Run with coverage report
docker compose run --rm test pytest tests/ --cov-report=html

# The coverage report will be in htmlcov/ directory
```

### 5. Running Examples

```bash
# Run example scripts
docker compose exec dev python examples/show_models.py
docker compose exec dev python examples/simulated_control.py
docker compose exec dev python examples/basic_control.py
```

## Docker Services

The docker compose.yml defines three services:

### `dev` - Development Service

- **Purpose**: Interactive development with live code mounting
- **Features**:
  - Full development environment with all dependencies
  - Source code mounted as volumes
  - Bash shell for interactive work
  - All development tools (pytest, black, ruff, mypy)
- **Ports**: 8000 (API), 8080 (Web UI)
- **Usage**: `docker compose up -d dev && docker compose exec dev bash`

### `test` - Testing Service

- **Purpose**: Run tests in isolation
- **Features**:
  - Optimized for testing
  - Generates coverage reports
  - Exits after tests complete
- **Usage**: `docker compose run --rm test`

### `app` - Application Service

- **Purpose**: Run the application in production-like mode
- **Features**:
  - Minimal image size
  - Runs in mock mode (no hardware)
  - Auto-restart on failure
- **Ports**: 8000 (API), 8080 (Web UI)
- **Usage**: `docker compose up app`

## Dockerfile Stages

The multi-stage Dockerfile includes:

1. **base**: Base Python image with system dependencies
2. **development**: Full dev environment with all tools
3. **testing**: Optimized for running tests
4. **production**: Minimal runtime environment

## Environment Variables

Available environment variables:

- `PYTHONPATH=/workspace` - Python module search path
- `MOCK_GPIO=1` - Enable GPIO mocking (automatically set in containers)
- `DEVELOPMENT=1` - Development mode flag

## Volumes

Mounted volumes for development:

- `./wheelchair_bot` - Main package source
- `./wheelchair_controller` - Controller source
- `./src` - Additional source files
- `./tests` - Test files
- `./examples` - Example scripts
- `./config` - Configuration files
- `./main.py`, `./demo.py` - Entry point scripts

## Common Tasks

### Install New Python Package

```bash
# Enter dev container
docker compose exec dev bash

# Install package
pip install --user package-name

# Add to requirements.txt or requirements-dev.txt on host
# Rebuild container to persist
docker compose build dev
```

### Update Dependencies

```bash
# Update requirements files on host machine
# Then rebuild the container
docker compose build dev
```

### Clean Up

```bash
# Stop all containers
docker compose down

# Remove containers and networks
docker compose down --remove-orphans

# Remove volumes as well
docker compose down -v

# Remove all images
docker compose down --rmi all
```

## Troubleshooting

### Port Already in Use

If ports 8000 or 8080 are already in use:

```bash
# Edit docker compose.yml and change port mappings, e.g.:
# ports:
#   - "8001:8000"  # Map to different host port
#   - "8081:8080"
```

### Permission Issues

If you encounter permission issues with mounted volumes:

```bash
# The container runs as user 'developer' (UID 1000)
# Ensure your host files are accessible
sudo chown -R 1000:1000 .
```

### Container Won't Start

```bash
# Check logs
docker compose logs dev

# Rebuild from scratch
docker compose build --no-cache dev

# Check Docker daemon is running
docker ps
```

### Tests Fail in Container

```bash
# Ensure all dependencies are installed
docker compose build test

# Run tests with verbose output
docker compose run --rm test pytest tests/ -v -s

# Check Python path
docker compose run --rm test python -c "import sys; print(sys.path)"
```

## Tips and Best Practices

1. **Use the dev service for development**: Mount your code and work interactively
2. **Use the test service for CI**: Quick, isolated test runs
3. **Use the app service for demos**: Show the system working without hardware
4. **Keep images updated**: Rebuild after changing dependencies
5. **Use .dockerignore**: Keeps build context small and fast
6. **Leverage caching**: Order Dockerfile commands from least to most frequently changing

## Integration with Existing Workflows

The Docker setup complements existing workflows:

- **Makefile**: Can add Docker targets to Makefile
- **Local development**: Continue using local Python environment if preferred
- **CI/CD**: Use Docker for consistent test environments
- **Deployment**: Production stage provides ready-to-deploy image

## Hardware Development

Note: Docker containers cannot access GPIO pins or camera hardware directly. For hardware testing:

1. Develop and test in the container with mock mode
2. Deploy to actual hardware (Raspberry Pi) for hardware testing
3. Use the container for rapid development and testing of logic

## Next Steps

- Read the main [README.md](README.md) for project overview
- Check [QUICKSTART.md](QUICKSTART.md) for setup instructions
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Python Docker Best Practices](https://docs.docker.com/language/python/)
