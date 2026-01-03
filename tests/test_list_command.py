"""Tests for list command functionality."""

import json
from pathlib import Path
from unittest.mock import patch

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
            "body": "Issue body",
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
    # Create manager with temporary workspace
    manager = IssuesManager(project_root=tmp_path)

    # Create data manager and save test issues
    data_manager = IssueDataManager(manager.workspace_dir)

    # Save each issue
    for issue in sample_issues:
        data_manager.save_issue(issue)

    return manager


class TestListCommand:
    """Tests for list command."""

    def test_list_all_issues(self, manager_with_issues):
        """Test listing all issues."""
        issues = manager_with_issues.list_issues()
        assert len(issues) == 3
        # Check that all issues are present (order may vary)
        issue_numbers = {issue["number"] for issue in issues}
        assert issue_numbers == {1, 2, 3}

    def test_filter_by_state_open(self, manager_with_issues):
        """Test filtering by open state."""
        issues = manager_with_issues.list_issues(state="open")
        assert len(issues) == 2
        assert all(issue["state"] == "open" for issue in issues)

    def test_filter_by_state_closed(self, manager_with_issues):
        """Test filtering by closed state."""
        issues = manager_with_issues.list_issues(state="closed")
        assert len(issues) == 1
        assert issues[0]["state"] == "closed"
        assert issues[0]["number"] == 3

    def test_filter_by_single_label(self, manager_with_issues):
        """Test filtering by a single label."""
        issues = manager_with_issues.list_issues(labels=["bug"])
        assert len(issues) == 2
        for issue in issues:
            label_names = [label["name"] for label in issue["labels"]]
            assert "bug" in label_names

    def test_filter_by_multiple_labels(self, manager_with_issues):
        """Test filtering by multiple labels."""
        issues = manager_with_issues.list_issues(labels=["bug", "priority:high"])
        assert len(issues) == 1
        assert issues[0]["number"] == 1

    def test_filter_by_assignee(self, manager_with_issues):
        """Test filtering by assignee."""
        issues = manager_with_issues.list_issues(assignee="user1")
        assert len(issues) == 2
        for issue in issues:
            assignee_logins = [a["login"] for a in issue["assignees"]]
            assert "user1" in assignee_logins

    def test_filter_by_milestone(self, manager_with_issues):
        """Test filtering by milestone."""
        issues = manager_with_issues.list_issues(milestone="v1.0")
        assert len(issues) == 1
        assert issues[0]["number"] == 1
        assert issues[0]["milestone"]["title"] == "v1.0"

    def test_filter_by_author(self, manager_with_issues):
        """Test filtering by author."""
        issues = manager_with_issues.list_issues(author="user1")
        assert len(issues) == 1
        assert issues[0]["number"] == 3
        assert issues[0]["user"]["login"] == "user1"

    def test_combined_filters(self, manager_with_issues):
        """Test combining multiple filters."""
        issues = manager_with_issues.list_issues(state="open", labels=["bug"], assignee="user1")
        assert len(issues) == 1
        assert issues[0]["number"] == 1

    def test_sort_by_created(self, manager_with_issues):
        """Test sorting by created date."""
        issues = manager_with_issues.list_issues(sort_by="created")
        # With reverse=True (default), should be newest first
        # Check that sorting works by comparing dates
        dates = [issue["created_at"] for issue in issues]
        assert dates == sorted(dates, reverse=True)

    def test_sort_by_updated(self, manager_with_issues):
        """Test sorting by updated date."""
        issues = manager_with_issues.list_issues(sort_by="updated")
        # Check that sorting works by comparing dates
        dates = [issue["updated_at"] for issue in issues]
        assert dates == sorted(dates, reverse=True)

    def test_sort_by_comments(self, manager_with_issues):
        """Test sorting by comment count."""
        issues = manager_with_issues.list_issues(sort_by="comments")
        assert issues[0]["number"] == 3  # 10 comments
        assert issues[2]["number"] == 2  # 2 comments

    def test_limit_results(self, manager_with_issues):
        """Test limiting number of results."""
        issues = manager_with_issues.list_issues(limit=2)
        assert len(issues) == 2

    def test_no_results(self, manager_with_issues):
        """Test when no issues match filters."""
        issues = manager_with_issues.list_issues(labels=["nonexistent"])
        assert len(issues) == 0

    def test_empty_issues_file(self, tmp_path):
        """Test listing when no issues exist."""
        manager = IssuesManager(project_root=tmp_path)
        issues = manager.list_issues()
        assert len(issues) == 0
