#!/usr/bin/env python3
"""
Issues导出工具
支持导出为CSV、Markdown、JSON格式
"""

import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Any


class IssuesExporter:
    """Issues导出器"""

    def __init__(self, issues: list[dict[str, Any]]):
        """
        初始化导出器

        Args:
            issues: Issues列表
        """
        self.issues = issues

    def export_to_csv(self, output_path: Path) -> bool:
        """
        导出为CSV格式

        Args:
            output_path: 输出文件路径

        Returns:
            是否成功
        """
        if not self.issues:
            print("⚠️ 没有Issues需要导出")
            return False

        try:
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)

                # 写入表头
                writer.writerow(
                    [
                        "Number",
                        "Title",
                        "State",
                        "Author",
                        "Labels",
                        "Assignees",
                        "Milestone",
                        "Created",
                        "Updated",
                        "Closed",
                        "Comments",
                        "URL",
                    ]
                )

                # 写入数据
                for issue in self.issues:
                    # 提取数据
                    number = issue.get("number", "")
                    title = issue.get("title", "")
                    state = issue.get("state", "")

                    # 作者
                    user = issue.get("user", {})
                    author = user.get("login", "") if isinstance(user, dict) else str(user)

                    # 标签
                    labels = issue.get("labels", [])
                    label_names = [
                        label["name"] if isinstance(label, dict) else label for label in labels
                    ]
                    labels_str = ", ".join(label_names)

                    # 负责人
                    assignees = issue.get("assignees", [])
                    assignee_names = [a["login"] if isinstance(a, dict) else a for a in assignees]
                    assignees_str = ", ".join(assignee_names)

                    # 里程碑
                    milestone = issue.get("milestone", {})
                    milestone_title = (
                        milestone.get("title", "")
                        if isinstance(milestone, dict)
                        else str(milestone)
                        if milestone
                        else ""
                    )

                    # 时间
                    created_at = issue.get("created_at", "")
                    updated_at = issue.get("updated_at", "")
                    closed_at = issue.get("closed_at", "")

                    # 评论数
                    comments = issue.get("comments", 0)

                    # URL
                    url = issue.get("html_url", "")

                    writer.writerow(
                        [
                            number,
                            title,
                            state,
                            author,
                            labels_str,
                            assignees_str,
                            milestone_title,
                            created_at,
                            updated_at,
                            closed_at,
                            comments,
                            url,
                        ]
                    )

            return True
        except Exception as e:
            print(f"❌ CSV导出失败: {e}")
            return False

    def export_to_json(self, output_path: Path, pretty: bool = True) -> bool:
        """
        导出为JSON格式

        Args:
            output_path: 输出文件路径
            pretty: 是否格式化输出

        Returns:
            是否成功
        """
        if not self.issues:
            print("⚠️ 没有Issues需要导出")
            return False

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                if pretty:
                    json.dump(self.issues, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(self.issues, f, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"❌ JSON导出失败: {e}")
            return False

    def export_to_markdown(self, output_path: Path, template: str = "default") -> bool:
        """
        导出为Markdown格式

        Args:
            output_path: 输出文件路径
            template: 模板类型 (default/roadmap/report)

        Returns:
            是否成功
        """
        if not self.issues:
            print("⚠️ 没有Issues需要导出")
            return False

        try:
            if template == "roadmap":
                content = self._generate_roadmap_markdown()
            elif template == "report":
                content = self._generate_report_markdown()
            else:
                content = self._generate_default_markdown()

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"❌ Markdown导出失败: {e}")
            return False

    def _generate_default_markdown(self) -> str:
        """生成默认Markdown格式"""
        lines = []
        lines.append("# Issues Export Report")
        lines.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\n**Total Issues**: {len(self.issues)}")
        lines.append("\n---\n")

        for issue in self.issues:
            number = issue.get("number", "N/A")
            title = issue.get("title", "Untitled")
            state = issue.get("state", "unknown")
            url = issue.get("html_url", "")

            lines.append(f"\n## #{number} - {title}")
            lines.append(f"\n**State**: {state}")

            # 作者
            user = issue.get("user", {})
            author = user.get("login", "") if isinstance(user, dict) else str(user)
            if author:
                lines.append(f"**Author**: @{author}")

            # 标签
            labels = issue.get("labels", [])
            if labels:
                label_names = [
                    label["name"] if isinstance(label, dict) else label for label in labels
                ]
                lines.append(f"**Labels**: {', '.join(label_names)}")

            # 负责人
            assignees = issue.get("assignees", [])
            if assignees:
                assignee_names = [a["login"] if isinstance(a, dict) else a for a in assignees]
                lines.append(f"**Assignees**: {', '.join(['@' + a for a in assignee_names])}")

            # 里程碑
            milestone = issue.get("milestone", {})
            if milestone:
                milestone_title = (
                    milestone.get("title", "") if isinstance(milestone, dict) else str(milestone)
                )
                if milestone_title:
                    lines.append(f"**Milestone**: {milestone_title}")

            # 正文摘要
            body = issue.get("body", "")
            if body:
                summary = body[:200].replace("\n", " ")
                if len(body) > 200:
                    summary += "..."
                lines.append(f"\n{summary}")

            if url:
                lines.append(f"\n[View on GitHub]({url})")

            lines.append("\n---\n")

        return "\n".join(lines)

    def _generate_roadmap_markdown(self) -> str:
        """生成路线图格式的Markdown"""
        lines = []
        lines.append("# Project Roadmap")
        lines.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\n**Total Items**: {len(self.issues)}")
        lines.append("\n---\n")

        # 按里程碑分组
        by_milestone: dict[str, list] = {}
        no_milestone = []

        for issue in self.issues:
            milestone = issue.get("milestone", {})
            if milestone and isinstance(milestone, dict):
                milestone_title = milestone.get("title", "No Milestone")
            elif milestone:
                milestone_title = str(milestone)
            else:
                milestone_title = None

            if milestone_title:
                if milestone_title not in by_milestone:
                    by_milestone[milestone_title] = []
                by_milestone[milestone_title].append(issue)
            else:
                no_milestone.append(issue)

        # 输出各里程碑
        for milestone_title, milestone_issues in sorted(by_milestone.items()):
            lines.append(f"\n## {milestone_title}")
            lines.append(f"\n**Items**: {len(milestone_issues)}\n")

            for issue in milestone_issues:
                number = issue.get("number", "")
                title = issue.get("title", "")
                state = issue.get("state", "")
                state_emoji = "✅" if state == "closed" else "🔵"

                # 标签
                labels = issue.get("labels", [])
                label_names = [
                    label["name"] if isinstance(label, dict) else label for label in labels
                ]
                labels_str = f" `{', '.join(label_names)}`" if label_names else ""

                lines.append(f"- {state_emoji} #{number} - {title}{labels_str}")

        # 无里程碑的Issues
        if no_milestone:
            lines.append("\n## Backlog (No Milestone)")
            lines.append(f"\n**Items**: {len(no_milestone)}\n")

            for issue in no_milestone:
                number = issue.get("number", "")
                title = issue.get("title", "")
                state = issue.get("state", "")
                state_emoji = "✅" if state == "closed" else "🔵"
                lines.append(f"- {state_emoji} #{number} - {title}")

        return "\n".join(lines)

    def _generate_report_markdown(self) -> str:
        """生成报告格式的Markdown"""
        lines = []
        lines.append("# Issues Report")
        lines.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"\n**Total Issues**: {len(self.issues)}")

        # 统计信息
        open_count = sum(1 for i in self.issues if i.get("state") == "open")
        closed_count = sum(1 for i in self.issues if i.get("state") == "closed")

        lines.append("\n## Summary\n")
        lines.append(f"- **Open Issues**: {open_count}")
        lines.append(f"- **Closed Issues**: {closed_count}")

        # 按状态分组
        lines.append("\n---\n")
        lines.append("\n## Open Issues\n")

        for issue in self.issues:
            if issue.get("state") != "open":
                continue

            number = issue.get("number", "")
            title = issue.get("title", "")
            url = issue.get("html_url", "")

            # 标签
            labels = issue.get("labels", [])
            label_names = [label["name"] if isinstance(label, dict) else label for label in labels]
            labels_str = f" `{', '.join(label_names)}`" if label_names else ""

            lines.append(f"- [#{number}]({url}) - {title}{labels_str}")

        return "\n".join(lines)
