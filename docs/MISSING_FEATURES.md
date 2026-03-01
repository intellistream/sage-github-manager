# Missing Features - Implementation TODO

This document tracks the features described in Copilot Instructions but not yet implemented in the codebase.

**Status**: 🔴 Not Started | 🟡 In Progress | 🟢 Completed

---

## 🔴 High Priority Features

### 1. `list` Command - Issue Listing and Filtering

**Description**: Flexible issue listing with multiple filter options for daily workflow.

**Expected Usage**:
```bash
github-manager list --state open
github-manager list --state open --label bug
github-manager list --assignee shuhao
github-manager list --milestone "v2.0" --state open
github-manager list --sort created --limit 20
github-manager list --label "priority:high" --assignee shuhao
```

**Implementation Requirements**:
- Filter by state (open/closed/all)
- Filter by label(s) - support multiple labels
- Filter by assignee
- Filter by milestone
- Sort options (created, updated, comments)
- Limit results
- Rich table output with color coding

**Files to Create/Modify**:
- `src/sage_github/cli.py` - Add `list` command
- `src/sage_github/helpers/filter_issues.py` - Create filter helper
- `src/sage_github/manager.py` - Add `list_issues()` method

**Status**: 🟢 Completed

**Implementation Date**: 2026-01-03

**Notes**: Fully implemented with filtering (state, labels, assignee, milestone, author), sorting, and Rich table output.

---

### 2. `export` Command - Data Export

**Description**: Export issues to various formats for reporting and analysis.

**Expected Usage**:
```bash
github-manager export --format csv --output sage_issues.csv
github-manager export --format markdown --output ROADMAP.md
github-manager export --format json --output issues.json
github-manager export --filter milestone=v2.0 --format csv
github-manager export --state open --label bug --format markdown
```

**Implementation Requirements**:
- CSV export with all issue fields
- Markdown export (suitable for documentation/roadmaps)
- JSON export (structured data)
- Support filtering before export
- Custom output path
- Template support for Markdown

**Files to Create/Modify**:
- `src/sage_github/cli.py` - Add `export` command
- `src/sage_github/helpers/export_issues.py` - Create export helper
- `src/sage_github/manager.py` - Add `export_issues()` method

**Status**: 🟢 Completed

**Implementation Date**: 2026-01-03

**Notes**: 
- Supports CSV, JSON, and Markdown formats
- Three Markdown templates: default (detailed list), roadmap (milestone-grouped), report (concise)
- Full filtering support (state, labels, assignee, milestone, author)
- Auto-adds file extension based on format
- Shows file size and location after export

---

### 3. `batch` Commands - Batch Operations

**Description**: Efficiently manage multiple issues at once.

**Expected Usage**:
```bash
# Close issues
github-manager batch-close --label "wontfix"
github-manager batch-close --state open --milestone "old-sprint"

# Add/remove labels
github-manager batch-label --add "priority:high" --label bug
github-manager batch-label --remove "needs-review" --state closed

# Assign issues
github-manager batch-assign -a shuhao --label "p0"
github-manager batch-assign -a shuhao --milestone "v2.0"

# Update milestone
github-manager batch-milestone "v3.0" --label "feature"
```

**Implementation Requirements**:
- Batch close issues (with confirmation)
- Batch add/remove labels
- Batch assign to users
- Batch milestone updates
- Dry-run mode (preview)
- Filter support (reuse list filters)
- Progress bar for large batches
- Confirmation prompts

**Files to Create/Modify**:
- `src/sage_github/cli.py` - Add `batch` command group
- `src/sage_github/helpers/batch_operations.py` - Create batch operations helper
- `src/sage_github/manager.py` - Add batch methods

**Status**: 🟢 Completed

**Implementation Date**: 2026-01-03

**Notes**:
- Four batch commands: batch-close, batch-label, batch-assign, batch-milestone
- All commands support dry-run mode (--dry-run) for previewing changes
- Confirmation prompts before executing (can skip with --yes)
- Rich preview table showing affected issues (first 20)
- Progress bars for operations
- Full filtering support (state, labels, assignee, milestone, author)
- Direct GitHub REST API integration
- Tested with 128 SAGE open issues

---

## 🟡 Medium Priority Features

### 4. AI Command Enhancements

**Description**: Specific AI commands instead of generic `--action` parameter.

**Current Implementation**:
```bash
github-manager ai --action analyze
github-manager ai --action dedupe
github-manager ai --action optimize
```

**Desired Implementation**:
```bash
github-manager summarize --issue 123
github-manager detect-duplicates
github-manager suggest-labels --issue 456
github-manager ai-analyze  # Keep general analysis
```

**Implementation Requirements**:
- Separate commands for clarity
- Issue-specific operations (summarize, suggest-labels)
- Workspace-level operations (detect-duplicates)
- Better output formatting
- Save results to metadata

**Files to Modify**:
- `src/sage_github/cli.py` - Add dedicated commands
- `src/sage_github/helpers/ai_analyzer.py` - Refactor for specific operations

**Status**: 🟢 Completed

**Implementation Date**: 2026-01-03

**Notes**:
- Three dedicated AI commands:
  - `summarize`: Generate AI summaries for specific issues (requires OpenAI/Claude API)
  - `detect-duplicates`: Find duplicate issues using text similarity (no API needed)
  - `suggest-labels`: Recommend labels based on keywords (no API needed)
- Silent mode for non-API operations
- Rich table output for duplicates
- Smart keyword matching for label suggestions
- Tested with 1304 SAGE issues: 592 duplicate pairs detected at 0.8 threshold

---

### 5. Command Naming Consistency

**Description**: Align command names with documentation.

**Issues**:
- Instructions say: `github-manager analytics`
- Code implements: `github-manager stats`

**Recommendation**: Either rename `stats` to `analytics` OR update documentation.

**Status**: 🟢 Completed

**Implementation Date**: 2026-01-03

**Solution**: Renamed `stats` to `analytics`
- Primary command: `github-manager analytics`
- Backward compatibility: `stats` still works but shows deprecation warning
- Updated all documentation (README, FAQ, QUICK_START, PROJECT_SUMMARY)
- Added comprehensive docstring with examples
- Command now hidden in help to encourage migration

---

## 🟢 Low Priority / Nice to Have

### 6. Advanced Filtering

**Description**: More sophisticated filtering options.

**Potential Features**:
- Filter by date ranges (`--created-after`, `--closed-before`)
- Filter by comment count (`--min-comments 5`)
- Filter by reaction count (popularity)
- Combined filters with AND/OR logic
- Saved filter presets

**Status**: 🔴 Not Started

---

### 7. Interactive Mode

**Description**: TUI (Text User Interface) for issue management.

**Potential Features**:
- Browse issues interactively
- Quick actions (close, label, assign)
- Real-time search/filter
- Keyboard shortcuts

**Status**: 🔴 Not Started

---

### 8. Webhook/Event Integration

**Description**: Real-time sync with GitHub webhooks.

**Potential Features**:
- Listen for GitHub events
- Auto-update local database
- Notification system

**Status**: 🔴 Not Started

---

## Implementation Plan

### Phase 1: Core Missing Features (Week 1-2)
1. ✅ Create this tracking document
2. 🔴 Implement `list` command with filters
3. 🔴 Implement `export` command (CSV, Markdown, JSON)
4. 🔴 Implement basic `batch` operations (close, label, assign)

### Phase 2: Enhancements (Week 3-4)
5. 🔴 Refactor AI commands for better UX
6. 🔴 Fix command naming consistency
7. 🔴 Add comprehensive tests for new features
8. 🔴 Update documentation

### Phase 3: Advanced Features (Future)
9. 🔴 Advanced filtering options
10. 🔴 Interactive mode (if needed)
11. 🔴 Real-time sync (if needed)

---

## Testing Requirements

Each new feature must include:
- ✅ Unit tests (`tests/test_<feature>.py`)
- ✅ Integration tests with mock GitHub API
- ✅ Documentation in README.md
- ✅ Usage examples in `examples/`
- ✅ Type hints and docstrings

---

## Notes

- All features should follow the **NO FALLBACK LOGIC** principle
- Use **Rich** library for beautiful terminal output
- Ensure **type hints** for all new functions
- Add to **pyproject.toml** if new dependencies needed
- Update **.github/copilot-instructions.md** after implementation

---

**Last Updated**: 2026-01-03
**Next Review**: After Phase 1 completion
