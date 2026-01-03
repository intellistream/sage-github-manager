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
