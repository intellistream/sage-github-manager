"""Tests for configuration module"""

import os
from pathlib import Path

import pytest
from sage_github.config import IssuesConfig


def test_default_config():
    """Test default configuration"""
    config = IssuesConfig()
    assert isinstance(config.project_root, Path)
    assert isinstance(config.workspace_path, Path)
    assert isinstance(config.output_path, Path)
    assert isinstance(config.metadata_path, Path)


def test_custom_project_root():
    """Test custom project root"""
    custom_root = Path("/tmp/test-github-manager")
    custom_root.mkdir(parents=True, exist_ok=True)

    config = IssuesConfig(project_root=custom_root)
    assert config.project_root == custom_root
    assert str(custom_root) in str(config.workspace_path)


def test_environment_variable_override():
    """Test environment variable override"""
    os.environ["GITHUB_OWNER"] = "test-owner"
    os.environ["GITHUB_REPO"] = "test-repo"

    config = IssuesConfig()
    assert config.GITHUB_OWNER == "test-owner"
    assert config.GITHUB_REPO == "test-repo"

    # Cleanup
    del os.environ["GITHUB_OWNER"]
    del os.environ["GITHUB_REPO"]


def test_parameter_override():
    """Test parameter override"""
    config = IssuesConfig(github_owner="param-owner", github_repo="param-repo")
    assert config.GITHUB_OWNER == "param-owner"
    assert config.GITHUB_REPO == "param-repo"


def test_github_token_loading():
    """Test GitHub token loading"""
    # This will be None unless actually configured
    config = IssuesConfig()
    # Token might be None, which is fine for testing
    assert config.github_token is None or isinstance(config.github_token, str)


def test_metadata_files_creation():
    """Test that metadata files are created"""
    config = IssuesConfig()

    expected_files = [
        "ai_analysis_summary.json",
        "update_history.json",
        "assignments.json",
        "settings.json",
    ]

    for filename in expected_files:
        filepath = config.metadata_path / filename
        assert filepath.exists(), f"Expected {filename} to exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
