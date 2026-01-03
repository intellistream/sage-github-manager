"""Basic tests for GitHub Issues Manager"""

import pytest
from sage_github import IssuesConfig, IssuesManager


def test_config_initialization():
    """Test config can be initialized"""
    config = IssuesConfig()
    assert config.GITHUB_OWNER is not None
    assert config.GITHUB_REPO is not None
    assert config.project_root is not None


def test_config_custom_repo():
    """Test custom repository configuration"""
    config = IssuesConfig(github_owner="test-org", github_repo="test-repo")
    assert config.GITHUB_OWNER == "test-org"
    assert config.GITHUB_REPO == "test-repo"


def test_manager_initialization():
    """Test manager can be initialized"""
    manager = IssuesManager()
    assert manager.config is not None
    assert manager.workspace_dir is not None
    assert manager.output_dir is not None


def test_directory_creation():
    """Test that required directories are created"""
    config = IssuesConfig()
    assert config.workspace_path.exists()
    assert config.output_path.exists()
    assert config.metadata_path.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
