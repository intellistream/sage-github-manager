#!/usr/bin/env python3
"""
精简版GitHub项目管理工具
只保留核心的API操作功能，用作其他脚本的helper
"""

import json
from pathlib import Path
import sys
import time

import requests

# 动态导入config模块
try:
    # 尝试相对导入（当作为模块运行时）
    from ..config import IssuesConfig
except ImportError:
    # 如果相对导入失败，使用绝对导入
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from config import IssuesConfig  # type: ignore[no-redef]


class GitHubProjectManager:
    """精简版GitHub项目管理器，只包含核心API功能"""

    def __init__(self, org="intellistream", repo="SAGE"):
        self.ORG = org
        self.REPO = repo
        self.github_token = self._get_github_token()
        self.graphql_headers = {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json",
        }

        # 加载配置
        self._load_configurations()

    def _get_github_token(self):
        """获取GitHub token"""
        config = IssuesConfig()
        token = config.github_token
        if token:
            print("✅ 从 IssuesConfig 获取到 GitHub Token")
            return token

        raise Exception("未找到GitHub Token，请设置GITHUB_TOKEN环境变量或创建.github_token文件")

    def _load_configurations(self):
        """加载团队和项目配置"""
        try:
            config = IssuesConfig()
            # 加载项目映射配置
            boards_file = config.metadata_path / "boards_metadata.json"
            with open(boards_file, encoding="utf-8") as f:
                boards_data = json.load(f)
                self.TARGET_TEAMS = boards_data.get("team_to_project", {})

                # 补充intellistream团队映射（如果不存在）
                if "intellistream" not in self.TARGET_TEAMS:
                    self.TARGET_TEAMS["intellistream"] = 6
                    print("📝 补充intellistream团队映射到项目#6")

                print("✅ 加载项目映射配置")

            # 加载团队成员配置
            team_file = config.metadata_path / "team_members.json"
            with open(team_file, encoding="utf-8") as f:
                self.team_members = json.load(f)
                print("✅ 加载团队成员配置")

        except Exception as e:
            print(f"⚠️ 加载配置失败: {e}")
            self.TARGET_TEAMS = {}
            self.team_members = {}

    def get_repository_issues(self, owner=None, repo_name=None):
        """获取指定仓库的issues，使用GraphQL确保获取node_id"""
        if owner is None:
            owner = self.ORG
        if repo_name is None:
            repo_name = self.REPO

        print(f"🔍 获取仓库 {owner}/{repo_name} 的Issues...")

        query = f"""query($after: String) {{
    repository(owner: "{owner}", name: "{repo_name}") {{
        issues(first: 100, after: $after, states: [OPEN, CLOSED]) {{
            pageInfo {{
                hasNextPage
                endCursor
            }}
            nodes {{
                number
                id
                title
                state
                url
                repository {{
                    name
                    owner {{
                        login
                    }}
                }}
            }}
        }}
    }}
}}"""

        after = None
        all_issues = []

        while True:
            variables = {"after": after} if after else {}
            resp = requests.post(
                "https://api.github.com/graphql",
                json={"query": query, "variables": variables},
                headers=self.graphql_headers,
            )

            if resp.status_code != 200:
                print(f"  ❌ 获取 {repo_name} Issues失败: HTTP {resp.status_code}")
                return []

            data = resp.json()
            if "errors" in data:
                print(f"  ❌ GraphQL错误: {data['errors']}")
                return []

            issues = data.get("data", {}).get("repository", {}).get("issues", {})
            nodes = issues.get("nodes", [])

            if not nodes:
                break

            all_issues.extend(nodes)

            page_info = issues.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                break

            after = page_info.get("endCursor")

        print(f"  📥 {repo_name}: {len(all_issues)} 个Issues")
        return all_issues

    def get_all_repository_issues(self):
        """获取组织下所有仓库的issues，使用GraphQL确保获取node_id"""
        print("🔍 获取组织中所有仓库的Issues...")

        # 首先获取组织下的所有仓库
        repos_query = f"""query {{
    organization(login: "{self.ORG}") {{
        repositories(first: 100) {{
            nodes {{
                name
                owner {{
                    login
                }}
            }}
        }}
    }}
}}"""

        resp = requests.post(
            "https://api.github.com/graphql",
            json={"query": repos_query},
            headers=self.graphql_headers,
        )

        if resp.status_code != 200:
            print(f"❌ 获取仓库列表失败: HTTP {resp.status_code}")
            return []

        data = resp.json()
        if "errors" in data:
            print(f"❌ GraphQL错误: {data['errors']}")
            return []

        repositories = (
            data.get("data", {}).get("organization", {}).get("repositories", {}).get("nodes", [])
        )
        print(f"📁 发现 {len(repositories)} 个仓库")

        all_issues = []

        # 为每个仓库获取issues
        for repo in repositories:
            repo_name = repo["name"]
            owner = repo["owner"]["login"]

            print(f"🔍 获取仓库 {owner}/{repo_name} 的Issues...")

            query = f"""query($after: String) {{
    repository(owner: "{owner}", name: "{repo_name}") {{
        issues(first: 100, after: $after, states: [OPEN, CLOSED]) {{
            pageInfo {{
                hasNextPage
                endCursor
            }}
            nodes {{
                number
                id
                title
                state
                url
                repository {{
                    name
                    owner {{
                        login
                    }}
                }}
            }}
        }}
    }}
}}"""

            after = None
            repo_issues = []

            while True:
                variables = {"after": after} if after else {}
                resp = requests.post(
                    "https://api.github.com/graphql",
                    json={"query": query, "variables": variables},
                    headers=self.graphql_headers,
                )

                if resp.status_code != 200:
                    print(f"  ❌ 获取 {repo_name} Issues失败: HTTP {resp.status_code}")
                    break

                data = resp.json()
                if "errors" in data:
                    print(f"  ❌ GraphQL错误: {data['errors']}")
                    break

                issues = data.get("data", {}).get("repository", {}).get("issues", {})
                nodes = issues.get("nodes", [])

                if not nodes:
                    break

                repo_issues.extend(nodes)

                page_info = issues.get("pageInfo", {})
                if not page_info.get("hasNextPage"):
                    break

                after = page_info.get("endCursor")

            print(f"  📥 {repo_name}: {len(repo_issues)} 个Issues")
            all_issues.extend(repo_issues)

        print(f"✅ 总共获取到 {len(all_issues)} 个Issues")
        return all_issues

    def get_project_by_number(self, project_number):
        """根据项目编号获取项目信息"""
        query = f"""query {{
    organization(login: "{self.ORG}") {{
        projectV2(number: {project_number}) {{
            id title number
        }}
    }}
}}"""

        resp = requests.post(
            "https://api.github.com/graphql",
            headers=self.graphql_headers,
            json={"query": query},
        )

        if resp.status_code != 200:
            return None

        data = resp.json()
        if "errors" in data:
            return None

        return data.get("data", {}).get("organization", {}).get("projectV2")

    def get_project_id(self, project_number):
        """根据项目编号获取项目ID"""
        project_info = self.get_project_by_number(project_number)
        if project_info:
            return project_info.get("id")
        return None

    def execute_graphql(self, query, variables=None):
        """执行GraphQL查询或变更"""
        payload = {"query": query}
        if variables:
            payload["variables"] = variables

        resp = requests.post(
            "https://api.github.com/graphql", headers=self.graphql_headers, json=payload
        )

        if resp.status_code != 200:
            return {"errors": [f"HTTP {resp.status_code}: {resp.text}"]}

        return resp.json()

    def get_project_items(self, project_number):
        """获取项目中的所有items"""
        query = f"""query($after: String) {{
    organization(login: "{self.ORG}") {{
        projectV2(number: {project_number}) {{
            items(first: 100, after: $after) {{
                pageInfo {{
                    hasNextPage
                    endCursor
                }}
                nodes {{
                    id
                    content {{
                        __typename
                        ... on Issue {{
                            number
                            title
                            state
                            url
                            repository {{
                                name
                                owner {{
                                    login
                                }}
                            }}
                            author {{
                                login
                            }}
                            assignees(first: 10) {{
                                nodes {{
                                    login
                                }}
                            }}
                        }}
                        ... on PullRequest {{
                            number
                            title
                            state
                            url
                            repository {{
                                name
                                owner {{
                                    login
                                }}
                            }}
                            author {{
                                login
                            }}
                            assignees(first: 10) {{
                                nodes {{
                                    login
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
}}"""

        all_items = []
        after = None

        while True:
            variables = {"after": after} if after else {}
            resp = requests.post(
                "https://api.github.com/graphql",
                headers=self.graphql_headers,
                json={"query": query, "variables": variables},
            )

            if resp.status_code != 200:
                break

            data = resp.json()
            if "errors" in data:
                break

            items_data = (
                data.get("data", {}).get("organization", {}).get("projectV2", {}).get("items", {})
            )
            nodes = items_data.get("nodes", [])
            all_items.extend(nodes)

            page_info = items_data.get("pageInfo", {})
            if page_info.get("hasNextPage"):
                after = page_info.get("endCursor")
                time.sleep(0.2)  # 避免API限制
            else:
                break

        return all_items

    def add_issue_to_project(self, project_id, issue_global_id):
        """将issue添加到项目"""
        mutation = """mutation($projectId: ID!, $contentId: ID!) {
    addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item {
            id
        }
    }
}"""
        variables = {"projectId": project_id, "contentId": issue_global_id}
        resp = requests.post(
            "https://api.github.com/graphql",
            headers=self.graphql_headers,
            json={"query": mutation, "variables": variables},
        )

        if resp.status_code != 200:
            return False, resp.text

        data = resp.json()
        if "errors" in data:
            return False, data["errors"]

        return True, data.get("data", {}).get("addProjectV2ItemById", {})

    def delete_project_item(self, project_id, item_id):
        """从项目中删除item"""
        mutation = """mutation($projectId: ID!, $itemId: ID!) {
    deleteProjectV2Item(input: {projectId: $projectId, itemId: $itemId}) {
        deletedItemId
    }
}"""
        variables = {"projectId": project_id, "itemId": item_id}
        resp = requests.post(
            "https://api.github.com/graphql",
            headers=self.graphql_headers,
            json={"query": mutation, "variables": variables},
        )

        if resp.status_code != 200:
            return False, resp.text

        data = resp.json()
        if "errors" in data:
            return False, data["errors"]

        return True, data.get("data", {}).get("deleteProjectV2Item", {})

    def is_user_in_team(self, username, team_slug):
        """检查用户是否在指定团队中"""
        if not self.team_members:
            return False

        team_info = self.team_members.get(team_slug, {})
        members = team_info.get("members", [])

        if members:
            if isinstance(members[0], dict):
                member_usernames = [
                    member.get("username", member.get("login", "")) for member in members
                ]
            else:
                member_usernames = members

            return username in member_usernames

        return False

    def get_target_project_for_user(self, username):
        """根据用户获取目标项目"""
        for team_slug, project_number in self.TARGET_TEAMS.items():
            if self.is_user_in_team(username, team_slug):
                return team_slug, project_number
        return None, None


# 为了向后兼容，保留旧的类名
IssueProjectMover = GitHubProjectManager
