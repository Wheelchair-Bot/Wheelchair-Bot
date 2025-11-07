# Wheelchair-Bot - GitHub Copilot Instructions

## Project Overview
Wheelchair-Bot is a Python-based robotics project designed to assist wheelchair users. This repository contains the software and control systems for an autonomous or semi-autonomous wheelchair assistance bot.

## Tech Stack & Environment
- **Language**: Python 3.x
- **Development Environment**: Cross-platform (Linux, Windows, macOS)
- **Package Management**: pip (Python Package Installer)
- **Version Control**: Git

## Project Structure
The project follows a standard Python project layout:
- Source code should be organized in logical modules
- Tests should be placed in a separate `tests/` directory
- Configuration files at the root level
- Documentation in `docs/` (if applicable)

## Coding Guidelines

### Python Style
- Follow PEP 8 style guide for Python code
- Use 4 spaces for indentation (not tabs)
- Maximum line length: 79 characters for code, 72 for docstrings/comments
- Use meaningful variable and function names
- Add docstrings to all functions, classes, and modules

### Code Quality
- Write clean, readable, and maintainable code
- Keep functions small and focused on a single task
- Avoid code duplication - use functions and classes to reuse code
- Add comments for complex logic, but prefer self-documenting code

### Documentation
- Use docstrings following the Google or NumPy style
- Include type hints where appropriate
- Document all public APIs
- Keep README.md updated with project changes

### Testing
- Write unit tests for new functionality
- Aim for good test coverage
- Use descriptive test names that explain what is being tested
- Follow the Arrange-Act-Assert pattern in tests

## File and Directory Conventions
- Use lowercase with underscores for Python files: `my_module.py`
- Use PascalCase for class names: `WheelchairController`
- Use lowercase with underscores for function and variable names: `calculate_speed`
- Use UPPERCASE for constants: `MAX_SPEED`

## Common Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run the main program (when available)
python main.py

# Run tests (when test framework is set up)
pytest

# Check code style
flake8 .

# Format code
black .
```

## Safety and Robotics Considerations
- **Safety First**: This is a wheelchair assistance bot - safety is paramount
- Always validate inputs and handle edge cases
- Include proper error handling and fail-safes
- Test thoroughly before deploying to hardware
- Document any assumptions about hardware or sensors
- Consider accessibility in all design decisions

## Dependencies
- Keep dependencies minimal and well-justified
- Pin specific versions in requirements.txt for reproducibility
- Document why each major dependency is needed
- Prefer well-maintained, popular libraries

## Git Workflow
- Write clear, descriptive commit messages
- Keep commits atomic and focused
- Use feature branches for new development
- Ensure code works before committing

## Copilot Behavior Guidance
- Ask clarifying questions if requirements are ambiguous
- Prioritize safety and robustness in all code suggestions
- Consider edge cases and error conditions
- Suggest tests alongside code changes
- Be explicit about assumptions, especially regarding hardware integration
