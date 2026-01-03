# Quick Start Guide

Get up and running with GitHub Issues Manager in 5 minutes!

## Prerequisites

- Python 3.10 or higher
- A GitHub account
- A GitHub Personal Access Token

## Step 1: Installation

```bash
# Install from source
git clone https://github.com/intellistream/sage-github-manager.git
cd sage-github-manager
pip install -e .
```

## Step 2: Get Your GitHub Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Give it a name (e.g., "Issues Manager")
4. Select scope: **repo** (full repository access)
5. Generate and copy the token

## Step 3: Configure Your Token

Choose one method:

### Method A: Environment Variable (Recommended)
```bash
export GITHUB_TOKEN="your_token_here"
```

### Method B: Token File
```bash
echo "your_token_here" > ~/.github_token
```

### Method C: Project-specific File
```bash
echo "your_token_here" > .github_token
```

## Step 4: Test Your Setup

```bash
# Check configuration
github-manager status

# Expected output:
# ✅ GitHub connection: Connected
# 📊 Configuration info
```

## Step 5: Download Your First Issues

```bash
# Set your repository (optional, defaults to intellistream/SAGE)
export GITHUB_OWNER="your-org"
export GITHUB_REPO="your-repo"

# Download all issues
github-manager download

# This will:
# - Connect to GitHub API
# - Download all issues with metadata
# - Save to .github-manager/workspace/
```

## Step 6: View Statistics

```bash
# Generate and view statistics
github-manager stats

# Output shows:
# - Total issues count
# - Open vs closed
# - Label distribution
# - Assignee statistics
# - Author distribution
```

## Common Tasks

### Download Only Open Issues
```bash
github-manager download --state open
```

### Update Team Information
```bash
github-manager team --update
```

### AI Analysis (Requires OpenAI API key)
```bash
export OPENAI_API_KEY="your_openai_key"
github-manager ai --action analyze
```

### Sync Changes to GitHub
```bash
github-manager sync --direction upload
```

### Organize Closed Issues
```bash
# Preview organization plan
github-manager organize --preview

# Execute organization
github-manager organize --apply --confirm
```

## Using as a Python Library

```python
from sage_github import IssuesConfig, IssuesManager

# Create configuration
config = IssuesConfig(
    github_owner="your-org",
    github_repo="your-repo"
)

# Create manager
manager = IssuesManager()

# Load and analyze
issues = manager.load_issues()
manager.show_statistics()
```

## Directory Structure After Setup

```
your-project/
├── .github-manager/       # Created automatically
│   ├── workspace/         # Raw data
│   │   ├── data/         # JSON files
│   │   └── views/        # Different views
│   ├── output/           # Generated reports
│   └── metadata/         # Config & tracking
└── .github_token         # Your token (if using file method)
```

## Troubleshooting

### Token Not Found
```bash
# Check if token is set
echo $GITHUB_TOKEN

# Or check file
cat ~/.github_token
```

### Connection Failed
```bash
# Test connection explicitly
github-manager status

# Check token has correct permissions:
# - repo scope must be enabled
```

### No Issues Downloaded
```bash
# Check repository settings
github-manager config

# Verify repository name and owner
export GITHUB_OWNER="correct-org"
export GITHUB_REPO="correct-repo"

# Try download again
github-manager download --force
```

### Import Errors
```bash
# Reinstall package
pip uninstall sage-github-manager
pip install -e .
```

## Next Steps

- Read the [full README](../README.md) for detailed documentation
- Check [examples/](../examples/) for usage examples
- See [FAQ](FAQ.md) for common questions
- Read [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute

## Getting Help

- 📖 Documentation: Check README and FAQ
- 🐛 Bugs: [Open an issue](https://github.com/intellistream/sage-github-manager/issues)
- 💬 Questions: [Start a discussion](https://github.com/intellistream/sage-github-manager/discussions)
- 📧 Email: shuhao_zhang@hust.edu.cn

Happy issue managing! 🎉
