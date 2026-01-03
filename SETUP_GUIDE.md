# sage-github-manager Setup Guide

## 🎯 Quick Setup for New VS Code Window

### 1. Open in VS Code

```bash
code /home/shuhao/sage-github-manager
```

### 2. Install Dependencies

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit with your credentials
export GITHUB_TOKEN=ghp_your_token_here
export GITHUB_OWNER=intellistream
export GITHUB_REPO=SAGE
```

### 4. Verify Setup

```bash
# Test installation
github-manager --help

# Run tests
make test

# Check code quality
make check
```

## 📁 Project Structure

```
sage-github-manager/
├── .github-copilot-instructions.md  # ← Copilot instructions (auto-loaded)
├── .pre-commit-config.yaml          # Git hooks configuration
├── pytest.ini                       # Test configuration
├── ruff.toml                        # Linting rules
├── Makefile                         # Development shortcuts
├── pyproject.toml                   # Package metadata
├── DEVELOPMENT.md                   # Detailed dev guide
├── .env.template                    # Environment template
├── .github/workflows/ci.yml         # CI/CD pipeline
├── src/sage_github/                 # Source code
│   ├── cli_main.py                  # Entry point
│   ├── cli.py                       # CLI commands
│   ├── config.py                    # Configuration
│   ├── manager.py                   # Core logic
│   └── helpers/                     # 13 helper modules
└── tests/                           # Test files
```

## 🚀 Available Commands

### Makefile Shortcuts

```bash
make help         # Show all available commands
make dev-setup    # Complete dev setup
make test         # Run all tests
make test-cov     # Run tests with coverage
make format       # Format code with ruff
make lint         # Lint code with ruff
make check        # Run all quality checks
make pre-commit   # Run pre-commit hooks
make clean        # Clean build artifacts
make build        # Build distribution
```

### Direct Commands

```bash
# CLI usage
github-manager --help
github-manager download
github-manager list
github-manager analytics

# Testing
pytest                              # All tests
pytest --cov=sage_github            # With coverage
pytest tests/test_config.py -v     # Specific test

# Code quality
ruff format .                       # Format code
ruff check --fix .                  # Lint and fix
mypy src/sage_github                # Type check
pre-commit run --all-files          # All pre-commit hooks
```

## 🔧 Configuration Files

### 1. .github-copilot-instructions.md
- **Purpose**: Copilot AI assistant instructions
- **Auto-loaded**: Yes (VS Code reads this automatically)
- **Contains**: Project overview, coding principles, dev workflow

### 2. .pre-commit-config.yaml
- **Purpose**: Git pre-commit hooks
- **Runs on**: Every git commit
- **Checks**: Formatting, linting, type checking, file checks

### 3. pytest.ini
- **Purpose**: Test configuration
- **Features**: Test discovery, markers, coverage reporting
- **Markers**: `unit`, `integration`, `network`, `github_api`

### 4. ruff.toml
- **Purpose**: Linting and formatting rules
- **Line length**: 100 characters
- **Python version**: 3.10+
- **Replaces**: black, isort, flake8

### 5. pyproject.toml
- **Purpose**: Package metadata and tool configurations
- **Contains**: Dependencies, scripts, tool settings
- **Scripts**: `github-manager`, `gh-issues`

### 6. Makefile
- **Purpose**: Development shortcuts
- **Usage**: `make <command>`
- **Run**: `make help` to see all commands

## 🎨 Development Workflow

### 1. Make Changes

```bash
git checkout -b feature/new-feature
# Edit code...
make format   # Auto-format
make lint     # Check issues
make test     # Run tests
```

### 2. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
# Pre-commit hooks run automatically
```

### 3. Push and PR

```bash
git push origin feature/new-feature
# Create PR on GitHub
```

## 📚 Documentation

- **README.md** - Main documentation
- **DEVELOPMENT.md** - Detailed development guide
- **CONTRIBUTING.md** - Contributing guidelines
- **docs/FAQ.md** - Frequently asked questions
- **docs/QUICK_START.md** - Quick start guide

## 🔍 Key Features

### Copilot Integration
- Instructions file auto-loaded by VS Code
- Context-aware code suggestions
- Follows project coding principles

### Pre-commit Hooks
- Automatic code formatting
- Linting checks
- Type checking
- File validation
- Runs before every commit

### Testing
- Unit tests with pytest
- Coverage reporting
- Test markers for filtering
- GitHub API integration tests

### CI/CD
- GitHub Actions workflow
- Runs on push and PR
- Tests on Python 3.10, 3.11, 3.12
- Code quality checks

## 🚨 CRITICAL: Coding Principles

### ❌ NO FALLBACK LOGIC
```python
# ❌ BAD
try:
    config = load_config()
except:
    config = {}  # Silent failure

# ✅ GOOD
config = load_config()  # Let it fail
```

### ✅ ALWAYS USE pyproject.toml
```bash
# ❌ BAD
pip install requests

# ✅ GOOD
# Add to pyproject.toml, then:
pip install -e ".[dev]"
```

### ✅ TYPE HINTS REQUIRED
```python
def process_issue(issue: Dict[str, Any]) -> str:
    """Process issue with clear types."""
    return issue["title"]
```

## 🐛 Troubleshooting

### Issue: Pre-commit hooks fail
```bash
pre-commit run --all-files
# Fix reported issues
```

### Issue: Tests fail
```bash
# Check environment
echo $GITHUB_TOKEN

# Run verbose
pytest -v
```

### Issue: Import errors
```bash
# Reinstall
pip install -e ".[dev]"
```

### Issue: Copilot not loading instructions
- VS Code should auto-detect `.github-copilot-instructions.md`
- Restart VS Code if needed
- Check file is in project root

## 📖 Next Steps

1. **Read DEVELOPMENT.md** - Comprehensive development guide
2. **Run `make dev-setup`** - Complete setup
3. **Run `make test`** - Verify everything works
4. **Start coding** - Follow the workflow above
5. **Check Copilot** - It should be aware of project context

## 🎉 You're Ready!

The project is now fully configured with:
- ✅ Copilot instructions
- ✅ Pre-commit hooks
- ✅ Test configuration
- ✅ Linting rules
- ✅ CI/CD pipeline
- ✅ Development shortcuts
- ✅ Documentation

Open in VS Code and start developing!
