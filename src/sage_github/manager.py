#!/usr/bin/env python3
"""
SAGE Issues管理工具 - 核心管理器 (适配sage-tools版本)
Lightweight manager that uses the centralized config
and calls helper scripts from helpers/ when available.
"""

from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any

from .config import IssuesConfig


class IssuesManager:
    """Issues管理器 - 适配sage-tools版本"""

    def __init__(self, project_root: Path | None = None):
        self.config = IssuesConfig(project_root)
        self.workspace_dir = self.config.workspace_path
        self.output_dir = self.config.output_path
        self.metadata_dir = self.config.metadata_path
        self.scripts_dir = Path(__file__).parent
        self.helpers_dir = self.scripts_dir / "helpers"
        self.ensure_output_dir()
        self.team_info = self._load_team_info()

    def ensure_output_dir(self):
        """确保输出目录存在"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_team_info(self):
        """Try to import generated `team_config.py` from the meta-data directory."""
        # 使用新的meta-data目录位置
        meta_data_dir = self.metadata_dir
        team_config_path = meta_data_dir / "team_config.py"

        if team_config_path.exists():
            try:
                # 清理可能存在的模块缓存
                if "team_config" in sys.modules:
                    del sys.modules["team_config"]

                sys.path.insert(0, str(meta_data_dir))
                import team_config

                TEAMS = getattr(team_config, "TEAMS", None)
                if TEAMS is not None:
                    # 处理两种格式的团队配置
                    all_usernames = []
                    processed_teams = {}

                    for team_name, team_data in TEAMS.items():
                        if isinstance(team_data, dict) and "members" in team_data:
                            # 新格式：包含详细成员信息
                            members = []
                            for member in team_data["members"]:
                                if isinstance(member, dict) and "username" in member:
                                    username = member["username"]
                                    members.append(username)
                                    all_usernames.append(username)
                                elif isinstance(member, str):
                                    members.append(member)
                                    all_usernames.append(member)
                            processed_teams[team_name] = members
                        elif isinstance(team_data, dict):
                            # 旧格式：简单的用户名映射
                            members = list(team_data.keys())
                            processed_teams[team_name] = members
                            all_usernames.extend(members)
                        elif isinstance(team_data, list):
                            # 列表格式
                            processed_teams[team_name] = team_data
                            all_usernames.extend(team_data)

                    print(f"✅ 已加载团队信息: {len(all_usernames)} 位成员")

                    # 如果没有成员，视为无效的团队信息
                    if len(all_usernames) == 0:
                        print("⚠️ 团队信息存在但没有成员，将尝试更新")
                        return None

                    return {"teams": processed_teams, "all_usernames": all_usernames}
            except Exception as e:
                print(f"⚠️ 加载团队信息失败: {e}")
            finally:
                # 清理sys.path
                if str(meta_data_dir) in sys.path:
                    sys.path.remove(str(meta_data_dir))

        print("⚠️ 团队信息未找到")
        print("💡 运行以下命令获取团队信息:")
        print("   sage-dev issues team --update")
        return None

    def load_issues(self) -> list[dict[str, Any]]:
        """Load issues from workspace data directory."""
        data_dir = self.workspace_dir / "data"
        if not data_dir.exists():
            print(f"❌ Issues数据目录不存在: {data_dir}")
            print("💡 请先运行下载Issues命令:")
            print("   sage-dev issues download")
            return []

        issues = []

        # 加载单个issue JSON文件
        for issue_file in data_dir.glob("issue_*.json"):
            try:
                with open(issue_file, encoding="utf-8") as f:
                    issue_data = json.load(f)

                # 适配从JSON格式到统计需要的格式
                if "metadata" in issue_data:
                    # 使用新格式的JSON数据
                    metadata = issue_data["metadata"]
                    adapted_issue = {
                        "number": metadata.get("number"),
                        "title": metadata.get("title", ""),
                        "body": issue_data.get("body", ""),
                        "state": metadata.get("state", "open"),
                        "user": {"login": metadata.get("user", "unknown")},
                        "labels": [{"name": label} for label in metadata.get("labels", [])],
                        "assignees": [
                            {"login": assignee} for assignee in metadata.get("assignees", [])
                        ],
                        "milestone": metadata.get("milestone"),
                        "created_at": metadata.get("created_at"),
                        "updated_at": metadata.get("updated_at"),
                        "closed_at": metadata.get("closed_at"),
                        "comments": metadata.get("comments_count", 0),
                    }
                else:
                    # 兼容旧格式的JSON数据
                    adapted_issue = issue_data

                issues.append(adapted_issue)

            except Exception as e:
                print(f"⚠️ 读取issue文件失败: {issue_file.name}: {e}")

        # 如果单个文件没找到，尝试加载批量文件
        if not issues:
            latest_file = data_dir / "issues_open_latest.json"
            if latest_file.exists():
                try:
                    with open(latest_file, encoding="utf-8") as f:
                        batch_issues = json.load(f)

                    # 批量文件应该是标准GitHub API格式
                    for issue in batch_issues:
                        issues.append(issue)

                except Exception as e:
                    print(f"⚠️ 读取批量Issues文件失败: {e}")

        print(f"✅ 加载了 {len(issues)} 个Issues")
        return issues

    def _parse_markdown_issue(self, content: str, filename: str) -> dict[str, Any]:
        """Parse markdown format issue file"""
        lines = content.split("\n")

        # Initialize issue data
        issue_data: dict[str, Any] = {
            "title": "",
            "body": content,
            "state": "open",  # default
            "user": {"login": "unknown"},
            "labels": [],
            "assignees": [],
        }

        # Extract title from first line (usually starts with #)
        if lines and lines[0].startswith("#"):
            issue_data["title"] = lines[0].strip("#").strip()

        # Extract state from filename
        if filename.startswith("open_"):
            issue_data["state"] = "open"
        elif filename.startswith("closed_"):
            issue_data["state"] = "closed"

        # Parse markdown content for metadata
        for i, line in enumerate(lines):
            line = line.strip()

            # Extract creator/author
            if (
                line.startswith("**创建者**:")
                or line.startswith("**作者**:")
                or line.startswith("**Creator**:")
            ):
                author = line.split(":", 1)[1].strip()
                issue_data["user"] = {"login": author}

            # Extract state from content
            elif line.startswith("**状态**:") or line.startswith("**State**:"):
                state = line.split(":", 1)[1].strip()
                issue_data["state"] = state

            # Extract labels (looking for label section)
            elif line == "## 标签" or line == "## Labels":
                # Check next few lines for labels
                j = i + 1
                while j < len(lines) and j < i + 5:  # Look ahead max 5 lines
                    next_line = lines[j].strip()
                    if (
                        next_line
                        and not next_line.startswith("#")
                        and not next_line.startswith("**")
                    ):
                        # Found label content
                        if next_line != "无" and next_line != "None" and next_line:
                            # Split by comma and clean up
                            labels = [
                                label.strip() for label in next_line.split(",") if label.strip()
                            ]
                            issue_data["labels"] = [{"name": label} for label in labels]
                        break
                    j += 1

            # Extract assignees
            elif line == "## 分配给" or line == "## Assigned to":
                j = i + 1
                while j < len(lines) and j < i + 5:
                    next_line = lines[j].strip()
                    if (
                        next_line
                        and not next_line.startswith("#")
                        and not next_line.startswith("**")
                    ):
                        if next_line != "未分配" and next_line != "Unassigned" and next_line:
                            assignees = [
                                assignee.strip()
                                for assignee in next_line.split(",")
                                if assignee.strip()
                            ]
                            issue_data["assignees"] = [
                                {"login": assignee} for assignee in assignees
                            ]
                        break
                    j += 1

        return issue_data

    def _generate_statistics(self, issues: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate statistics from issues data."""
        stats: dict[str, Any] = {
            "total": len(issues),
            "open": 0,
            "closed": 0,
            "labels": {},
            "assignees": {},
            "authors": {},
        }

        for issue in issues:
            # Count by state
            state = issue.get("state", "open")
            if state == "open":
                stats["open"] += 1
            else:
                stats["closed"] += 1

            # Count labels
            labels = issue.get("labels", [])
            if isinstance(labels, list):
                for label in labels:
                    label_name = label if isinstance(label, str) else label.get("name", "unknown")
                    stats["labels"][label_name] = stats["labels"].get(label_name, 0) + 1

            # Count assignees
            assignees = issue.get("assignees", [])
            if isinstance(assignees, list):
                for assignee in assignees:
                    assignee_name = (
                        assignee if isinstance(assignee, str) else assignee.get("login", "unknown")
                    )
                    stats["assignees"][assignee_name] = stats["assignees"].get(assignee_name, 0) + 1

            # Count authors
            author = issue.get("user", {})
            author_name = (
                author.get("login", "unknown") if isinstance(author, dict) else str(author)
            )
            stats["authors"][author_name] = stats["authors"].get(author_name, 0) + 1

        return stats

    def list_issues(
        self,
        state: str = "all",
        labels: list[str] | None = None,
        assignee: str | None = None,
        milestone: str | None = None,
        author: str | None = None,
        sort_by: str = "created",
        reverse: bool = True,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        列出和过滤Issues

        Args:
            state: 状态过滤 (all/open/closed)
            labels: 标签过滤
            assignee: 负责人过滤
            milestone: 里程碑过滤
            author: 创建者过滤
            sort_by: 排序字段 (created/updated/comments/number)
            reverse: 是否降序
            limit: 限制结果数量

        Returns:
            过滤后的Issues列表
        """
        from sage_github.helpers.filter_issues import IssuesFilter

        issues = self.load_issues()
        if not issues:
            return []

        # 使用过滤器
        filter_tool = IssuesFilter(issues)
        filtered_issues = filter_tool.apply_filters(
            state=state,
            labels=labels,
            assignee=assignee,
            milestone=milestone,
            author=author,
            sort_by=sort_by,
            reverse=reverse,
            limit=limit,
        )

        return filtered_issues

    def export_issues(
        self,
        output_path: Path | str,
        format: str = "csv",
        state: str = "all",
        labels: list[str] | None = None,
        assignee: str | None = None,
        milestone: str | None = None,
        author: str | None = None,
        template: str = "default",
    ) -> bool:
        """
        导出Issues到文件

        Args:
            output_path: 输出文件路径
            format: 导出格式 (csv/json/markdown)
            state: 状态过滤
            labels: 标签过滤
            assignee: 负责人过滤
            milestone: 里程碑过滤
            author: 创建者过滤
            template: Markdown模板 (default/roadmap/report)

        Returns:
            是否成功
        """
        from sage_github.helpers.export_issues import IssuesExporter

        # 获取过滤后的Issues
        issues = self.list_issues(
            state=state,
            labels=labels,
            assignee=assignee,
            milestone=milestone,
            author=author,
            sort_by="created",
            reverse=True,
        )

        if not issues:
            print("⚠️ 没有符合条件的Issues")
            return False

        # 转换路径
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 导出
        exporter = IssuesExporter(issues)

        if format == "csv":
            success = exporter.export_to_csv(output_path)
        elif format == "json":
            success = exporter.export_to_json(output_path, pretty=True)
        elif format == "markdown":
            success = exporter.export_to_markdown(output_path, template=template)
        else:
            print(f"❌ 不支持的格式: {format}")
            return False

        if success:
            print(f"✅ 导出成功: {output_path}")
            print(f"📊 导出了 {len(issues)} 个Issues")
        return success

    def batch_close(
        self,
        state: str = "all",
        labels: list[str] | None = None,
        assignee: str | None = None,
        milestone: str | None = None,
        author: str | None = None,
        dry_run: bool = False,
        auto_confirm: bool = False,
    ) -> dict[str, Any]:
        """批量关闭Issues

        Args:
            state: 状态过滤
            labels: 标签过滤
            assignee: 负责人过滤
            milestone: 里程碑过滤
            author: 创建者过滤
            dry_run: 是否为预览模式
            auto_confirm: 是否自动确认

        Returns:
            操作结果统计
        """
        from sage_github.helpers.batch_operations import BatchOperations

        # 获取匹配的Issues
        issues = self.list_issues(
            state=state,
            labels=labels,
            assignee=assignee,
            milestone=milestone,
            author=author,
        )

        # 执行批量关闭
        batch_ops = BatchOperations(
            owner=self.config.GITHUB_OWNER,
            repo=self.config.GITHUB_REPO,
            token=self.config.github_token,
        )
        return batch_ops.close_issues(issues, dry_run=dry_run, auto_confirm=auto_confirm)

    def batch_add_labels(
        self,
        add_labels: list[str],
        state: str = "all",
        labels: list[str] | None = None,
        assignee: str | None = None,
        milestone: str | None = None,
        author: str | None = None,
        dry_run: bool = False,
        auto_confirm: bool = False,
    ) -> dict[str, Any]:
        """批量添加标签

        Args:
            add_labels: 要添加的标签列表
            state: 状态过滤
            labels: 标签过滤
            assignee: 负责人过滤
            milestone: 里程碑过滤
            author: 创建者过滤
            dry_run: 是否为预览模式
            auto_confirm: 是否自动确认

        Returns:
            操作结果统计
        """
        from sage_github.helpers.batch_operations import BatchOperations

        issues = self.list_issues(
            state=state,
            labels=labels,
            assignee=assignee,
            milestone=milestone,
            author=author,
        )

        batch_ops = BatchOperations(
            owner=self.config.GITHUB_OWNER,
            repo=self.config.GITHUB_REPO,
            token=self.config.github_token,
        )
        return batch_ops.add_labels(issues, add_labels, dry_run=dry_run, auto_confirm=auto_confirm)

    def batch_remove_labels(
        self,
        remove_labels: list[str],
        state: str = "all",
        labels: list[str] | None = None,
        assignee: str | None = None,
        milestone: str | None = None,
        author: str | None = None,
        dry_run: bool = False,
        auto_confirm: bool = False,
    ) -> dict[str, Any]:
        """批量移除标签

        Args:
            remove_labels: 要移除的标签列表
            state: 状态过滤
            labels: 标签过滤
            assignee: 负责人过滤
            milestone: 里程碑过滤
            author: 创建者过滤
            dry_run: 是否为预览模式
            auto_confirm: 是否自动确认

        Returns:
            操作结果统计
        """
        from sage_github.helpers.batch_operations import BatchOperations

        issues = self.list_issues(
            state=state,
            labels=labels,
            assignee=assignee,
            milestone=milestone,
            author=author,
        )

        batch_ops = BatchOperations(
            owner=self.config.GITHUB_OWNER,
            repo=self.config.GITHUB_REPO,
            token=self.config.github_token,
        )
        return batch_ops.remove_labels(
            issues, remove_labels, dry_run=dry_run, auto_confirm=auto_confirm
        )

    def batch_assign(
        self,
        assignees: list[str],
        state: str = "all",
        labels: list[str] | None = None,
        assignee: str | None = None,
        milestone: str | None = None,
        author: str | None = None,
        dry_run: bool = False,
        auto_confirm: bool = False,
    ) -> dict[str, Any]:
        """批量分配Issues

        Args:
            assignees: 负责人列表
            state: 状态过滤
            labels: 标签过滤
            assignee: 负责人过滤
            milestone: 里程碑过滤
            author: 创建者过滤
            dry_run: 是否为预览模式
            auto_confirm: 是否自动确认

        Returns:
            操作结果统计
        """
        from sage_github.helpers.batch_operations import BatchOperations

        issues = self.list_issues(
            state=state,
            labels=labels,
            assignee=assignee,
            milestone=milestone,
            author=author,
        )

        batch_ops = BatchOperations(
            owner=self.config.GITHUB_OWNER,
            repo=self.config.GITHUB_REPO,
            token=self.config.github_token,
        )
        return batch_ops.assign_issues(
            issues, assignees, dry_run=dry_run, auto_confirm=auto_confirm
        )

    def batch_set_milestone(
        self,
        milestone: str,
        state: str = "all",
        labels: list[str] | None = None,
        assignee: str | None = None,
        milestone_filter: str | None = None,
        author: str | None = None,
        dry_run: bool = False,
        auto_confirm: bool = False,
    ) -> dict[str, Any]:
        """批量设置里程碑

        Args:
            milestone: 要设置的里程碑
            state: 状态过滤
            labels: 标签过滤
            assignee: 负责人过滤
            milestone_filter: 里程碑过滤
            author: 创建者过滤
            dry_run: 是否为预览模式
            auto_confirm: 是否自动确认

        Returns:
            操作结果统计
        """
        from sage_github.helpers.batch_operations import BatchOperations

        issues = self.list_issues(
            state=state,
            labels=labels,
            assignee=assignee,
            milestone=milestone_filter,
            author=author,
        )

        batch_ops = BatchOperations(
            owner=self.config.GITHUB_OWNER,
            repo=self.config.GITHUB_REPO,
            token=self.config.github_token,
        )
        return batch_ops.set_milestone(
            issues, milestone, dry_run=dry_run, auto_confirm=auto_confirm
        )

    def summarize_issue(
        self, issue_number: int, api_provider: str = "openai", max_length: int = 200
    ) -> dict[str, Any] | None:
        """生成 Issue 摘要

        Args:
            issue_number: Issue 编号
            api_provider: API 提供商 (openai/claude)
            max_length: 最大摘要长度

        Returns:
            包含摘要的字典，如果失败返回 None
        """
        from sage_github.helpers.ai_helper import AIHelper

        # 加载 Issues
        issues = self.load_issues()
        issue = next((i for i in issues if i.get("number") == issue_number), None)

        if not issue:
            print(f"❌ 未找到 Issue #{issue_number}")
            return None

        # 生成摘要
        ai = AIHelper(api_provider=api_provider)
        summary = ai.summarize_issue(issue, max_length=max_length)

        if summary:
            return {
                "number": issue_number,
                "title": issue.get("title"),
                "summary": summary,
                "url": issue.get("html_url"),
            }

        return None

    def detect_duplicates(self, threshold: float = 0.7) -> list[dict[str, Any]]:
        """检测重复的 Issues

        Args:
            threshold: 相似度阈值 (0-1)

        Returns:
            重复对列表
        """
        from sage_github.helpers.ai_helper import AIHelper

        issues = self.load_issues()
        if not issues:
            print("❌ 没有可用的 Issues")
            return []

        ai = AIHelper(silent=True)  # 不需要 API，使用静默模式
        duplicates = ai.detect_duplicates(issues, threshold=threshold)

        results = []
        for issue1, issue2, similarity in duplicates:
            results.append(
                {
                    "issue1": {
                        "number": issue1.get("number"),
                        "title": issue1.get("title"),
                        "url": issue1.get("html_url"),
                    },
                    "issue2": {
                        "number": issue2.get("number"),
                        "title": issue2.get("title"),
                        "url": issue2.get("html_url"),
                    },
                    "similarity": round(similarity, 2),
                }
            )

        return results

    def suggest_labels_for_issue(self, issue_number: int) -> dict[str, Any] | None:
        """为 Issue 推荐标签

        Args:
            issue_number: Issue 编号

        Returns:
            包含推荐标签的字典，如果失败返回 None
        """
        from sage_github.helpers.ai_helper import AIHelper

        issues = self.load_issues()
        issue = next((i for i in issues if i.get("number") == issue_number), None)

        if not issue:
            print(f"❌ 未找到 Issue #{issue_number}")
            return None

        ai = AIHelper(silent=True)  # 标签建议不需要 API
        suggested = ai.suggest_labels(issue)

        existing_labels = [label.get("name") for label in issue.get("labels", [])]

        return {
            "number": issue_number,
            "title": issue.get("title"),
            "existing_labels": existing_labels,
            "suggested_labels": suggested,
            "new_labels": [label for label in suggested if label not in existing_labels],
            "url": issue.get("html_url"),
        }

    def show_statistics(self) -> bool:
        """显示Issues统计信息"""
        print("📊 显示Issues统计信息...")
        issues = self.load_issues()
        if not issues:
            return False

        stats = self._generate_statistics(issues)

        print("\n📈 Issues统计报告")
        print("=" * 40)
        print(f"总Issues数: {stats['total']}")
        print(f"开放Issues: {stats['open']}")
        print(f"已关闭Issues: {stats['closed']}")

        if stats["labels"]:
            print("\n🏷️ 标签分布 (前10):")
            for label, count in sorted(stats["labels"].items(), key=lambda x: x[1], reverse=True)[
                :10
            ]:
                print(f"  - {label}: {count}")

        if stats["assignees"]:
            print("\n👤 分配情况 (前10):")
            for assignee, count in sorted(
                stats["assignees"].items(), key=lambda x: x[1], reverse=True
            )[:10]:
                print(f"  - {assignee}: {count}")

        if stats["authors"]:
            print("\n✍️ 作者分布 (前10):")
            for author, count in sorted(stats["authors"].items(), key=lambda x: x[1], reverse=True)[
                :10
            ]:
                print(f"  - {author}: {count}")

        # Save detailed report
        report_file = (
            self.output_dir / f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"\n📄 详细报告已保存到: {report_file}")
        return True

    def create_new_issue(self) -> bool:
        """创建新Issue"""
        print("✨ 创建新Issue...")
        # Check if helper script exists
        helper_script = self.helpers_dir / "create_issue.py"
        if helper_script.exists():
            print("🔄 调用创建Issue助手...")
            result = subprocess.run(
                [sys.executable, str(helper_script)], capture_output=False, text=True
            )
            return result.returncode == 0
        else:
            print("⚠️ 创建Issue助手不存在")
            print("📝 请手动创建Issue或实现create_issue.py助手")
            return True

    def team_analysis(self) -> bool:
        """团队分析"""
        print("👥 团队分析...")
        if not self.team_info:
            print("❌ 没有团队信息，无法进行分析")
            return False

        # 直接显示基本团队信息，不依赖外部脚本
        print("📊 基本团队信息:")
        teams = self.team_info.get("teams", {})
        total_members = 0

        for team_name, members in teams.items():
            member_count = len(members) if isinstance(members, list) else 0
            total_members += member_count
            print(f"  - {team_name}: {member_count} 成员")

        print("\n📈 团队总览:")
        print(f"  - 团队总数: {len(teams)}")
        print(f"  - 成员总数: {total_members}")

        # 如果有GitHub Token，可以尝试获取更详细信息
        if self.config.github_token:
            print("\n� GitHub连接正常，可以获取详细团队信息")
            print("💡 如需更新团队信息，请运行: sage-dev issues team --update")
        else:
            print("\n⚠️ 未配置GitHub Token，无法获取最新团队信息")
            print("💡 配置Token后可获取更多详细信息")

        return True

    def project_management(self) -> bool:
        """项目管理 - 自动检测并修复错误分配的Issues"""
        print("📋 项目管理...")

        # Check if our fix script exists
        fix_script = self.helpers_dir / "fix_misplaced_issues.py"
        execute_script = self.helpers_dir / "execute_fix_plan.py"

        if fix_script.exists():
            print("🔍 扫描错误分配的Issues...")

            # First, run detection to generate fix plan
            detection_result = subprocess.run(
                [sys.executable, str(fix_script), "--dry-run"],
                capture_output=True,
                text=True,
                cwd=str(self.scripts_dir),
            )

            if detection_result.returncode != 0:
                print(f"❌ 检测脚本执行失败: {detection_result.stderr}")
                return False

            print(detection_result.stdout)

            # Check if there's a fix plan file generated
            fix_plan_files = list(self.output_dir.glob("issues_fix_plan_*.json"))

            if fix_plan_files:
                latest_plan = max(fix_plan_files, key=lambda x: x.stat().st_mtime)
                print(f"📋 发现修复计划: {latest_plan.name}")

                # Ask user if they want to execute the fix
                try:
                    response = input("🤔 是否执行修复计划? (y/N): ").strip().lower()
                    if response in ["y", "yes"]:
                        print("🚀 执行修复计划...")
                        execute_result = subprocess.run(
                            [
                                sys.executable,
                                str(execute_script),
                                str(latest_plan),
                                "--live",
                            ],
                            capture_output=False,
                            text=True,
                            cwd=str(self.scripts_dir),
                        )

                        return execute_result.returncode == 0
                    else:
                        print("✅ 跳过执行，仅进行了检测")
                        return True
                except KeyboardInterrupt:
                    print("\n✅ 操作被用户取消")
                    return True
            else:
                print("✅ 没有发现需要修复的Issues")
                return True

        else:
            print("⚠️ Issues修复助手不存在")
            print("📝 请检查 helpers/fix_misplaced_issues.py")
            return True

    def update_team_info(self) -> bool:
        """更新团队信息"""
        print("🔄 更新团队信息...")

        # 检查GitHub Token
        if not self.config.github_token:
            print("❌ GitHub Token未配置，无法更新团队信息")
            print("💡 请设置GitHub Token:")
            print(
                "   export GITHUB_TOKEN=your_token  # 或 export GIT_TOKEN=your_token / export SAGE_REPO_TOKEN=your_token"
            )
            print("   或创建 ~/.github_token 文件")
            return False

        # 使用配置系统来调用团队获取脚本
        helper_script = self.helpers_dir / "get_team_members.py"
        if helper_script.exists():
            print("🔄 正在从GitHub API获取最新团队信息...")

            # 设置环境变量确保脚本能获取到token
            env = os.environ.copy()
            env["GITHUB_TOKEN"] = self.config.github_token

            result = subprocess.run(
                [sys.executable, str(helper_script)],
                capture_output=True,
                text=True,
                env=env,
                cwd=str(self.scripts_dir),
            )

            if result.returncode == 0:
                print("✅ 团队信息更新成功")
                print(result.stdout)
                # Reload team info
                self.team_info = self._load_team_info()
                return True
            else:
                print("❌ 团队信息更新失败")
                print(f"错误信息: {result.stderr}")
                return False
        else:
            print("❌ get_team_members.py助手不存在")
            return False

    def test_github_connection(self) -> bool:
        """测试GitHub连接"""
        print("🔍 测试GitHub连接...")
        try:
            if self.config.test_github_connection():
                print("✅ GitHub连接正常")
                return True
            else:
                print("❌ GitHub连接失败")
                return False
        except Exception as e:
            print(f"❌ GitHub连接错误: {e}")
            return False
