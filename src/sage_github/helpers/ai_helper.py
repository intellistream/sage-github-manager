"""AI 功能助手

提供 Issue 摘要、重复检测、标签建议等 AI 功能。
支持 OpenAI 和 Anthropic Claude API。
"""

import os
from typing import Any

from rich.console import Console

console = Console()


class AIHelper:
    """AI 助手类

    提供基于 AI 的 Issue 分析功能。
    """

    def __init__(
        self, api_provider: str = "openai", api_key: str | None = None, silent: bool = False
    ):
        """初始化 AI 助手

        Args:
            api_provider: API 提供商 (openai/claude)
            api_key: API 密钥
            silent: 静默模式（不打印警告）
        """
        self.api_provider = api_provider.lower()
        self.api_key = api_key or self._get_api_key()
        self.silent = silent

        if not self.api_key and not silent:
            console.print("⚠️  [yellow]未配置 API Key[/yellow]")
            console.print("💡 设置环境变量:")
            if self.api_provider == "openai":
                console.print("   export OPENAI_API_KEY=sk-...")
            else:
                console.print("   export ANTHROPIC_API_KEY=sk-ant-...")

    def _get_api_key(self) -> str | None:
        """获取 API 密钥"""
        if self.api_provider == "openai":
            return os.getenv("OPENAI_API_KEY")
        elif self.api_provider == "claude":
            return os.getenv("ANTHROPIC_API_KEY")
        return None

    def is_available(self) -> bool:
        """检查 AI 功能是否可用"""
        if not self.api_key:
            return False

        try:
            if self.api_provider == "openai":
                import openai  # noqa: F401

                return True
            elif self.api_provider == "claude":
                import anthropic  # noqa: F401

                return True
        except ImportError:
            console.print(f"⚠️  [yellow]{self.api_provider} 库未安装[/yellow]")
            if self.api_provider == "openai":
                console.print("💡 安装: pip install openai")
            else:
                console.print("💡 安装: pip install anthropic")
            return False

        return False

    def summarize_issue(self, issue: dict[str, Any], max_length: int = 200) -> str | None:
        """生成 Issue 摘要

        Args:
            issue: Issue 数据
            max_length: 最大摘要长度

        Returns:
            摘要文本，如果失败返回 None
        """
        if not self.is_available():
            return None

        title = issue.get("title", "")
        body = issue.get("body", "")

        if not body:
            return title

        prompt = f"""请用中文简洁总结以下 GitHub Issue（不超过{max_length}字）：

标题: {title}

内容:
{body[:2000]}  # 限制输入长度

要求：
1. 一句话概括问题核心
2. 如果有解决方案或建议，简要提及
3. 语言简洁、专业
"""

        try:
            if self.api_provider == "openai":
                return self._summarize_with_openai(prompt, max_length)
            elif self.api_provider == "claude":
                return self._summarize_with_claude(prompt, max_length)
        except Exception as e:
            console.print(f"❌ [red]生成摘要失败: {e}[/red]")
            return None

        return None

    def _summarize_with_openai(self, prompt: str, max_length: int) -> str | None:
        """使用 OpenAI 生成摘要"""
        try:
            import openai

            client = openai.OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的技术文档助手，擅长总结 GitHub Issues。",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=max_length,
                temperature=0.3,
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            console.print(f"❌ [red]OpenAI API 调用失败: {e}[/red]")
            return None

    def _summarize_with_claude(self, prompt: str, max_length: int) -> str | None:
        """使用 Claude 生成摘要"""
        try:
            import anthropic

            client = anthropic.Anthropic(api_key=self.api_key)

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_length,
                messages=[{"role": "user", "content": prompt}],
            )

            return message.content[0].text.strip()
        except Exception as e:
            console.print(f"❌ [red]Claude API 调用失败: {e}[/red]")
            return None

    def detect_duplicates(
        self, issues: list[dict[str, Any]], threshold: float = 0.7
    ) -> list[tuple[dict[str, Any], dict[str, Any], float]]:
        """检测重复的 Issues

        使用标题和内容的文本相似度检测重复。

        Args:
            issues: Issues 列表
            threshold: 相似度阈值 (0-1)

        Returns:
            重复对列表，每个元素为 (issue1, issue2, similarity)
        """
        from difflib import SequenceMatcher

        duplicates = []

        for i in range(len(issues)):
            for j in range(i + 1, len(issues)):
                issue1 = issues[i]
                issue2 = issues[j]

                # 计算标题相似度
                title1 = issue1.get("title", "").lower()
                title2 = issue2.get("title", "").lower()

                if not title1 or not title2:
                    continue

                title_sim = SequenceMatcher(None, title1, title2).ratio()

                # 如果标题非常相似，检查内容
                if title_sim > threshold:
                    body1 = (issue1.get("body") or "")[:500].lower()
                    body2 = (issue2.get("body") or "")[:500].lower()

                    if body1 and body2:
                        body_sim = SequenceMatcher(None, body1, body2).ratio()
                        similarity = title_sim * 0.7 + body_sim * 0.3  # 标题权重更高
                    else:
                        similarity = title_sim

                    if similarity > threshold:
                        duplicates.append((issue1, issue2, similarity))

        # 按相似度排序
        duplicates.sort(key=lambda x: x[2], reverse=True)
        return duplicates

    def suggest_labels(self, issue: dict[str, Any]) -> list[str]:
        """为 Issue 推荐标签

        基于标题和内容关键词推荐合适的标签。

        Args:
            issue: Issue 数据

        Returns:
            推荐的标签列表
        """
        title = issue.get("title", "").lower()
        body = (issue.get("body") or "").lower()
        text = f"{title} {body}"

        # 关键词映射到标签
        label_keywords = {
            "bug": [
                "bug",
                "error",
                "错误",
                "异常",
                "exception",
                "fail",
                "失败",
                "crash",
                "崩溃",
            ],
            "enhancement": [
                "feature",
                "enhance",
                "improve",
                "增强",
                "改进",
                "优化",
                "新功能",
                "add",
            ],
            "documentation": ["doc", "文档", "readme", "guide", "tutorial", "教程"],
            "performance": ["performance", "性能", "slow", "慢", "latency", "延迟", "optimize"],
            "security": ["security", "安全", "vulnerability", "漏洞", "cve"],
            "test": ["test", "测试", "unit test", "integration"],
            "refactor": ["refactor", "重构", "cleanup", "清理"],
            "dependency": ["dependency", "依赖", "package", "upgrade", "update"],
            "breaking-change": ["breaking", "破坏性", "incompatible", "不兼容"],
            "good-first-issue": ["easy", "简单", "beginner", "新手"],
        }

        suggested = []
        for label, keywords in label_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    suggested.append(label)
                    break  # 找到一个关键词就够了

        return list(set(suggested))  # 去重

    def analyze_issues_batch(
        self, issues: list[dict[str, Any]], operation: str = "summarize"
    ) -> dict[str, Any]:
        """批量分析 Issues

        Args:
            issues: Issues 列表
            operation: 操作类型 (summarize/labels/all)

        Returns:
            分析结果字典
        """
        results = {"total": len(issues), "processed": 0, "failed": 0, "data": []}

        for issue in issues:
            try:
                item = {
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "url": issue.get("html_url"),
                }

                if operation in ["summarize", "all"]:
                    summary = self.summarize_issue(issue)
                    if summary:
                        item["summary"] = summary

                if operation in ["labels", "all"]:
                    labels = self.suggest_labels(issue)
                    if labels:
                        item["suggested_labels"] = labels

                results["data"].append(item)
                results["processed"] += 1

            except Exception as e:
                console.print(f"❌ 处理 Issue #{issue.get('number')} 失败: {e}")
                results["failed"] += 1

        return results
