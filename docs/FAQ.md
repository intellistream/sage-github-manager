# Frequently Asked Questions

## Installation & Setup

### Q: How do I get a GitHub Personal Access Token?

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token"
3. Select scopes: `repo` (full repository access)
4. Copy the token and save it securely

Set it as an environment variable:
```bash
export GITHUB_TOKEN="your_token_here"
```

Or save to a file:
```bash
echo "your_token_here" > ~/.github_token
```

### Q: Where is my data stored?

By default, data is stored in `.github-manager/` in your project root:
- `workspace/`: Raw issues data
- `output/`: Generated reports
- `metadata/`: Configuration and tracking files

### Q: Can I use this with multiple repositories?

Yes! You can either:
1. Set environment variables for each repository:
   ```bash
   export GITHUB_OWNER="org1" GITHUB_REPO="repo1"
   github-manager download
   ```

2. Use Python API with custom config:
   ```python
   config = IssuesConfig(github_owner="org1", github_repo="repo1")
   manager = IssuesManager()
   ```

## Usage

### Q: How do I download issues for the first time?

```bash
# Set your repository
export GITHUB_OWNER="your-org"
export GITHUB_REPO="your-repo"

# Download all issues
github-manager download --state all
```

### Q: Can I filter issues by state?

Yes:
```bash
github-manager download --state open   # Only open issues
github-manager download --state closed # Only closed issues
github-manager download --state all    # All issues (default)
```

### Q: How often should I sync issues?

It depends on your needs:
- For active projects: Daily or before each analysis
- For archived projects: Weekly or as needed

Use `github-manager sync` to update both local and remote.

### Q: What AI features are available?

The tool supports several AI-powered features:
- `analyze`: Comprehensive issue analysis
- `dedupe`: Find duplicate issues
- `optimize`: Optimize labels and categories
- `report`: Generate detailed reports

Example:
```bash
github-manager ai --action analyze
```

## Troubleshooting

### Q: I get "GitHub Token未配置" error

Make sure you have set your GitHub token:
```bash
export GITHUB_TOKEN="your_token"
```

Or create a file:
```bash
echo "your_token" > ~/.github_token
```

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
