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

### Quick Install (Recommended)

Run the automated installation script:

```bash
git clone https://github.com/intellistream/sage-github-manager.git
cd sage-github-manager
bash quickstart.sh
```

The script will:
- ✓ Check Python 3.10+ installation
- ✓ Install package and dependencies
- ✓ Set up virtual environment (optional)
- ✓ Configure GitHub credentials
- ✓ Install pre-commit hooks
- ✓ Verify installation

### Manual Installation

```bash
# Clone repository
git clone https://github.com/intellistream/sage-github-manager.git
cd sage-github-manager

# Install with dev dependencies
pip install -e ".[dev]"

# Set up environment variables
export GITHUB_TOKEN="your_github_token"
export GITHUB_OWNER="intellistream"
export GITHUB_REPO="SAGE"
```

### From PyPI (coming soon)

```bash
pip install sage-github-manager
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

Use the quick start script for automatic setup:

```bash
# One-line installation and setup
bash quickstart.sh
```

Or manually:

```bash
# Check status
github-manager status

# Download issues
github-manager download

# List open issues
github-manager list

# Show statistics
github-manager analytics

# Export to CSV
github-manager export issues.csv

# Team analysis
github-manager team

# Create new issue
github-manager create
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

### List Issues ✨ NEW

Flexibly list and filter issues with rich formatting:

```bash
# Basic listing
github-manager list                                # List all open issues
github-manager list --state all                    # List all issues
github-manager list --state closed                 # List closed issues

# Filter by labels (multiple labels = AND)
github-manager list --label bug
github-manager list --label bug --label priority:high

# Filter by assignee
github-manager list --assignee shuhao
github-manager list --assignee @me                 # Your own issues

# Filter by milestone
github-manager list --milestone "v2.0"

# Filter by author
github-manager list --author shuhao

# Sorting options
github-manager list --sort created                 # Sort by creation time
github-manager list --sort updated                 # Sort by last update
github-manager list --sort comments                # Sort by comment count

# Limit results
github-manager list --limit 10                     # Show top 10

# Combined filters
github-manager list --state open --label bug \
  --assignee shuhao --sort comments --limit 20

# Show issue body preview
github-manager list --body
```

**Output**: Color-coded table with issue number, title, state, labels, assignee, and statistics.

### Export Issues ✨ NEW

Export issues to various formats for reporting and analysis:

```bash
# CSV Export (for Excel/Google Sheets)
github-manager export issues.csv
github-manager export bugs.csv --state open --label bug

# JSON Export (structured data)
github-manager export issues.json --format json
github-manager export open.json -f json --state open

# Markdown Export (for documentation)
github-manager export ROADMAP.md --format markdown
github-manager export ROADMAP.md -f markdown --template roadmap
github-manager export REPORT.md -f markdown --template report

# Combined filtering
github-manager export sprint.csv \
  --state open --milestone "v2.0" --label priority:high

# Export with custom filters
github-manager export release_notes.md \
  -f markdown --template report \
  --state closed --milestone "v1.5"
```

**Supported Formats**:
- **CSV**: Excel-compatible spreadsheet
- **JSON**: Structured data with all fields
- **Markdown**: Three templates:
  - `default`: Detailed list with metadata
  - `roadmap`: Grouped by milestone
  - `report`: Concise summary

### Batch Operations ✨ NEW

Efficiently manage multiple issues at once:

```bash
# Batch close issues (with dry-run preview)
github-manager batch-close --label wontfix --dry-run
github-manager batch-close --label duplicate
github-manager batch-close --state open --milestone old-sprint

# Batch add labels
github-manager batch-label --add priority:high --label bug
github-manager batch-label --add reviewed --state closed
github-manager batch-label --add needs-docs --assignee shuhao

# Batch remove labels
github-manager batch-label --remove needs-review --state closed
github-manager batch-label --remove stale --milestone "v2.0"

# Batch assign issues (multiple assignees supported)
github-manager batch-assign --assignee shuhao --label p0
github-manager batch-assign --assignee alice,bob --label bug

# Batch set milestone
github-manager batch-milestone "v3.0" --state open
github-manager batch-milestone "v2.5" --label priority:high
```

**Safety Features**:
- `--dry-run`: Preview changes without executing
- Confirmation prompts before batch operations
- Detailed logs of all changes

### AI-Powered Features ✨ NEW

Leverage AI for intelligent issue management:

```bash
# Summarize long issue discussions
github-manager summarize --issue 123
github-manager summarize --issue 456 --model gpt-4

# Detect duplicate issues automatically
github-manager detect-duplicates
github-manager detect-duplicates --threshold 0.8

# Auto-suggest labels based on content
github-manager suggest-labels --issue 789
github-manager suggest-labels --issue 123 --model claude

# Comprehensive AI analysis
github-manager ai --action analyze       # Overall analysis
github-manager ai --action dedupe        # Find duplicates
github-manager ai --action optimize      # Optimize labels
github-manager ai --action report        # Generate AI report
```

**Setup**: Requires OpenAI or Anthropic API key:

```bash
# OpenAI (GPT-3.5/GPT-4)
export OPENAI_API_KEY=sk-...

# Anthropic (Claude)
export ANTHROPIC_API_KEY=sk-ant-...
```

**Use Cases**:
- 📝 **Summarize**: Quick insights from 100+ comment threads
- 🔍 **Detect Duplicates**: Find similar issues automatically
- 🏷️ **Suggest Labels**: Consistent labeling
- 📊 **Analyze**: Identify patterns and trends

### Statistics & Analysis

```bash
# Show statistics
github-manager analytics

# Team analysis
github-manager team

# Update team information from GitHub
github-manager team --update

# Combined analysis
github-manager team --update --analysis
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
