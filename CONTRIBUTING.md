# Contributing to Wheelchair-Bot

Thank you for your interest in contributing to Wheelchair-Bot! This project aims to provide a safe and accessible interface for controlling electric wheelchairs.

## Code of Conduct

Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, Node version)

### Suggesting Features

Feature requests are welcome! Please create an issue describing:
- The problem you're trying to solve
- Your proposed solution
- Any alternatives you've considered

### Pull Requests

1. **Fork the repository** and create a new branch from `main`
2. **Make your changes** following the coding standards below
3. **Add tests** for any new functionality
4. **Ensure all tests pass**
5. **Update documentation** as needed
6. **Submit a pull request**

## Development Setup

See [Getting Started Guide](docs/getting-started.md) for detailed setup instructions.

Quick start:
1. Fork and clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Install in development mode: `pip install -e .`
4. Run tests: `pytest`

## Adding a New Wheelchair Model

To add support for a new wheelchair model:

1. Create a new class in `wheelchair_bot/wheelchairs/models.py` that inherits from `Wheelchair`
2. Implement the `get_motor_config()` method
3. Add your model to the imports in `wheelchair_bot/wheelchairs/__init__.py`
4. Update the examples and documentation

Example:

```python
class MyWheelchair(Wheelchair):
    def __init__(self):
        super().__init__(
            name="My Wheelchair Model",
            max_speed=2.0,  # m/s
            wheel_base=0.45,  # meters
            wheel_diameter=0.35,  # meters
        )
    
    def get_motor_config(self):
        return {
            "type": "mid_wheel_drive",
            "motor_count": 2,
            "motor_type": "brushless_dc",
            "max_voltage": 24,
            "max_current": 50,
        }
```

## Adding a New Controller Type

To add support for a new controller:

1. Create a new file in `wheelchair_bot/controllers/`
2. Create a class that inherits from `Controller`
3. Implement all abstract methods: `connect()`, `disconnect()`, `read_input()`, `is_connected()`
4. Add your controller to the imports in `wheelchair_bot/controllers/__init__.py`

## Coding Standards

### Python

- Follow PEP 8 style guide
- Use type hints where appropriate
- Format code with `black`
- Lint with `ruff`
- Write docstrings for all functions and classes
- Keep functions focused and single-purpose
- Write tests for new functionality

### JavaScript/React

- Follow ESLint configuration
- Use functional components and hooks
- Write clear, descriptive variable names
- Keep components small and focused
- Use proper prop types

## Testing

### Backend Tests

```bash
cd packages/backend
pytest
```

### Shared Library Tests

```bash
cd packages/shared
pytest
```

### Integration Tests

```bash
python tests/test_integration.py
```

## Commit Messages

Use clear, descriptive commit messages:
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit first line to 72 characters
- Reference issues and pull requests

Example:
```
Add movement speed control to API

- Add speed parameter to move endpoint
- Update tests for speed validation
- Update documentation

Fixes #123
```

## Safety Considerations

This project deals with wheelchair control, which has real-world safety implications:

- Always prioritize safety in your contributions
- Test thoroughly before submitting
- Document any safety-related changes
- Consider edge cases and failure modes
- Never remove or weaken existing safety features without discussion

## Documentation

Update documentation when you:
- Add new features
- Change existing functionality
- Add new dependencies
- Change configuration

## Questions?

Feel free to create an issue for any questions about contributing.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
