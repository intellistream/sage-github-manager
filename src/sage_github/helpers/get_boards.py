#!/usr/bin/env python3
"""
获取GitHub组织的项目板信息并生成boards_metadata.json配置文件

功能:
- 查询GitHub组织的所有项目板
- 生成SAGE团队到项目板的映射配置
- 保存到metadata目录

作者: SAGE Team
日期: 2025-08-30
"""

from datetime import datetime
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
    from config import IssuesConfig


class BoardsMetadataGenerator:
    """项目板metadata生成器"""

    def __init__(self):
        self.config = IssuesConfig()

    def generate_boards_metadata(self):
        """生成boards_metadata.json文件"""
        boards_file = self.config.metadata_path / "boards_metadata.json"

        # 默认的项目板配置
        default_boards_config = {
            "description": "SAGE团队到GitHub项目板的映射配置",
            "organization": "intellistream",
            "repository": "SAGE",
            "team_to_project": {
                "sage-apps": 14,
                "sage-middleware": 13,
                "sage-kernel": 12,
            },
            "metadata": {
                "version": "1.0",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "description": "这个文件定义了SAGE团队到GitHub项目板的映射关系",
                "usage": "project_manage.py 脚本使用此文件来确定将Issues分配到哪个项目板",
            },
            "teams": {
                "sage-apps": {
                    "name": "SAGE Apps Team",
                    "description": "负责SAGE应用层开发和集成",
                    "project_number": 14,
                    "project_url": "https://github.com/orgs/intellistream/projects/14",
                },
                "sage-middleware": {
                    "name": "SAGE Middleware Team",
                    "description": "负责SAGE中间件和服务层开发",
                    "project_number": 13,
                    "project_url": "https://github.com/orgs/intellistream/projects/13",
                },
                "sage-kernel": {
                    "name": "SAGE Kernel Team",
                    "description": "负责SAGE核心引擎和内核开发",
                    "project_number": 12,
                    "project_url": "https://github.com/orgs/intellistream/projects/12",
                },
            },
        }

        try:
            # 如果有GitHub Token，尝试从API获取实际的项目板信息
            if self.config.github_token:
                print("🔍 尝试从GitHub API获取项目板信息...")
                api_boards = self._fetch_boards_from_api()
                if api_boards:
                    # 更新配置中的项目板信息
                    for team_name, board_info in api_boards.items():
                        if team_name in default_boards_config["teams"]:
                            default_boards_config["teams"][team_name].update(board_info)
                    print(f"✅ 成功从API获取 {len(api_boards)} 个项目板信息")
                else:
                    print("⚠️ 无法从API获取项目板信息，使用默认配置")
            else:
                print("ℹ️ 未配置GitHub Token，使用默认项目板配置")

            # 保存配置文件
            with open(boards_file, "w", encoding="utf-8") as f:
                json.dump(default_boards_config, f, indent=2, ensure_ascii=False)

            print(f"✅ 项目板配置文件已生成: {boards_file}")
            return True

        except Exception as e:
            print(f"❌ 生成项目板配置失败: {e}")
            return False

    def _fetch_boards_from_api(self):
        """从GitHub API获取项目板信息"""
        try:
            # 使用GraphQL API查询组织的项目板
            query = """
            {
              organization(login: "intellistream") {
                projectsV2(first: 20) {
                  nodes {
                    number
                    title
                    url
                    shortDescription
                  }
                }
              }
            }
            """

            headers = {
                "Authorization": f"token {self.config.github_token}",
                "Content-Type": "application/json",
            }

            response = requests.post(
                "https://api.github.com/graphql",
                json={"query": query},
                headers=headers,
                timeout=30,
            )

            if response.status_code != 200:
                print(f"API请求失败: {response.status_code}")
                return None

            data = response.json()

            if "errors" in data:
                print(f"GraphQL查询错误: {data['errors']}")
                return None

            projects = (
                data.get("data", {}).get("organization", {}).get("projectsV2", {}).get("nodes", [])
            )

            # 映射项目编号到团队名称
            project_to_team = {
                12: "sage-kernel",
                13: "sage-middleware",
                14: "sage-apps",
            }

            boards_info = {}
            for project in projects:
                project_num = project.get("number")
                if project_num in project_to_team:
                    team_name = project_to_team[project_num]
                    boards_info[team_name] = {
                        "project_number": project_num,
                        "project_url": project.get("url", ""),
                        "title": project.get("title", ""),
                        "description": project.get("shortDescription", ""),
                    }

            return boards_info

        except Exception as e:
            print(f"从API获取项目板信息失败: {e}")
            return None


def main():
    """主函数"""
    generator = BoardsMetadataGenerator()
    success = generator.generate_boards_metadata()

    if success:
        print("\n🎉 项目板metadata生成完成！")
        sys.exit(0)
    else:
        print("\n💥 项目板metadata生成失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
