#!/usr/bin/env python3
"""
通用GitHub Issue创建工具
支持交互式创建或通过命令行参数创建
"""

import argparse
import json
from pathlib import Path
import sys

import requests

# 动态导入config模块
try:
    # 尝试相对导入（当作为模块运行时）
    from ..config import IssuesConfig
except ImportError:
    # 如果相对导入失败，使用绝对导入
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import IssuesConfig  # type: ignore[no-redef]

config = IssuesConfig()


class GitHubIssueCreator:
    def __init__(self):
        # Use unified config system
        if not config.github_token:
            print("❌ 未找到GitHub Token，请先配置")
            sys.exit(1)

        self.github_token = config.github_token
        self.repo = f"{config.GITHUB_OWNER}/{config.GITHUB_REPO}"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

    def validate_token(self) -> bool:
        """验证GitHub token是否有效"""
        if not self.github_token:
            print("❌ GitHub Token未配置")
            return False

        # Test token by getting user info
        try:
            response = requests.get("https://api.github.com/user", headers=self.headers)
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ GitHub Token有效，用户: {user_info.get('login', 'unknown')}")
                return True
            else:
                print(f"❌ GitHub Token无效: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Token验证失败: {e}")
            return False

    def get_available_labels(self) -> list[str]:
        """获取仓库可用的标签"""
        try:
            url = f"https://api.github.com/repos/{self.repo}/labels"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                labels = response.json()
                return [label["name"] for label in labels]
        except Exception as e:
            print(f"⚠️ 获取标签失败: {e}")
        return []

    def interactive_input(self) -> dict:
        """交互式输入Issue信息"""
        print("\n🎯 创建新的GitHub Issue")
        print("=" * 40)

        try:
            # 标题 (必填)
            title = ""
            while not title.strip():
                title = input("\n📝 请输入Issue标题: ").strip()
                if not title:
                    print("❌ 标题不能为空，请重新输入")

            # 描述 (可选)
            print("\n📄 请输入Issue描述 (输入空行结束):")
            body_lines = []
            while True:
                try:
                    line = input()
                    if not line:
                        break
                    body_lines.append(line)
                except EOFError:
                    break
            body = "\n".join(body_lines) if body_lines else ""

            # 标签
            available_labels = self.get_available_labels()
            if available_labels:
                print(f"\n🏷️ 可用标签: {', '.join(available_labels[:10])}...")
                try:
                    labels_input = input("请输入标签 (用逗号分隔，留空跳过): ").strip()
                    labels = (
                        [label.strip() for label in labels_input.split(",") if label.strip()]
                        if labels_input
                        else []
                    )
                except EOFError:
                    labels = []
            else:
                labels = []

            # 分配给某人 (可选)
            try:
                assignee = input("\n👤 分配给 (GitHub用户名，留空跳过): ").strip() or None
            except EOFError:
                assignee = None

            # 里程碑 (可选)
            try:
                milestone_input = input("\n🎯 里程碑编号 (留空跳过): ").strip()
                milestone = int(milestone_input) if milestone_input.isdigit() else None
            except (EOFError, ValueError):
                milestone = None

            return {
                "title": title,
                "body": body,
                "labels": labels,
                "assignee": assignee,
                "milestone": milestone,
            }

        except KeyboardInterrupt:
            print("\n\n❌ 操作被用户取消")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 输入过程中出现错误: {e}")
            sys.exit(1)

    def create_issue(self, issue_data: dict) -> bool:
        """创建GitHub Issue"""
        # 清理数据，移除空值
        clean_data = {k: v for k, v in issue_data.items() if v is not None and v != []}

        url = f"https://api.github.com/repos/{self.repo}/issues"

        print("\n🚀 正在创建GitHub Issue...")
        print(f"📝 标题: {clean_data['title']}")
        if clean_data.get("labels"):
            print(f"🏷️ 标签: {', '.join(clean_data['labels'])}")
        if clean_data.get("assignee"):
            print(f"👤 分配给: {clean_data['assignee']}")

        try:
            response = requests.post(url, headers=self.headers, json=clean_data)

            if response.status_code == 201:
                issue_info = response.json()
                print("\n✅ Issue创建成功!")
                print(f"🔗 Issue链接: {issue_info['html_url']}")
                print(f"📊 Issue编号: #{issue_info['number']}")
                return True
            else:
                print(f"\n❌ 创建失败! 状态码: {response.status_code}")
                print(f"错误信息: {response.text}")
                return False

        except Exception as e:
            print(f"\n❌ 发生错误: {str(e)}")
            return False


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="创建GitHub Issue")
    parser.add_argument("--title", "-t", help="Issue标题")
    parser.add_argument("--body", "-b", help="Issue描述")
    parser.add_argument("--labels", "-l", help="标签 (用逗号分隔)")
    parser.add_argument("--assignee", "-a", help="分配给的用户")
    parser.add_argument("--milestone", "-m", type=int, help="里程碑编号")
    parser.add_argument("--file", "-f", help="从文件读取issue内容 (JSON格式)")

    return parser.parse_args()


def load_from_file(file_path: str) -> dict | None:
    """从文件加载issue数据"""
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)  # type: ignore[no-any-return]
    except Exception as e:
        print(f"❌ 读取文件失败: {e}")
        return None


def main():
    print("🎯 GitHub Issue 创建工具")
    print("=" * 40)

    creator = GitHubIssueCreator()

    # 验证GitHub token
    if not creator.validate_token():
        sys.exit(1)

    args = parse_arguments()

    # 确定issue数据来源
    if args.file:
        # 从文件读取
        issue_data = load_from_file(args.file)
        if not issue_data:
            sys.exit(1)
    elif args.title:
        # 从命令行参数
        issue_data = {
            "title": args.title,
            "body": args.body or "待补充详细描述...",
            "labels": args.labels.split(",") if args.labels else [],
            "assignee": args.assignee,
            "milestone": args.milestone,
        }
    else:
        # 交互式输入
        issue_data = creator.interactive_input()

    # 创建issue
    success = creator.create_issue(issue_data)

    if success:
        print("\n🎉 任务完成! Issue已成功创建到GitHub仓库。")
    else:
        print("\n💡 提示: 请检查网络连接和GitHub token权限。")
        sys.exit(1)


if __name__ == "__main__":
    main()
