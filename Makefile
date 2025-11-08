.PHONY: help install test sim clean lint format docker-build docker-dev docker-test docker-clean

help:
	@echo "Wheelchair Bot - Makefile commands:"
	@echo ""
	@echo "Local Development:"
	@echo "  make install         - Install package and dependencies"
	@echo "  make test            - Run all tests with coverage"
	@echo "  make sim             - Run wheelchair emulator"
	@echo "  make lint            - Run code linters"
	@echo "  make format          - Format code with black"
	@echo "  make clean           - Clean build artifacts"
	@echo ""
	@echo "Docker Development:"
	@echo "  make docker-build    - Build Docker development image"
	@echo "  make docker-dev      - Start interactive development container"
	@echo "  make docker-test     - Run tests in Docker container"
	@echo "  make docker-app      - Run application in Docker (mock mode)"
	@echo "  make docker-clean    - Clean Docker containers and images"
	@echo "  make docker-shell    - Open shell in running dev container"
	@echo ""

install:
	pip install -e ".[dev]"

test:
	python scripts/run_tests.py

sim:
	wheelchair-sim --config config/default.yaml

sim-interactive:
	wheelchair-sim --config config/default.yaml --interactive

sim-duration:
	wheelchair-sim --config config/default.yaml --duration 10

lint:
	ruff check src/ wheelchair_bot/ wheelchair_controller/
	mypy src/wheelchair --ignore-missing-imports

format:
	black src/ wheelchair_bot/ wheelchair_controller/ tests/
	ruff check --fix src/ wheelchair_bot/ wheelchair_controller/

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Docker targets
docker-build:
	docker compose build

docker-dev:
	docker compose up -d dev
	@echo "Development container started. Use 'make docker-shell' to enter it."

docker-shell:
	docker compose exec dev bash

docker-test:
	docker compose run --rm test

docker-app:
	docker compose up app

docker-clean:
	docker compose down -v --remove-orphans
	docker compose down --rmi local || true
