# GitHub Issues Manager

🐙 A comprehensive GitHub Issues management tool with AI-powered features for downloading, analyzing, organizing, and managing GitHub Issues.

## Features

- 📥 **Download & Sync**: Download and synchronize GitHub Issues with full metadata
- 📊 **Statistics & Analytics**: Generate comprehensive statistics and reports
- 🤖 **AI-Powered Analysis**: Intelligent issue categorization, deduplication, and priority assessment
- 👥 **Team Management**: Team member tracking and automated assignment
- 📋 **Project Management**: Auto-organize issues based on status and timeline
- 🔄 **Bidirectional Sync**: Sync changes between local and GitHub
- 📝 **Multiple Views**: Support for JSON, Markdown, and metadata views

## Installation

### From PyPI (coming soon)

```bash
pip install sage-github-manager
```

### From Source

```bash
git clone https://github.com/intellistream/sage-github-manager.git
cd sage-github-manager
pip install -e .
```

## Quick Start

### 1. Set up GitHub Token

You need a GitHub Personal Access Token with `repo` scope to access the GitHub API.

```bash
# Set environment variable
export GITHUB_TOKEN="your_github_token"

# Or create a file
echo "your_github_token" > ~/.github_token
```

### 2. Configure Repository

You can set the target repository via environment variables:

```bash
export GITHUB_OWNER="your-org"
export GITHUB_REPO="your-repo"
```

Or pass them as parameters in your code.

### 3. Basic Usage

```bash
# Check status
github-manager status

# Download issues
github-manager download --state all

# Show statistics
github-manager analytics

# Team analysis
github-manager team

# Create new issue
github-manager create

# AI analysis
github-manager ai --action analyze
```

## CLI Commands

### Status & Configuration

```bash
# Show current configuration and status
github-manager status

# Show detailed configuration
github-manager config
```

### Download & Sync

```bash
# Download all issues
github-manager download

# Download only open issues
github-manager download --state open

# Force re-download
github-manager download --force

# Sync to GitHub
github-manager sync --direction upload

# Bidirectional sync
github-manager sync --direction both
```

### Statistics & Analysis

```bash
# Show statistics
github-manager analytics

# Team analysis
github-manager team

# Update team information from GitHub
github-manager team --update

# AI-powered analysis
github-manager ai --action analyze
github-manager ai --action dedupe
github-manager ai --action optimize
```

### Organization & Management

```bash
# Organize issues by status
github-manager organize --preview

# Execute organization plan
github-manager organize --apply --confirm

# Project management (detect and fix misassignments)
github-manager project
```

### Testing

```bash
# Run test suite
github-manager test
```

## Python API

### Basic Usage

```python
from sage_github import IssuesManager, IssuesConfig

# Create manager
config = IssuesConfig(
    github_owner="intellistream",
    github_repo="SAGE"
)
manager = IssuesManager()

# Load and analyze issues
issues = manager.load_issues()
manager.show_statistics()
manager.team_analysis()
```

### Custom Configuration

```python
from sage_github import IssuesConfig
from pathlib import Path

# Custom configuration
config = IssuesConfig(
    project_root=Path("/path/to/project"),
    github_owner="your-org",
    github_repo="your-repo"
)

# Test connection
if config.test_github_connection():
    print("Connected to GitHub successfully!")

# Get repository info
repo_info = config.get_repo_info()
print(f"Repository: {repo_info['full_name']}")
print(f"Stars: {repo_info['stargazers_count']}")
```

## Directory Structure

After initialization, the tool creates the following directory structure:

```
.github-manager/
├── workspace/          # Raw data storage
│   ├── data/          # JSON data files
│   ├── views/         # Different views (markdown, metadata, summaries)
│   └── cache/         # Temporary cache
├── output/            # Generated reports and statistics
└── metadata/          # Configuration and tracking files
    ├── settings.json
    ├── team_config.py
    ├── boards_metadata.json
    ├── ai_analysis_summary.json
    ├── update_history.json
    └── assignments.json
```

## Advanced Features

### AI Analysis

The AI analysis feature supports multiple engines and actions:

```bash
# Comprehensive analysis
github-manager ai --action analyze --engine openai

# Find duplicate issues
github-manager ai --action dedupe

# Optimize labels and categories
github-manager ai --action optimize

# Generate detailed report
github-manager ai --action report
```

### Team Management

```bash
# Show team info and statistics
github-manager team

# Update from GitHub API
github-manager team --update

# Combined update and analysis
github-manager team --update --analysis
```

### Project Organization

Automatically organize closed issues based on their closure time:

- **Done**: Issues closed within the last week
- **Archive**: Issues closed 1 week to 1 month ago
- **History**: Issues closed more than 1 month ago

```bash
# Preview organization plan
github-manager organize --preview

# Execute organization
github-manager organize --apply --confirm
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub Personal Access Token | (required) |
| `GH_TOKEN` | Alternative name for GitHub token | - |
| `GIT_TOKEN` | Alternative name for GitHub token | - |
| `GITHUB_OWNER` | Repository owner/organization | intellistream |
| `GITHUB_REPO` | Repository name | SAGE |

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/intellistream/sage-github-manager.git
cd sage-github-manager

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
black src/ tests/
isort src/ tests/
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sage_github --cov-report=html

# Run specific test
pytest tests/test_config.py -v
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original implementation from [SAGE](https://github.com/intellistream/SAGE) project
- Inspired by GitHub CLI and project management best practices

## Support

- **Issues**: [GitHub Issues](https://github.com/intellistream/sage-github-manager/issues)
- **Discussions**: [GitHub Discussions](https://github.com/intellistream/sage-github-manager/discussions)
- **Email**: shuhao_zhang@hust.edu.cn

## Related Projects

- [SAGE](https://github.com/intellistream/SAGE) - AI/LLM data processing pipeline framework
- [GitHub CLI](https://cli.github.com/) - Official GitHub command-line tool

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.
