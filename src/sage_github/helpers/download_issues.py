#!/usr/bin/env python3
"""
SAGE Issues下载工具 - 新架构版本
使用统一数据管理器和视图分离架构
"""

import argparse
from datetime import datetime
import json
import sys

import requests

# 导入配置和新的数据管理器
from ..issue_data_manager import IssueDataManager


class IssuesDownloader:
    """Issues下载器 - 新架构版本"""

    def __init__(self, config):
        self.config = config
        self.github = config.get_github_client()

        self.workspace = self.config.workspace_path

        # 使用新的数据管理器
        self.data_manager = IssueDataManager(self.workspace)

        # 加载project映射信息
        self.project_mapping = self.load_project_mapping()
        # 添加issue到project的映射缓存
        self.issue_project_cache = {}
        # 加载团队配置
        self.team_config = self.load_team_config()

    def get_download_status(self):
        """获取下载状态信息"""
        try:
            issues_count = len(self.data_manager.list_all_issues())

            # 获取最后更新时间
            last_update = None
            workspace_path = self.config.workspace_path
            if workspace_path.exists():
                # 查找最新的数据文件
                data_files = list(workspace_path.glob("issue_*.json"))
                if data_files:
                    latest_file = max(data_files, key=lambda f: f.stat().st_mtime)
                    last_update = latest_file.stat().st_mtime

            # 获取可用文件列表
            available_files = []
            if workspace_path.exists():
                available_files = [f.name for f in workspace_path.glob("issue_*.json")]

            return {
                "issues_count": issues_count,
                "last_update": last_update,
                "available_files": available_files,
                "workspace_path": str(workspace_path),
            }
        except Exception:
            return {
                "issues_count": 0,
                "last_update": None,
                "available_files": [],
                "workspace_path": str(self.config.workspace_path),
            }

    def load_team_config(self):
        """加载团队配置"""
        try:
            config_path = self.config.metadata_path / "team_config.py"
            if config_path.exists():
                team_config = {}
                exec(open(config_path).read(), team_config)
                return team_config.get("TEAMS", {})
            else:
                print("⚠️ 团队配置文件不存在，将不进行自动分配")
                return {}
        except Exception as e:
            print(f"⚠️ 加载团队配置失败: {e}")
            return {}

    def load_project_mapping(self):
        """加载project映射信息"""
        try:
            boards_file = self.config.metadata_path / "boards_metadata.json"
            if boards_file.exists():
                with open(boards_file, encoding="utf-8") as f:
                    data = json.load(f)
                    # 从boards_metadata.json读取实际的team_to_project映射
                    team_to_project = data.get("team_to_project", {})
                    # 反转映射：project_number -> team_name
                    return {
                        int(project_num): team_name
                        for team_name, project_num in team_to_project.items()
                    }
            else:
                # 如果文件不存在，返回默认映射
                return {
                    6: "intellistream",  # IntelliStream总体项目
                    12: "sage-kernel",
                    13: "sage-middleware",
                    14: "sage-apps",
                }
        except Exception as e:
            print(f"⚠️ 加载project映射失败: {e}")
            # 返回默认映射作为备选
            return {
                6: "intellistream",  # IntelliStream总体项目
                12: "sage-kernel",
                13: "sage-middleware",
                14: "sage-apps",
            }

    def bulk_get_project_info(self, issue_numbers: list):
        """批量获取多个issues的project归属信息，提高性能"""
        if not issue_numbers:
            return

        print(f"📊 批量获取 {len(issue_numbers)} 个issues的项目信息...")

        try:
            # 首先获取所有项目基本信息
            projects_query = """
            {
              organization(login: "intellistream") {
                projectsV2(first: 20) {
                  nodes {
                    number
                    title
                  }
                }
              }
            }
            """

            response = requests.post(
                "https://api.github.com/graphql",
                headers=self.github,
                json={"query": projects_query},
                timeout=30,
            )

            if response.status_code != 200:
                print(f"GraphQL API错误: {response.status_code}")
                return

            data = response.json()

            if "errors" in data:
                print(f"GraphQL查询错误: {data['errors']}")
                return

            projects = (
                data.get("data", {}).get("organization", {}).get("projectsV2", {}).get("nodes", [])
            )
            if not projects:
                print("未找到projects数据")
                return

            # 构建issue到project的映射
            found_count = 0

            # 对每个项目，分页获取所有items
            for project in projects:
                project_num = project["number"]
                project_title = project["title"]
                team_name = self.project_mapping.get(project_num, f"unknown-{project_num}")

                # 分页获取项目中的所有items
                has_next_page = True
                after_cursor = None

                while has_next_page:
                    # 构建分页查询，动态获取直到没有更多数据
                    items_query = f"""
                    {{
                      organization(login: "intellistream") {{
                        projectV2(number: {project_num}) {{
                          items(first: 100{f', after: "{after_cursor}"' if after_cursor else ""}) {{
                            pageInfo {{
                              hasNextPage
                              endCursor
                            }}
                            nodes {{
                              content {{
                                ... on Issue {{
                                  number
                                  repository {{
                                    name
                                  }}
                                }}
                              }}
                            }}
                          }}
                        }}
                      }}
                    }}
                    """

                    items_response = requests.post(
                        "https://api.github.com/graphql",
                        headers=self.github,
                        json={"query": items_query},
                        timeout=30,
                    )

                    if items_response.status_code != 200:
                        print(f"获取项目 {project_num} items失败: {items_response.status_code}")
                        break

                    items_data = items_response.json()

                    if "errors" in items_data:
                        print(f"获取项目 {project_num} items错误: {items_data['errors']}")
                        break

                    project_data = (
                        items_data.get("data", {}).get("organization", {}).get("projectV2", {})
                    )
                    if not project_data:
                        break

                    items_info = project_data.get("items", {})
                    items = items_info.get("nodes", [])
                    page_info = items_info.get("pageInfo", {})

                    # 处理当前页的items
                    for item in items:
                        content = item.get("content")
                        if not content:
                            continue

                        issue_number = content.get("number")
                        if (
                            issue_number in issue_numbers
                            and content.get("repository", {}).get("name")
                            == self.config.repository_name
                        ):
                            if issue_number not in self.issue_project_cache:
                                self.issue_project_cache[issue_number] = []

                            self.issue_project_cache[issue_number].append(
                                {
                                    "number": project_num,
                                    "title": project_title,
                                    "team": team_name,
                                }
                            )
                            found_count += 1

                    # 检查是否有下一页
                    has_next_page = page_info.get("hasNextPage", False)
                    after_cursor = page_info.get("endCursor")

            print(f"✅ 成功获取 {found_count} 个issues的项目信息")

        except Exception as e:
            print(f"⚠️ 批量获取项目信息失败: {e}")
            import traceback

            traceback.print_exc()

    def get_issue_project_info(self, issue_number: int):
        """获取issue的project归属信息（优先从缓存获取）"""
        # 首先检查缓存
        if issue_number in self.issue_project_cache:
            return self.issue_project_cache[issue_number]

        # 如果缓存中没有，返回空列表（避免单独的API请求）
        return []

    def get_issue_comments(self, issue_number: int):
        """获取issue评论"""
        try:
            base = (
                f"https://api.github.com/repos/{self.config.GITHUB_OWNER}/{self.config.GITHUB_REPO}"
            )
            url = f"{base}/issues/{issue_number}/comments"
            resp = requests.get(url, headers=self.github)
            resp.raise_for_status()

            comments = resp.json()
            # 简化评论数据
            simplified_comments = []
            for comment in comments:
                simplified_comments.append(
                    {
                        "id": comment.get("id"),
                        "user": comment.get("user", {}).get("login"),
                        "created_at": comment.get("created_at"),
                        "updated_at": comment.get("updated_at"),
                        "body": comment.get("body", ""),
                    }
                )

            return simplified_comments
        except Exception as e:
            print(f"⚠️ 获取 Issue #{issue_number} 评论失败: {e}")
            return []

    def auto_assign_project_and_assignee(self, issue: dict, project_info: list):
        """自动分配project和assignee（如果缺失）"""
        if not self.team_config:
            return issue, project_info  # 如果没有团队配置，直接返回原issue

        # 获取创建者信息
        creator = (
            issue.get("user", {}).get("login")
            if isinstance(issue.get("user"), dict)
            else issue.get("user")
        )
        if not creator:
            return issue, project_info

        # 检查是否已有project分配
        has_project = project_info and len(project_info) > 0

        # 检查是否已有assignee
        has_assignee = (
            issue.get("assignees") and len(issue.get("assignees", [])) > 0
        ) or issue.get("assignee")

        # 如果已有project和assignee，不需要自动分配
        if has_project and has_assignee:
            return issue, project_info

        # 确定创建者所属的团队
        creator_team = None
        for team_name, team_info in self.team_config.items():
            team_members = [member["username"] for member in team_info.get("members", [])]
            if creator in team_members:
                creator_team = team_name
                break

        if not creator_team:
            # 创建者不在任何已知团队中，默认分配到intellistream
            creator_team = "intellistream"

        updated_project_info = project_info

        # 如果没有project分配，尝试自动分配
        if not has_project:
            # 根据团队名称确定project
            project_assignments = {
                "intellistream": {
                    "number": 6,
                    "title": "IntelliStream Project",
                    "team": "intellistream",
                },
                "sage-kernel": {
                    "number": 12,
                    "title": "SAGE Kernel Development",
                    "team": "sage-kernel",
                },
                "sage-middleware": {
                    "number": 13,
                    "title": "SAGE Middleware",
                    "team": "sage-middleware",
                },
                "sage-apps": {
                    "number": 14,
                    "title": "SAGE Applications",
                    "team": "sage-apps",
                },
            }

            if creator_team in project_assignments:
                updated_project_info = [project_assignments[creator_team]]
                print(
                    f"🎯 Issue #{issue['number']} 自动分配到project: {creator_team} (基于创建者 {creator})"
                )

        # 如果没有assignee，分配给创建者
        if not has_assignee:
            # 确保创建者在团队中
            if creator_team and creator_team in self.team_config:
                team_members = [
                    member["username"]
                    for member in self.team_config[creator_team].get("members", [])
                ]
                if creator in team_members:
                    # 修改issue的assignee信息
                    issue["assignees"] = [{"login": creator}]
                    issue["assignee"] = {"login": creator}
                    print(f"👤 Issue #{issue['number']} 自动分配给创建者: {creator}")

        return issue, updated_project_info

    def save_issue(self, issue: dict, skip_comments=False):
        """保存单个Issue"""
        try:
            # 获取project信息
            project_info = self.get_issue_project_info(issue["number"])

            # 添加project信息到issue数据中（不进行自动分配）
            issue["projects"] = project_info

            # 获取评论（可选）
            comments = []
            if not skip_comments:
                comments = self.get_issue_comments(issue["number"])

            # 使用数据管理器保存
            success = self.data_manager.save_issue(issue, comments)

            if success:
                print(f"✅ Issue #{issue['number']} 保存成功")
            else:
                print(f"❌ Issue #{issue['number']} 保存失败")

            return success

        except Exception as e:
            print(f"❌ 保存Issue #{issue['number']} 失败: {e}")
            return False

    def download_issues(self, state="all", skip_comments=False) -> bool:
        """下载Issues

        Args:
            state: Issues状态 ("open", "closed", "all")
            skip_comments: 是否跳过评论获取以加快速度

        Returns:
            bool: 下载是否成功
        """
        print(f"🚀 开始下载 {state} 状态的Issues...")
        if skip_comments:
            print("⚡ 快速模式：跳过评论下载")

        try:
            # 获取Issues - 直接调用GitHub API
            base_url = f"https://api.github.com/repos/{self.config.GITHUB_OWNER}/{self.config.GITHUB_REPO}/issues"
            params = {"state": state, "per_page": 100}

            issues = []
            page = 1
            next_url = None

            while True:
                # 使用next_url如果存在，否则使用基础URL和参数
                if next_url:
                    response = requests.get(next_url, headers=self.github)
                else:
                    response = requests.get(base_url, headers=self.github, params=params)

                response.raise_for_status()

                page_issues = response.json()
                if not page_issues:
                    break

                issues.extend(page_issues)
                print(f"📥 已获取第{page}页，共{len(page_issues)}个Issues (总数: {len(issues)})")
                page += 1

                # 解析Link header获取下一页URL
                link_header = response.headers.get("Link", "")
                next_url = None

                if link_header:
                    # Link header格式: <url>; rel="next", <url>; rel="last"
                    links = link_header.split(", ")
                    for link in links:
                        if 'rel="next"' in link:
                            # 提取URL: <https://api.github.com/...> -> https://api.github.com/...
                            next_url = link.split("; ")[0].strip("<>")
                            break

                # 如果没有下一页链接，停止
                if not next_url:
                    break

                # 避免无限循环（安全措施）
                if page > 50:
                    print("⚠️ 达到最大页数限制，停止下载")
                    break

            if not issues:
                print("📭 没有找到符合条件的Issues")
                return True

            print(f"📥 共找到 {len(issues)} 个Issues，开始下载...")

            # 批量获取所有issues的项目信息（优化性能）
            issue_numbers = [issue["number"] for issue in issues]
            self.bulk_get_project_info(issue_numbers)

            # 保存Issues
            saved_count = 0
            for issue in issues:
                try:
                    if self.save_issue(issue, skip_comments=skip_comments):
                        saved_count += 1

                    if saved_count % 10 == 0:
                        print(f"✅ 已保存 {saved_count}/{len(issues)} 个Issues")
                except Exception as e:
                    print(f"❌ 保存Issue #{issue['number']} 失败: {e}")

            print(f"📊 数据下载完成！成功保存 {saved_count}/{len(issues)} 个Issues到数据源")

            # 生成所有视图
            print("🔄 生成视图文件...")
            view_results = self.data_manager.generate_all_views()
            print(f"📊 视图生成完成: {view_results}")

            # 生成下载报告
            self.generate_download_report(issues, saved_count, state, view_results)

            print("🎉 下载和视图生成完成！")
            print(f"📁 数据源位置: {self.data_manager.data_dir}")
            print(f"📁 Markdown视图: {self.data_manager.markdown_dir}")
            print(f"📁 元数据视图: {self.data_manager.metadata_dir}")

            return True

        except Exception as e:
            print(f"💥 下载失败: {e}")
            import traceback

            traceback.print_exc()
            return False

    def generate_download_report(
        self, issues: list, saved_count: int, state: str, view_results: dict
    ):
        """生成下载报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.config.output_path / f"download_report_v2_{state}_{timestamp}.md"

        # 统计信息
        total_issues = len(issues)
        open_count = len([i for i in issues if i["state"] == "open"])
        closed_count = len([i for i in issues if i["state"] == "closed"])

        # 标签统计
        label_stats: dict[str, int] = {}
        milestone_stats: dict[str, int] = {}
        team_stats: dict[str, int] = {}

        for issue in issues:
            # 标签统计
            for label in issue.get("labels", []):
                label_name = label["name"] if isinstance(label, dict) else label
                label_stats[label_name] = label_stats.get(label_name, 0) + 1

            # Milestone统计
            milestone = issue.get("milestone")
            if milestone:
                milestone_title = milestone.get("title", "unknown")
                milestone_stats[milestone_title] = milestone_stats.get(milestone_title, 0) + 1

            # 团队统计
            projects = issue.get("projects", [])
            for project in projects:
                team = project.get("team", "unknown")
                team_stats[team] = team_stats.get(team, 0) + 1

        # 生成报告内容
        report_content = f"""# Issues下载报告 (新架构)

**下载时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**请求状态**: {state}
**下载结果**: {saved_count}/{total_issues} 成功

## 统计信息

- 开放Issues: {open_count}
- 已关闭Issues: {closed_count}
- 总计: {total_issues}

## 新架构优势

✅ **单一数据源**: 所有数据存储在 `data/` 目录的JSON文件中
✅ **视图分离**: 自动生成markdown和元数据视图
✅ **完整信息**: 包含milestone、reactions、comments等完整信息
✅ **向后兼容**: 保持原有的目录结构和API

## 视图生成结果

- Markdown视图: {view_results.get("markdown_success", 0)}/{view_results.get("total", 0)} 成功
- 元数据视图: {view_results.get("metadata_success", 0)}/{view_results.get("total", 0)} 成功
- 失败: {view_results.get("failed", 0)}

## 按团队分布

"""

        # 添加团队统计
        for team, count in sorted(team_stats.items(), key=lambda x: x[1], reverse=True):
            report_content += f"- {team}: {count}\n"

        report_content += "\n## 按Milestone分布\n\n"

        # 添加milestone统计
        for milestone, count in sorted(milestone_stats.items(), key=lambda x: x[1], reverse=True):
            report_content += f"- {milestone}: {count}\n"

        report_content += "\n## 标签分布\n\n"

        # 添加标签统计（显示前20个）
        for label, count in sorted(label_stats.items(), key=lambda x: x[1], reverse=True)[:20]:
            report_content += f"- {label}: {count}\n"

        report_content += f"""

## 存储架构

### 数据源 (单一真实来源)
`{self.data_manager.data_dir}/`
- issue_XXX.json: 完整的issue数据，包含元数据、内容和追踪信息

### 视图文件 (自动生成)
`{self.data_manager.markdown_dir}/`: 人类可读的markdown文件
`{self.data_manager.metadata_dir}/`: 向后兼容的元数据JSON文件
`{self.data_manager.summaries_dir}/`: 汇总统计信息

### 向后兼容
原有的 `issues/` 和 `metadata/` 目录现在是指向视图目录的符号链接

## 文件命名规则

数据源: `issue_{{编号}}.json`
Markdown视图: `{{状态}}_{{编号}}_{{标题}}.md`
元数据视图: `issue_{{编号}}_metadata.json`
"""

        # 保存报告
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"📊 下载报告已保存: {report_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="下载GitHub Issues (新架构)")
    parser.add_argument(
        "--state",
        choices=["open", "closed", "all"],
        default="all",
        help="要下载的Issues状态 (default: all)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="显示详细输出")
    parser.add_argument("--migrate-only", action="store_true", help="仅执行数据迁移，不下载新数据")
    parser.add_argument("--skip-comments", action="store_true", help="跳过评论下载以加快速度")

    args = parser.parse_args()

    # 创建配置实例
    from ..config import IssuesConfig

    config = IssuesConfig()

    if args.verbose:
        print("🔧 配置信息:")
        print(f"   仓库: {config.GITHUB_OWNER}/{config.GITHUB_REPO}")
        print(f"   工作目录: {config.workspace_path}")
        print(f"   Token状态: {'✅' if config.github_token else '❌'}")
        print()

    downloader = IssuesDownloader(config)

    if args.migrate_only:
        print("🔄 执行数据迁移...")
        migrate_results = downloader.data_manager.migrate_from_old_format()
        print(f"📊 迁移结果: {migrate_results}")

        print("🔄 生成所有视图...")
        view_results = downloader.data_manager.generate_all_views()
        print(f"📊 视图生成结果: {view_results}")

        print("✅ 迁移完成！")
        sys.exit(0)

    # 执行下载
    success = downloader.download_issues(state=args.state, skip_comments=args.skip_comments)

    if success:
        print("\n🎉 下载完成！")
        print("\n💡 新架构特点:")
        print("   - 所有数据存储在单一JSON文件中")
        print("   - 包含完整的milestone、reactions等信息")
        print("   - 自动生成markdown和元数据视图")
        print("   - 保持向后兼容性")
        sys.exit(0)
    else:
        print("\n💥 下载失败！")
        sys.exit(1)


# 向后兼容性别名
IssuesDownloader = IssuesDownloader


if __name__ == "__main__":
    main()
