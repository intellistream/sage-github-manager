# GitHub Issues Manager - Project Summary

## Overview

**GitHub Issues Manager** is a comprehensive command-line tool and Python library for managing GitHub Issues at scale. Extracted from the SAGE project, it provides powerful features for downloading, analyzing, organizing, and managing GitHub Issues with AI-powered capabilities.

## Origin

This project was extracted from the [SAGE project](https://github.com/intellistream/SAGE)'s `sage-tools` package (`packages/sage-tools/src/sage/tools/dev/issues/`) and made into a standalone, independent tool.

## Key Features

### Core Functionality
- **Download & Sync**: Full bidirectional synchronization with GitHub
- **Data Management**: Unified data storage with multiple view formats
- **Statistics**: Comprehensive analytics and reporting
- **Team Management**: Track team members and assignments

### Advanced Features
- **AI Analysis**: Intelligent categorization and duplicate detection
- **Auto-organization**: Timeline-based issue organization
- **Project Management**: Automated issue assignment and tracking
- **Custom Views**: JSON, Markdown, and metadata formats

## Project Structure

```
sage-github-manager/
├── src/sage_github/           # Main package
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # CLI commands
│   ├── cli_main.py           # CLI entry point
│   ├── config.py             # Configuration management
│   ├── manager.py            # Core manager class
│   ├── issue_data_manager.py # Data management
│   ├── tests.py              # Test suite
│   └── helpers/              # Helper utilities
│       ├── download_issues.py
│       ├── sync_issues.py
│       ├── ai_analyzer.py
│       ├── organize_issues.py
│       ├── get_team_members.py
│       └── ... (other helpers)
├── tests/                    # Test suite
│   ├── test_basic.py
│   ├── test_config.py
│   └── __init__.py
├── examples/                 # Usage examples
│   ├── basic_usage.py
│   └── advanced_usage.py
├── docs/                     # Documentation
│   ├── FAQ.md
│   └── QUICK_START.md
├── pyproject.toml           # Project configuration
├── setup.py                 # Setup script
├── README.md                # Main documentation
├── LICENSE                  # MIT License
├── CHANGELOG.md             # Version history
├── CONTRIBUTING.md          # Contribution guidelines
├── MANIFEST.in              # Package manifest
└── .gitignore              # Git ignore rules
```

## Dependencies

### Core Dependencies
- `typer` - CLI framework
- `rich` - Terminal output formatting
- `requests` - HTTP library for GitHub API
- `click` - Command-line interface utilities
- `jinja2` - Template engine
- `pyyaml` - YAML parsing

### Development Dependencies
- `pytest` - Testing framework
- `pytest-cov` - Coverage reporting
- `black` - Code formatting
- `isort` - Import sorting
- `mypy` - Type checking

## Key Adaptations from SAGE

### 1. Removed SAGE Dependencies
- Removed `sage.common.config.output_paths`
- Replaced with `.github-manager/` directory structure
- Self-contained configuration system

### 2. Simplified Imports
- Changed from `sage.tools.dev.issues` to `sage_github`
- Updated all internal imports
- Made package fully standalone

### 3. CLI Changes
- Command changed from `sage-dev issues` to `github-manager`
- Added alternative `gh-issues` command
- Updated help text and branding

### 4. Configuration
- Environment variables: `GITHUB_OWNER`, `GITHUB_REPO`
- Token sources: `GITHUB_TOKEN`, `GH_TOKEN`, `GIT_TOKEN`
- Default paths: `.github-manager/` instead of `.sage/issues/`

## Installation Methods

### Development Installation
```bash
git clone https://github.com/intellistream/sage-github-manager.git
cd sage-github-manager
pip install -e ".[dev]"
```

### User Installation (PyPI - Coming Soon)
```bash
pip install sage-github-manager
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `github-manager status` | Show configuration and connection status |
| `github-manager download` | Download issues from GitHub |
| `github-manager analytics` | Generate statistics report |
| `github-manager team` | Team management and analysis |
| `github-manager ai` | AI-powered analysis |
| `github-manager sync` | Sync with GitHub |
| `github-manager organize` | Organize issues by status |
| `github-manager project` | Project management |
| `github-manager config` | Show configuration |
| `github-manager test` | Run test suite |

## Python API

```python
from sage_github import IssuesConfig, IssuesManager

# Configuration
config = IssuesConfig(
    github_owner="your-org",
    github_repo="your-repo"
)

# Manager
manager = IssuesManager()
issues = manager.load_issues()
manager.show_statistics()
```

## Data Storage

### Directory Structure
```
.github-manager/
├── workspace/
│   ├── data/          # JSON: issue_{number}.json
│   ├── views/
│   │   ├── markdown/  # Human-readable .md files
│   │   ├── metadata/  # Structured metadata
│   │   └── summaries/ # AI summaries
│   └── cache/         # Temporary files
├── output/            # Generated reports
│   └── statistics_*.json
└── metadata/          # Configuration
    ├── settings.json
    ├── team_config.py
    ├── boards_metadata.json
    └── update_history.json
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sage_github --cov-report=html

# Run specific test
pytest tests/test_config.py -v
```

## Release Process

1. Update version in `src/sage_github/__init__.py`
2. Update `CHANGELOG.md`
3. Run tests: `pytest`
4. Run linting: `black src/ tests/ && isort src/ tests/`
5. Build: `python -m build`
6. Tag release: `git tag v0.1.0`
7. Push: `git push origin v0.1.0`
8. Publish to PyPI: `twine upload dist/*`

## Future Enhancements

### Planned Features
- [ ] Web UI dashboard
- [ ] Real-time webhooks support
- [ ] Multi-repository management
- [ ] Custom plugins system
- [ ] Export to various formats (CSV, Excel, etc.)
- [ ] Advanced filtering and search
- [ ] Integration with other project management tools

### Under Consideration
- [ ] GitHub Actions integration
- [ ] Slack/Discord notifications
- [ ] Automated issue triage
- [ ] Machine learning for priority prediction
- [ ] GraphQL API support

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Acknowledgments

- Extracted from [SAGE project](https://github.com/intellistream/SAGE)
- Developed by IntelliStream Team
- Inspired by GitHub CLI and project management best practices

## Contact

- **Author**: IntelliStream Team
- **Email**: shuhao_zhang@hust.edu.cn
- **Repository**: https://github.com/intellistream/sage-github-manager
- **Issues**: https://github.com/intellistream/sage-github-manager/issues

## Version

Current version: **0.1.0**

Initial standalone release extracted from SAGE project.
