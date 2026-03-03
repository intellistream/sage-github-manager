#!/usr/bin/env python3
"""
Issues 统一同步脚本 - 支持所有属性的同步

功能:
- 基本属性同步: assignee, labels, title, body, milestone (REST API)
- 项目板同步: projects (GraphQL API)
- 支持强制更新和预览模式
- 完整的错误处理和状态报告

使用方法:
    python3 sync_issues.py --preview                    # 预览所有更改
    python3 sync_issues.py --apply-all --confirm        # 应用所有更改
    python3 sync_issues.py --apply-basic --confirm      # 仅同步基本属性
    python3 sync_issues.py --apply-projects --confirm   # 仅同步项目板
    python3 sync_issues.py --force-update               # 强制更新（忽略时间戳）

作者: SAGE Team
日期: 2025-08-30
"""

import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import sys
import time
from typing import Any

from github_helper import GitHubProjectManager
import requests

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent))  # Add parent directory to path


# 动态导入config模块
try:
    # 尝试相对导入（当作为模块运行时）
    from ..config import IssuesConfig
    from ..issue_data_manager import IssueDataManager
except ImportError:
    # 如果相对导入失败，使用绝对导入
    sys.path.insert(0, str(SCRIPT_DIR.parent))
    from config import IssuesConfig  # type: ignore[no-redef]
    from issue_data_manager import IssueDataManager  # type: ignore[no-redef]

# Import github_helper directly
sys.path.insert(0, str(SCRIPT_DIR))


class GitHubClient:
    """Simple GitHub API client"""

    def __init__(self, config):
        self.config = config
        self.session = requests.Session()

        if config.github_token:
            headers = {
                "Authorization": f"token {config.github_token}",
                "Accept": "application/vnd.github.v3+json",
            }
            self.session.headers.update(headers)
        else:
            raise ValueError("GitHub Token is required for sync operations")


def graphql_request(
    session: requests.Session,
    query: str,
    variables: dict | None = None,
    retries: int = 2,
):
    payload: dict[str, Any] = {"query": query}
    if variables is not None:
        payload["variables"] = variables
    attempt = 0
    while True:
        try:
            resp = session.post("https://api.github.com/graphql", json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return True, data
        except Exception as e:
            attempt += 1
            if attempt > retries:
                return False, str(e)
            time.sleep(1 * attempt)


class IssuesSyncer:
    def __init__(self):
        self.config = IssuesConfig()
        self.github_client = GitHubClient(self.config)
        self.project_manager = GitHubProjectManager()
        self.workspace_dir = self.config.workspace_path
        self.output_dir = self.config.output_path

        # 初始化数据管理器
        self.data_manager = IssueDataManager(self.workspace_dir)

        # 默认启用强制更新
        self.force_update = True

        # 团队到项目的映射
        self.team_to_project = {
            "intellistream": 6,  # IntelliStream总体项目
            "sage-kernel": 12,
            "sage-middleware": 13,
            "sage-apps": 14,
        }

    def detect_all_changes(self):
        """检测所有类型的更改"""
        basic_changes = self.detect_basic_changes()
        project_changes = self.detect_project_changes()

        all_changes = basic_changes + project_changes

        if all_changes:
            print(f"📋 检测到 {len(all_changes)} 个待同步更改:")

            basic_count = len([c for c in all_changes if c["type"] == "basic"])
            project_count = len([c for c in all_changes if c["type"] == "project"])

            if basic_count > 0:
                print(f"  🔧 基本属性更改: {basic_count} 个")
            if project_count > 0:
                print(f"  📋 项目板更改: {project_count} 个")

            for change in all_changes[:20]:  # 只显示前20个
                print(f"   - [{change['type']}] {change['description']}")

            if len(all_changes) > 20:
                print(f"   ... 以及其他 {len(all_changes) - 20} 个更改")

        return all_changes

    def detect_changes_limited(self, limit=50, recent_only=False):
        """检测有限数量的更改（用于快速预览）"""
        from datetime import datetime, timedelta

        changes = []

        # 使用新架构：读取data目录下的JSON文件
        data_dir = self.workspace_dir / "data"
        if not data_dir.exists():
            print("❌ data目录不存在，请先下载issues数据")
            return changes

        files = list(data_dir.glob("issue_*.json"))

        # 如果只检查最近更新的issues
        if recent_only:
            cutoff_date = datetime.now() - timedelta(days=7)
            filtered_files = []

            for f in files:
                try:
                    issue_data = self.data_manager.get_issue(int(f.stem.split("_")[1]))
                    if issue_data:
                        updated_str = issue_data["metadata"].get("updated_at", "")
                        if updated_str:
                            updated_date = datetime.fromisoformat(
                                updated_str.replace("Z", "+00:00")
                            )
                            if updated_date.replace(tzinfo=None) > cutoff_date:
                                filtered_files.append(f)
                except Exception:
                    continue

            files = filtered_files
            print(f"🔍 过滤到最近7天更新的issues: {len(files)} 个")

        # 限制检查数量
        files = files[:limit]
        print(f"🔎 检查 {len(files)} 个JSON文件...")

        for i, f in enumerate(files):
            print(f"🔎 进度: {i + 1}/{len(files)} - Issue #{f.stem.split('_')[1]}")

            try:
                # 使用数据管理器读取issue
                issue_number = int(f.stem.split("_")[1])
                local_data = self.data_manager.get_issue(issue_number)
                if not local_data:
                    continue

                # 获取远端数据
                remote_data = self._get_remote_issue(issue_number)
                if not remote_data:
                    continue

                # 比较并检测更改
                changes_detected = self._compare_basic_attributes_json(
                    local_data, remote_data, issue_number, str(f)
                )
                changes.extend(changes_detected)

            except Exception as e:
                print(f"❌ 处理文件 {f} 时出错: {e}")
                continue

        return changes

    def sync_all_changes(self, apply_projects=False, auto_confirm=False):
        """统一同步所有类型的更改"""
        changes = self.detect_all_changes()
        if not changes:
            print("✅ 没有检测到需要同步的更改")
            return True

        # 分组处理不同类型的更改
        basic_changes = [c for c in changes if c["type"] == "basic"]
        project_changes = [c for c in changes if c["type"] == "project"]

        print(f"📋 检测到 {len(changes)} 个待同步更改:")
        if basic_changes:
            print(f"  🔧 基本属性更改: {len(basic_changes)} 个")
        if project_changes:
            print(f"  📋 项目板更改: {len(project_changes)} 个")

        # 如果没有apply_projects且有项目更改，只显示预览
        if project_changes and not apply_projects:
            print(f"\n💡 发现 {len(project_changes)} 个项目板更改:")
            for change in project_changes[:10]:  # 显示前10个
                print(f"   - {change['description']}")
            if len(project_changes) > 10:
                print(f"   ... 以及其他 {len(project_changes) - 10} 个项目板更改")
            print("💡 使用 --apply-projects 参数来应用项目板更改")

            # 只处理基本属性更改
            if basic_changes:
                print(f"\n🚀 开始同步基本属性更改 ({len(basic_changes)} 个)...")
                return self._sync_basic_changes_only(basic_changes)
            else:
                return True

        # 需要用户确认（除非auto_confirm为True）
        if not auto_confirm:
            confirm = input(f"\n是否同步这 {len(changes)} 个更改? (y/N): ").lower().strip()
            if confirm != "y":
                print("❌ 同步已取消")
                return False

        print(f"\n🚀 开始同步 {len(changes)} 个更改...")

        success_count = 0

        # 处理基本属性更改 (使用REST API)
        if basic_changes:
            print(f"\n📝 同步基本属性更改 ({len(basic_changes)} 个)...")
            for change in basic_changes:
                if self._apply_basic_change(change):
                    success_count += 1
                    print(f"✅ {change['description']}")
                else:
                    print(f"❌ {change['description']}")

        # 处理项目板更改 (使用GraphQL API)
        if project_changes and apply_projects:
            print(f"\n📋 同步项目板更改 ({len(project_changes)} 个)...")
            success = self._apply_project_changes(project_changes)
            if success:
                success_count += len(project_changes)
                print(f"✅ 成功处理 {len(project_changes)} 个项目板更改")
            else:
                print("❌ 项目板更改处理失败")

        print(f"\n✨ 同步完成: {success_count}/{len(changes)} 个更改成功")

        # 如果有成功的更改，重新生成视图
        if success_count > 0:
            print("\n🔄 重新生成视图...")
            try:
                # 重新下载并更新本地数据
                self._update_local_data_after_sync(basic_changes[:success_count])

                # 重新生成所有视图
                self.data_manager.generate_all_views()
                print("✅ 视图重新生成完成")
            except Exception as e:
                print(f"⚠️ 视图重新生成失败: {e}")

        return success_count == len(changes)

    def _update_local_data_after_sync(self, successful_changes):
        """同步成功后更新本地数据"""
        for change in successful_changes:
            if change["type"] == "basic":
                issue_number = change["issue_number"]
                try:
                    # 重新从GitHub获取最新数据
                    remote_data = self._get_remote_issue(issue_number)
                    if remote_data:
                        # 获取现有的本地数据
                        local_data = self.data_manager.get_issue(issue_number)
                        if local_data:
                            # 更新metadata部分
                            local_data["metadata"].update(
                                {
                                    "title": remote_data.get("title", ""),
                                    "labels": [
                                        label.get("name") for label in remote_data.get("labels", [])
                                    ],
                                    "assignees": (
                                        [remote_data["assignee"]["login"]]
                                        if remote_data.get("assignee")
                                        else []
                                    ),
                                    "milestone": remote_data.get("milestone"),
                                    "updated_at": remote_data.get("updated_at"),
                                }
                            )

                            # 更新content部分
                            local_data["content"]["body"] = remote_data.get("body", "")

                            # 更新tracking信息
                            local_data["tracking"]["last_synced"] = datetime.now().isoformat()
                            local_data["tracking"]["update_history"].append(
                                {
                                    "timestamp": datetime.now().isoformat(),
                                    "action": "sync_update",
                                    "github_updated": remote_data.get("updated_at"),
                                }
                            )

                            # 保存更新后的数据
                            self.data_manager.save_issue(issue_number, local_data)
                            print(f"  ✅ 已更新本地数据: Issue #{issue_number}")

                except Exception as e:
                    print(f"  ⚠️ 更新本地数据失败 Issue #{issue_number}: {e}")

    def _sync_basic_changes_only(self, basic_changes):
        """仅同步基本属性更改"""
        success_count = 0
        for change in basic_changes:
            if self._apply_basic_change(change):
                success_count += 1
                print(f"✅ {change['description']}")
            else:
                print(f"❌ {change['description']}")

        print(f"\n✨ 基本属性同步完成: {success_count}/{len(basic_changes)} 个更改成功")
        return success_count == len(basic_changes)

    def _apply_basic_change(self, change):
        """应用基本属性更改 (REST API)"""
        issue_number = change["issue_number"]
        local_data = change["local_data"]

        url = f"https://api.github.com/repos/{self.config.GITHUB_OWNER}/{self.config.GITHUB_REPO}/issues/{issue_number}"

        # 构建更新数据
        update_data = {}

        # 只更新有差异的属性
        for attr in change["changed_attributes"]:
            if attr == "标题" and local_data["title"]:
                update_data["title"] = local_data["title"]
            elif attr == "内容" and local_data["body"]:
                update_data["body"] = local_data["body"]
            elif attr == "标签":
                update_data["labels"] = local_data["labels"]
            elif attr == "分配给":
                if local_data["assignee"]:
                    update_data["assignee"] = local_data["assignee"]
                else:
                    update_data["assignee"] = None
            elif attr == "里程碑":
                if local_data["milestone"]:
                    # 需要获取milestone的number
                    milestone_number = self._get_milestone_number(local_data["milestone"])
                    if milestone_number:
                        update_data["milestone"] = milestone_number
                else:
                    update_data["milestone"] = None

        if not update_data:
            return True

        try:
            resp = self.github_client.session.patch(url, json=update_data, timeout=30)
            return resp.status_code == 200
        except Exception as e:
            print(f"   ❌ 更新失败: {e}")
            return False

    def _apply_project_changes(self, project_changes):
        """应用项目板更改 (GraphQL API)"""
        if not project_changes:
            return True

        success_count = 0

        try:
            for change in project_changes:
                issue_number = change["issue_number"]
                target_project_number = change["target_project_number"]
                target_project = change["target_project"]

                print(
                    f"   🔄 移动Issue #{issue_number}到项目{target_project} (#{target_project_number})..."
                )

                # 获取issue的node_id
                issue_data = self._get_remote_issue(issue_number)
                if not issue_data:
                    print(f"   ❌ 无法获取Issue #{issue_number}的数据")
                    continue

                issue_node_id = issue_data.get("node_id")
                if not issue_node_id:
                    print(f"   ❌ 无法获取Issue #{issue_number}的node_id")
                    continue

                # 获取项目的project_id
                project_id = self.project_manager.get_project_id(target_project_number)
                if not project_id:
                    print(f"   ❌ 无法获取项目#{target_project_number}的project_id")
                    continue

                # 检查issue是否已在目标项目中
                if target_project_number in change["current_projects"]:
                    print(f"   ⏭️ Issue #{issue_number}已在目标项目中，跳过")
                    success_count += 1
                    continue

                # 使用GraphQL添加issue到项目
                success = self._add_issue_to_project(
                    issue_node_id, project_id, target_project_number
                )
                if success:
                    success_count += 1
                    print(f"   ✅ 成功移动Issue #{issue_number}到项目{target_project}")
                else:
                    print(f"   ❌ 移动Issue #{issue_number}失败")

            return success_count == len(project_changes)

        except Exception as e:
            print(f"   ❌ 项目板更改失败: {e}")
            return False

    def _add_issue_to_project(self, issue_node_id, project_id, project_number):
        """使用GraphQL将issue添加到项目"""
        try:
            mutation = """
                mutation($projectId: ID!, $contentId: ID!) {
                    addProjectV2ItemById(input: {
                        projectId: $projectId,
                        contentId: $contentId
                    }) {
                        item {
                            id
                        }
                    }
                }
            """

            variables = {"projectId": project_id, "contentId": issue_node_id}

            # 使用project_manager的GraphQL客户端
            response = self.project_manager.execute_graphql(mutation, variables)

            if response and "data" in response and response["data"]["addProjectV2ItemById"]:
                return True
            else:
                print(f"   ❌ GraphQL响应错误: {response}")
                return False

        except Exception as e:
            print(f"   ❌ GraphQL调用失败: {e}")
            return False

    def _get_milestone_number(self, milestone_title):
        """获取milestone的编号"""
        url = f"https://api.github.com/repos/{self.config.GITHUB_OWNER}/{self.config.GITHUB_REPO}/milestones"
        try:
            resp = self.github_client.session.get(url, timeout=20)
            if resp.status_code == 200:
                milestones = resp.json()
                for m in milestones:
                    if m["title"] == milestone_title:
                        return m["number"]
        except Exception:
            pass
        return None

    def sync_one_issue(self, issue_number):
        """同步单个issue"""
        print(f"🔄 检查issue #{issue_number}...")

        issues_dir = self.workspace_dir / "issues"
        file_pattern = f"open_{issue_number}_*.md"
        files = list(issues_dir.glob(file_pattern))

        if not files:
            print(f"❌ 未找到issue #{issue_number}的本地文件")
            return False

        # 检测这个issue的所有更改
        all_changes = []
        for f in files:
            text = f.read_text(encoding="utf-8")
            local_data = self._parse_local_issue(text)

            # 检测基本属性更改
            remote_data = self._get_remote_issue(issue_number)
            if remote_data:
                basic_changes = self._compare_basic_attributes(
                    local_data, remote_data, issue_number, str(f)
                )
                all_changes.extend(basic_changes)

            # 检测项目更改
            local_project = self._parse_local_project(text)
            if local_project:
                current_projects = self._get_issue_current_projects(issue_number)
                expected_project_num = self.team_to_project.get(local_project)
                if expected_project_num and expected_project_num not in current_projects:
                    all_changes.append(
                        {
                            "type": "project",
                            "description": f"Issue #{issue_number} - 移动到项目 {local_project}",
                            "issue_number": issue_number,
                            "current_projects": current_projects,
                            "target_project": local_project,
                            "target_project_number": expected_project_num,
                            "file": str(f),
                        }
                    )

        if not all_changes:
            print(f"✅ Issue #{issue_number} 无需同步")
            return True

        print(f"📋 发现 {len(all_changes)} 个更改:")
        for change in all_changes:
            print(f"   - {change['description']}")

        # 应用更改
        success_count = 0
        for change in all_changes:
            if change["type"] == "basic":
                if self._apply_basic_change(change):
                    success_count += 1
                    print(f"✅ {change['description']}")
                else:
                    print(f"❌ {change['description']}")
            elif change["type"] == "project":
                if self._apply_project_changes([change]):
                    success_count += 1
                    print(f"✅ {change['description']}")
                else:
                    print(f"❌ {change['description']}")

        print(f"✨ 同步完成: {success_count}/{len(all_changes)} 个更改成功")
        return success_count == len(all_changes)

    def show_sync_status(self):
        """显示同步状态概览"""
        print("\n🔍 检查同步状态...")

        changes = self.detect_all_changes()

        if not changes:
            print("✅ 所有issues都已同步")
            return

        # 按类型分组统计
        basic_changes = [c for c in changes if c["type"] == "basic"]
        project_changes = [c for c in changes if c["type"] == "project"]

        print("\n📊 同步状态概览:")
        print(f"   总共需要同步: {len(changes)} 个更改")

        if basic_changes:
            print(f"   基本属性更改: {len(basic_changes)} 个")
            # 按属性类型分组
            attr_count = {}
            for change in basic_changes:
                for attr in change.get("changed_attributes", []):
                    attr_count[attr] = attr_count.get(attr, 0) + 1

            for attr, count in attr_count.items():
                print(f"      - {attr}: {count} 个")

        if project_changes:
            print(f"   项目板更改: {len(project_changes)} 个")
            # 按目标项目分组
            project_count = {}
            for change in project_changes:
                target = change.get("target_project", "未知")
                project_count[target] = project_count.get(target, 0) + 1

            for project, count in project_count.items():
                print(f"      - {project}: {count} 个")

        print("\n💡 运行 'sync_issues.py sync' 来同步所有更改")
        print("💡 运行 'sync_issues.py sync <issue_number>' 来同步单个issue")

    def detect_basic_changes(self):
        """检测基本属性更改 (assignee, labels, title, body, milestone)"""
        changes = []

        # 使用新架构：读取data目录下的JSON文件
        data_dir = self.workspace_dir / "data"
        if not data_dir.exists():
            print("❌ data目录不存在，请先下载issues数据")
            return changes

        files = list(data_dir.glob("issue_*.json"))
        print(f"🔎 scanning {len(files)} JSON files for basic changes...")

        for i, f in enumerate(files):
            if i % 50 == 0:
                print(f"🔎 scanning files... progress: {i}/{len(files)}")

            try:
                # 使用数据管理器读取issue
                issue_number = int(f.stem.split("_")[1])
                local_data = self.data_manager.get_issue(issue_number)
                if not local_data:
                    continue

                # 获取远端数据
                remote_data = self._get_remote_issue(issue_number)
                if not remote_data:
                    continue

                # 比较并检测更改
                changes_detected = self._compare_basic_attributes_json(
                    local_data, remote_data, issue_number, str(f)
                )
                changes.extend(changes_detected)

            except Exception as e:
                print(f"❌ 处理文件 {f} 时出错: {e}")
                continue

        return changes

    def check_outdated_timestamps(self, limit=50, recent_only=False):
        """超快速检查：只比较时间戳，不调用GitHub API获取详细数据"""
        from datetime import datetime, timedelta

        outdated_issues = []

        # 使用新架构：读取data目录下的JSON文件
        data_dir = self.workspace_dir / "data"
        if not data_dir.exists():
            print("❌ data目录不存在，请先下载issues数据")
            return outdated_issues

        files = list(data_dir.glob("issue_*.json"))

        # 如果只检查最近更新的issues
        if recent_only:
            cutoff_date = datetime.now() - timedelta(days=7)
            filtered_files = []

            for f in files:
                try:
                    issue_data = self.data_manager.get_issue(int(f.stem.split("_")[1]))
                    if issue_data:
                        updated_str = issue_data["metadata"].get("updated_at", "")
                        if updated_str:
                            updated_date = datetime.fromisoformat(
                                updated_str.replace("Z", "+00:00")
                            )
                            if updated_date.replace(tzinfo=None) > cutoff_date:
                                filtered_files.append(f)
                except Exception:
                    continue

            files = filtered_files
            print(f"🔍 过滤到最近7天更新的issues: {len(files)} 个")

        # 限制检查数量
        files = files[:limit]
        print(f"🔎 检查 {len(files)} 个JSON文件的时间戳...")

        for i, f in enumerate(files):
            if i % 10 == 0:
                print(f"🔎 进度: {i + 1}/{len(files)}")

            try:
                # 读取本地数据
                issue_number = int(f.stem.split("_")[1])
                local_data = self.data_manager.get_issue(issue_number)
                if not local_data:
                    continue

                # 获取本地记录的GitHub更新时间
                local_github_time = local_data["metadata"].get("updated_at", "")
                local_sync_time = local_data["tracking"].get("last_synced", "")

                if not local_github_time:
                    continue

                # 简单的启发式检查：如果本地有未同步的修改时间晚于GitHub时间，可能需要同步
                try:
                    github_time = datetime.fromisoformat(local_github_time.replace("Z", "+00:00"))
                    sync_time = (
                        datetime.fromisoformat(local_sync_time) if local_sync_time else github_time
                    )

                    # 如果同步时间早于GitHub时间，说明GitHub上有新的更新
                    if sync_time < github_time:
                        outdated_issues.append(
                            {
                                "number": issue_number,
                                "local_time": sync_time.strftime("%Y-%m-%d %H:%M:%S"),
                                "github_time": github_time.strftime("%Y-%m-%d %H:%M:%S"),
                            }
                        )

                except Exception:
                    continue

            except Exception:
                continue

        return outdated_issues

    def detect_project_changes(self):
        """检测项目板更改"""
        changes = []

        # 使用新架构：读取data目录下的JSON文件
        data_dir = self.workspace_dir / "data"
        if not data_dir.exists():
            print("❌ data目录不存在，请先下载issues数据")
            return changes

        files = list(data_dir.glob("issue_*.json"))
        print(f"🔎 scanning {len(files)} JSON files for project changes...")

        # 批量获取所有项目数据，避免重复API调用
        print("📥 预加载项目板数据...")
        project_items_cache = {}
        for project_num in [
            6,
            12,
            13,
            14,
        ]:  # intellistream, sage-kernel, sage-middleware, sage-apps
            try:
                items = self.project_manager.get_project_items(project_num)
                if items:
                    project_items_cache[project_num] = items
                    print(f"  ✅ 项目#{project_num}: {len(items)} 个items")
                else:
                    project_items_cache[project_num] = []
            except Exception as e:
                print(f"  ⚠️ 获取项目#{project_num}数据失败: {e}")
                project_items_cache[project_num] = []

        for i, f in enumerate(files):
            if i % 50 == 0:
                print(f"🔎 scanning files... progress: {i}/{len(files)}")

            try:
                # 使用数据管理器读取issue
                issue_number = int(f.stem.split("_")[1])
                local_data = self.data_manager.get_issue(issue_number)
                if not local_data:
                    continue

                # 从JSON数据中获取项目信息
                local_projects = local_data.get("metadata", {}).get("projects", [])
                if local_projects:
                    # 取第一个项目的team信息
                    local_project_team = local_projects[0].get("team")

                    if local_project_team:
                        # 使用缓存数据检查issue当前所在的项目
                        current_projects = self._get_issue_current_projects_from_cache(
                            issue_number, project_items_cache
                        )

                        expected_project_num = self.team_to_project.get(local_project_team)
                        if expected_project_num and expected_project_num not in current_projects:
                            changes.append(
                                {
                                    "type": "project",
                                    "description": f"Issue #{issue_number} - 移动到项目 {local_project_team}",
                                    "issue_number": issue_number,
                                    "current_projects": current_projects,
                                    "target_project": local_project_team,
                                    "target_project_number": expected_project_num,
                                    "file": str(f),
                                }
                            )

            except Exception as e:
                print(f"❌ 处理文件 {f} 时出错: {e}")
                continue

        return changes

    def _extract_original_body(self, text, include_update_history=None):
        """
        Extracts the main body content from a local issue file, with optional inclusion of the update history section.

        This method processes the issue file text, skipping metadata and extracting the main body content.
        The extraction logic handles several edge cases:
        - Skips metadata and title at the top of the file to find the start of the body.
        - If `include_update_history` is True, extraction stops at the first separator line (`---`), or at lines starting with
          "**GitHub链接**:" or "**下载时间**:".
        - If `include_update_history` is False, extraction also stops at the "## 更新记录" section in addition to the above markers.
        - Trailing empty lines are removed from the extracted body.

        Args:
            text (str): The full content of the issue file.
            include_update_history (bool or None): Whether to include the update history section. If None, uses the config setting.

        Returns:
            str: The extracted body content.
        """
        if include_update_history is None:
            include_update_history = self.config.sync_update_history

        lines = text.splitlines()

        # 跳过元数据部分，从第一个非元数据内容开始提取
        content_start = -1

        # 查找内容开始位置，跳过标题和元数据部分
        for i, line in enumerate(lines):
            stripped = line.strip()

            # 跳过标题行（以 # 开头）
            if stripped.startswith("# "):
                continue

            # 跳过元数据部分（Issue #, 状态, 创建时间等）
            if (
                stripped.startswith("**Issue #**:")
                or stripped.startswith("**状态**:")
                or stripped.startswith("**创建时间**:")
                or stripped.startswith("**更新时间**:")
                or stripped.startswith("**创建者**:")
            ):
                continue

            # 跳过Project归属、标签、分配给等section标题和内容，以及我们添加的"## 描述"标题
            if (
                stripped in ["## Project归属", "## 标签", "## 分配给", "## 描述"]
                or stripped.startswith("- **")
                or (
                    stripped
                    and not stripped.startswith("##")
                    and i > 0
                    and lines[i - 1].strip() in ["## Project归属", "## 标签", "## 分配给"]
                )
            ):
                continue

            # 找到第一个非元数据的内容行
            if stripped and not stripped.startswith("**"):
                content_start = i
                break

        if content_start == -1:
            return ""

        # 提取内容
        body_lines = []
        for i in range(content_start, len(lines)):
            line = lines[i]
            stripped = line.strip()

            # 停止条件的判断
            if include_update_history:
                # 如果要包含更新记录，只在遇到分隔线或GitHub链接时停止
                if (
                    stripped == "---"
                    or stripped.startswith("**GitHub链接**:")
                    or stripped.startswith("**下载时间**:")
                ):
                    break
            else:
                # 如果不包含更新记录，遇到更新记录部分也要停止
                if (
                    stripped == "## 更新记录"
                    or stripped == "---"
                    or stripped.startswith("**GitHub链接**:")
                    or stripped.startswith("**下载时间**:")
                ):
                    break

            body_lines.append(line)

        # 去除末尾的空行
        while body_lines and not body_lines[-1].strip():
            body_lines.pop()

        return "\n".join(body_lines)

    def _parse_local_issue(self, text):
        """解析本地issue文件的所有属性"""
        data = {
            "title": None,
            "body": self._extract_original_body(
                text, include_update_history=False
            ),  # 解析元数据时不包含更新记录
            "labels": [],
            "assignee": None,
            "milestone": None,
            "project": None,
        }

        lines = text.splitlines()

        # 解析标题
        for line in lines:
            if line.strip().startswith("# "):
                data["title"] = line.strip().lstrip("# ").strip()
                break

        # 解析各个section
        current_section = None
        for _i, line in enumerate(lines):
            line = line.strip()

            if line.startswith("## "):
                current_section = line[3:].strip()
                continue

            if current_section == "标签" and line and not line.startswith("##"):
                # 处理标签
                for part in line.split(","):
                    label = part.strip()
                    if label:
                        data["labels"].append(label)

            elif (
                current_section == "分配给"
                and line
                and not line.startswith("##")
                and line != "未分配"
            ):
                data["assignee"] = line

            elif current_section == "Project归属" and line.startswith("- **") and "**" in line:
                # 格式: - **sage-apps** (Project Board ID: 14: SAGE-Apps)
                team_match = re.search(r"\*\*(.+?)\*\*", line)
                if team_match:
                    data["project"] = team_match.group(1)

        return data

    def _parse_local_project(self, text):
        """单独解析项目归属"""
        lines = text.splitlines()

        for i, line in enumerate(lines):
            if line.strip() == "## Project归属":
                # 查找下一行的项目信息
                for j in range(i + 1, min(i + 5, len(lines))):
                    l_strip = lines[j].strip()
                    if l_strip.startswith("- **") and "**" in l_strip:
                        team_match = re.search(r"\*\*(.+?)\*\*", l_strip)
                        if team_match:
                            return team_match.group(1)
                break

        return None

    def _get_remote_issue(self, issue_number):
        """获取远端issue数据"""
        url = f"https://api.github.com/repos/{self.config.GITHUB_OWNER}/{self.config.GITHUB_REPO}/issues/{issue_number}"
        try:
            resp = self.github_client.session.get(url, timeout=20)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return None

    def _get_issue_current_projects(self, issue_number):
        """获取issue当前所在的项目板"""
        current_projects = []

        # 检查所有相关项目板
        projects_to_check = [
            6,
            12,
            13,
            14,
        ]  # intellistream, sage-kernel, sage-middleware, sage-apps

        for project_num in projects_to_check:
            try:
                items = self.project_manager.get_project_items(project_num)
                if items:
                    # 检查这个issue是否在当前项目中
                    for item in items:
                        content = item.get("content", {})
                        if content.get("number") == issue_number:
                            current_projects.append(project_num)
                            break
            except Exception as e:
                print(f"⚠️ 检查项目#{project_num}时出错: {e}")

        return current_projects

    def _get_issue_current_projects_from_cache(self, issue_number, project_items_cache):
        """从缓存数据中获取issue当前所在的项目板"""
        current_projects = []

        for project_num, items in project_items_cache.items():
            for item in items:
                content = item.get("content", {})
                if content.get("number") == issue_number:
                    current_projects.append(project_num)
                    break

        return current_projects

    def _compare_basic_attributes(self, local_data, remote_data, issue_number, file_path):
        """比较基本属性并生成更改列表"""
        changes = []

        # 获取远端数据
        remote_title = remote_data.get("title", "")
        remote_body = remote_data.get("body", "")
        remote_labels = [label.get("name") for label in remote_data.get("labels", [])]
        remote_assignee = None
        if remote_data.get("assignee"):
            remote_assignee = remote_data["assignee"]["login"]
        remote_milestone = None
        if remote_data.get("milestone"):
            remote_milestone = remote_data["milestone"]["title"]

        # 比较各个属性
        changed_attrs = []

        if local_data["title"] and local_data["title"] != remote_title:
            changed_attrs.append("标题")

        if local_data["body"] and local_data["body"] != remote_body:
            changed_attrs.append("内容")

        if set(local_data["labels"]) != set(remote_labels):
            changed_attrs.append("标签")

        if local_data["assignee"] != remote_assignee:
            changed_attrs.append("分配给")

        if local_data["milestone"] != remote_milestone:
            changed_attrs.append("里程碑")

        if changed_attrs:
            changes.append(
                {
                    "type": "basic",
                    "description": f"Issue #{issue_number} - 更新{'/'.join(changed_attrs)}",
                    "issue_number": issue_number,
                    "file": file_path,
                    "local_data": local_data,
                    "remote_data": {
                        "title": remote_title,
                        "body": remote_body,
                        "labels": remote_labels,
                        "assignee": remote_assignee,
                        "milestone": remote_milestone,
                    },
                    "remote_updated_at": remote_data.get("updated_at"),
                    "changed_attributes": changed_attrs,
                }
            )

        return changes

    def _compare_basic_attributes_json(self, local_data, remote_data, issue_number, file_path):
        """比较基本属性并生成更改列表 - JSON格式版本"""
        changes = []

        # 从JSON数据中提取信息
        local_metadata = local_data.get("metadata", {})
        local_content = local_data.get("content", {})

        local_title = local_metadata.get("title", "")
        local_body = local_content.get("body", "")
        local_labels = local_metadata.get("labels", [])
        local_assignees = local_metadata.get("assignees", [])
        local_assignee = local_assignees[0] if local_assignees else None
        local_milestone = local_metadata.get("milestone", {})
        local_milestone_title = local_milestone.get("title") if local_milestone else None

        # 获取远端数据
        remote_title = remote_data.get("title", "")
        remote_body = remote_data.get("body", "")
        remote_labels = [label.get("name") for label in remote_data.get("labels", [])]
        remote_assignee = None
        if remote_data.get("assignee"):
            remote_assignee = remote_data["assignee"]["login"]
        remote_milestone = None
        if remote_data.get("milestone"):
            remote_milestone = remote_data["milestone"]["title"]

        # 比较各个属性
        changed_attrs = []

        if local_title and local_title != remote_title:
            changed_attrs.append("标题")

        if local_body and local_body != remote_body:
            changed_attrs.append("内容")

        if set(local_labels) != set(remote_labels):
            changed_attrs.append("标签")

        if local_assignee != remote_assignee:
            changed_attrs.append("分配给")

        if local_milestone_title != remote_milestone:
            changed_attrs.append("里程碑")

        if changed_attrs:
            changes.append(
                {
                    "type": "basic",
                    "description": f"Issue #{issue_number} - 更新{'/'.join(changed_attrs)}",
                    "issue_number": issue_number,
                    "file": file_path,
                    "local_data": {
                        "title": local_title,
                        "body": local_body,
                        "labels": local_labels,
                        "assignee": local_assignee,
                        "milestone": local_milestone_title,
                    },
                    "remote_data": {
                        "title": remote_title,
                        "body": remote_body,
                        "labels": remote_labels,
                        "assignee": remote_assignee,
                        "milestone": remote_milestone,
                    },
                    "remote_updated_at": remote_data.get("updated_at"),
                    "changed_attributes": changed_attrs,
                }
            )

        return changes

    def sync_label_changes(self):
        label_changes = self.detect_label_changes()
        if not label_changes:
            print("✅ 没有检测到标签更改")
            return True
        return self.execute_sync(label_changes)

    def sync_status_changes(self):
        status_changes = self.detect_status_changes()
        if not status_changes:
            print("✅ 没有检测到状态更改")
            return True
        return self.execute_sync(status_changes)

    def preview_changes(self):
        all_changes = self.detect_all_changes()
        if not all_changes:
            print("✅ 没有检测到需要同步的更改")
            return True

        print(f"\n⚡ 检测到 {len(all_changes)} 个待同步更改:\n")
        for change in all_changes:
            print(f" - [{change['type']}] {change['description']}")

        report_file = (
            self.output_dir / f"sync_preview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        )
        self.save_preview_report(all_changes, report_file)
        print(f"📄 详细预览报告已保存到: {report_file}")
        return True

    def find_latest_plan(self):
        plans = sorted(self.output_dir.glob("project_move_plan_*.json"), reverse=True)
        if plans:
            return plans[0]
        return None

    def load_plan(self, path=None):
        if path:
            p = Path(path)
            print(f"🔍 使用指定的计划文件: {p}")
        else:
            p = self.find_latest_plan()
            if p:
                print(f"🔍 使用最新的计划文件: {p}")
            else:
                print("🔍 未找到任何计划文件")
        if not p or not p.exists():
            print("❌ 未找到 plan 文件，请先运行 helpers/fix_misplaced_issues.py")
            return []
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            print(f"✅ 已加载计划: {p.name}，{len(data)} 项")
            return data
        except Exception as e:
            print(f"❌ 解析 plan 失败: {e}")
            return []

    def preview_plan(self, plan):
        if not plan:
            print("✅ 计划为空")
            return True
        print(f"\n🔎 计划预览 ({len(plan)} 项):")
        for i, act in enumerate(plan, 1):
            print(
                f" [{i}/{len(plan)}] #{act.get('issue_number')} -> project {act.get('to_project')} ({act.get('to_project_number')}) staged={act.get('staged')}"
            )
        return True

    def apply_plan(self, plan, dry_run=True, batch_size=5):
        session = self.github_client.session
        logs = []
        total = len(plan)
        for idx, act in enumerate(plan, 1):
            issue_number = act.get("issue_number")
            issue_node_id = act.get("issue_node_id")
            item_id = act.get("item_id")
            project_id = act.get("to_project_id")
            project_number = act.get("to_project_number")
            entry = {"issue_number": issue_number, "project_number": project_number}
            print(f"[{idx}/{total}] 处理 Issue #{issue_number} -> project #{project_number}")

            # Idempotency check: does project already contain this contentId?
            q_check = """query($projectId: ID!) { node(id: $projectId) { ... on ProjectV2 { items(first:100) { nodes { content { __typename ... on Issue { id } } } pageInfo { hasNextPage endCursor } } } } }"""
            ok, resp = graphql_request(session, q_check, {"projectId": project_id}, retries=1)
            already = False
            if ok:
                nodes = resp.get("data", {}).get("node", {}).get("items", {}).get("nodes", [])
                for n in nodes:
                    c = n.get("content") or {}
                    if c.get("id") == issue_node_id:
                        already = True
                        break

            if already:
                print("  ⏭️ 目标 project 已包含此 issue，跳过 add")
                entry["added"] = False
            else:
                if dry_run:
                    print(
                        f"  [dry-run] 会执行 addProjectV2ItemById(projectId={project_id}, contentId={issue_node_id})"
                    )
                    entry["added"] = "dry-run"
                else:
                    mut = """mutation($projectId: ID!, $contentId: ID!) { addProjectV2ItemById(input:{projectId:$projectId, contentId:$contentId}) { item { id } } }"""
                    ok2, resp2 = graphql_request(
                        session,
                        mut,
                        {"projectId": project_id, "contentId": issue_node_id},
                        retries=2,
                    )
                    if not ok2 or "errors" in (resp2 or {}):
                        print(f"  ❌ add 失败: {resp2}")
                        entry["added"] = False
                        entry["add_response"] = resp2
                    else:
                        print("  ✅ 已添加到目标 project")
                        entry["added"] = True
                        entry["add_response"] = resp2

            # If we added (or existed), we should remove the original org project item
            if dry_run:
                print(f"  [dry-run] 会执行 deleteProjectV2Item(itemId={item_id})")
                entry["deleted"] = "dry-run"
            else:
                # GitHub API now requires both projectId and itemId for deleteProjectV2Item
                from_project_id = act.get("from_project_id")
                if not from_project_id:
                    print("  ❌ 缺少 from_project_id，无法删除原项目中的 item")
                    entry["deleted"] = False
                    entry["delete_response"] = {"error": "missing from_project_id"}
                else:
                    mut_del = """mutation($projectId: ID!, $itemId: ID!) { deleteProjectV2Item(input: {projectId: $projectId, itemId: $itemId}) { deletedItemId } }"""
                    ok3, resp3 = graphql_request(
                        session,
                        mut_del,
                        {"projectId": from_project_id, "itemId": item_id},
                        retries=2,
                    )
                    if not ok3 or "errors" in (resp3 or {}):
                        print(f"  ❌ delete 失败: {resp3}")
                        entry["deleted"] = False
                        entry["delete_response"] = resp3
                    else:
                        print("  ✅ 已从原组织 project 删除 item")
                        entry["deleted"] = True
                        entry["delete_response"] = resp3

            logs.append(entry)
            # gentle rate limiting
            time.sleep(0.5)

        # write log
        log_path = self.output_dir / f"project_move_log_{int(time.time())}.json"
        log_path.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n📝 日志已写入: {log_path}")
        return logs

    def log_sync_operation(self, changes, success, sync_type="all"):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "sync_type": sync_type,
            "changes_count": len(changes),
            "success": success,
            "changes": changes,
        }
        log_file = self.output_dir / f"sync_log_{datetime.now().strftime('%Y%m%d')}.json"
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text(encoding="utf-8"))
            except Exception:
                logs = []
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, ensure_ascii=False, indent=2), encoding="utf-8")

    def save_preview_report(self, changes, report_file):
        content = f"""# Issues同步预览报告

**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**待同步更改总数**: {len(changes)}

## 更改详情

"""
        for i, change in enumerate(changes, 1):
            content += (
                f"### {i}. {change['type'].upper()} 更改\n- **描述**: {change['description']}\n\n"
            )
        content += "\n---\n*此报告由SAGE Issues管理工具生成*\n"
        report_file.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="统一的Issues同步工具")

    # 添加新的统一命令
    parser.add_argument(
        "command",
        nargs="?",
        choices=["sync", "status", "preview", "quick-preview", "timestamp-check"],
        help="操作命令: sync (同步), status (状态), preview (预览), quick-preview (快速预览), timestamp-check (时间戳检查)",
    )
    parser.add_argument(
        "issue_number",
        nargs="?",
        type=int,
        help="要同步的特定issue编号 (与sync命令一起使用)",
    )

    # 预览优化参数
    parser.add_argument("--limit", type=int, default=50, help="限制检查的issues数量 (默认50)")
    parser.add_argument("--recent-only", action="store_true", help="只检查最近7天更新的issues")

    # 项目板同步优化参数
    parser.add_argument("--apply-projects", action="store_true", help="自动应用项目板更改而不预览")
    parser.add_argument(
        "--auto-confirm", action="store_true", help="自动确认所有操作而无需用户输入"
    )

    # 保留旧的命令行选项以保持兼容性
    parser.add_argument("--all", action="store_true", help="同步所有更改")
    parser.add_argument("--labels-only", action="store_true", help="仅同步标签更改")
    parser.add_argument("--status-only", action="store_true", help="仅同步状态更改")
    parser.add_argument("--preview", action="store_true", help="预览待同步更改")
    parser.add_argument(
        "--plan-preview",
        action="store_true",
        help="预览 project_move_plan_*.json 中的计划",
    )
    parser.add_argument(
        "--apply-plan",
        action="store_true",
        help="对 plan 执行远端变更（需 --confirm 才会真正 apply）",
    )
    parser.add_argument(
        "--plan-file",
        type=str,
        help="指定 plan 文件路径（可选，默认取最新的 project_move_plan_*.json）",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="确认执行（与 --apply-plan 一起使用以实际 apply）",
    )
    parser.add_argument("--batch-size", type=int, default=5, help="每批处理数量（默认 5）")
    parser.add_argument(
        "--content-preview",
        action="store_true",
        help="预览本地 content 更改（title/body/labels）",
    )
    parser.add_argument(
        "--apply-content",
        action="store_true",
        help="对本地 content 更改执行远端更新（需 --confirm ）",
    )
    parser.add_argument(
        "--force-content", action="store_true", help="强制覆盖远端（忽略远端更新时间）"
    )
    parser.add_argument(
        "--content-limit",
        type=int,
        default=None,
        help="只处理前 N 个 content 更改（用于试点）",
    )

    args = parser.parse_args()

    syncer = IssuesSyncer()
    success = False

    # 处理新的统一命令
    if args.command == "sync":
        if args.issue_number:
            # 同步单个issue
            success = syncer.sync_one_issue(args.issue_number)
        else:
            # 同步所有更改，传递新参数
            success = syncer.sync_all_changes(
                apply_projects=args.apply_projects, auto_confirm=args.auto_confirm
            )
    elif args.command == "status":
        # 显示同步状态
        syncer.show_sync_status()
        success = True
    elif args.command == "preview":
        # 预览所有更改
        changes = syncer.detect_all_changes()
        if not changes:
            print("✅ 没有检测到需要同步的更改")
        else:
            print(f"📋 检测到 {len(changes)} 个待同步更改:")
            for change in changes[:50]:  # 最多显示50个
                print(f"   - {change['description']}")
            if len(changes) > 50:
                print(f"   ... 以及其他 {len(changes) - 50} 个更改")
        success = True
    elif args.command == "quick-preview":
        # 快速预览（只检查少量issues）
        print(f"🚀 快速预览模式（最多检查 {args.limit} 个issues）")
        changes = syncer.detect_changes_limited(limit=args.limit, recent_only=args.recent_only)
        if not changes:
            print("✅ 没有检测到需要同步的更改")
        else:
            print(f"📋 检测到 {len(changes)} 个待同步更改:")
            for change in changes:
                print(f"   - {change['description']}")
        success = True
    elif args.command == "timestamp-check":
        # 超快速检查（只比较时间戳）
        print(f"⚡ 超快速时间戳检查（最多检查 {args.limit} 个issues）")
        outdated_issues = syncer.check_outdated_timestamps(
            limit=args.limit, recent_only=args.recent_only
        )
        if not outdated_issues:
            print("✅ 所有issues的时间戳都是最新的")
        else:
            print(f"⚠️ 发现 {len(outdated_issues)} 个可能需要同步的issues:")
            for issue_info in outdated_issues:
                print(
                    f"   - Issue #{issue_info['number']}: 本地={issue_info['local_time']}, GitHub={issue_info['github_time']}"
                )
        success = True
    # 处理旧的命令行选项 (保持兼容性)
    elif args.all:
        success = syncer.sync_all_changes(
            apply_projects=args.apply_projects, auto_confirm=args.auto_confirm
        )
    elif args.labels_only:
        success = syncer.sync_label_changes()
    elif args.status_only:
        success = syncer.sync_status_changes()
    elif args.preview:
        success = syncer.preview_changes()
    elif args.plan_preview:
        plan = syncer.load_plan(args.plan_file)
        success = syncer.preview_plan(plan)
    elif args.apply_plan:
        plan = syncer.load_plan(args.plan_file)
        if not plan:
            sys.exit(1)
        dry = not args.confirm
        print(f"🔔 apply_plan dry_run={dry} batch_size={args.batch_size}")
        syncer.apply_plan(plan, dry_run=dry, batch_size=args.batch_size)
        success = True
    elif args.content_preview:
        changes = syncer.detect_content_changes(limit=args.content_limit)
        if not changes:
            print("✅ 未检测到内容差异")
        else:
            p = syncer.save_content_plan(changes)
            print(f"预览 {len(changes)} 项内容差异，计划已保存: {p}")
        success = True
    elif args.apply_content:
        changes = syncer.detect_content_changes(limit=args.content_limit)
        if not changes:
            print("✅ 未检测到内容差异")
            sys.exit(0)
        syncer.save_content_plan(changes)
        dry = not args.confirm
        syncer.apply_content_plan(
            changes, dry_run=dry, force=args.force_content, limit=args.content_limit
        )
        success = True
    else:
        # 如果没有指定任何命令，显示帮助和状态
        print("🔧 统一的Issues同步工具")
        print("\n使用方法:")
        print("  python sync_issues.py sync           # 同步所有更改")
        print("  python sync_issues.py sync 123       # 同步issue #123")
        print("  python sync_issues.py status         # 显示同步状态")
        print("  python sync_issues.py preview        # 预览待同步更改")
        print()
        syncer.show_sync_status()
        success = True

    if success:
        if args.command in ["sync", "status", "preview"] or not args.command:
            pass  # 不显示额外消息
        else:
            print("🎉 操作完成！")
    else:
        print("💥 操作失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
