.PHONY: help install test sim clean lint format

help:
	@echo "Wheelchair Bot - Makefile commands:"
	@echo ""
	@echo "  make install    - Install package and dependencies"
	@echo "  make test       - Run all tests with coverage"
	@echo "  make sim        - Run wheelchair emulator"
	@echo "  make lint       - Run code linters"
	@echo "  make format     - Format code with black"
	@echo "  make clean      - Clean build artifacts"
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
