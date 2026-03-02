"""批量操作功能

支持批量关闭、标签管理、分配和里程碑设置。
"""

from typing import Any

import requests
from rich.console import Console
from rich.prompt import Confirm
from rich.table import Table

console = Console()


class BatchOperations:
    """批量操作管理器

    提供批量关闭、标签管理、分配和里程碑设置功能。
    所有操作支持 dry-run 模式和确认提示。
    """

    def __init__(self, owner: str, repo: str, token: str | None):
        """初始化批量操作管理器

        Args:
            owner: GitHub仓库所有者
            repo: GitHub仓库名称
            token: GitHub访问令牌
        """
        self.owner = owner
        self.repo = repo
        self.token = token
        self.headers: dict[str, str] = {
            "Accept": "application/vnd.github.v3+json",
        }
        if token:
            self.headers["Authorization"] = f"token {token}"
        self.base_url = f"https://api.github.com/repos/{owner}/{repo}"

    def _update_issue(self, issue_number: int, **kwargs) -> bool:
        """更新Issue

        Args:
            issue_number: Issue编号
            **kwargs: 要更新的字段

        Returns:
            是否成功
        """
        url = f"{self.base_url}/issues/{issue_number}"
        response = requests.patch(url, headers=self.headers, json=kwargs, timeout=30)
        return response.status_code == 200

    def _get_milestones(self) -> list[dict[str, Any]]:
        """获取里程碑列表

        Returns:
            里程碑列表
        """
        url = f"{self.base_url}/milestones"
        response = requests.get(url, headers=self.headers, params={"state": "all"}, timeout=30)
        if response.status_code == 200:
            return response.json()  # type: ignore[no-any-return]
        return []

    def close_issues(
        self,
        issues: list[dict[str, Any]],
        dry_run: bool = False,
        auto_confirm: bool = False,
    ) -> dict[str, Any]:
        """批量关闭 Issues

        Args:
            issues: 要关闭的 Issues 列表
            dry_run: 是否为预览模式（不实际执行）
            auto_confirm: 是否自动确认（跳过用户确认）

        Returns:
            操作结果统计信息
        """
        if not issues:
            console.print("⚠️  [yellow]没有匹配的 Issues[/yellow]")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}

        # 显示预览表格
        self._show_preview_table(issues, "Close")

        # Dry-run 模式直接返回
        if dry_run:
            console.print(f"\n🔍 [yellow]预览模式: 将关闭 {len(issues)} 个 Issues[/yellow]")
            return {"total": len(issues), "success": 0, "failed": 0, "skipped": len(issues)}

        # 确认操作
        if not auto_confirm:
            if not Confirm.ask(f"\n❓ 确认关闭 {len(issues)} 个 Issues?"):
                console.print("❌ [red]操作已取消[/red]")
                return {"total": len(issues), "success": 0, "failed": 0, "skipped": len(issues)}

        # 执行关闭操作
        success_count = 0
        failed_count = 0

        from rich.progress import Progress, SpinnerColumn, TextColumn

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("关闭 Issues...", total=len(issues))

            for issue in issues:
                try:
                    self._update_issue(issue["number"], state="closed")
                    success_count += 1
                except Exception as e:
                    console.print(f"❌ [red]关闭 #{issue['number']} 失败: {e}[/red]")
                    failed_count += 1
                progress.advance(task)

        # 显示结果
        console.print(f"\n✅ [green]成功关闭 {success_count} 个 Issues[/green]")
        if failed_count > 0:
            console.print(f"❌ [red]失败 {failed_count} 个[/red]")

        return {
            "total": len(issues),
            "success": success_count,
            "failed": failed_count,
            "skipped": 0,
        }

    def add_labels(
        self,
        issues: list[dict[str, Any]],
        labels: list[str],
        dry_run: bool = False,
        auto_confirm: bool = False,
    ) -> dict[str, Any]:
        """批量添加标签

        Args:
            issues: 要添加标签的 Issues 列表
            labels: 要添加的标签列表
            dry_run: 是否为预览模式
            auto_confirm: 是否自动确认

        Returns:
            操作结果统计信息
        """
        if not issues:
            console.print("⚠️  [yellow]没有匹配的 Issues[/yellow]")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}

        if not labels:
            console.print("⚠️  [yellow]请指定要添加的标签[/yellow]")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}

        # 显示预览
        self._show_preview_table(issues, f"Add labels: {', '.join(labels)}")

        if dry_run:
            console.print(
                f"\n🔍 [yellow]预览模式: 将为 {len(issues)} 个 Issues 添加标签 {labels}[/yellow]"
            )
            return {"total": len(issues), "success": 0, "failed": 0, "skipped": len(issues)}

        if not auto_confirm:
            if not Confirm.ask(f"\n❓ 确认为 {len(issues)} 个 Issues 添加标签 {labels}?"):
                console.print("❌ [red]操作已取消[/red]")
                return {"total": len(issues), "success": 0, "failed": 0, "skipped": len(issues)}

        # 执行添加标签
        success_count = 0
        failed_count = 0

        from rich.progress import Progress, SpinnerColumn, TextColumn

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("添加标签...", total=len(issues))

            for issue in issues:
                try:
                    # 获取现有标签
                    existing_labels = [label["name"] for label in issue.get("labels", [])]
                    # 合并标签（去重）
                    new_labels = list(set(existing_labels + labels))
                    self._update_issue(issue["number"], labels=new_labels)
                    success_count += 1
                except Exception as e:
                    console.print(f"❌ [red]为 #{issue['number']} 添加标签失败: {e}[/red]")
                    failed_count += 1
                progress.advance(task)

        console.print(f"\n✅ [green]成功为 {success_count} 个 Issues 添加标签[/green]")
        if failed_count > 0:
            console.print(f"❌ [red]失败 {failed_count} 个[/red]")

        return {
            "total": len(issues),
            "success": success_count,
            "failed": failed_count,
            "skipped": 0,
        }

    def remove_labels(
        self,
        issues: list[dict[str, Any]],
        labels: list[str],
        dry_run: bool = False,
        auto_confirm: bool = False,
    ) -> dict[str, Any]:
        """批量移除标签

        Args:
            issues: 要移除标签的 Issues 列表
            labels: 要移除的标签列表
            dry_run: 是否为预览模式
            auto_confirm: 是否自动确认

        Returns:
            操作结果统计信息
        """
        if not issues:
            console.print("⚠️  [yellow]没有匹配的 Issues[/yellow]")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}

        if not labels:
            console.print("⚠️  [yellow]请指定要移除的标签[/yellow]")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}

        # 显示预览
        self._show_preview_table(issues, f"Remove labels: {', '.join(labels)}")

        if dry_run:
            console.print(
                f"\n🔍 [yellow]预览模式: 将从 {len(issues)} 个 Issues 移除标签 {labels}[/yellow]"
            )
            return {"total": len(issues), "success": 0, "failed": 0, "skipped": len(issues)}

        if not auto_confirm:
            if not Confirm.ask(f"\n❓ 确认从 {len(issues)} 个 Issues 移除标签 {labels}?"):
                console.print("❌ [red]操作已取消[/red]")
                return {"total": len(issues), "success": 0, "failed": 0, "skipped": len(issues)}

        # 执行移除标签
        success_count = 0
        failed_count = 0

        from rich.progress import Progress, SpinnerColumn, TextColumn

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("移除标签...", total=len(issues))

            for issue in issues:
                try:
                    # 获取现有标签并移除指定标签
                    existing_labels = [label["name"] for label in issue.get("labels", [])]
                    new_labels = [label for label in existing_labels if label not in labels]
                    self._update_issue(issue["number"], labels=new_labels)
                    success_count += 1
                except Exception as e:
                    console.print(f"❌ [red]从 #{issue['number']} 移除标签失败: {e}[/red]")
                    failed_count += 1
                progress.advance(task)

        console.print(f"\n✅ [green]成功从 {success_count} 个 Issues 移除标签[/green]")
        if failed_count > 0:
            console.print(f"❌ [red]失败 {failed_count} 个[/red]")

        return {
            "total": len(issues),
            "success": success_count,
            "failed": failed_count,
            "skipped": 0,
        }

    def assign_issues(
        self,
        issues: list[dict[str, Any]],
        assignees: list[str],
        dry_run: bool = False,
        auto_confirm: bool = False,
    ) -> dict[str, Any]:
        """批量分配 Issues

        Args:
            issues: 要分配的 Issues 列表
            assignees: 负责人列表
            dry_run: 是否为预览模式
            auto_confirm: 是否自动确认

        Returns:
            操作结果统计信息
        """
        if not issues:
            console.print("⚠️  [yellow]没有匹配的 Issues[/yellow]")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}

        if not assignees:
            console.print("⚠️  [yellow]请指定负责人[/yellow]")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}

        # 显示预览
        self._show_preview_table(issues, f"Assign to: {', '.join(assignees)}")

        if dry_run:
            console.print(
                f"\n🔍 [yellow]预览模式: 将分配 {len(issues)} 个 Issues 给 {assignees}[/yellow]"
            )
            return {"total": len(issues), "success": 0, "failed": 0, "skipped": len(issues)}

        if not auto_confirm:
            if not Confirm.ask(f"\n❓ 确认分配 {len(issues)} 个 Issues 给 {assignees}?"):
                console.print("❌ [red]操作已取消[/red]")
                return {"total": len(issues), "success": 0, "failed": 0, "skipped": len(issues)}

        # 执行分配
        success_count = 0
        failed_count = 0

        from rich.progress import Progress, SpinnerColumn, TextColumn

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("分配 Issues...", total=len(issues))

            for issue in issues:
                try:
                    self._update_issue(issue["number"], assignees=assignees)
                    success_count += 1
                except Exception as e:
                    console.print(f"❌ [red]分配 #{issue['number']} 失败: {e}[/red]")
                    failed_count += 1
                progress.advance(task)

        console.print(f"\n✅ [green]成功分配 {success_count} 个 Issues[/green]")
        if failed_count > 0:
            console.print(f"❌ [red]失败 {failed_count} 个[/red]")

        return {
            "total": len(issues),
            "success": success_count,
            "failed": failed_count,
            "skipped": 0,
        }

    def set_milestone(
        self,
        issues: list[dict[str, Any]],
        milestone: str,
        dry_run: bool = False,
        auto_confirm: bool = False,
    ) -> dict[str, Any]:
        """批量设置里程碑

        Args:
            issues: 要设置里程碑的 Issues 列表
            milestone: 里程碑名称
            dry_run: 是否为预览模式
            auto_confirm: 是否自动确认

        Returns:
            操作结果统计信息
        """
        if not issues:
            console.print("⚠️  [yellow]没有匹配的 Issues[/yellow]")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}

        if not milestone:
            console.print("⚠️  [yellow]请指定里程碑[/yellow]")
            return {"total": 0, "success": 0, "failed": 0, "skipped": 0}

        # 显示预览
        self._show_preview_table(issues, f"Set milestone: {milestone}")

        if dry_run:
            console.print(
                f"\n🔍 [yellow]预览模式: 将为 {len(issues)} 个 Issues 设置里程碑 '{milestone}'[/yellow]"
            )
            return {"total": len(issues), "success": 0, "failed": 0, "skipped": len(issues)}

        if not auto_confirm:
            if not Confirm.ask(f"\n❓ 确认为 {len(issues)} 个 Issues 设置里程碑 '{milestone}'?"):
                console.print("❌ [red]操作已取消[/red]")
                return {"total": len(issues), "success": 0, "failed": 0, "skipped": len(issues)}

        # 先获取里程碑 ID
        try:
            milestone_id = self._get_milestone_id(milestone)
            if milestone_id is None:
                console.print(f"❌ [red]找不到里程碑 '{milestone}'[/red]")
                return {"total": len(issues), "success": 0, "failed": len(issues), "skipped": 0}
        except Exception as e:
            console.print(f"❌ [red]获取里程碑失败: {e}[/red]")
            return {"total": len(issues), "success": 0, "failed": len(issues), "skipped": 0}

        # 执行设置里程碑
        success_count = 0
        failed_count = 0

        from rich.progress import Progress, SpinnerColumn, TextColumn

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("设置里程碑...", total=len(issues))

            for issue in issues:
                try:
                    self._update_issue(issue["number"], milestone=milestone_id)
                    success_count += 1
                except Exception as e:
                    console.print(f"❌ [red]为 #{issue['number']} 设置里程碑失败: {e}[/red]")
                    failed_count += 1
                progress.advance(task)

        console.print(f"\n✅ [green]成功为 {success_count} 个 Issues 设置里程碑[/green]")
        if failed_count > 0:
            console.print(f"❌ [red]失败 {failed_count} 个[/red]")

        return {
            "total": len(issues),
            "success": success_count,
            "failed": failed_count,
            "skipped": 0,
        }

    def _get_milestone_id(self, milestone_title: str) -> int | None:
        """获取里程碑 ID

        Args:
            milestone_title: 里程碑标题

        Returns:
            里程碑 ID，如果不存在返回 None
        """
        milestones = self._get_milestones()
        for milestone in milestones:
            if milestone["title"] == milestone_title:
                return milestone["number"]  # type: ignore[no-any-return]
        return None

    def _show_preview_table(self, issues: list[dict[str, Any]], operation: str) -> None:
        """显示预览表格

        Args:
            issues: Issues 列表
            operation: 操作描述
        """
        console.print(f"\n🔍 [yellow]将要执行的操作: {operation}[/yellow]\n")

        # 限制显示前 20 个
        display_issues = issues[:20]

        table = Table(title=f"匹配的 Issues (共 {len(issues)} 个)")
        table.add_column("#", style="cyan", no_wrap=True)
        table.add_column("标题", style="white")
        table.add_column("状态", style="magenta")
        table.add_column("标签", style="green")

        for issue in display_issues:
            labels = ", ".join([label["name"] for label in issue.get("labels", [])])
            state_emoji = "🟢" if issue["state"] == "open" else "🔴"
            table.add_row(
                str(issue["number"]),
                issue["title"][:50] + "..." if len(issue["title"]) > 50 else issue["title"],
                f"{state_emoji} {issue['state']}",
                labels[:30] + "..." if len(labels) > 30 else labels,
            )

        if len(issues) > 20:
            table.caption = f"... 还有 {len(issues) - 20} 个 Issues"

        console.print(table)
