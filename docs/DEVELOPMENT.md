# Development Guide

This guide covers development setup, workflow, and best practices for contributing to sage-github-manager.

## Quick Start

```bash
# Clone and setup
cd /home/shuhao/sage-github-manager
pip install -e ".[dev]"
pre-commit install

# Set environment variables
export GITHUB_TOKEN=your_token
export GITHUB_OWNER=intellistream
export GITHUB_REPO=SAGE

# Run tests
make test

# Check code quality
make check
```

## Development Setup

### 1. Install Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- pytest and pytest-cov for testing
- ruff for linting and formatting
- mypy for type checking
- pre-commit for git hooks
- Type stubs for requests and PyYAML

### 2. Install Pre-commit Hooks

```bash
pre-commit install
```

This will automatically run checks before each commit:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON/TOML validation
- Ruff formatting and linting
- Mypy type checking

### 3. Configure Environment

Create `.env` file (gitignored):
```bash
cp .env.template .env
# Edit .env with your credentials
```

## Development Workflow

### Making Changes

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make changes**
   - Write code following the style guide
   - Add tests for new features
   - Update documentation

3. **Run quality checks**
   ```bash
   make format   # Auto-format code
   make lint     # Check for issues
   make test     # Run tests
   ```

4. **Commit changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```
   Pre-commit hooks will run automatically.

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature
   ```

### Running Tests

```bash
# All tests
pytest

# With coverage
make test-cov

# Specific test file
pytest tests/test_config.py -v

# Specific test function
pytest tests/test_config.py::test_config_loading -v

# Skip network tests
pytest -m "not network"
```

### Code Quality

```bash
# Format code
make format

# Lint code
make lint

# Type check
mypy src/sage_github

# Run all checks
make check

# Run pre-commit on all files
make pre-commit
```

## Code Style Guide

### General Principles

1. **NO FALLBACK LOGIC** - Never use silent try-except fallbacks
2. **Type hints** - All functions should have type annotations
3. **Line length** - Maximum 100 characters
4. **Docstrings** - Use Google style docstrings
5. **Error messages** - Clear, actionable error messages

### Good Examples

```python
from typing import Dict, List

def load_config(path: str) -> Dict[str, Any]:
    """Load configuration from file.

    Args:
        path: Path to configuration file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Config file not found: {path}. "
            f"Please create it from .env.template"
        )

    with open(path) as f:
        return yaml.safe_load(f)
```

### Bad Examples

```python
# ❌ NO - Silent fallback
def load_config(path: str):
    try:
        with open(path) as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {}  # Hides error

# ❌ NO - No type hints
def process_issue(issue):
    return issue["title"]

# ❌ NO - Unclear error
def validate_token(token):
    if not token:
        raise ValueError("Invalid")  # What's invalid?
```

## Project Structure

```
sage-github-manager/
├── src/sage_github/           # Source code
│   ├── cli_main.py            # CLI entry point
│   ├── cli.py                 # Command definitions
│   ├── config.py              # Configuration
│   ├── manager.py             # Core logic
│   ├── issue_data_manager.py  # Data persistence
│   └── helpers/               # Feature modules
│       ├── download.py
│       ├── analytics.py
│       ├── batch.py
│       └── ...
├── tests/                     # Tests
│   ├── test_basic.py
│   ├── test_config.py
│   └── ...
├── examples/                  # Usage examples
├── docs/                      # Documentation
├── .github/workflows/         # CI/CD
├── pyproject.toml             # Package config
├── .pre-commit-config.yaml    # Pre-commit hooks
├── pytest.ini                 # Test config
├── ruff.toml                  # Linting rules
├── Makefile                   # Dev shortcuts
└── README.md                  # Main docs
```

## Adding New Features

### 1. Create Helper Module (if needed)

```python
# src/sage_github/helpers/new_feature.py
from typing import List, Dict

def new_feature_function(data: List[Dict]) -> str:
    """Process data for new feature.

    Args:
        data: List of dictionaries

    Returns:
        Processed result
    """
    # Implementation
    pass
```

### 2. Add to Manager

```python
# src/sage_github/manager.py
from .helpers.new_feature import new_feature_function

class GitHubManager:
    def new_feature(self):
        """Public API for new feature."""
        data = self.get_issues()
        return new_feature_function(data)
```

### 3. Add CLI Command

```python
# src/sage_github/cli.py
@app.command()
def new_feature(
    ctx: typer.Context,
    option: str = typer.Option("default", help="Option description")
):
    """Command description."""
    manager = ctx.obj["manager"]
    result = manager.new_feature()
    console.print(result)
```

### 4. Add Tests

```python
# tests/test_new_feature.py
import pytest
from sage_github.helpers.new_feature import new_feature_function

def test_new_feature():
    """Test new feature functionality."""
    data = [{"id": 1, "title": "Test"}]
    result = new_feature_function(data)
    assert result is not None

@pytest.mark.network
def test_new_feature_integration(manager):
    """Integration test with real API (requires GITHUB_TOKEN)."""
    result = manager.new_feature()
    assert result is not None
```

### 5. Update Documentation

```markdown
# docs/NEW_FEATURE.md
# New Feature

Description of the new feature.

## Usage

\```bash
github-manager new-feature --option value
\```

## Examples

...
```

## Testing Strategy

### Test Types

1. **Unit Tests** - Test individual functions
   ```python
   @pytest.mark.unit
   def test_parse_issue():
       issue = {"id": 1, "title": "Test"}
       result = parse_issue(issue)
       assert result["id"] == 1
   ```

2. **Integration Tests** - Test with GitHub API (requires token)
   ```python
   @pytest.mark.github_api
   def test_download_issues(manager):
       issues = manager.download_issues()
       assert len(issues) > 0
   ```

3. **Network Tests** - Test network operations
   ```python
   @pytest.mark.network
   def test_api_request():
       response = make_request("https://api.github.com")
       assert response.status_code == 200
   ```

### Running Specific Test Types

```bash
# Unit tests only
pytest -m unit

# Skip network tests
pytest -m "not network"

# Skip GitHub API tests
pytest -m "not github_api"
```

## Common Tasks

### Update Dependencies

```bash
# Edit pyproject.toml
# Then reinstall
pip install -e ".[dev]"
```

### Clean Build Artifacts

```bash
make clean
```

### Build Package

```bash
make build
```

### Publish to TestPyPI

```bash
make build
make publish-test
```

## Troubleshooting

### Pre-commit Hooks Fail

```bash
# Run manually to see issues
pre-commit run --all-files

# Update hooks
pre-commit autoupdate

# Skip hooks (not recommended)
git commit --no-verify
```

### Tests Fail

```bash
# Check environment variables
echo $GITHUB_TOKEN

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_config.py::test_specific -v
```

### Import Errors

```bash
# Reinstall in editable mode
pip install -e ".[dev]"

# Check installation
pip list | grep sage-github
```

## Resources

- [README.md](README.md) - Main documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) - Contributing guidelines
- [FAQ.md](docs/FAQ.md) - Frequently asked questions
- [QUICK_START.md](docs/QUICK_START.md) - Quick start guide
