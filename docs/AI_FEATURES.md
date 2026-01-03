# AI-Powered Features Guide

This guide covers the AI-powered features in `sage-github-manager` for intelligent issue management.

## Overview

The AI features use Large Language Models (LLMs) to:
- 📝 **Summarize** long issue discussions
- 🔍 **Detect** duplicate issues automatically
- 🏷️ **Suggest** relevant labels based on content
- 📊 **Analyze** issue patterns and trends

## Setup

### API Keys

AI features require an API key from OpenAI or Anthropic:

```bash
# OpenAI (GPT-3.5-turbo, GPT-4)
export OPENAI_API_KEY=sk-...

# Anthropic (Claude-3-sonnet, Claude-3-opus)
export ANTHROPIC_API_KEY=sk-ant-...
```

Add to your `.bashrc` or `.zshrc` for persistence:

```bash
echo 'export OPENAI_API_KEY=sk-...' >> ~/.bashrc
source ~/.bashrc
```

### Supported Models

| Provider | Model | Best For | Speed | Cost |
|----------|-------|----------|-------|------|
| OpenAI | gpt-3.5-turbo | Quick summaries | ⚡ Fast | 💰 Low |
| OpenAI | gpt-4 | Complex analysis | 🐌 Slow | 💰💰 High |
| Anthropic | claude-3-sonnet | Balanced | ⚡ Fast | 💰 Medium |
| Anthropic | claude-3-opus | Best quality | 🐌 Slow | 💰💰💰 High |

## Features

### 1. Summarize Issues

**Use Case**: Get quick insights from long issue threads (100+ comments).

```bash
# Basic summarization
github-manager summarize --issue 123

# Use specific model
github-manager summarize --issue 456 --model gpt-4
github-manager summarize --issue 789 --model claude-3-opus

# Batch summarize multiple issues
for i in 123 456 789; do
  github-manager summarize --issue $i
done
```

**Output Example**:
```
📝 Issue #123 Summary
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Title: Memory leak in data processing pipeline

🎯 Key Points:
- Memory usage increases over time in production
- Reproducible with large datasets (>10GB)
- Affects v2.1.0 and v2.1.1

💡 Proposed Solutions:
1. Implement streaming processing (main proposal)
2. Add memory profiling tools
3. Upgrade to Python 3.11 for better GC

🔍 Status: In Progress
👥 Contributors: alice, bob, charlie (3 people)
📅 Activity: 45 comments over 2 weeks
```

**When to Use**:
- Issue has 20+ comments
- Need to onboard new team members quickly
- Preparing for sprint planning
- Creating status reports

### 2. Detect Duplicates

**Use Case**: Find similar or duplicate issues automatically.

```bash
# Detect all duplicates
github-manager detect-duplicates

# Adjust similarity threshold (0.0-1.0)
github-manager detect-duplicates --threshold 0.8  # Strict
github-manager detect-duplicates --threshold 0.6  # Relaxed

# Filter by state
github-manager detect-duplicates --state open
```

**Output Example**:
```
🔍 Duplicate Detection Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Found 3 duplicate groups:

📦 Group 1 (Similarity: 95%)
  #123: Memory leak in data pipeline
  #156: Data processing memory issue
  #178: Pipeline memory consumption growing

  💡 Recommendation: Close #156 and #178 as duplicates of #123

📦 Group 2 (Similarity: 87%)
  #234: API timeout errors
  #267: Timeout when calling API

  💡 Recommendation: Merge discussions into #234

📦 Group 3 (Similarity: 81%)
  #345: Docker build fails on M1 Mac
  #389: Build error on Apple Silicon

  💡 Recommendation: Close #389 as duplicate
```

**When to Use**:
- Before creating a new issue (search duplicates first)
- During issue triage (weekly/monthly)
- After large feature releases (many similar bug reports)
- Cleaning up old issues

**Best Practices**:
- Start with threshold 0.8 (strict) to avoid false positives
- Lower to 0.7 if you want more suggestions
- Always review suggestions before closing issues
- Add links to original issues when closing duplicates

### 3. Suggest Labels

**Use Case**: Automatically suggest relevant labels based on issue content.

```bash
# Suggest labels for an issue
github-manager suggest-labels --issue 123

# Use specific model
github-manager suggest-labels --issue 456 --model claude

# Batch suggest for multiple issues
github-manager suggest-labels --issue 123,456,789
```

**Output Example**:
```
🏷️ Label Suggestions for Issue #123
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Title: Memory leak in data processing pipeline

📋 Suggested Labels:
  ✅ bug              (confidence: 95%)  [High Priority]
  ✅ performance      (confidence: 90%)  [High Priority]
  ✅ memory           (confidence: 85%)
  ⚠️  needs-profiling (confidence: 70%)
  ⚠️  python          (confidence: 65%)

🔍 Reasoning:
- "memory leak" clearly indicates a bug
- Performance issue based on description
- Explicit mention of memory problems
- May need profiling tools for diagnosis
- Python-specific based on stack trace

💡 Current Labels: bug, help-wanted
📝 Recommendation: Add "performance" and "memory"

Apply these labels? [y/N]
```

**When to Use**:
- New issues without labels
- Inconsistent labeling across issues
- After reorganizing label taxonomy
- Training new contributors on labeling

**Configuration**:

You can customize label suggestions by creating `.github-manager/label_config.yaml`:

```yaml
# Label taxonomy
categories:
  type:
    - bug
    - feature
    - documentation
  priority:
    - priority:high
    - priority:medium
    - priority:low
  area:
    - backend
    - frontend
    - database

# Auto-apply rules
auto_apply:
  - pattern: "memory|leak|gc"
    labels: ["performance", "memory"]
  - pattern: "crash|segfault|core dump"
    labels: ["bug", "priority:high"]
```

### 4. Comprehensive AI Analysis

**Use Case**: Get overall insights about your issue tracker health.

```bash
# Full analysis
github-manager ai --action analyze

# Find duplicates
github-manager ai --action dedupe

# Optimize categorization
github-manager ai --action optimize

# Generate report
github-manager ai --action report
```

**Output Example** (analyze):
```
📊 AI Analysis Report
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: 2024-01-15 10:30:45

📈 Issue Health Metrics:
  Total Issues: 247
  Open: 89 (36%)
  Closed: 158 (64%)
  Avg. Resolution Time: 12.5 days

🏷️ Labeling Quality:
  Well-labeled: 198 (80%)  ✅ Good
  Missing labels: 35 (14%)  ⚠️ Needs improvement
  Over-labeled: 14 (6%)     ℹ️  Minor issue

🔍 Common Patterns:
  1. 23 potential duplicates found
  2. 12 stale issues (>90 days no activity)
  3. 8 issues missing assignee

💡 Recommendations:
  1. Close or update 12 stale issues
  2. Review 23 duplicate candidates
  3. Assign owners to unassigned P0 issues
  4. Add labels to 35 unlabeled issues

📋 Top Issues by Activity:
  #123: Memory leak (45 comments, 12 participants)
  #156: API redesign (38 comments, 8 participants)
  #178: Docker support (31 comments, 6 participants)
```

## Advanced Usage

### Batch Processing

Process multiple issues efficiently:

```bash
# Summarize all issues in a milestone
github-manager list --milestone "v2.0" --format json | \
  jq -r '.[].number' | \
  xargs -I {} github-manager summarize --issue {}

# Suggest labels for all unlabeled issues
github-manager list --state open | \
  grep "No labels" | \
  awk '{print $1}' | \
  xargs -I {} github-manager suggest-labels --issue {}
```

### Integration with Workflows

Add to your CI/CD pipeline:

```yaml
# .github/workflows/issue-management.yml
name: AI Issue Management

on:
  issues:
    types: [opened]

jobs:
  ai-triage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Suggest Labels
        run: |
          github-manager suggest-labels \
            --issue ${{ github.event.issue.number }} \
            --auto-apply
```

### Custom Analysis Scripts

```python
from sage_github import IssuesManager

manager = IssuesManager()

# Summarize high-priority issues
high_priority = manager.list_issues(
    labels=["priority:high"],
    state="open"
)

for issue in high_priority:
    summary = manager.summarize_issue(issue["number"])
    print(f"Issue #{issue['number']}: {summary}")
```

## Performance & Cost

### API Usage

| Operation | API Calls | Avg. Tokens | Est. Cost (GPT-4) |
|-----------|-----------|-------------|-------------------|
| Summarize (short) | 1 | 500 | $0.01 |
| Summarize (long) | 1 | 2000 | $0.06 |
| Detect Duplicates | N×N/2 | 200×N | $0.02×N |
| Suggest Labels | 1 | 300 | $0.01 |
| Full Analysis | N×2 | 500×N | $0.03×N |

**Cost Optimization Tips**:
1. Use GPT-3.5-turbo for routine tasks (10× cheaper)
2. Cache results locally (automatically enabled)
3. Batch process during off-hours
4. Set token limits in configuration

### Configuration

Create `.github-manager/ai_config.yaml`:

```yaml
# Model selection
default_model: gpt-3.5-turbo
fallback_model: gpt-4

# Token limits
max_tokens:
  summarize: 500
  analyze: 1000
  report: 2000

# Caching
cache_enabled: true
cache_ttl: 86400  # 24 hours

# Cost control
monthly_budget: 50  # USD
warn_threshold: 0.8  # 80%
```

## Troubleshooting

### Common Issues

**1. "API key not found"**
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Set key
export OPENAI_API_KEY=sk-...

# Verify
github-manager config | grep -i "api key"
```

**2. "Rate limit exceeded"**
```bash
# Wait and retry
sleep 60
github-manager summarize --issue 123

# Or use different provider
github-manager summarize --issue 123 --model claude
```

**3. "Token limit exceeded"**
```bash
# Reduce max tokens
github-manager summarize --issue 123 --max-tokens 300

# Or split long issues
github-manager summarize --issue 123 --focus recent
```

### Debug Mode

Enable verbose logging:

```bash
export LOG_LEVEL=DEBUG
github-manager summarize --issue 123 --verbose
```

## Best Practices

### 1. Regular Maintenance

```bash
# Weekly routine
github-manager detect-duplicates --state open
github-manager ai --action analyze

# Monthly deep dive
github-manager ai --action report > monthly_report.md
```

### 2. Team Collaboration

- Share AI summaries in sprint planning
- Use duplicate detection before triage meetings
- Auto-suggest labels for new contributors

### 3. Privacy & Security

- Never share API keys in repositories
- Review AI suggestions before applying
- Be mindful of private issue content
- Consider self-hosted models for sensitive data

### 4. Quality Control

- Always review AI suggestions
- Validate duplicate detection results
- Verify label suggestions make sense
- Monitor API costs regularly

## Examples

### Daily Triage Workflow

```bash
#!/bin/bash
# daily_triage.sh

echo "🔍 Detecting duplicates..."
github-manager detect-duplicates --state open > duplicates.txt

echo "🏷️ Suggesting labels for unlabeled issues..."
github-manager list --state open | grep "No labels" | \
  awk '{print $1}' | head -10 | \
  xargs -I {} github-manager suggest-labels --issue {}

echo "📊 Generating analysis..."
github-manager ai --action analyze > analysis_$(date +%Y%m%d).md

echo "✅ Done! Check duplicates.txt and analysis file."
```

### Sprint Planning Report

```bash
#!/bin/bash
# sprint_report.sh

MILESTONE="v2.0"

echo "📋 Generating sprint report for $MILESTONE..."

# Export issues
github-manager export sprint_${MILESTONE}.csv \
  --milestone "$MILESTONE" --state open

# Summarize high-priority issues
github-manager list --milestone "$MILESTONE" \
  --label priority:high --format json | \
  jq -r '.[].number' | \
  xargs -I {} github-manager summarize --issue {} > summaries.txt

echo "✅ Report ready: sprint_${MILESTONE}.csv + summaries.txt"
```

## Further Reading

- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude Documentation](https://docs.anthropic.com/)
- [GitHub Issues Best Practices](https://docs.github.com/en/issues)
- [SAGE GitHub Manager Wiki](https://github.com/intellistream/sage-github-manager/wiki)

## Feedback

Found a bug or have a suggestion? [Open an issue](https://github.com/intellistream/sage-github-manager/issues/new)!
