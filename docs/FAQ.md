# Frequently Asked Questions (FAQ)

## Installation & Setup

### Q: How do I install sage-github-manager?

**A:** Use the quick start script (recommended):
```bash
bash quickstart.sh
```

Or install manually:
```bash
pip install -e ".[dev]"
```

### Q: How do I get a GitHub Personal Access Token (PAT)?

**A:** Follow these steps:

1. Go to GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Click **"Generate new token (classic)"**
3. Give it a name (e.g., "SAGE Issues Manager")
4. Select scope: **repo** (full repository access)
5. Click **Generate token** and **copy it immediately**

Set it as an environment variable:
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Add to shell config for persistence
echo 'export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"' >> ~/.bashrc
source ~/.bashrc
```

Or save to a file:
```bash
echo "ghp_xxxxxxxxxxxx" > ~/.github_token
chmod 600 ~/.github_token  # Secure permissions
```

### Q: Where is my data stored?

**A:** Data is stored in `~/.github-manager/` (home directory):

```
~/.github-manager/
├── data/
│   └── {owner}/
│       └── {repo}/
│           ├── issues/           # JSON files for each issue
│           └── metadata.json     # Repository metadata
├── config.yaml                   # User configuration
├── label_config.yaml             # Label taxonomy
└── team_config.py                # Team settings
```

This allows you to work with multiple repositories without conflicts.

### Q: Can I use this with multiple repositories?

**A:** Yes! Each repository's data is stored separately:

```bash
# Repository 1
export GITHUB_OWNER="intellistream"
export GITHUB_REPO="SAGE"
github-manager download

# Repository 2
export GITHUB_OWNER="myorg"
export GITHUB_REPO="myproject"
github-manager download
```

Or use Python API:
```python
from sage_github import IssuesManager, IssuesConfig

# Manager automatically uses current env vars
manager = IssuesManager()

# Or create separate configs
config1 = IssuesConfig(github_owner="intellistream", github_repo="SAGE")
config2 = IssuesConfig(github_owner="myorg", github_repo="myproject")
```

## Basic Usage

### Q: How do I download issues for the first time?

**A:**
```bash
# Set your repository
export GITHUB_OWNER="intellistream"
export GITHUB_REPO="SAGE"
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Download all issues
github-manager download

# Or download only open issues
github-manager download --state open
```

First download may take a few minutes for large repositories.

### Q: How do I list issues?

**A:** Use the `list` command with various filters:

```bash
# Basic listing
github-manager list                           # All open issues
github-manager list --state all               # All issues
github-manager list --state closed            # Only closed issues

# Filter by labels
github-manager list --label bug
github-manager list --label bug --label priority:high  # Multiple labels

# Filter by assignee
github-manager list --assignee shuhao
github-manager list --assignee @me            # Your own issues

# Filter by milestone
github-manager list --milestone "v2.0"

# Sorting and limiting
github-manager list --sort created --limit 10
github-manager list --sort comments           # Most discussed

# Combined filters
github-manager list --state open --label bug --assignee shuhao
```

### Q: How do I export issues?

**A:** Use the `export` command:

```bash
# CSV export (for Excel/Google Sheets)
github-manager export issues.csv
github-manager export bugs.csv --label bug --state open

# JSON export (structured data)
github-manager export issues.json --format json

# Markdown export (for documentation)
github-manager export ROADMAP.md --format markdown
github-manager export ROADMAP.md -f markdown --template roadmap  # Grouped by milestone
github-manager export REPORT.md -f markdown --template report    # Concise format

# With filtering
github-manager export sprint.csv --milestone "v2.0" --state open
```

**Supported Formats**:
- **CSV**: Comma-separated values (Excel/Google Sheets compatible)
- **JSON**: Structured data with all fields
- **Markdown**: Three templates (default, roadmap, report)

### Q: How do I perform batch operations?

**A:** Use batch commands with `--dry-run` for safety:

```bash
# Batch close issues (preview first!)
github-manager batch-close --label wontfix --dry-run
github-manager batch-close --label duplicate          # Execute

# Batch add/remove labels
github-manager batch-label --add priority:high --label bug
github-manager batch-label --remove needs-review --state closed

# Batch assign issues
github-manager batch-assign --assignee shuhao --label p0
github-manager batch-assign --assignee alice,bob --milestone "v2.0"

# Batch set milestone
github-manager batch-milestone "v3.0" --state open
```

**Safety Features**:
- `--dry-run`: Preview changes without executing
- Confirmation prompts before operations
- Detailed logs of all changes

### Q: How often should I sync issues?

**A:** It depends on your workflow:

- **Active projects**: Daily (before morning standup)
- **Sprint planning**: Before each sprint meeting
- **Release preparation**: Before and after releases
- **Archived projects**: Weekly or as needed

```bash
# Quick sync (incremental)
github-manager download

# Force full re-download
github-manager download --force

# Bidirectional sync
github-manager sync --direction both
```

Incremental downloads are fast (only fetches new/updated issues).

## AI Features

### Q: What AI features are available?

**A:** Three main AI-powered features:

1. **Summarize**: Get quick insights from long issue threads
   ```bash
   github-manager summarize --issue 123
   ```

2. **Detect Duplicates**: Find similar issues automatically
   ```bash
   github-manager detect-duplicates
   github-manager detect-duplicates --threshold 0.8
   ```

3. **Suggest Labels**: Auto-recommend labels based on content
   ```bash
   github-manager suggest-labels --issue 456
   ```

4. **Comprehensive Analysis**: Overall insights
   ```bash
   github-manager ai --action analyze
   ```

See [AI Features Guide](AI_FEATURES.md) for details.

### Q: Do I need an API key for AI features?

**A:** It depends on the feature:

**Requires API Key**:
- `summarize`: Needs OpenAI or Anthropic API
- `ai --action analyze`: Needs OpenAI or Anthropic API

**No API Key Needed**:
- `detect-duplicates`: Uses local text similarity
- `suggest-labels`: Uses keyword matching

**Setup**:
```bash
# OpenAI (GPT-3.5/GPT-4)
export OPENAI_API_KEY="sk-..."

# Anthropic (Claude)
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Q: How much do AI features cost?

**A:** Estimated costs (using GPT-4):

| Operation | API Calls | Avg. Tokens | Est. Cost |
|-----------|-----------|-------------|-----------|
| Summarize (short) | 1 | 500 | $0.01 |
| Summarize (long) | 1 | 2000 | $0.06 |
| Suggest Labels | 1 | 300 | $0.01 |
| Full Analysis | N×2 | 500×N | $0.03×N |

**Cost Optimization**:
- Use GPT-3.5-turbo instead of GPT-4 (10× cheaper)
- Results are cached locally for 24 hours
- Detect duplicates is free (no API calls)

## Troubleshooting

### Q: I get "GITHUB_TOKEN not found" error

**A:** Make sure you have set your GitHub token:
```bash
# Check if token is set
echo $GITHUB_TOKEN

# Set it if empty
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# Or create token file
echo "ghp_xxxxxxxxxxxx" > ~/.github_token
chmod 600 ~/.github_token

# Verify
github-manager status
```

### Q: Connection to GitHub fails

**A:** Test your token and connection:

```bash
# Test token directly with GitHub API
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Expected: Your GitHub user info in JSON
# If error: Token is invalid or expired, regenerate it
```

Common issues:
- Token doesn't have `repo` scope
- Token has expired
- Network/firewall issues

### Q: No issues are downloaded

**A:** Check your repository settings:

```bash
# Check configuration
github-manager config

# Verify correct repository
export GITHUB_OWNER="intellistream"  # Correct owner
export GITHUB_REPO="SAGE"            # Correct repo name

# Force re-download
github-manager download --force
```

Make sure you have access to the repository.

### Q: Command not found after installation

**A:** Ensure the package is properly installed:

```bash
# Reinstall with dev dependencies
pip install -e ".[dev]"

# Check if command is available
which github-manager

# If not found, add to PATH
export PATH="$PATH:$HOME/.local/bin"

# Or use python -m
python -m sage_github.cli_main --help
```

### Q: Import errors when using Python API

**A:** Make sure you're in the correct directory and package is installed:

```bash
# Navigate to project root
cd /path/to/sage-github-manager

# Reinstall package
pip uninstall sage-github-manager
pip install -e ".[dev]"

# Test import
python -c "from sage_github import IssuesManager; print('OK')"
```

### Q: Rate limit exceeded

**A:** GitHub API has rate limits:

**Authenticated requests**: 5,000 requests/hour
**Unauthenticated**: 60 requests/hour

If you hit the limit:
```bash
# Wait for rate limit reset (check headers)
# Or use multiple tokens (for different repositories)

# Check current rate limit
curl -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/rate_limit
```

The tool automatically handles rate limits and retries.

## Advanced Usage

### Q: Can I customize label suggestions?

**A:** Yes! Create `.github-manager/label_config.yaml`:

```yaml
# Label taxonomy
categories:
  type: [bug, feature, documentation]
  priority: [priority:high, priority:medium, priority:low]
  area: [backend, frontend, database]

# Auto-apply rules
auto_apply:
  - pattern: "memory|leak|gc"
    labels: ["performance", "memory"]
  - pattern: "crash|segfault"
    labels: ["bug", "priority:high"]
```

### Q: Can I automate daily syncs?

**A:** Yes! Set up a cron job:

```bash
# Edit crontab
crontab -e

# Add daily sync at 9 AM
0 9 * * * cd /path/to/sage-github-manager && github-manager download

# Or create a script
cat > ~/daily_sync.sh << 'EOF'
#!/bin/bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
export GITHUB_OWNER="intellistream"
export GITHUB_REPO="SAGE"
cd /path/to/sage-github-manager
github-manager download
github-manager analytics > daily_report.txt
EOF

chmod +x ~/daily_sync.sh

# Add to cron
0 9 * * * ~/daily_sync.sh
```

### Q: Can I use this in CI/CD pipelines?

**A:** Yes! Example GitHub Actions workflow:

```yaml
# .github/workflows/issue-sync.yml
name: Daily Issue Sync

on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM daily
  workflow_dispatch:      # Manual trigger

jobs:
  sync-issues:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install sage-github-manager
        run: pip install -e .

      - name: Download Issues
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_OWNER: ${{ github.repository_owner }}
          GITHUB_REPO: ${{ github.event.repository.name }}
        run: |
          github-manager download
          github-manager analytics
```

### Q: How do I migrate from another issue tracker?

**A:** The tool primarily works with GitHub Issues. To migrate:

1. **Export from other tool**: Most issue trackers support CSV export
2. **Convert to GitHub format**: Use GitHub's CSV import or API
3. **Import to GitHub**: Use GitHub's bulk import feature
4. **Sync with sage-github-manager**: Run `github-manager download`

For custom migrations, use the Python API:

```python
from sage_github import IssuesManager
import requests

manager = IssuesManager()

# Example: Import from Jira
for jira_issue in jira_issues:
    github_issue = {
        "title": jira_issue["summary"],
        "body": jira_issue["description"],
        "labels": jira_issue["labels"]
    }
    # Create in GitHub using requests
    # Then sync with manager.download()
```

## Performance

### Q: How long does it take to download issues?

**A:** Depends on repository size:

- **Small (<100 issues)**: 10-30 seconds
- **Medium (100-1000)**: 1-5 minutes
- **Large (>1000)**: 5-15 minutes
- **Very Large (>5000)**: 15-30 minutes

**Incremental updates** (after first download) are much faster (10-30 seconds).

### Q: Can I speed up downloads?

**A:** Yes! Several optimizations:

1. **Download only open issues** (if closed issues aren't needed):
   ```bash
   github-manager download --state open
   ```

2. **Use incremental sync** (only new/updated):
   ```bash
   github-manager download  # Automatic incremental
   ```

3. **Increase concurrency** (advanced):
   ```python
   # Edit config
   max_workers = 10  # Default is 5
   ```

4. **Use local caching** (automatic)

## Integration

### Q: Can I integrate with Slack/Discord?

**A:** Yes! Example scripts:

**Slack Webhook**:
```bash
#!/bin/bash
# slack_report.sh

WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Generate report
report=$(github-manager analytics)

# Send to Slack
curl -X POST -H 'Content-type: application/json' \
  --data "{\"text\":\"Daily Issue Report:\n\`\`\`$report\`\`\`\"}" \
  $WEBHOOK_URL
```

**Discord Webhook**:
```python
import requests
from sage_github import IssuesManager

manager = IssuesManager()
issues = manager.list_issues(state="open", labels=["priority:high"])

webhook_url = "https://discord.com/api/webhooks/YOUR/WEBHOOK"
message = f"🚨 {len(issues)} high-priority issues open!"

requests.post(webhook_url, json={"content": message})
```

### Q: Can I use this with Notion/Obsidian?

**A:** Yes! Export to Markdown:

```bash
# Export for Notion (import Markdown)
github-manager export NOTION_IMPORT.md --format markdown

# For Obsidian (daily note)
github-manager export ~/Obsidian/DailyNotes/issues_$(date +%Y-%m-%d).md \
  --format markdown --template report --state open
```

## Security

### Q: Is my GitHub token stored securely?

**A:** The tool itself doesn't store your token in any file. It reads from:

1. Environment variables (most secure)
2. Token files with restricted permissions (`.github_token`)

**Best practices**:
- Never commit tokens to git (add `.env` to `.gitignore`)
- Use `chmod 600` for token files
- Rotate tokens every 90 days
- Consider fine-grained GitHub PATs (more granular permissions)

### Q: Can I use fine-grained GitHub tokens?

**A:** Yes! Fine-grained Personal Access Tokens (beta) are supported:

1. Go to GitHub → Settings → Developer settings → **Personal access tokens** → **Fine-grained tokens**
2. Click **Generate new token**
3. Set **Repository access** → Select repositories
4. Set **Permissions** → Repository permissions → Issues (Read and write)
5. Generate and use like classic tokens

Fine-grained tokens are more secure (limited scope and expiration).

## Contributing

### Q: How can I contribute?

**A:** Contributions are welcome!

1. **Report bugs**: [Open an issue](https://github.com/intellistream/sage-github-manager/issues/new)
2. **Suggest features**: [Start a discussion](https://github.com/intellistream/sage-github-manager/discussions)
3. **Submit PRs**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
4. **Improve docs**: Documentation PRs are highly appreciated!

**Development setup**:
```bash
git clone https://github.com/intellistream/sage-github-manager.git
cd sage-github-manager
pip install -e ".[dev]"
pre-commit install
pytest  # Run tests
```

### Q: Where can I get help?

**A:** Multiple channels:

- 📖 **Documentation**: See [docs/](.) folder
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/intellistream/sage-github-manager/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/intellistream/sage-github-manager/discussions)
- 📧 **Email**: shuhao_zhang@hust.edu.cn

## Comparison

### Q: How is this different from GitHub CLI (`gh`)?

**A:** Different focus:

| Feature | sage-github-manager | GitHub CLI (`gh`) |
|---------|---------------------|-------------------|
| **Purpose** | Issue management & analytics | General GitHub operations |
| **Local Storage** | ✅ Full local database | ❌ No local storage |
| **Batch Operations** | ✅ Advanced batch commands | ⚠️ Basic |
| **AI Features** | ✅ Summaries, duplicates, labels | ❌ None |
| **Export Formats** | ✅ CSV, JSON, Markdown | ⚠️ Limited |
| **Filtering** | ✅ Rich filtering options | ⚠️ Basic |
| **Analytics** | ✅ Comprehensive analytics | ❌ Minimal |
| **Offline Mode** | ✅ Work offline | ❌ Requires internet |

**When to use sage-github-manager**:
- Managing large issue backlogs
- Need local analytics and reporting
- Batch operations on multiple issues
- AI-powered insights
- Offline access to issue data

**When to use GitHub CLI**:
- Creating/editing issues quickly
- Managing PRs, repos, gists
- Git operations
- GitHub Actions management

You can use both together!

### Q: Can I use this with GitHub Projects (beta)?

**A:** Partially. The tool focuses on Issues, but you can:

1. **Export issues** for import to Projects
2. **Use labels** that correspond to Project fields
3. **Batch update milestones** that sync with Projects

Direct GitHub Projects API integration is a future enhancement.

## Miscellaneous

### Q: What's the difference between `download` and `sync`?

**A:**

- **`download`**: One-way sync (GitHub → Local)
  ```bash
  github-manager download  # Fetch latest from GitHub
  ```

- **`sync`**: Two-way sync (supports upload)
  ```bash
  github-manager sync --direction upload  # Local → GitHub
  github-manager sync --direction both    # Bidirectional
  ```

Use `download` for read-only workflows (most common).

### Q: Can I export specific fields only?

**A:** Not directly, but you can filter in Python:

```python
from sage_github import IssuesManager
import csv

manager = IssuesManager()
issues = manager.load_issues()

# Export custom fields
with open('custom.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Number', 'Title', 'Author'])
    for issue in issues:
        writer.writerow([
            issue['number'],
            issue['title'],
            issue['user']['login']
        ])
```

Or use `jq` with JSON export:
```bash
github-manager export issues.json -f json
jq '.[] | {number, title, author: .user.login}' issues.json
```

### Q: Does this work with GitHub Enterprise?

**A:** Yes! Set the API URL:

```bash
export GITHUB_API_URL="https://github.company.com/api/v3"
export GITHUB_TOKEN="your_enterprise_token"

github-manager download
```

Or in Python:
```python
config = IssuesConfig(
    github_api_url="https://github.company.com/api/v3",
    github_owner="org",
    github_repo="repo"
)
```

### Q: Can I contribute custom templates?

**A:** Yes! Create templates in `.github-manager/templates/`:

```bash
mkdir -p ~/.github-manager/templates
cat > ~/.github-manager/templates/my_template.md << 'EOF'
# Custom Report: {date}

## Issues by Priority

{issues_by_priority}

## Recent Activity

{recent_issues}
EOF
```

Then use:
```bash
github-manager export report.md --template my_template
```

Submit your templates as PRs to share with the community!

---

## Still Have Questions?

- 📖 Read the [Complete Documentation](../README.md)
- 🚀 Check [Quick Start Guide](QUICK_START.md)
- 🤖 See [AI Features Guide](AI_FEATURES.md)
- 💬 [Start a Discussion](https://github.com/intellistream/sage-github-manager/discussions)
- 🐛 [Report a Bug](https://github.com/intellistream/sage-github-manager/issues/new)


### Q: The tool can't find my issues

1. Check you've downloaded them first:
   ```bash
   github-manager download
   ```

2. Verify your repository settings:
   ```bash
   github-manager config
   ```

3. Check GitHub connection:
   ```bash
   github-manager status
   ```

### Q: API rate limit errors

GitHub has rate limits for API calls:
- Authenticated: 5000 requests/hour
- Unauthenticated: 60 requests/hour

Solutions:
- Ensure you're using a GitHub token
- Wait for rate limit to reset
- Use `--force` flag sparingly

### Q: Import errors when using as a library

Make sure the package is installed:
```bash
pip install sage-github-manager
# Or for development:
pip install -e .
```

## Advanced

### Q: Can I customize the output directory?

Yes, you can specify a custom project root:

```python
from pathlib import Path
config = IssuesConfig(project_root=Path("/custom/path"))
```

### Q: How do I integrate this with CI/CD?

Example GitHub Actions workflow:

```yaml
name: Sync Issues
on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install sage-github-manager
      - run: github-manager download
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      - run: github-manager analytics
```

### Q: Can I export data to other formats?

Currently supports:
- JSON (raw data)
- Markdown (human-readable)
- Metadata files (structured)

Custom exports can be implemented using the Python API.

### Q: How do I contribute?

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Still have questions?

- Check the [README](README.md) for comprehensive documentation
- Open an [issue](https://github.com/intellistream/sage-github-manager/issues)
- Email: shuhao_zhang@hust.edu.cn
