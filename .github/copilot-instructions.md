# GitHub Issues Manager - Copilot Instructions

## Overview

**sage-github-manager** is a Python 3.10+ CLI tool for downloading, analyzing, and managing GitHub Issues with AI capabilities. It provides a command-line interface for GitHub Issues management, analytics, and batch operations.

## Project Structure

```
sage-github-manager/
├── src/sage_github/           # Source code
│   ├── cli_main.py            # CLI entry point
│   ├── cli.py                 # Typer CLI commands
│   ├── config.py              # Configuration management
│   ├── manager.py             # Core GitHubManager class
│   ├── issue_data_manager.py  # Issue data persistence
│   └── helpers/               # 13 helper modules
│       ├── download.py        # Issue downloading
│       ├── analytics.py       # Analytics & reporting
│       ├── batch.py           # Batch operations
│       ├── export.py          # Data export (JSON/CSV/Markdown)
│       ├── filter.py          # Issue filtering
│       ├── formatters.py      # Output formatting
│       ├── integrations.py    # External integrations
│       ├── network.py         # Network utilities
│       ├── priority.py        # Priority management
│       ├── search.py          # Issue search
│       ├── summary.py         # AI summaries
│       ├── sync.py            # Data synchronization
│       └── validation.py      # Data validation
├── tests/                     # Test files
│   ├── test_basic.py
│   ├── test_config.py
│   └── ...
├── examples/                  # Usage examples
├── docs/                      # Documentation
├── pyproject.toml             # Package configuration
├── .pre-commit-config.yaml    # Pre-commit hooks
├── pytest.ini                 # Test configuration
└── ruff.toml                  # Linting configuration
```

## CRITICAL Coding Principles

### ✅ Key Design Decisions

1. **Configuration Storage**: Uses `~/.github-manager/` directory (NOT `.sage/issues/`)
2. **CLI Command**: `github-manager <command>` or `gh-issues <command>`
3. **Environment Variables**: `GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO`
4. **Data Storage**: JSON files in `~/.github-manager/data/<owner>/<repo>/`

### ❌ NO FALLBACK LOGIC - PROJECT-WIDE RULE

**NEVER use try-except fallback patterns anywhere in the codebase.**

#### ❌ BAD Examples (Do NOT do this):

```python
# Configuration loading
try:
    config = load_config()
except FileNotFoundError:
    config = {}  # ❌ NO - hides missing config

# Environment variables
token = os.getenv("GITHUB_TOKEN") or "default"  # ❌ NO - hides missing token
```

#### ✅ GOOD Examples (Do this instead):

```python
# Let exceptions propagate with clear error messages
config = load_config()  # FileNotFoundError if missing

# Environment variables - explicit check
token = os.environ["GITHUB_TOKEN"]  # KeyError if missing

# Or provide helpful error messages
if "GITHUB_TOKEN" not in os.environ:
    raise ValueError(
        "GITHUB_TOKEN not set. Please set it with: export GITHUB_TOKEN=your_token"
    )
```

**Rationale**: Fail fast, fail loud. Silent fallbacks hide bugs and make debugging harder.

### ❌ NEVER MANUAL PIP INSTALL - ALWAYS USE pyproject.toml

**ALL dependencies MUST be declared in pyproject.toml. NEVER use manual `pip install` commands.**

#### ❌ FORBIDDEN:
```bash
pip install requests
pip install typer==0.15.0
```

#### ✅ CORRECT:
```toml
# In pyproject.toml
dependencies = [
    "requests>=2.31.0,<3.0.0",
    "typer>=0.15.0,<1.0.0",
]
```

```bash
pip install -e ".[dev]"  # Install with dependencies
```

## Installation & Setup

### Development Setup

```bash
# Clone repository
cd /home/shuhao/sage-github-manager

# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Set up environment variables
export GITHUB_TOKEN=your_github_token
export GITHUB_OWNER=your_org
export GITHUB_REPO=your_repo
```

### Environment Variables

Create `.env` file (gitignored):
```bash
GITHUB_TOKEN=ghp_xxxxxxxxxxxxx
GITHUB_OWNER=intellistream
GITHUB_REPO=SAGE
```

## Usage Examples

```bash
# Download issues
github-manager download

# List issues
github-manager list

# Show analytics
github-manager analytics

# Export data
github-manager export --format csv --output issues.csv

# Batch operations
github-manager batch close --label "wontfix"
```

## Testing & Quality

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=sage_github --cov-report=html

# Specific test
pytest tests/test_config.py -v
```

### Code Quality

```bash
# Run all checks (format + lint)
pre-commit run --all-files

# Format code
ruff format .

# Lint code
ruff check --fix .

# Type checking
mypy src/sage_github
```

### Pre-commit Hooks

Pre-commit hooks will automatically run on every commit:
- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON/TOML validation
- Ruff formatting and linting
- Type checking (mypy)

To skip hooks (not recommended):
```bash
git commit --no-verify -m "message"
```

## Common Development Tasks

### Adding a New Feature

1. Create a new module in `src/sage_github/helpers/` if needed
2. Update `manager.py` or `cli.py` with new functionality
3. Add tests in `tests/`
4. Update documentation in `docs/`
5. Run quality checks: `pre-commit run --all-files`
6. Run tests: `pytest`

### Adding a New Dependency

1. Add to `pyproject.toml` under `dependencies` or `dev` optional dependencies
2. Reinstall: `pip install -e ".[dev]"`
3. Update requirements in documentation if needed

### Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use rich console for better output
from rich.console import Console
console = Console()
console.print("[bold red]Debug info here[/]")
```

## Key Locations

```
src/sage_github/
  cli_main.py          # Entry point (github-manager command)
  cli.py               # Typer CLI commands definition
  config.py            # Configuration management
  manager.py           # Core GitHubManager class
  issue_data_manager.py # Data persistence layer
  helpers/             # Feature modules (13 files)
tests/                 # Test files
  test_basic.py        # Basic functionality tests
  test_config.py       # Configuration tests
examples/              # Usage examples
  basic_usage.py       # Simple usage example
  advanced_usage.py    # Advanced features example
docs/                  # Documentation
  FAQ.md               # Frequently asked questions
  QUICK_START.md       # Quick start guide
.pre-commit-config.yaml # Pre-commit hooks
pytest.ini             # Pytest configuration
ruff.toml              # Ruff linting rules
pyproject.toml         # Package metadata & dependencies
```

## Configuration Files

### .pre-commit-config.yaml
Pre-commit hooks for code quality (ruff, mypy, file checks)

### pytest.ini
Test configuration (cache dir, markers, coverage)

### ruff.toml
Linting and formatting rules (line length 100, Python 3.10+)

### pyproject.toml
Package metadata, dependencies, tool configurations

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| `GITHUB_TOKEN not set` | Export environment variable: `export GITHUB_TOKEN=ghp_xxx` |
| `ModuleNotFoundError` | Install package: `pip install -e ".[dev]"` |
| Pre-commit hooks fail | Run `pre-commit run --all-files` and fix issues |
| Tests fail | Check that GITHUB_TOKEN is set, run `pytest -v` for details |
| Import errors | Ensure running from project root, package installed in editable mode |

## Response Style for Copilot

- Be concise but comprehensive
- Provide exact commands that can be copy-pasted
- Reference specific files and line numbers when relevant
- Emphasize code quality and testing
- Follow the NO FALLBACK LOGIC principle strictly
- Always declare dependencies in pyproject.toml

## Architecture Principles

1. **Single Responsibility**: Each helper module handles one aspect
2. **Configuration First**: All settings go through config.py
3. **Data Persistence**: Use IssueDataManager for all data operations
4. **Rich Output**: Use Rich library for terminal output
5. **Type Hints**: All functions should have type annotations
6. **Error Messages**: Clear, actionable error messages
7. **Testing**: Every feature should have tests

## When Helping Developers

1. **Check configuration first**: Many issues are due to missing environment variables
2. **Guide on testing**: Tests should be run from project root
3. **Enforce quality standards**: Ruff formatting (line 100), type hints, no fallback logic
4. **Provide context**: Reference documentation when relevant
5. **Debug systematically**: Check env vars → Check installation → Check file paths
