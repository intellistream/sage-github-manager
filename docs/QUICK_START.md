# Quick Start Guide

Get up and running with **sage-github-manager** in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- Git (optional, for cloning)
- A GitHub account
- A GitHub Personal Access Token (PAT)

## Quick Installation

### Option 1: Automatic Setup (Recommended)

Use the quick start script for one-line installation:

```bash
# Download and run
curl -O https://raw.githubusercontent.com/intellistream/sage-github-manager/main/quickstart.sh
bash quickstart.sh

# Or if you've cloned the repo
cd sage-github-manager
bash quickstart.sh
```

The script will:
- ✅ Check Python version (3.10+)
- ✅ Detect your environment (conda/venv/system)
- ✅ Install dependencies
- ✅ Set up pre-commit hooks
- ✅ Guide you through GitHub token setup
- ✅ Show usage examples

### Option 2: Manual Installation

```bash
# Clone repository
git clone https://github.com/intellistream/sage-github-manager.git
cd sage-github-manager

# Install package with dev dependencies
pip install -e ".[dev]"

# (Optional) Set up pre-commit hooks
pre-commit install
```

## GitHub Token Setup

### Step 1: Generate Token

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **"Generate new token (classic)"**
3. Give it a name (e.g., "SAGE Issues Manager")
4. Select scope: **repo** (full repository access)
5. Click **Generate token** and **copy it immediately**

### Step 2: Configure Token

Choose one method:

**Method A: Environment Variable (Recommended)**
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Add to your shell config for persistence
echo 'export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc
```

**Method B: Token File**
```bash
echo "ghp_xxxxxxxxxxxx" > ~/.github_token
chmod 600 ~/.github_token  # Secure permissions
```

**Method C: .env File**
```bash
# Create .env file in project directory
cat > .env << EOF
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_OWNER=intellistream
GITHUB_REPO=SAGE
EOF
```

## Initial Configuration

### Step 1: Set Repository

Configure which repository to manage:

```bash
# Set via environment variables (recommended)
export GITHUB_OWNER="intellistream"
export GITHUB_REPO="SAGE"

# Or add to .env file (see above)
```

### Step 2: Verify Connection

```bash
# Check configuration and test connection
github-manager status

# Expected output:
# ✅ GitHub connection: Connected
# 📊 Repository: intellistream/SAGE
# 🔑 Token: Found and valid
# 📁 Data directory: ~/.github-manager/data/intellistream/SAGE/
```

### Step 3: Download Issues

```bash
# Download all issues (first time may take a few minutes)
github-manager download

# Progress will be shown:
# Downloading issues... ━━━━━━━━━━━━━━━━━━ 100% 247/247
# ✅ Downloaded 247 issues
```

## Your First Commands

### 1. List Issues

```bash
# List all open issues
github-manager list

# Filter by label
github-manager list --label bug

# Filter by assignee
github-manager list --assignee shuhao

# Combine filters
github-manager list --state open --label "priority:high" --sort comments
```

**Output**: Color-coded table showing issues with metadata.

### 2. View Analytics

```bash
# Show overall statistics
github-manager analytics

# Output includes:
# - Issue distribution (open/closed)
# - Label statistics
# - Assignee workload
# - Activity trends
```

### 3. Export Issues

```bash
# Export to CSV
github-manager export issues.csv

# Export to JSON
github-manager export issues.json --format json

# Export to Markdown
github-manager export ROADMAP.md --format markdown --template roadmap
```

### 4. Batch Operations

```bash
# Close multiple issues (dry-run first!)
github-manager batch-close --label wontfix --dry-run

# Add labels to issues
github-manager batch-label --add reviewed --state closed

# Assign issues
github-manager batch-assign --assignee shuhao --label p0
```

## Common Workflows

### Daily Issue Triage

```bash
# 1. Sync latest issues
github-manager download

# 2. List new issues (created today)
github-manager list --sort created --limit 10

# 3. View analytics
github-manager analytics

# 4. Export for team meeting
github-manager export daily_report.csv --state open
```

### Sprint Planning

```bash
# 1. List issues for milestone
github-manager list --milestone "v2.0" --state open

# 2. Export sprint backlog
github-manager export sprint_backlog.csv --milestone "v2.0"

# 3. Generate roadmap
github-manager export ROADMAP.md --format markdown --template roadmap

# 4. Assign issues to team
github-manager batch-assign --assignee alice --milestone "v2.0" --label frontend
github-manager batch-assign --assignee bob --milestone "v2.0" --label backend
```

### Release Preparation

```bash
# 1. List release blockers
github-manager list --label release-blocker --state open

# 2. Export closed issues for release notes
github-manager export release_notes.md \
  --format markdown \
  --template report \
  --state closed \
  --milestone "v1.5"

# 3. Mark issues as released
github-manager batch-label --add released --milestone "v1.5" --state closed
```

### Issue Cleanup

```bash
# 1. Find potential duplicates
github-manager detect-duplicates

# 2. Close resolved issues
github-manager batch-close --label resolved --dry-run  # Preview first
github-manager batch-close --label resolved            # Execute

# 3. Remove stale labels
github-manager batch-label --remove stale --state closed
```

## AI Features (Optional)

AI features require an OpenAI or Anthropic API key.

### Setup

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Or Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Usage

```bash
# Summarize a long issue thread
github-manager summarize --issue 123

# Detect duplicate issues
github-manager detect-duplicates

# Suggest labels for an issue
github-manager suggest-labels --issue 456

# Full AI analysis
github-manager ai --action analyze
```

See [AI Features Guide](AI_FEATURES.md) for detailed documentation.

## Advanced Operations

### Sync Changes to GitHub
```bash
# Upload local changes to GitHub
github-manager sync --direction upload

# Bidirectional sync
github-manager sync --direction both
```

### Organize Closed Issues
```bash
# Preview organization plan
github-manager organize --preview

# Execute organization (groups by age)
github-manager organize --apply --confirm
```

### Team Management
```bash
# Update team information from GitHub
github-manager team --update

# View team statistics
github-manager team
```

## Using as a Python Library

```python
from sage_github import IssuesConfig, IssuesManager

# Create configuration
config = IssuesConfig(
    github_owner="intellistream",
    github_repo="SAGE"
)

# Create manager
manager = IssuesManager()

# Load and analyze
issues = manager.load_issues()

# List filtered issues
open_bugs = manager.list_issues(
    state="open",
    labels=["bug"],
    sort="created"
)

# Export to file
manager.export_issues(
    output_file="bugs.csv",
    format="csv",
    filters={"state": "open", "labels": ["bug"]}
)

# Show statistics
manager.show_statistics()
```

## Directory Structure After Setup

```
~/.github-manager/                  # Config directory
├── data/                           # Issue data
│   └── intellistream/
│       └── SAGE/
│           ├── issues/            # JSON files for each issue
│           └── metadata.json      # Repository metadata
├── config.yaml                     # User configuration
├── label_config.yaml               # Label taxonomy
└── team_config.py                  # Team settings

your-project/
├── .env                            # Environment variables (gitignored)
├── issues.csv                      # Exported data
└── ROADMAP.md                      # Generated reports
```

## Troubleshooting

### Issue: "GITHUB_TOKEN not found"

**Solution**:
```bash
# Check if token is set
echo $GITHUB_TOKEN

# Set it if empty
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Or check file
cat ~/.github_token

# Verify
github-manager status
```

### Issue: "Connection failed"

**Solution**:
```bash
# Test token directly
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Expected: Your GitHub user info
# If error: Regenerate token with 'repo' scope
```

### Issue: "No issues downloaded"

**Solution**:
```bash
# Check repository settings
github-manager config

# Verify correct repository
export GITHUB_OWNER="intellistream"
export GITHUB_REPO="SAGE"

# Force re-download
github-manager download --force
```

### Issue: "Command not found"

**Solution**:
```bash
# Reinstall package
pip install -e ".[dev]"

# Check if installed
which github-manager

# If not found, add to PATH
export PATH="$PATH:$HOME/.local/bin"
```

### Issue: Import errors

**Solution**:
```bash
# Ensure in correct directory
cd /path/to/sage-github-manager

# Reinstall with dependencies
pip uninstall sage-github-manager
pip install -e ".[dev]"

# Test import
python -c "from sage_github import IssuesManager; print('OK')"
```

## Next Steps

### Documentation

- 📚 [Complete CLI Reference](../README.md#cli-commands)
- 🤖 [AI Features Guide](AI_FEATURES.md)
- ❓ [FAQ](FAQ.md)
- 📋 [Development Guide](../DEVELOPMENT.md)
- 🤝 [Contributing Guide](../CONTRIBUTING.md)

### Examples

Check out [examples/](../examples/) for:
- `basic_usage.py` - Simple scripts
- `advanced_usage.py` - Complex workflows
- `batch_operations.sh` - Shell scripts

### Advanced Customization

1. **Label Taxonomy**: Edit `~/.github-manager/label_config.yaml`
2. **Team Aliases**: Edit `~/.github-manager/team_config.py`
3. **Templates**: Create custom export templates
4. **Automation**: Set up cron jobs for daily syncs

## Getting Help

- 📖 **Documentation**: See [docs/](../docs/) folder
- 🐛 **Bug Reports**: [Open an issue](https://github.com/intellistream/sage-github-manager/issues/new)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/intellistream/sage-github-manager/discussions)
- 📧 **Email**: shuhao_zhang@hust.edu.cn

## Tips & Best Practices

### Performance

- Run `github-manager download` regularly (incremental updates are fast)
- Use filters with `list` and `export` to reduce processing
- AI summaries are cached locally for 24 hours

### Workflow

- **Morning**: `download` → `list --sort created` → `analytics`
- **Before Meetings**: `export --format markdown`
- **After Releases**: `batch-label --add "released"`
- **Weekly**: `detect-duplicates` and cleanup

### Security

- Never commit `.env` files (add to `.gitignore`)
- Use `chmod 600 ~/.github_token` for file-based tokens
- Rotate tokens every 90 days
- Consider fine-grained GitHub PATs for better security

Happy issue managing! 🎉
