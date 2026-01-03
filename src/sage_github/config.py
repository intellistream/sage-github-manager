#!/usr/bin/env python3
"""
GitHub Issues管理工具 - 配置管理
统一的配置管理和GitHub API客户端
"""

import json
import os
from pathlib import Path

import requests


class IssuesConfig:
    """Issues管理配置类"""

    # GitHub仓库配置 - 可以通过环境变量覆盖
    GITHUB_OWNER = os.getenv("GITHUB_OWNER", "intellistream")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "SAGE")

    # 专业领域匹配规则 - 可自定义
    EXPERTISE_RULES = {}

    def __init__(self, project_root: Path | None = None, github_owner: str | None = None, github_repo: str | None = None):
        # 如果提供了owner和repo参数，使用它们
        if github_owner:
            self.GITHUB_OWNER = github_owner
        if github_repo:
            self.GITHUB_REPO = github_repo

        # 如果没有提供project_root，尝试找到项目根目录
        if project_root is None:
            self.project_root = self._find_project_root()
        else:
            self.project_root = Path(project_root)

        # 工作目录配置 - 使用.github-manager目录
        self.base_dir = self.project_root / ".github-manager"
        self.workspace_path = self.base_dir / "workspace"
        self.output_path = self.base_dir / "output"
        self.metadata_path = self.base_dir / "metadata"

        # 确保目录存在
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.output_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)

        # 默认值
        self.github_token_env: str | None = None

        # 加载用户设置
        self._load_user_settings()

        # 确保默认metadata文件存在
        self._ensure_default_metadata_files()

        # GitHub Token
        self.github_token = self._load_github_token()

        # 仓库名称（兼容性属性）
        self.repository_name = self.GITHUB_REPO

    def _find_project_root(self) -> Path:
        """找到项目根目录"""
        current = Path.cwd()

        # 从当前目录向上查找，直到找到包含特定标记文件的目录
        while current.parent != current:
            # 优先检查.git目录（开发环境的项目根目录标记）
            if (current / ".git").exists():
                return current
            current = current.parent

        # 最后回退到当前工作目录
        return Path.cwd()

    def _load_user_settings(self):
        """加载用户设置"""
        settings_file = self.metadata_path / "settings.json"
        default_settings = {
            "sync_update_history": True,  # 默认同步更新记录到GitHub
            "auto_backup": True,
            "verbose_output": False,
        }

        if settings_file.exists():
            try:
                with open(settings_file, encoding="utf-8") as f:
                    user_settings = json.load(f)
                # 合并默认设置和用户设置
                default_settings.update(user_settings)
            except Exception as e:
                print(f"⚠️ 加载用户设置失败，使用默认设置: {e}")

        # 设置属性
        for key, value in default_settings.items():
            setattr(self, key, value)

    def _ensure_default_metadata_files(self):
        """确保默认的metadata文件存在"""

        # ai_analysis_summary.json
        ai_analysis_file = self.metadata_path / "ai_analysis_summary.json"
        if not ai_analysis_file.exists():
            default_ai_analysis = {
                "last_update": None,
                "ai_summaries": {},
                "auto_labeled_issues": [],
                "priority_assessments": {},
                "duplicate_analyses": {},
            }
            with open(ai_analysis_file, "w", encoding="utf-8") as f:
                json.dump(default_ai_analysis, f, indent=2, ensure_ascii=False)

        # update_history.json
        update_history_file = self.metadata_path / "update_history.json"
        if not update_history_file.exists():
            default_history = {"updates": [], "last_sync": None}
            with open(update_history_file, "w", encoding="utf-8") as f:
                json.dump(default_history, f, indent=2, ensure_ascii=False)

        # assignments.json
        assignments_file = self.metadata_path / "assignments.json"
        if not assignments_file.exists():
            default_assignments = {
                "auto_assignments": {},
                "manual_assignments": {},
                "assignment_rules": {},
            }
            with open(assignments_file, "w", encoding="utf-8") as f:
                json.dump(default_assignments, f, indent=2, ensure_ascii=False)

    def _load_github_token(self) -> str | None:
        """加载GitHub Token"""

        # 1. 从环境变量加载
        for env_name in ("GITHUB_TOKEN", "GH_TOKEN", "GIT_TOKEN"):
            token = os.getenv(env_name)
            if token:
                self.github_token_env = env_name
                return token

        # 2. 从配置文件加载 (项目根目录)
        token_file = self.project_root / ".github_token"
        if token_file.exists():
            try:
                with open(token_file) as f:
                    return f.read().strip()
            except Exception:
                pass

        # 3. 从用户主目录加载
        home_token_file = Path.home() / ".github_token"
        if home_token_file.exists():
            try:
                with open(home_token_file) as f:
                    return f.read().strip()
            except Exception:
                pass

        return None

    def get_github_client(self):
        """获取GitHub API客户端"""
        if not self.github_token:
            raise ValueError(
                "GitHub Token未配置，请设置 GITHUB_TOKEN / GH_TOKEN / GIT_TOKEN 环境变量，或创建 .github_token 文件"
            )

        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        return headers

    def test_github_connection(self) -> bool:
        """测试GitHub连接"""
        if not self.github_token:
            return False

        try:
            headers = self.get_github_client()
            response = requests.get(
                f"https://api.github.com/repos/{self.GITHUB_OWNER}/{self.GITHUB_REPO}",
                headers=headers,
                timeout=10,
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_repo_info(self) -> dict:
        """获取仓库信息"""
        headers = self.get_github_client()
        response = requests.get(
            f"https://api.github.com/repos/{self.GITHUB_OWNER}/{self.GITHUB_REPO}",
            headers=headers,
        )
        response.raise_for_status()
        return response.json()


# 兼容性别名
Config = IssuesConfig
