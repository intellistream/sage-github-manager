"""Tests for batch command functionality."""

from unittest.mock import Mock, patch

import pytest

from sage_github.issue_data_manager import IssueDataManager
from sage_github.manager import IssuesManager


@pytest.fixture
def sample_issues():
    """Create sample issues for testing."""
    return [
        {
            "number": 1,
            "title": "Bug to fix",
            "state": "open",
            "labels": [{"name": "bug"}, {"name": "wontfix"}],
            "assignees": [],
            "milestone": None,
            "user": {"login": "user1"},
            "created_at": "2026-01-01T10:00:00Z",
            "updated_at": "2026-01-02T10:00:00Z",
            "comments": 5,
            "body": "Issue body 1",
        },
        {
            "number": 2,
            "title": "Feature request",
            "state": "open",
            "labels": [{"name": "enhancement"}, {"name": "needs-review"}],
            "assignees": [],
            "milestone": None,
            "user": {"login": "user2"},
            "created_at": "2026-01-02T10:00:00Z",
            "updated_at": "2026-01-02T11:00:00Z",
            "comments": 2,
            "body": "Feature body",
        },
        {
            "number": 3,
            "title": "Another bug",
            "state": "open",
            "labels": [{"name": "bug"}],
            "assignees": [],
            "milestone": None,
            "user": {"login": "user3"},
            "created_at": "2026-01-03T10:00:00Z",
            "updated_at": "2026-01-03T11:00:00Z",
            "comments": 0,
            "body": "Bug body",
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


class TestBatchCloseCommand:
    """Tests for batch-close command."""

    @patch("sage_github.helpers.batch_operations.BatchOperations.close_issues")
    def test_batch_close_by_label(self, mock_close, manager_with_issues):
        """Test batch closing issues by label."""
        mock_close.return_value = {"closed": 1, "failed": 0, "issues": [1]}

        result = manager_with_issues.batch_close(labels=["wontfix"])

        assert result is not None
        assert isinstance(result, dict)
        mock_close.assert_called_once()

    @patch("sage_github.helpers.batch_operations.BatchOperations.close_issues")
    def test_batch_close_dry_run(self, mock_close, manager_with_issues):
        """Test batch close in dry-run mode."""
        mock_close.return_value = {"matched": 1, "dry_run": True}

        result = manager_with_issues.batch_close(labels=["wontfix"], dry_run=True)

        assert isinstance(result, dict)
        mock_close.assert_called_once()

    @patch("sage_github.helpers.batch_operations.BatchOperations.close_issues")
    def test_batch_close_with_filters(self, mock_close, manager_with_issues):
        """Test batch close with multiple filters."""
        mock_close.return_value = {"closed": 1, "failed": 0}

        result = manager_with_issues.batch_close(state="open", labels=["bug"], auto_confirm=True)

        assert result is not None
        mock_close.assert_called_once()


class TestBatchLabelCommand:
    """Tests for batch-label command."""

    @patch("sage_github.helpers.batch_operations.BatchOperations.add_labels")
    def test_batch_add_label(self, mock_add, manager_with_issues):
        """Test adding labels to issues in batch."""
        mock_add.return_value = {"updated": 2, "failed": 0}

        result = manager_with_issues.batch_add_labels(add_labels=["priority:high"], labels=["bug"])

        assert result is not None
        assert isinstance(result, dict)
        mock_add.assert_called_once()

    @patch("sage_github.helpers.batch_operations.BatchOperations.remove_labels")
    def test_batch_remove_label(self, mock_remove, manager_with_issues):
        """Test removing labels from issues in batch."""
        mock_remove.return_value = {"updated": 1, "failed": 0}

        result = manager_with_issues.batch_remove_labels(remove_labels=["wontfix"], labels=["bug"])

        assert result is not None
        assert isinstance(result, dict)
        mock_remove.assert_called_once()

    @patch("sage_github.helpers.batch_operations.BatchOperations.add_labels")
    def test_batch_add_label_dry_run(self, mock_add, manager_with_issues):
        """Test batch label in dry-run mode."""
        mock_add.return_value = {"matched": 2, "dry_run": True}

        result = manager_with_issues.batch_add_labels(
            add_labels=["test"], labels=["bug"], dry_run=True
        )

        assert isinstance(result, dict)
        mock_add.assert_called_once()


class TestBatchAssignCommand:
    """Tests for batch-assign command."""

    @patch("sage_github.helpers.batch_operations.BatchOperations.assign_issues")
    def test_batch_assign_by_label(self, mock_assign, manager_with_issues):
        """Test batch assigning issues by label."""
        mock_assign.return_value = {"assigned": 2, "failed": 0}

        result = manager_with_issues.batch_assign(assignees=["testuser"], labels=["bug"])

        assert result is not None
        assert isinstance(result, dict)
        mock_assign.assert_called_once()

    @patch("sage_github.helpers.batch_operations.BatchOperations.assign_issues")
    def test_batch_assign_multiple_users(self, mock_assign, manager_with_issues):
        """Test assigning issues to multiple users."""
        mock_assign.return_value = {"assigned": 3, "failed": 0}

        result = manager_with_issues.batch_assign(assignees=["user1", "user2"], state="open")

        assert result is not None
        mock_assign.assert_called_once()

    @patch("sage_github.helpers.batch_operations.BatchOperations.assign_issues")
    def test_batch_assign_dry_run(self, mock_assign, manager_with_issues):
        """Test batch assign in dry-run mode."""
        mock_assign.return_value = {"matched": 2, "dry_run": True}

        result = manager_with_issues.batch_assign(
            assignees=["testuser"], labels=["bug"], dry_run=True
        )

        assert isinstance(result, dict)
        mock_assign.assert_called_once()


class TestBatchMilestoneCommand:
    """Tests for batch-milestone command."""

    @patch("sage_github.helpers.batch_operations.BatchOperations.set_milestone")
    def test_batch_set_milestone(self, mock_milestone, manager_with_issues):
        """Test batch setting milestone."""
        mock_milestone.return_value = {"updated": 2, "failed": 0}

        result = manager_with_issues.batch_set_milestone(milestone="v1.0", labels=["bug"])

        assert result is not None
        assert isinstance(result, dict)
        mock_milestone.assert_called_once()

    @patch("sage_github.helpers.batch_operations.BatchOperations.set_milestone")
    def test_batch_set_milestone_all_open(self, mock_milestone, manager_with_issues):
        """Test setting milestone for all open issues."""
        mock_milestone.return_value = {"updated": 3, "failed": 0}

        result = manager_with_issues.batch_set_milestone(milestone="v2.0", state="open")

        assert result is not None
        mock_milestone.assert_called_once()

    @patch("sage_github.helpers.batch_operations.BatchOperations.set_milestone")
    def test_batch_set_milestone_dry_run(self, mock_milestone, manager_with_issues):
        """Test batch milestone in dry-run mode."""
        mock_milestone.return_value = {"matched": 2, "dry_run": True}

        result = manager_with_issues.batch_set_milestone(
            milestone="v1.0", labels=["bug"], dry_run=True
        )

        assert isinstance(result, dict)
        mock_milestone.assert_called_once()


class TestBatchFiltering:
    """Tests for batch command filtering."""

    @patch("sage_github.helpers.batch_operations.BatchOperations.close_issues")
    def test_batch_filter_by_state(self, mock_close, manager_with_issues):
        """Test filtering by state in batch operations."""
        mock_close.return_value = {"closed": 3, "failed": 0}

        result = manager_with_issues.batch_close(state="open", auto_confirm=True)

        assert result is not None
        mock_close.assert_called_once()
        # Verify issues were filtered before being passed
        call_args = mock_close.call_args
        issues_arg = call_args[0][0]  # First positional argument
        assert len(issues_arg) == 3  # All 3 test issues are open

    @patch("sage_github.helpers.batch_operations.BatchOperations.assign_issues")
    def test_batch_combined_filters(self, mock_assign, manager_with_issues):
        """Test using multiple filters in batch operations."""
        mock_assign.return_value = {"assigned": 2, "failed": 0}

        result = manager_with_issues.batch_assign(
            assignees=["testuser"], labels=["bug"], state="open"
        )

        assert result is not None
        mock_assign.assert_called_once()
        # Verify filtering worked
        call_args = mock_assign.call_args
        issues_arg = call_args[0][0]
        assert len(issues_arg) == 2  # 2 bugs


class TestBatchWithNoMatches:
    """Tests for batch commands with no matching issues."""

    @patch("sage_github.helpers.batch_operations.BatchOperations.close_issues")
    def test_batch_with_no_matching_issues(self, mock_close, manager_with_issues):
        """Test batch operations with no matching issues."""
        mock_close.return_value = {"closed": 0, "failed": 0, "matched": 0}

        # Filter that matches no issues
        result = manager_with_issues.batch_close(labels=["nonexistent"], auto_confirm=True)

        assert result is not None
        mock_close.assert_called_once()
        # Should be called with empty list
        call_args = mock_close.call_args
        issues_arg = call_args[0][0]
        assert len(issues_arg) == 0
