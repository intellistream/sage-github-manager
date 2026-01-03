#!/usr/bin/env python3
"""
GitHub Issues操作执行脚本
基于AI分析结果执行GitHub操作
"""

from pathlib import Path
import sys
import time

import requests


class GitHubIssuesExecutor:
    def __init__(self):
        # 使用IssuesConfig获取token
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from ..config import IssuesConfig

        config = IssuesConfig()
        self.github_token = config.github_token

        if not self.github_token:
            print("❌ 请设置GITHUB_TOKEN环境变量或配置IssuesConfig")
            sys.exit(1)

        self.repo = "intellistream/SAGE"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json",
        }

        # 使用统一的.sage/issues目录
        from sage.common.config.output_paths import get_sage_paths

        sage_paths = get_sage_paths()
        self.output_dir = sage_paths.issues_dir / "github_ops"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.duplicate_groups = []
        self.label_recommendations = {}

        # 初始化标准化标签（不依赖AI分析结果）
        self.init_standard_labels()

    def init_standard_labels(self):
        """初始化标准化标签（不依赖AI分析结果）"""
        # 标准化的标签映射
        self.standard_labels = {
            # 类型标签
            "bug": {"color": "d73a4a", "description": "Bug report"},
            "feature": {"color": "0075ca", "description": "New feature"},
            "enhancement": {
                "color": "a2eeef",
                "description": "Enhancement to existing feature",
            },
            "documentation": {"color": "0075ca", "description": "Documentation"},
            "refactor": {"color": "d4c5f9", "description": "Code refactoring"},
            "task": {"color": "e4e669", "description": "General task"},
            "algorithm": {"color": "7057ff", "description": "Algorithm related"},
            "dataset": {"color": "006b75", "description": "Dataset related"},
            "literature-review": {
                "color": "fbca04",
                "description": "Literature review",
            },
            # 优先级标签
            "priority:high": {"color": "d93f0b", "description": "High priority"},
            "priority:medium": {"color": "fbca04", "description": "Medium priority"},
            "priority:low": {"color": "0e8a16", "description": "Low priority"},
            # 组件标签
            "component:core": {"color": "5319e7", "description": "Core component"},
            "component:cli": {"color": "1d76db", "description": "CLI component"},
            "component:frontend": {
                "color": "0052cc",
                "description": "Frontend component",
            },
            "component:docs": {
                "color": "0075ca",
                "description": "Documentation component",
            },
            "component:testing": {
                "color": "c2e0c6",
                "description": "Testing component",
            },
            # 功能标签
            "rag": {"color": "ff6b6b", "description": "RAG related"},
            "memory": {"color": "ffa500", "description": "Memory related"},
            "retrieval": {"color": "9932cc", "description": "Retrieval related"},
            "graph": {"color": "2e8b57", "description": "Graph related"},
            "embedding": {"color": "4682b4", "description": "Embedding related"},
            "distributed": {"color": "8b4513", "description": "Distributed system"},
            "engine": {"color": "ff4500", "description": "Engine related"},
            "operator": {"color": "dda0dd", "description": "Operator related"},
            "pipeline": {"color": "20b2aa", "description": "Pipeline related"},
            "job": {"color": "cd853f", "description": "Job related"},
            "api": {"color": "32cd32", "description": "API related"},
            "config": {"color": "ffd700", "description": "Configuration related"},
            "testing": {"color": "98fb98", "description": "Testing related"},
        }

    def load_ai_analysis_results(self):
        """加载AI分析结果（可选）"""
        print("🔍 寻找AI分析结果...")

        # 查找最新的AI分析文件
        analysis_files = []

        # 重复检测分析
        duplicate_files = list(self.output_dir.glob("duplicate_analysis_*.md"))
        if duplicate_files:
            latest_duplicate = max(duplicate_files, key=lambda x: x.stat().st_mtime)
            analysis_files.append(("重复检测", latest_duplicate))

        # 标签优化分析
        label_files = list(self.output_dir.glob("label_analysis_*.md"))
        if label_files:
            latest_label = max(label_files, key=lambda x: x.stat().st_mtime)
            analysis_files.append(("标签优化", latest_label))

        # 综合管理分析
        management_files = list(self.output_dir.glob("comprehensive_management_*.md"))
        if management_files:
            latest_management = max(management_files, key=lambda x: x.stat().st_mtime)
            analysis_files.append(("综合管理", latest_management))

        if not analysis_files:
            print("⚠️ 未找到AI分析结果文件，仅支持标签创建功能")
            return

        print(f"✅ 找到 {len(analysis_files)} 个AI分析文件:")
        for analysis_type, file_path in analysis_files:
            print(f"   📄 {analysis_type}: {file_path.name}")

        # 解析分析结果
        self.parse_analysis_files(analysis_files)

    def parse_analysis_files(self, analysis_files):
        """解析AI分析文件"""
        print("\n📖 解析AI分析结果...")

        for analysis_type, file_path in analysis_files:
            try:
                content = file_path.read_text(encoding="utf-8")

                if "重复检测" in analysis_type:
                    self.parse_duplicate_analysis(content)
                elif "标签优化" in analysis_type:
                    self.parse_label_analysis(content)
                elif "综合管理" in analysis_type:
                    self.parse_management_analysis(content)

            except Exception as e:
                print(f"❌ 解析 {analysis_type} 文件失败: {e}")

        print(
            f"✅ 解析完成: 找到 {len(self.duplicate_groups)} 个重复组, {len(self.label_recommendations)} 个标签建议"
        )

    def parse_duplicate_analysis(self, content):
        """解析重复检测分析结果"""
        import re

        # 查找重复组信息 - 匹配 "Issue #xxx 和 Issue #yyy 重复" 这样的模式
        duplicate_patterns = [
            r"Issue #(\d+) 和 Issue #(\d+) 重复",
            r"#(\d+) 和 #(\d+) 是重复的",
            r"issues #(\d+) 和 #(\d+) 重复",
            r"Issue (\d+) 与 Issue (\d+) 重复",
        ]

        for pattern in duplicate_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                issue1, issue2 = int(match[0]), int(match[1])

                # 找到现有的重复组或创建新的
                found_group = None
                for group in self.duplicate_groups:
                    if (
                        issue1 in [group["main"]] + group["duplicates"]
                        or issue2 in [group["main"]] + group["duplicates"]
                    ):
                        found_group = group
                        break

                if found_group:
                    # 添加到现有组
                    if issue1 not in [found_group["main"]] + found_group["duplicates"]:
                        found_group["duplicates"].append(issue1)
                    if issue2 not in [found_group["main"]] + found_group["duplicates"]:
                        found_group["duplicates"].append(issue2)
                else:
                    # 创建新组，较小的号码作为主issue
                    main_issue = min(issue1, issue2)
                    duplicate_issue = max(issue1, issue2)
                    self.duplicate_groups.append(
                        {
                            "main": main_issue,
                            "duplicates": [duplicate_issue],
                            "reason": "AI检测出的重复issues",
                        }
                    )

    def parse_label_analysis(self, content):
        """解析标签优化分析结果"""
        import re

        # 查找标签建议 - 匹配 "Issue #xxx: 建议标签: tag1, tag2" 这样的模式
        label_patterns = [
            r"Issue #(\d+)[：:]\s*建议标签[：:]\s*([^\n]+)",
            r"#(\d+)[：:]\s*标签建议[：:]\s*([^\n]+)",
            r"Issue (\d+)[：:]\s*推荐标签[：:]\s*([^\n]+)",
        ]

        for pattern in label_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                issue_num = int(match[0])
                labels_str = match[1].strip()

                # 解析标签列表
                labels = [label.strip() for label in labels_str.split(",") if label.strip()]

                if labels:
                    self.label_recommendations[issue_num] = labels

    def parse_management_analysis(self, content):
        """解析综合管理分析结果"""
        # 综合管理分析可能包含重复检测和标签建议
        self.parse_duplicate_analysis(content)
        self.parse_label_analysis(content)

    def create_standard_labels(self):
        """创建标准化标签"""
        print("🏷️ 创建标准化标签...")

        for label_name, label_info in self.standard_labels.items():
            self.create_or_update_label(label_name, label_info)
            time.sleep(0.1)  # 避免API限制

    def create_or_update_label(self, name, info):
        """创建或更新标签（智能合并现有标签）"""
        url = f"https://api.github.com/repos/{self.repo}/labels/{name}"

        # 检查标签是否存在
        response = requests.get(url, headers=self.headers)

        data = {
            "name": name,
            "color": info["color"],
            "description": info["description"],
        }

        if response.status_code == 200:
            # 标签已存在，检查是否需要更新
            existing_label = response.json()

            # 如果颜色和描述都相同，跳过更新
            if (
                existing_label.get("color") == info["color"]
                and existing_label.get("description") == info["description"]
            ):
                print(f"  ⏭️ 标签已是最新: {name}")
                return

            # 更新标签
            response = requests.patch(url, headers=self.headers, json=data)
            if response.status_code == 200:
                print(f"  ✅ 更新标签: {name}")
            else:
                print(f"  ❌ 更新失败: {name} - {response.text}")
        else:
            # 创建新标签
            create_url = f"https://api.github.com/repos/{self.repo}/labels"
            response = requests.post(create_url, headers=self.headers, json=data)
            if response.status_code == 201:
                print(f"  ✅ 创建标签: {name}")
            else:
                print(f"  ❌ 创建失败: {name} - {response.text}")

    def get_issue_details(self, issue_number):
        """获取issue详情"""
        url = f"https://api.github.com/repos/{self.repo}/issues/{issue_number}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ 获取issue #{issue_number}失败: {response.text}")
            return None

    def close_duplicate_issue(self, issue_number, main_issue_number, reason):
        """关闭重复issue"""
        print(f"  🔄 关闭重复issue #{issue_number} (合并到 #{main_issue_number})")

        # 添加评论说明合并原因
        comment_url = f"https://api.github.com/repos/{self.repo}/issues/{issue_number}/comments"
        comment_data = {
            "body": f"✨ **Issues合并通知**\\n\\n这个issue与 #{main_issue_number} 重复，原因：{reason}\\n\\n已自动合并到主issue中，请在 #{main_issue_number} 中继续讨论。"
        }

        comment_response = requests.post(comment_url, headers=self.headers, json=comment_data)
        if comment_response.status_code == 201:
            print("    ✅ 添加合并说明评论")
        else:
            print(f"    ❌ 添加评论失败: {comment_response.text}")

        # 关闭issue
        url = f"https://api.github.com/repos/{self.repo}/issues/{issue_number}"
        close_data = {"state": "closed", "labels": ["duplicate"]}  # 添加重复标签

        response = requests.patch(url, headers=self.headers, json=close_data)
        if response.status_code == 200:
            print(f"    ✅ 成功关闭issue #{issue_number}")
            return True
        else:
            print(f"    ❌ 关闭失败: {response.text}")
            return False

    def update_main_issue(self, main_issue_number, duplicates, reason):
        """更新主issue，添加合并信息"""
        issue = self.get_issue_details(main_issue_number)
        if not issue:
            return False

        # 添加合并说明评论
        duplicate_list = ", ".join([f"#{num}" for num in duplicates])
        comment_url = (
            f"https://api.github.com/repos/{self.repo}/issues/{main_issue_number}/comments"
        )
        comment_data = {
            "body": f"🔗 **Issues合并更新**\\n\\n以下重复issues已合并到此issue：{duplicate_list}\\n\\n合并原因：{reason}\\n\\n请在此issue中统一讨论相关内容。"
        }

        response = requests.post(comment_url, headers=self.headers, json=comment_data)
        if response.status_code == 201:
            print(f"    ✅ 主issue #{main_issue_number} 添加合并说明")
            return True
        else:
            print(f"    ❌ 主issue更新失败: {response.text}")
            return False

    def update_issue_labels(self, issue_number, new_labels, replace=False):
        """智能更新issue标签（默认追加，不替换现有标签）"""
        # 首先获取当前issue的信息
        issue = self.get_issue_details(issue_number)
        if not issue:
            return False

        # 检查issue是否已关闭
        if issue.get("state") == "closed":
            print(f"  ⏭️ 跳过已关闭的issue: #{issue_number}")
            return False

        # 获取现有标签
        existing_labels = [label["name"] for label in issue.get("labels", [])]

        if replace:
            # 替换模式：完全替换现有标签
            final_labels = new_labels
        else:
            # 追加模式：保留现有标签，添加新标签
            final_labels = list(set(existing_labels + new_labels))

        # 如果标签没有变化，跳过更新
        if set(final_labels) == set(existing_labels):
            print(f"  ⏭️ 标签无需更新: #{issue_number}")
            return True

        url = f"https://api.github.com/repos/{self.repo}/issues/{issue_number}"
        data = {"labels": final_labels}

        response = requests.patch(url, headers=self.headers, json=data)
        if response.status_code == 200:
            added_labels = set(final_labels) - set(existing_labels)
            if added_labels:
                print(f"  ✅ 添加标签: #{issue_number} -> {', '.join(added_labels)}")
            return True
        else:
            print(f"  ❌ 标签更新失败: #{issue_number} - {response.text}")
            return False

    def process_duplicates(self):
        """处理重复issues（跳过已关闭的issues）"""
        print("🔄 处理重复issues...")

        if not self.duplicate_groups:
            print("⚠️ 没有发现重复的issues")
            return

        for group in self.duplicate_groups:
            main_issue = group["main"]
            duplicates = group["duplicates"]
            reason = group["reason"]

            # 检查主issue是否已关闭
            main_issue_details = self.get_issue_details(main_issue)
            if main_issue_details and main_issue_details.get("state") == "closed":
                print(f"⏭️ 跳过已关闭的主issue #{main_issue}")
                continue

            print(f"\\n📋 处理重复组: 主issue #{main_issue}")
            print(f"   重复issues: {', '.join([f'#{num}' for num in duplicates])}")
            print(f"   合并原因: {reason}")

            # 检查重复issues是否已关闭
            active_duplicates = []
            for duplicate in duplicates:
                duplicate_details = self.get_issue_details(duplicate)
                if duplicate_details and duplicate_details.get("state") == "open":
                    active_duplicates.append(duplicate)
                else:
                    print(f"   ⏭️ 跳过已关闭的重复issue #{duplicate}")

            if not active_duplicates:
                print("   ⚠️ 所有重复issues都已关闭，跳过处理")
                continue

            # 更新主issue
            if self.update_main_issue(main_issue, active_duplicates, reason):
                # 关闭重复issues
                for duplicate in active_duplicates:
                    self.close_duplicate_issue(duplicate, main_issue, reason)
                    time.sleep(1)  # 避免API限制

        print("\\n✅ 重复issues处理完成!")

    def generate_labels_update_plan(self):
        """基于AI分析结果生成标签更新计划"""
        # 如果有AI分析的标签建议，使用AI分析结果
        if self.label_recommendations:
            print(f"📋 使用AI分析的标签建议: {len(self.label_recommendations)} 个issues")
            return self.label_recommendations

        # 如果没有AI分析结果，返回空计划
        print("⚠️ 没有AI分析的标签建议，跳过标签更新")
        return {}

    def update_all_labels(self):
        """基于AI分析批量更新issues标签"""
        print("🏷️ 基于AI分析批量更新issues标签...")

        label_updates = self.generate_labels_update_plan()

        if not label_updates:
            print("⚠️ 没有可用的标签更新计划")
            return

        for issue_number, labels in label_updates.items():
            print(f"\n📋 更新issue #{issue_number}")
            if self.update_issue_labels(issue_number, labels, replace=False):
                time.sleep(0.5)  # 避免API限制

        print("\n✅ 标签更新完成!")

    def generate_summary_report(self):
        """生成处理总结报告"""
        report_content = f"""# Issues整理处理报告

**处理时间**: {self.get_current_time()}
**处理范围**: SAGE项目开放issues

## 📊 处理统计

### 🔄 重复Issues处理
- 重复组数量: {len(self.duplicate_groups)} 组
- 合并的issues数量: {sum(len(group["duplicates"]) for group in self.duplicate_groups)} 个
- 保留的主issues: {len(self.duplicate_groups)} 个

### 🏷️ 标签优化
- 创建标准化标签: {len(self.standard_labels)} 个
- 更新issues标签: {len(self.generate_labels_update_plan())} 个

## 📋 重复Issues合并详情

"""
        for i, group in enumerate(self.duplicate_groups, 1):
            report_content += f"""### 组 {i}: #{group["main"]}
- **主issue**: #{group["main"]}
- **合并的重复issues**: {", ".join([f"#{num}" for num in group["duplicates"]])}
- **合并原因**: {group["reason"]}

"""

        report_content += """## 🎯 标签体系

### 类型标签
- `bug`: Bug报告
- `feature`: 新功能
- `enhancement`: 功能增强
- `documentation`: 文档相关
- `refactor`: 代码重构
- `task`: 一般任务
- `algorithm`: 算法相关
- `dataset`: 数据集相关

### 优先级标签
- `priority:high`: 高优先级
- `priority:medium`: 中优先级
- `priority:low`: 低优先级

### 组件标签
- `component:core`: 核心组件
- `component:cli`: CLI组件
- `component:frontend`: 前端组件
- `component:docs`: 文档组件
- `component:testing`: 测试组件

### 功能标签
- `rag`: RAG相关
- `memory`: 内存相关
- `retrieval`: 检索相关
- `distributed`: 分布式系统
- `engine`: 引擎相关
- `job`: 作业相关
- `api`: API相关
- `config`: 配置相关

## ✅ 处理结果

1. **重复Issues合并**: 将相似和重复的issues合并到主issue中，避免分散讨论
2. **标签标准化**: 建立统一的标签体系，便于issues分类和查找
3. **优先级设置**: 根据issues重要性设置优先级，便于开发计划安排
4. **组件分类**: 按照项目组件对issues进行分类，便于责任分工

所有处理都已同步到GitHub仓库，可以在项目issues页面查看更新结果。
"""

        # 统一输出到.sage/issues目录
        from sage.common.config.output_paths import get_sage_paths

        sage_paths = get_sage_paths()
        output_dir = sage_paths.issues_dir
        output_dir.mkdir(exist_ok=True)
        report_path = output_dir / "processing_report.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"✅ 处理报告已生成: {report_path}")
        return report_path

    def get_current_time(self):
        """获取当前时间"""
        from datetime import datetime

        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run_full_management(self):
        """运行完整的issues管理流程（基于AI分析）"""
        print("🚀 开始基于AI分析的GitHub Issues管理...")

        # 加载AI分析结果
        self.load_ai_analysis_results()

        try:
            actions_performed = []

            # 1. 创建标准化标签（总是执行）
            print("\n🏷️ 创建/更新标准化标签...")
            self.create_standard_labels()
            actions_performed.append("标准化标签")

            # 2. 处理重复issues（仅在有AI分析结果时）
            if self.duplicate_groups:
                print("\n🔄 处理重复issues...")
                self.process_duplicates()
                actions_performed.append("重复issues处理")
            else:
                print("\n⚠️ 未发现重复issues，跳过合并操作")

            # 3. 批量更新标签（仅在有AI分析结果时）
            if self.label_recommendations:
                print("\n🏷️ 批量更新issues标签...")
                self.update_all_labels()
                actions_performed.append("标签更新")
            else:
                print("\n⚠️ 没有AI标签建议，跳过标签更新")

            # 4. 生成处理报告
            print("\n📋 生成处理报告...")
            report_path = self.generate_summary_report()
            actions_performed.append("报告生成")

            print(
                f"""
🎉 Issues管理完成！

📈 执行的操作:
{chr(10).join([f"- {action}" for action in actions_performed])}

📊 处理统计:
- 标准化标签: {len(self.standard_labels)} 个
- 重复组处理: {len(self.duplicate_groups)} 组
- 标签更新: {len(self.label_recommendations)} 个issues
- 处理报告: {report_path}

🔗 在GitHub上查看更新结果:
https://github.com/{self.repo}/issues

✨ 建议后续操作:
1. 检查GitHub issues页面确认更新结果
2. 使用新的标签体系来管理future issues
3. 运行AI分析生成更多管理建议
"""
            )

        except Exception as e:
            print(f"❌ 处理过程中出现错误: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    manager = GitHubIssuesExecutor()

    # 检查参数
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "labels":
            manager.create_standard_labels()
        elif command == "duplicates":
            manager.process_duplicates()
        elif command == "update-labels":
            manager.update_all_labels()
        elif command == "report":
            manager.generate_summary_report()
        else:
            print("用法: python3 manage_github_issues.py [labels|duplicates|update-labels|report]")
    else:
        # 运行完整流程
        manager.run_full_management()
