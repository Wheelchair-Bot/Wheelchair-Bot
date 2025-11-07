# Contributing to Wheelchair-Bot

Thank you for your interest in contributing to Wheelchair-Bot! This project aims to make powered wheelchairs more accessible through remote control capabilities.

## Code of Conduct

- Be respectful and inclusive
- Focus on what is best for the community
- Show empathy towards others
- Be patient with newcomers

## How to Contribute

### Reporting Bugs

Before creating a bug report:
1. Check existing issues to avoid duplicates
2. Collect information about your environment
3. Describe steps to reproduce the issue

Create an issue with:
- Clear, descriptive title
- Detailed description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, etc.)
- Relevant logs or screenshots

### Suggesting Features

Feature requests are welcome! Please:
1. Check if the feature has already been suggested
2. Explain the use case clearly
3. Describe the desired behavior
4. Consider implementation complexity

### Pull Requests

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR-USERNAME/Wheelchair-Bot.git
   cd Wheelchair-Bot
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation as needed
   - Ensure security best practices

4. **Test Your Changes**
   ```bash
   # Run syntax check
   python3 -m py_compile services/**/*.py
   
   # Run integration tests
   ./start.sh
   python test_services.py
   ```

5. **Commit**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```
   
   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation only
   - `style:` Code style (formatting, etc.)
   - `refactor:` Code restructuring
   - `test:` Adding tests
   - `chore:` Build/tooling changes

6. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then create a Pull Request on GitHub with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes
   - Test results

### Code Style

**Python:**
- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use meaningful variable names
- Add docstrings to functions/classes

**JavaScript:**
- Use camelCase for variables/functions
- Use PascalCase for classes
- Add comments for complex logic
- Handle errors appropriately

**General:**
- Keep functions small and focused
- Write self-documenting code
- Add comments for "why", not "what"
- Avoid premature optimization

### Security

- Never commit secrets or credentials
- Validate all user inputs
- Use secure communication (HTTPS/WSS in production)
- Follow OWASP guidelines
- Report security issues privately

### Testing

- Test on real hardware when possible
- Test edge cases
- Test error conditions
- Verify safety features work correctly
- Test on different platforms (Pi, x86, etc.)

### Documentation

- Update README.md if adding features
- Update API.md for API changes
- Update HARDWARE.md for hardware requirements
- Add code comments for complex logic
- Include examples where helpful

## Project Structure

```
services/
  teleopd/          # Teleoperation daemon (WebSocket + REST)
  streamer/         # Video streaming (WebRTC)
  safety_agent/     # Safety monitoring
  net_agent/        # Network monitoring
web_client/         # Web interface
docs/              # Documentation
config/            # Configuration examples
```

## Development Environment

### Recommended Tools

- **IDE:** VSCode with Python and JavaScript extensions
- **Python Tools:** Black (formatting), Flake8 (linting)
- **Testing:** pytest for unit tests
- **Git:** Git with conventional commits

### Local Testing Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install black flake8 pytest pytest-asyncio
   ```

2. Run services locally:
   ```bash
   ./start.sh
   ```

3. Access web interface:
   ```
   http://localhost:8080
   ```

## Priority Areas

We especially welcome contributions in:

1. **Hardware Integration**
   - Support for different wheelchair models
   - Additional sensor integration
   - Motor controller interfaces

2. **Safety Features**
   - Enhanced obstacle detection
   - Better E-stop mechanisms
   - Failsafe improvements

3. **Network Resilience**
   - Better handling of connection loss
   - Network quality monitoring
   - Automatic reconnection

4. **UI/UX Improvements**
   - Mobile app development
   - Better joystick controls
   - Accessibility features

5. **Documentation**
   - Tutorial videos
   - Setup guides for specific hardware
   - Translation to other languages

## Questions?

- Open an issue for general questions
- Check existing documentation
- Ask in discussions

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Acknowledged in the project

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for helping make wheelchair control more accessible! 🦽
