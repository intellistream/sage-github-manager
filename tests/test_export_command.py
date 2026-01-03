"""Tests for export command functionality."""

import csv
import json
from pathlib import Path

import pytest

from sage_github.issue_data_manager import IssueDataManager
from sage_github.manager import IssuesManager


@pytest.fixture
def sample_issues():
    """Create sample issues for testing."""
    return [
        {
            "number": 1,
            "title": "Bug in authentication",
            "state": "open",
            "labels": [{"name": "bug"}, {"name": "priority:high"}],
            "assignees": [{"login": "user1"}],
            "milestone": {"title": "v1.0"},
            "user": {"login": "user2"},
            "created_at": "2026-01-01T10:00:00Z",
            "updated_at": "2026-01-02T10:00:00Z",
            "comments": 5,
            "body": "Issue body 1",
        },
        {
            "number": 2,
            "title": "Feature request: Add export",
            "state": "open",
            "labels": [{"name": "enhancement"}],
            "assignees": [],
            "milestone": {"title": "v2.0"},
            "user": {"login": "user3"},
            "created_at": "2026-01-02T10:00:00Z",
            "updated_at": "2026-01-02T11:00:00Z",
            "comments": 2,
            "body": "Feature body",
        },
        {
            "number": 3,
            "title": "Closed bug",
            "state": "closed",
            "labels": [{"name": "bug"}],
            "assignees": [{"login": "user1"}],
            "milestone": None,
            "user": {"login": "user1"},
            "created_at": "2025-12-01T10:00:00Z",
            "updated_at": "2025-12-05T10:00:00Z",
            "comments": 10,
            "body": "Closed issue",
        },
    ]


@pytest.fixture
def manager_with_issues(tmp_path, sample_issues):
    """Create a manager with sample issues."""
    manager = IssuesManager(project_root=tmp_path)
    data_manager = IssueDataManager(manager.workspace_dir)

    for issue in sample_issues:
        data_manager.save_issue(issue)

    return manager


class TestExportCommand:
    """Tests for export command."""

    def test_export_csv_all_issues(self, manager_with_issues, tmp_path):
        """Test exporting all issues to CSV."""
        output_file = tmp_path / "test_export.csv"
        result = manager_with_issues.export_issues(output_path=output_file, format="csv")

        assert result is True
        assert output_file.exists()

        # Read and verify CSV content
        with open(output_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 3
        # CSV headers are capitalized
        assert rows[0]["Number"] in ["1", "2", "3"]
        assert "Title" in rows[0]
        assert "State" in rows[0]

    def test_export_csv_filtered_by_state(self, manager_with_issues, tmp_path):
        """Test exporting filtered issues to CSV."""
        output_file = tmp_path / "open_issues.csv"
        result = manager_with_issues.export_issues(
            output_path=output_file, format="csv", state="open"
        )

        assert result is True
        assert output_file.exists()

        with open(output_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        for row in rows:
            assert row["State"] == "open"

    def test_export_csv_filtered_by_label(self, manager_with_issues, tmp_path):
        """Test exporting issues filtered by label to CSV."""
        output_file = tmp_path / "bug_issues.csv"
        result = manager_with_issues.export_issues(
            output_path=output_file, format="csv", labels=["bug"]
        )

        assert result is True
        with open(output_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2

    def test_export_json_all_issues(self, manager_with_issues, tmp_path):
        """Test exporting all issues to JSON."""
        output_file = tmp_path / "test_export.json"
        result = manager_with_issues.export_issues(output_path=output_file, format="json")

        assert result is True
        assert output_file.exists()

        # Read and verify JSON content
        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 3
        assert all("number" in issue for issue in data)
        assert all("title" in issue for issue in data)

    def test_export_json_filtered(self, manager_with_issues, tmp_path):
        """Test exporting filtered issues to JSON."""
        output_file = tmp_path / "closed_issues.json"
        result = manager_with_issues.export_issues(
            output_path=output_file, format="json", state="closed"
        )

        assert result is True

        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["state"] == "closed"

    def test_export_markdown_all_issues(self, manager_with_issues, tmp_path):
        """Test exporting all issues to Markdown."""
        output_file = tmp_path / "test_export.md"
        result = manager_with_issues.export_issues(output_path=output_file, format="markdown")

        assert result is True
        assert output_file.exists()

        # Read and verify Markdown content
        content = output_file.read_text(encoding="utf-8")
        assert "# Issues Report" in content or "Issue" in content
        assert "#1" in content or "Bug in authentication" in content

    def test_export_markdown_roadmap_template(self, manager_with_issues, tmp_path):
        """Test exporting issues with roadmap template."""
        output_file = tmp_path / "roadmap.md"
        result = manager_with_issues.export_issues(
            output_path=output_file, format="markdown", template="roadmap"
        )

        assert result is True
        content = output_file.read_text(encoding="utf-8")
        # Roadmap should group by milestone or state
        assert len(content) > 0

    def test_export_markdown_report_template(self, manager_with_issues, tmp_path):
        """Test exporting issues with report template."""
        output_file = tmp_path / "report.md"
        result = manager_with_issues.export_issues(
            output_path=output_file, format="markdown", template="report"
        )

        assert result is True
        content = output_file.read_text(encoding="utf-8")
        assert len(content) > 0

    def test_export_with_milestone_filter(self, manager_with_issues, tmp_path):
        """Test exporting issues filtered by milestone."""
        output_file = tmp_path / "v1_issues.csv"
        result = manager_with_issues.export_issues(
            output_path=output_file, format="csv", milestone="v1.0"
        )

        assert result is True

        with open(output_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["Number"] == "1"

    def test_export_with_assignee_filter(self, manager_with_issues, tmp_path):
        """Test exporting issues filtered by assignee."""
        output_file = tmp_path / "user1_issues.json"
        result = manager_with_issues.export_issues(
            output_path=output_file, format="json", assignee="user1"
        )

        assert result is True

        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 2

    def test_export_with_author_filter(self, manager_with_issues, tmp_path):
        """Test exporting issues filtered by author."""
        output_file = tmp_path / "author_issues.csv"
        result = manager_with_issues.export_issues(
            output_path=output_file, format="csv", author="user1"
        )

        assert result is True

        with open(output_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 1

    def test_export_combined_filters(self, manager_with_issues, tmp_path):
        """Test exporting with multiple filters."""
        output_file = tmp_path / "filtered.json"
        result = manager_with_issues.export_issues(
            output_path=output_file,
            format="json",
            state="open",
            labels=["bug"],
        )

        assert result is True

        with open(output_file, encoding="utf-8") as f:
            data = json.load(f)

        assert len(data) == 1
        assert data[0]["number"] == 1

    def test_export_empty_results(self, manager_with_issues, tmp_path):
        """Test exporting when no issues match filters."""
        output_file = tmp_path / "empty.csv"
        result = manager_with_issues.export_issues(
            output_path=output_file, format="csv", labels=["nonexistent"]
        )

        # Export with no matches returns False
        assert result is False

    def test_export_creates_parent_directories(self, manager_with_issues, tmp_path):
        """Test that export creates parent directories if needed."""
        output_file = tmp_path / "subdir" / "nested" / "export.csv"
        result = manager_with_issues.export_issues(output_path=output_file, format="csv")

        assert result is True
        assert output_file.exists()
        assert output_file.parent.exists()

    def test_export_overwrites_existing_file(self, manager_with_issues, tmp_path):
        """Test that export overwrites existing files."""
        output_file = tmp_path / "overwrite.csv"

        # Create initial file
        output_file.write_text("old content")

        # Export should overwrite
        result = manager_with_issues.export_issues(output_path=output_file, format="csv")

        assert result is True
        content = output_file.read_text()
        assert "old content" not in content
        assert "Number" in content  # CSV header (capitalized)

    def test_export_with_string_path(self, manager_with_issues, tmp_path):
        """Test export accepts string paths."""
        output_file = str(tmp_path / "string_path.csv")
        result = manager_with_issues.export_issues(output_path=output_file, format="csv")

        assert result is True
        assert Path(output_file).exists()
