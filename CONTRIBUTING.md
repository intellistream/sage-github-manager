# Contributing to GitHub Issues Manager

Thank you for your interest in contributing to GitHub Issues Manager! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to foster an inclusive and welcoming community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear title and description
- Steps to reproduce the bug
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant error messages or logs

### Suggesting Features

For feature requests:
- Check if the feature has already been requested
- Provide a clear use case
- Explain how it would benefit users
- Consider providing implementation ideas

### Pull Requests

1. **Fork the repository** and create a branch from `main`
2. **Make your changes** with clear, descriptive commits
3. **Add tests** if applicable
4. **Update documentation** for any changed functionality
5. **Ensure tests pass**: `pytest`
6. **Format your code**: `black src/ tests/` and `isort src/ tests/`
7. **Check types**: `mypy src/`
8. **Submit the PR** with a clear description

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/sage-github-manager.git
cd sage-github-manager

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run formatting
black src/ tests/
isort src/ tests/

# Run type checking
mypy src/
```

### Code Style

- Follow PEP 8 guidelines
- Use Black for formatting (line length: 100)
- Use isort for import sorting
- Add type hints where appropriate
- Write docstrings for public functions and classes

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add AI-powered duplicate detection
fix: handle rate limiting in GitHub API calls
docs: update installation instructions
test: add tests for team management
refactor: simplify config loading logic
```

### Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for good test coverage
- Test with different configurations

### Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Keep CHANGELOG.md updated

## Project Structure

```
sage-github-manager/
├── src/sage_github/      # Main package
│   ├── __init__.py
│   ├── cli.py           # CLI interface
│   ├── config.py        # Configuration management
│   ├── manager.py       # Core manager
│   ├── issue_data_manager.py
│   └── helpers/         # Helper utilities
├── tests/               # Test suite
├── examples/            # Usage examples
└── docs/                # Additional documentation
```

## Questions?

Feel free to:
- Open an issue for discussion
- Join our community discussions
- Email: shuhao_zhang@hust.edu.cn

Thank you for contributing!
