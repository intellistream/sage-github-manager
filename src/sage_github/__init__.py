"""
GitHub Issues Management Tool

A comprehensive tool for downloading, analyzing, and managing GitHub Issues
with AI-powered features.

Features:
- Download and sync Issues from GitHub
- AI-powered analysis and organization
- Statistics and reporting
- Team collaboration management
- Project management and auto-assignment

Usage:
    from sage_github import IssuesManager

    manager = IssuesManager()
    manager.show_statistics()
"""

__version__ = "0.1.0"
__author__ = "IntelliStream Team"
__email__ = "shuhao_zhang@hust.edu.cn"

from .config import IssuesConfig
from .manager import IssuesManager

# 如果在CLI环境中，也导出CLI应用
try:
    from .cli import app as cli_app  # noqa: F401

    __all__ = ["IssuesManager", "IssuesConfig", "cli_app"]
except ImportError:
    __all__ = ["IssuesManager", "IssuesConfig"]
