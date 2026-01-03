"""
GitHub Issues Manager命令 - CLI接口
集成到sage-dev命令组中
"""

import os
from pathlib import Path
import subprocess
import sys

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
import typer

from sage_github import IssuesConfig, IssuesManager
from sage_github.helpers import IssuesDownloader

console = Console()
app = typer.Typer(help="🐛 Issues管理 - GitHub Issues下载、分析和管理")


@app.command("status")
def status():
    """显示Issues管理状态"""
    console.print("📊 [bold blue]GitHub Issues Manager状态[/bold blue]")

    config = IssuesConfig()

    # 显示配置信息
    console.print("\n⚙️ 配置信息:")
    console.print(f"  • 项目根目录: {config.project_root}")
    console.print(f"  • 工作目录: {config.workspace_path}")
    console.print(f"  • 输出目录: {config.output_path}")
    console.print(f"  • 元数据目录: {config.metadata_path}")
    console.print(f"  • GitHub仓库: {config.GITHUB_OWNER}/{config.GITHUB_REPO}")
    if config.github_token:
        console.print(f"  • GitHub Token来源: {config.github_token_env or '未知环境变量'}")

    # 测试GitHub连接
    console.print("\n🔍 GitHub连接:")
    try:
        if config.test_github_connection():
            console.print("  ✅ [green]连接正常[/green]")
        else:
            console.print("  ❌ [red]连接失败 - 请检查GitHub Token[/red]")
            console.print("  💡 设置方法:")
            console.print(
                "    export GITHUB_TOKEN=your_token  # 或 export GIT_TOKEN=your_token / export SAGE_REPO_TOKEN=your_token"
            )
            console.print("    或创建 ~/.github_token 文件")
    except Exception as e:
        console.print(f"  ❌ [red]连接错误: {e}[/red]")

    # 显示本地数据状态
    if config.github_token:
        try:
            downloader = IssuesDownloader(config)
            download_status = downloader.get_download_status()

            console.print("\n📂 本地数据:")
            console.print(f"  • Issues数量: {download_status['issues_count']}")
            console.print(f"  • 最后更新: {download_status['last_update'] or '未知'}")

            if download_status["available_files"]:
                console.print(f"  • 数据文件: {len(download_status['available_files'])} 个")
        except Exception as e:
            console.print(f"\n📂 [red]本地数据状态获取失败: {e}[/red]")
    else:
        console.print("\n📂 本地数据: [yellow]需要GitHub Token才能查看[/yellow]")


@app.command("download")
def download(
    state: str = typer.Option("all", help="下载状态: all, open, closed"),
    force: bool = typer.Option(False, "--force", "-f", help="强制重新下载"),
):
    """下载GitHub Issues"""
    console.print(f"📥 [bold blue]下载Issues (状态: {state})[/bold blue]")

    # 检查GitHub Token
    config = IssuesConfig()
    if not config.github_token:
        console.print("❌ [red]GitHub Token未配置[/red]")
        console.print("💡 设置方法:")
        console.print(
            "   export GITHUB_TOKEN=your_token  # 或 export GIT_TOKEN=your_token / export SAGE_REPO_TOKEN=your_token"
        )
        console.print("   或创建 ~/.github_token 文件")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("下载中...", total=None)

        downloader = IssuesDownloader(config)
        success = downloader.download_issues(state=state)

        progress.update(task, completed=True)

    if success:
        # 显示下载结果
        status = downloader.get_download_status()
        console.print("\n✅ [green]下载成功![/green]")
        console.print(f"📊 Issues数量: {status['issues_count']}")
        console.print(f"📂 保存位置: {status['workspace_path']}")
    else:
        console.print("❌ [red]下载失败[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_issues(
    state: str = "open",
    label: list[str] | None = None,
    assignee: str | None = None,
    milestone: str | None = None,
    author: str | None = None,
    sort: str = "created",
    reverse: bool = True,
    limit: int | None = None,
    show_body: bool = False,
):
    """列出和过滤Issues

    灵活的Issues列表和筛选功能，支持多种过滤条件组合。

    示例:
      github-manager list                                # 列出所有开放的Issues
      github-manager list --state all                    # 列出所有Issues
      github-manager list --label bug --state open       # 列出开放的bug
      github-manager list --assignee shuhao              # 列出分配给shuhao的Issues
      github-manager list --milestone "v2.0"             # 列出v2.0里程碑的Issues
      github-manager list --sort comments --limit 10     # 列出评论最多的10个Issues
      github-manager list --body                         # 显示Issue正文摘要

    参数:
      --state: Issue状态 (all, open, closed), 默认: open
      --label, -l: 按标签过滤 (可多次使用)
      --assignee, -a: 按负责人过滤
      --milestone, -m: 按里程碑过滤
      --author: 按创建者过滤
      --sort: 排序字段 (created, updated, comments, number), 默认: created
      --reverse: 降序排列, 默认: True
      --limit, -n: 限制显示数量
      --body, -b: 显示Issue正文摘要
    """
    console.print(f"📋 [bold blue]Issues列表 (状态: {state})[/bold blue]")

    manager = IssuesManager()

    # 获取过滤后的Issues
    issues = manager.list_issues(
        state=state,
        labels=label if label else None,
        assignee=assignee,
        milestone=milestone,
        author=author,
        sort_by=sort,
        reverse=reverse,
        limit=limit,
    )

    if not issues:
        console.print("📭 [yellow]没有找到符合条件的Issues[/yellow]")
        return

    # 创建表格显示
    table = Table(title=f"找到 {len(issues)} 个Issues")
    table.add_column("#", style="cyan", width=6)
    table.add_column("标题", style="white", no_wrap=False)
    table.add_column("状态", style="green", width=8)
    table.add_column("标签", style="yellow", width=20)
    table.add_column("负责人", style="blue", width=12)

    if show_body:
        table.add_column("摘要", style="dim", width=30)

    for issue in issues:
        # 提取数据
        number = str(issue.get("number", "N/A"))
        title = issue.get("title", "未知")[:60]
        state_value = issue.get("state", "open")
        state_emoji = "🟢" if state_value == "open" else "🔴"

        # 标签
        labels = issue.get("labels", [])
        label_names = [label["name"] if isinstance(label, dict) else label for label in labels]
        labels_str = ", ".join(label_names[:3])  # 最多显示3个标签
        if len(label_names) > 3:
            labels_str += "..."

        # 负责人
        assignees = issue.get("assignees", [])
        assignee_names = [a["login"] if isinstance(a, dict) else a for a in assignees]
        assignees_str = ", ".join(assignee_names[:2]) if assignees else "未分配"
        if len(assignee_names) > 2:
            assignees_str += "..."

        row = [
            number,
            title,
            f"{state_emoji} {state_value}",
            labels_str or "-",
            assignees_str,
        ]

        if show_body:
            body = issue.get("body", "")
            summary = body[:50].replace("\n", " ") if body else "-"
            if len(body) > 50:
                summary += "..."
            row.append(summary)

        table.add_row(*row)

    console.print(table)

    # 显示过滤条件摘要
    filters_applied = []
    if state != "all":
        filters_applied.append(f"状态={state}")
    if label:
        filters_applied.append(f"标签={', '.join(label)}")
    if assignee is not None:
        filters_applied.append(f"负责人={assignee or '未分配'}")
    if milestone is not None:
        filters_applied.append(f"里程碑={milestone or '无'}")
    if author:
        filters_applied.append(f"创建者={author}")

    if filters_applied:
        console.print(f"\n🔍 过滤条件: {' | '.join(filters_applied)}")


@app.command("export")
def export_issues(
    output: str = typer.Argument(..., help="输出文件路径"),
    format: str = typer.Option("csv", "--format", "-f", help="导出格式: csv, json, markdown"),
    state: str = typer.Option("all", help="Issue状态: all, open, closed"),
    label: list[str] = typer.Option([], "--label", "-l", help="按标签过滤"),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="按负责人过滤"),
    milestone: str | None = typer.Option(None, "--milestone", "-m", help="按里程碑过滤"),
    author: str | None = typer.Option(None, "--author", help="按创建者过滤"),
    template: str = typer.Option("default", help="Markdown模板: default, roadmap, report"),
):
    """导出Issues到文件

    支持多种导出格式和过滤条件，方便生成报告和分析。

    示例:
      github-manager export issues.csv                    # 导出所有Issues到CSV
      github-manager export issues.json -f json          # 导出为JSON
      github-manager export roadmap.md -f markdown       # 导出为Markdown
      github-manager export open_bugs.csv --state open --label bug
      github-manager export v2.0.md -f markdown --milestone "v2.0" --template roadmap

    支持的格式:
      - csv: 适合在Excel/Sheets中分析
      - json: 适合程序处理和API集成
      - markdown: 适合文档和报告

    Markdown模板:
      - default: 完整的Issue详情列表
      - roadmap: 按里程碑分组的路线图
      - report: 简洁的报告格式
    """
    console.print(f"📤 [bold blue]导出Issues (格式: {format})[/bold blue]")

    manager = IssuesManager()
    output_path = Path(output)

    # 自动添加扩展名
    if not output_path.suffix:
        if format == "csv":
            output_path = output_path.with_suffix(".csv")
        elif format == "json":
            output_path = output_path.with_suffix(".json")
        elif format == "markdown":
            output_path = output_path.with_suffix(".md")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("导出中...", total=None)

        success = manager.export_issues(
            output_path=output_path,
            format=format,
            state=state,
            labels=label if label else [],
            assignee=assignee,
            milestone=milestone,
            author=author,
            template=template,
        )

        progress.update(task, completed=True)

    if not success:
        console.print("❌ [red]导出失败[/red]")
        raise typer.Exit(1)

    # 显示导出信息
    console.print(f"\n📁 [green]文件位置[/green]: {output_path.absolute()}")
    console.print(f"📊 [green]文件大小[/green]: {output_path.stat().st_size / 1024:.2f} KB")

    # 显示过滤条件
    filters_applied = []
    if state != "all":
        filters_applied.append(f"状态={state}")
    if label:
        filters_applied.append(f"标签={', '.join(label)}")
    if assignee is not None:
        filters_applied.append(f"负责人={assignee or '未分配'}")
    if milestone is not None:
        filters_applied.append(f"里程碑={milestone or '无'}")
    if author:
        filters_applied.append(f"创建者={author}")

    if filters_applied:
        console.print(f"\n🔍 应用的过滤条件: {' | '.join(filters_applied)}")


@app.command("batch-close")
def batch_close(
    state: str = typer.Option("open", help="Issue状态: all, open, closed"),
    label: list[str] = typer.Option([], "--label", "-l", help="按标签过滤"),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="按负责人过滤"),
    milestone: str | None = typer.Option(None, "--milestone", "-m", help="按里程碑过滤"),
    author: str | None = typer.Option(None, "--author", help="按创建者过滤"),
    dry_run: bool = typer.Option(False, "--dry-run", help="预览模式（不实际执行）"),
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过确认提示"),
):
    """批量关闭Issues

    根据过滤条件批量关闭匹配的Issues。

    示例:
      github-manager batch-close --label wontfix                  # 关闭所有wontfix标签的Issues
      github-manager batch-close --state open --milestone "v1.0"  # 关闭v1.0里程碑的所有打开Issues
      github-manager batch-close --dry-run --label bug           # 预览要关闭的bug Issues
      github-manager batch-close --assignee shuhao --yes         # 无需确认关闭shuhao的Issues

    ⚠️  危险操作: 批量关闭Issues无法撤销，建议先使用 --dry-run 预览
    """
    console.print("🔒 [bold red]批量关闭Issues[/bold red]")

    manager = IssuesManager()

    result = manager.batch_close(
        state=state,
        labels=label if label else None,
        assignee=assignee,
        milestone=milestone,
        author=author,
        dry_run=dry_run,
        auto_confirm=yes,
    )

    if result["skipped"] == result["total"] and not dry_run:
        raise typer.Exit(1)


@app.command("batch-label")
def batch_label(
    add: list[str] = typer.Option([], "--add", help="要添加的标签"),
    remove: list[str] = typer.Option([], "--remove", help="要移除的标签"),
    state: str = typer.Option("all", help="Issue状态: all, open, closed"),
    label: list[str] = typer.Option([], "--label", "-l", help="按标签过滤"),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="按负责人过滤"),
    milestone: str | None = typer.Option(None, "--milestone", "-m", help="按里程碑过滤"),
    author: str | None = typer.Option(None, "--author", help="按创建者过滤"),
    dry_run: bool = typer.Option(False, "--dry-run", help="预览模式（不实际执行）"),
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过确认提示"),
):
    """批量管理标签

    根据过滤条件批量添加或移除标签。

    示例:
      github-manager batch-label --add "priority:high" --label bug        # 为所有bug添加高优先级
      github-manager batch-label --remove "needs-review" --state closed   # 从已关闭Issues移除待审核标签
      github-manager batch-label --add "v2.0" --milestone "v2.0"          # 为v2.0里程碑添加标签
      github-manager batch-label --add "urgent" --assignee shuhao --yes  # 无需确认添加urgent标签

    💡 提示: 可以同时使用 --add 和 --remove 来执行多个操作
    """
    if not add and not remove:
        console.print("❌ [red]请指定要添加（--add）或移除（--remove）的标签[/red]")
        raise typer.Exit(1)

    manager = IssuesManager()

    # 执行添加标签
    if add:
        console.print(f"🏷️  [bold blue]批量添加标签: {', '.join(add)}[/bold blue]")
        result_add = manager.batch_add_labels(
            add_labels=add,
            state=state,
            labels=label if label else None,
            assignee=assignee,
            milestone=milestone,
            author=author,
            dry_run=dry_run,
            auto_confirm=yes,
        )
        if result_add["skipped"] == result_add["total"] and not dry_run:
            raise typer.Exit(1)

    # 执行移除标签
    if remove:
        console.print(f"🏷️  [bold blue]批量移除标签: {', '.join(remove)}[/bold blue]")
        result_remove = manager.batch_remove_labels(
            remove_labels=remove,
            state=state,
            labels=label if label else None,
            assignee=assignee,
            milestone=milestone,
            author=author,
            dry_run=dry_run,
            auto_confirm=yes,
        )
        if result_remove["skipped"] == result_remove["total"] and not dry_run:
            raise typer.Exit(1)


@app.command("batch-assign")
def batch_assign(
    assignee: list[str] = typer.Option([], "--assignee", "-a", help="负责人（可多个）"),
    state: str = typer.Option("all", help="Issue状态: all, open, closed"),
    label: list[str] = typer.Option([], "--label", "-l", help="按标签过滤"),
    milestone: str | None = typer.Option(None, "--milestone", "-m", help="按里程碑过滤"),
    author: str | None = typer.Option(None, "--author", help="按创建者过滤"),
    dry_run: bool = typer.Option(False, "--dry-run", help="预览模式（不实际执行）"),
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过确认提示"),
):
    """批量分配Issues

    根据过滤条件批量分配Issues给指定负责人。

    示例:
      github-manager batch-assign -a shuhao --label "priority:high"    # 分配高优先级Issues
      github-manager batch-assign -a alice -a bob --milestone "v2.0"   # 分配给多人
      github-manager batch-assign -a shuhao --state open --dry-run     # 预览分配
      github-manager batch-assign -a team-lead --label bug --yes       # 无需确认分配bugs

    💡 提示: 使用多个 -a 可以分配给多个负责人
    """
    if not assignee:
        console.print("❌ [red]请指定负责人（--assignee 或 -a）[/red]")
        raise typer.Exit(1)

    console.print(f"👥 [bold blue]批量分配给: {', '.join(assignee)}[/bold blue]")

    manager = IssuesManager()

    result = manager.batch_assign(
        assignees=assignee,
        state=state,
        labels=label if label else None,
        milestone=milestone,
        author=author,
        dry_run=dry_run,
        auto_confirm=yes,
    )

    if result["skipped"] == result["total"] and not dry_run:
        raise typer.Exit(1)


@app.command("batch-milestone")
def batch_milestone(
    milestone: str = typer.Argument(..., help="要设置的里程碑名称"),
    state: str = typer.Option("all", help="Issue状态: all, open, closed"),
    label: list[str] = typer.Option([], "--label", "-l", help="按标签过滤"),
    assignee: str | None = typer.Option(None, "--assignee", "-a", help="按负责人过滤"),
    current_milestone: str | None = typer.Option(
        None, "--current-milestone", help="按当前里程碑过滤"
    ),
    author: str | None = typer.Option(None, "--author", help="按创建者过滤"),
    dry_run: bool = typer.Option(False, "--dry-run", help="预览模式（不实际执行）"),
    yes: bool = typer.Option(False, "--yes", "-y", help="跳过确认提示"),
):
    """批量设置里程碑

    根据过滤条件批量设置Issues的里程碑。

    示例:
      github-manager batch-milestone "v2.0" --label feature           # 将所有feature设置到v2.0
      github-manager batch-milestone "v3.0" --current-milestone "v2.0" # 将v2.0迁移到v3.0
      github-manager batch-milestone "Sprint 5" --state open --dry-run # 预览设置
      github-manager batch-milestone "Q1-2026" --assignee shuhao --yes # 无需确认设置

    💡 提示: 使用 --current-milestone 可以批量迁移里程碑
    """
    console.print(f"🎯 [bold blue]批量设置里程碑: {milestone}[/bold blue]")

    manager = IssuesManager()

    result = manager.batch_set_milestone(
        milestone=milestone,
        state=state,
        labels=label if label else None,
        assignee=assignee,
        milestone_filter=current_milestone,
        author=author,
        dry_run=dry_run,
        auto_confirm=yes,
    )

    if result["skipped"] == result["total"] and not dry_run:
        raise typer.Exit(1)


@app.command("stats")
def statistics():
    """显示Issues统计信息"""
    console.print("📊 [bold blue]Issues统计分析[/bold blue]")

    manager = IssuesManager()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("分析中...", total=None)
        success = manager.show_statistics()
        progress.update(task, completed=True)

    if not success:
        console.print("❌ [red]统计失败 - 请先下载Issues[/red]")
        console.print("💡 运行: github-manager download")
        raise typer.Exit(1)


@app.command("team")
def team(
    update: bool = typer.Option(
        False, "--update", "-u", help="更新团队信息（从GitHub API获取最新数据）"
    ),
    analysis: bool = typer.Option(
        False, "--analysis", "-a", help="显示团队分析（默认行为，可省略）"
    ),
):
    """团队管理和分析

    显示团队信息、成员分布等。支持从GitHub API更新最新团队数据。

    示例:
      github-manager team              # 显示团队分析
      github-manager team --update    # 更新团队信息
      github-manager team -u -a       # 更新并分析
    """
    manager = IssuesManager()

    if update:
        console.print("🔄 [bold blue]更新团队信息[/bold blue]")
        success = manager.update_team_info()
        if not success:
            console.print("❌ [red]更新失败[/red]")
            raise typer.Exit(1)

    if analysis or not update:
        console.print("👥 [bold blue]团队分析[/bold blue]")
        success = manager.team_analysis()
        if not success:
            console.print("❌ [red]分析失败[/red]")
            raise typer.Exit(1)


@app.command("create")
def create_issue():
    """创建新Issue"""
    console.print("✨ [bold blue]创建新Issue[/bold blue]")

    manager = IssuesManager()
    success = manager.create_new_issue()

    if not success:
        console.print("❌ [red]创建失败[/red]")
        raise typer.Exit(1)


@app.command("project")
def project_management():
    """项目管理 - 检测和修复错误分配"""
    console.print("📋 [bold blue]项目管理[/bold blue]")

    manager = IssuesManager()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("检查中...", total=None)
        success = manager.project_management()
        progress.update(task, completed=True)

    if not success:
        console.print("❌ [red]项目管理失败[/red]")
        raise typer.Exit(1)


@app.command("config")
def show_config():
    """显示配置信息"""
    console.print("⚙️ [bold blue]配置信息[/bold blue]")

    config = IssuesConfig()

    table = Table(title="GitHub Issues Manager配置")
    table.add_column("配置项", style="cyan")
    table.add_column("值", style="green")

    table.add_row("GitHub仓库", f"{config.GITHUB_OWNER}/{config.GITHUB_REPO}")
    table.add_row("项目根目录", str(config.project_root))
    table.add_row("工作目录", str(config.workspace_path))
    table.add_row("输出目录", str(config.output_path))
    table.add_row("元数据目录", str(config.metadata_path))
    table.add_row("GitHub Token", "已配置" if config.github_token else "未配置")

    console.print(table)

    # 显示用户设置
    console.print("\n📋 用户设置:")
    console.print(f"  • 同步更新历史: {getattr(config, 'sync_update_history', True)}")
    console.print(f"  • 自动备份: {getattr(config, 'auto_backup', True)}")
    console.print(f"  • 详细输出: {getattr(config, 'verbose_output', False)}")


@app.command("ai")
def ai_analysis(
    action: str = typer.Option("analyze", help="AI操作类型: analyze, dedupe, optimize, report"),
    engine: str = typer.Option("interactive", help="AI引擎: openai, claude, interactive"),
    dry_run: bool = typer.Option(False, "--dry-run", help="预览模式，不实际修改"),
):
    """AI智能分析和整理Issues

    支持多种AI操作:
    - analyze: 综合分析Issues
    - dedupe: 识别重复Issues
    - optimize: 优化标签分类
    - report: 生成分析报告

    示例:
      github-manager ai --action analyze    # AI综合分析
      github-manager ai --action dedupe     # 查找重复Issues
      github-manager ai --dry-run           # 预览模式
    """
    console.print(f"🤖 [bold blue]AI智能分析 (操作: {action})[/bold blue]")

    config = IssuesConfig()
    if not config.github_token:
        console.print("❌ [red]GitHub Token未配置[/red]")
        console.print("💡 AI分析需要GitHub Token来访问API")
        raise typer.Exit(1)

    # 检查AI分析脚本
    ai_script = Path(__file__).parent / "helpers" / "ai_analyzer.py"
    if not ai_script.exists():
        console.print("❌ [red]AI分析脚本不存在[/red]")
        console.print(f"💡 请确保文件存在: {ai_script}")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("AI分析中...", total=None)

        # 设置环境变量
        env = os.environ.copy()
        env["GITHUB_TOKEN"] = config.github_token

        # 构建命令参数
        cmd_args = [sys.executable, str(ai_script)]
        if action != "analyze":
            cmd_args.extend(["--action", action])
        if engine != "interactive":
            cmd_args.extend(["--engine", engine])
        if dry_run:
            cmd_args.append("--dry-run")

        # 执行AI分析
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            env=env,
            cwd=str(config.workspace_path),
        )

        progress.update(task, completed=True)

    if result.returncode == 0:
        console.print("✅ [green]AI分析完成![/green]")
        if result.stdout:
            console.print(result.stdout)
    else:
        console.print("❌ [red]AI分析失败[/red]")
        if result.stderr:
            console.print(f"[red]错误信息: {result.stderr}[/red]")
        raise typer.Exit(1)


@app.command("sync")
def sync_issues(
    direction: str = typer.Option("upload", help="同步方向: upload, download, both"),
    dry_run: bool = typer.Option(False, "--dry-run", help="预览模式，不实际修改"),
    force: bool = typer.Option(False, "--force", help="强制同步，忽略冲突检查"),
):
    """同步Issues到GitHub

    支持双向同步:
    - upload: 上传本地修改到GitHub
    - download: 下载GitHub最新数据
    - both: 双向同步

    示例:
      github-manager sync --direction upload   # 上传到GitHub
      github-manager sync --dry-run           # 预览模式
      github-manager sync --force             # 强制同步
    """
    console.print(f"🔄 [bold blue]Issues同步 (方向: {direction})[/bold blue]")

    config = IssuesConfig()
    if not config.github_token:
        console.print("❌ [red]GitHub Token未配置[/red]")
        console.print("💡 同步功能需要GitHub Token来访问API")
        raise typer.Exit(1)

    # 检查同步脚本
    sync_script = Path(__file__).parent / "helpers" / "sync_issues.py"
    if not sync_script.exists():
        console.print("❌ [red]同步脚本不存在[/red]")
        console.print(f"💡 请确保文件存在: {sync_script}")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("同步中...", total=None)

        # 设置环境变量
        env = os.environ.copy()
        env["GITHUB_TOKEN"] = config.github_token

        # 构建命令参数
        cmd_args = [sys.executable, str(sync_script)]
        if dry_run:
            cmd_args.append("preview")  # Use preview command for dry-run
        else:
            cmd_args.append("sync")  # Use sync command for actual sync
        if force:
            cmd_args.append("--auto-confirm")

        # 执行同步
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            env=env,
            cwd=str(config.workspace_path),
        )

        progress.update(task, completed=True)

    if result.returncode == 0:
        console.print("✅ [green]同步完成![/green]")
        if result.stdout:
            console.print(result.stdout)
    else:
        console.print("❌ [red]同步失败[/red]")
        if result.stderr:
            console.print(f"[red]错误信息: {result.stderr}[/red]")
        raise typer.Exit(1)


@app.command("organize")
def organize_issues(
    preview: bool = typer.Option(False, "--preview", "-p", help="预览整理计划"),
    apply: bool = typer.Option(False, "--apply", "-a", help="执行整理"),
    confirm: bool = typer.Option(False, "--confirm", "-c", help="确认执行（与--apply一起使用）"),
):
    """整理Issues - 根据关闭时间移动到不同状态列

    根据issues的关闭时间自动整理到相应的状态列：
    - 最近一周完成的issues -> "Done" 列
    - 超过一周但一个月以内的 -> "Archive" 列
    - 超过一个月的 -> "History" 列

    示例:
      github-manager organize --preview          # 预览整理计划
      github-manager organize --apply --confirm  # 执行整理
    """
    if not preview and not apply:
        console.print("❌ [red]请指定 --preview 或 --apply 参数[/red]")
        console.print("\n💡 使用方法:")
        console.print("  github-manager organize --preview          # 预览整理计划")
        console.print("  github-manager organize --apply --confirm  # 执行整理")
        raise typer.Exit(1)

    if apply and not confirm:
        console.print("❌ [red]执行整理需要 --confirm 参数确认[/red]")
        console.print("💡 使用: github-manager organize --apply --confirm")
        raise typer.Exit(1)

    console.print("🗂️ [bold blue]Issues整理工具[/bold blue]")

    config = IssuesConfig()
    if not config.github_token:
        console.print("❌ [red]GitHub Token未配置[/red]")
        console.print("💡 整理功能需要GitHub Token来访问Projects API")
        raise typer.Exit(1)

    # 检查整理脚本
    organize_script = Path(__file__).parent / "helpers" / "organize_issues.py"
    if not organize_script.exists():
        console.print("❌ [red]整理脚本不存在[/red]")
        console.print(f"💡 请确保文件存在: {organize_script}")
        raise typer.Exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("整理中...", total=None)

        # 设置环境变量
        env = os.environ.copy()
        env["GITHUB_TOKEN"] = config.github_token

        # 构建命令参数
        cmd_args = [sys.executable, str(organize_script)]
        if preview:
            cmd_args.append("--preview")
        if apply:
            cmd_args.append("--apply")
            cmd_args.append("--confirm")

        # 执行整理
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            env=env,
            cwd=str(config.workspace_path),
        )

        progress.update(task, completed=True)

    if result.returncode == 0:
        console.print("✅ [green]整理完成![/green]")
        if result.stdout:
            console.print(result.stdout)
    else:
        console.print("❌ [red]整理失败[/red]")
        if result.stderr:
            console.print(f"错误信息: {result.stderr}")
        raise typer.Exit(1)


@app.command("test")
def run_tests():
    """运行Issues管理测试套件

    验证所有核心功能:
    - 配置验证
    - GitHub连接测试
    - 下载功能测试
    - 统计生成测试
    - 团队分析测试
    - 文件操作测试

    示例:
      github-manager test    # 运行全部测试
    """
    console.print("🧪 [bold blue]运行Issues管理测试套件[/bold blue]")

    try:
        from .tests import IssuesTestSuite

        test_suite = IssuesTestSuite()
        success = test_suite.run_all_tests()

        if success:
            console.print("🎉 [green]所有测试通过！[/green]")
        else:
            console.print("⚠️ [yellow]部分测试失败[/yellow]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"❌ [red]测试运行失败: {e}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
