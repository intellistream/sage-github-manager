#!/usr/bin/env python3
"""
Issues过滤工具
提供灵活的Issues筛选功能
"""

from datetime import datetime
from typing import Any


class IssuesFilter:
    """Issues过滤器"""

    def __init__(self, issues: list[dict[str, Any]]):
        """
        初始化过滤器

        Args:
            issues: Issues列表
        """
        self.issues = issues

    def filter_by_state(self, state: str) -> list[dict[str, Any]]:
        """
        按状态过滤

        Args:
            state: 状态 (open/closed/all)

        Returns:
            过滤后的Issues列表
        """
        if state == "all":
            return self.issues
        return [issue for issue in self.issues if issue.get("state") == state]

    def filter_by_labels(self, labels: list[str]) -> list[dict[str, Any]]:
        """
        按标签过滤 (AND逻辑 - 必须包含所有指定标签)

        Args:
            labels: 标签列表

        Returns:
            过滤后的Issues列表
        """
        if not labels:
            return self.issues

        result = []
        for issue in self.issues:
            issue_labels = [
                label["name"] if isinstance(label, dict) else label
                for label in issue.get("labels", [])
            ]
            if all(label in issue_labels for label in labels):
                result.append(issue)
        return result

    def filter_by_assignee(self, assignee: str | None) -> list[dict[str, Any]]:
        """
        按负责人过滤

        Args:
            assignee: 负责人用户名 (None表示未分配)

        Returns:
            过滤后的Issues列表
        """
        if assignee is None:
            # 未分配
            return [
                issue
                for issue in self.issues
                if not issue.get("assignees") or len(issue.get("assignees", [])) == 0
            ]

        result = []
        for issue in self.issues:
            assignees = issue.get("assignees", [])
            assignee_names = [a["login"] if isinstance(a, dict) else a for a in assignees]
            if assignee in assignee_names:
                result.append(issue)
        return result

    def filter_by_milestone(self, milestone: str | None) -> list[dict[str, Any]]:
        """
        按里程碑过滤

        Args:
            milestone: 里程碑名称 (None表示未设置里程碑)

        Returns:
            过滤后的Issues列表
        """
        if milestone is None:
            # 未设置里程碑
            return [issue for issue in self.issues if not issue.get("milestone")]

        result = []
        for issue in self.issues:
            ms = issue.get("milestone")
            if ms:
                ms_title = ms["title"] if isinstance(ms, dict) else ms
                if ms_title == milestone:
                    result.append(issue)
        return result

    def filter_by_author(self, author: str) -> list[dict[str, Any]]:
        """
        按创建者过滤

        Args:
            author: 创建者用户名

        Returns:
            过滤后的Issues列表
        """
        result = []
        for issue in self.issues:
            user = issue.get("user", {})
            user_login = user.get("login") if isinstance(user, dict) else user
            if user_login == author:
                result.append(issue)
        return result

    def sort_issues(
        self, issues: list[dict[str, Any]], sort_by: str = "created", reverse: bool = True
    ) -> list[dict[str, Any]]:
        """
        排序Issues

        Args:
            issues: Issues列表
            sort_by: 排序字段 (created/updated/comments/number)
            reverse: 是否降序

        Returns:
            排序后的Issues列表
        """
        if sort_by == "created":
            return sorted(
                issues,
                key=lambda x: datetime.fromisoformat(
                    x.get("created_at", "1970-01-01T00:00:00Z").replace("Z", "+00:00")
                ),
                reverse=reverse,
            )
        elif sort_by == "updated":
            return sorted(
                issues,
                key=lambda x: datetime.fromisoformat(
                    x.get("updated_at", "1970-01-01T00:00:00Z").replace("Z", "+00:00")
                ),
                reverse=reverse,
            )
        elif sort_by == "comments":
            return sorted(issues, key=lambda x: x.get("comments", 0), reverse=reverse)
        elif sort_by == "number":
            return sorted(issues, key=lambda x: x.get("number", 0), reverse=reverse)
        else:
            return issues

    def apply_filters(
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
        应用多个过滤条件

        Args:
            state: 状态过滤
            labels: 标签过滤
            assignee: 负责人过滤
            milestone: 里程碑过滤
            author: 创建者过滤
            sort_by: 排序字段
            reverse: 是否降序
            limit: 限制结果数量

        Returns:
            过滤和排序后的Issues列表
        """
        result = self.issues

        # 应用状态过滤
        if state != "all":
            result = [issue for issue in result if issue.get("state") == state]

        # 应用标签过滤
        if labels:
            filtered = []
            for issue in result:
                issue_labels = [
                    label["name"] if isinstance(label, dict) else label
                    for label in issue.get("labels", [])
                ]
                if all(label in issue_labels for label in labels):
                    filtered.append(issue)
            result = filtered

        # 应用负责人过滤
        if assignee is not None:
            if assignee == "":
                # 未分配
                result = [
                    issue
                    for issue in result
                    if not issue.get("assignees") or len(issue.get("assignees", [])) == 0
                ]
            else:
                filtered = []
                for issue in result:
                    assignees = issue.get("assignees", [])
                    assignee_names = [a["login"] if isinstance(a, dict) else a for a in assignees]
                    if assignee in assignee_names:
                        filtered.append(issue)
                result = filtered

        # 应用里程碑过滤
        if milestone is not None:
            if milestone == "":
                # 未设置里程碑
                result = [issue for issue in result if not issue.get("milestone")]
            else:
                filtered = []
                for issue in result:
                    ms = issue.get("milestone")
                    if ms:
                        ms_title = ms["title"] if isinstance(ms, dict) else ms
                        if ms_title == milestone:
                            filtered.append(issue)
                result = filtered

        # 应用创建者过滤
        if author:
            filtered = []
            for issue in result:
                user = issue.get("user", {})
                user_login = user.get("login") if isinstance(user, dict) else user
                if user_login == author:
                    filtered.append(issue)
            result = filtered

        # 排序
        result = self.sort_issues(result, sort_by, reverse)

        # 限制数量
        if limit and limit > 0:
            result = result[:limit]

        return result
