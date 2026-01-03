# VS Code 工作区配置说明

此目录包含 sage-github-manager 项目的 VS Code 工作区配置。

## 📁 配置文件

### settings.json
**用途**: VS Code 工作区设置

**配置内容**:
- ✅ Python 解释器路径 (`.venv/bin/python`)
- ✅ Pylance 类型检查 (basic 模式)
- ✅ Pytest 测试框架集成
- ✅ Ruff 作为默认格式化器
- ✅ 保存时自动格式化和修复
- ✅ 行宽限制 100 字符
- ✅ 自动清理尾随空白和文件末尾空行
- ✅ 隐藏 `__pycache__` 等缓存目录
- ✅ Mypy 类型检查参数
- ✅ GitHub Copilot 启用

### extensions.json
**用途**: 推荐的 VS Code 扩展

**推荐扩展**:
1. `ms-python.python` - Python 语言支持
2. `ms-python.vscode-pylance` - 高级 Python 语言服务
3. `charliermarsh.ruff` - Ruff 格式化和检查
4. `ms-python.mypy-type-checker` - Mypy 类型检查
5. `github.copilot` - GitHub Copilot AI 助手
6. `github.copilot-chat` - Copilot 聊天界面
7. `github.vscode-pull-request-github` - GitHub PR 集成
8. `tamasfe.even-better-toml` - TOML 文件支持
9. `redhat.vscode-yaml` - YAML 文件支持
10. `yzhang.markdown-all-in-one` - Markdown 增强

VS Code 打开项目时会自动提示安装这些扩展。

### launch.json
**用途**: 调试配置

**可用配置**:
1. **Python: Current File** - 调试当前打开的 Python 文件
2. **Python: CLI** - 调试 CLI 命令 (github-manager)
3. **Python: Pytest (Current File)** - 调试当前测试文件
4. **Python: Pytest (All Tests)** - 调试所有测试

**使用方法**:
1. 打开要调试的文件
2. 按 `F5` 或点击 "Run and Debug" 面板
3. 选择相应的调试配置
4. 设置断点 (点击行号左侧)

### tasks.json
**用途**: VS Code 任务配置

**可用任务**:
- `Install Dev Dependencies` - 安装开发依赖
- `Run Tests` - 运行测试 (默认测试任务)
- `Run Tests with Coverage` - 运行测试并生成覆盖率报告
- `Format Code (Ruff)` - 格式化代码
- `Lint Code (Ruff)` - 检查代码
- `Type Check (Mypy)` - 类型检查
- `Run Pre-commit Hooks` - 运行所有预提交钩子
- `Clean Build Artifacts` - 清理构建产物

**使用方法**:
1. 按 `Ctrl+Shift+P` (Linux/Windows) 或 `Cmd+Shift+P` (Mac)
2. 输入 "Tasks: Run Task"
3. 选择要运行的任务

或者使用快捷键:
- `Ctrl+Shift+B` - 运行默认构建任务
- `Ctrl+Shift+T` - 运行默认测试任务

## 🚀 首次设置

打开项目后，VS Code 会自动:

1. **提示安装推荐扩展** - 点击 "Install All" 安装所有推荐扩展
2. **检测 Python 解释器** - 选择 `.venv/bin/python` (如果存在)
3. **加载 Copilot 指令** - 从 `.github/copilot-instructions.md` 加载项目上下文

如果没有虚拟环境，运行:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows
pip install -e ".[dev]"
```

## ⚙️ 自动化功能

### 保存时自动执行:
- ✅ **代码格式化** (Ruff format)
- ✅ **导入排序** (Ruff isort)
- ✅ **自动修复** (Ruff --fix)
- ✅ **清理尾随空白**
- ✅ **添加文件末尾空行**

### 实时反馈:
- ✅ **类型检查** (Mypy) - 显示类型错误
- ✅ **代码检查** (Ruff) - 显示代码问题
- ✅ **测试状态** (Pytest) - 运行测试并显示结果

## 🎯 快捷键

| 快捷键 | 功能 |
|--------|------|
| `F5` | 开始调试 |
| `Ctrl+Shift+P` | 命令面板 |
| `Ctrl+Shift+B` | 运行构建任务 |
| `Ctrl+Shift+T` | 运行测试任务 |
| `Shift+Alt+F` | 格式化文档 |
| `Ctrl+Shift+I` | 格式化选定内容 |
| `F12` | 跳转到定义 |
| `Alt+F12` | 查看定义 (不跳转) |
| `Shift+F12` | 查找所有引用 |

## 📖 相关文档

- **项目文档**: `../README.md`
- **开发指南**: `../DEVELOPMENT.md`
- **设置指南**: `../SETUP_GUIDE.md`
- **Copilot 指令**: `../.github/copilot-instructions.md`

## 🐛 故障排除

### 扩展未安装
- 手动打开扩展面板 (Ctrl+Shift+X)
- 搜索并安装 `extensions.json` 中列出的扩展

### Python 解释器未找到
- 按 `Ctrl+Shift+P` → "Python: Select Interpreter"
- 选择 `.venv/bin/python`
- 如果没有虚拟环境，先创建: `python -m venv .venv`

### Ruff 格式化不工作
- 确保已安装 Ruff 扩展: `charliermarsh.ruff`
- 检查 `ruff.toml` 文件存在
- 重新加载 VS Code 窗口

### 测试发现失败
- 确保已安装开发依赖: `pip install -e ".[dev]"`
- 检查 `pytest.ini` 配置
- 查看 "Python" 输出面板的错误信息

### Copilot 未加载指令
- 确认文件位于 `.github/copilot-instructions.md` (不是 `.github-copilot-instructions.md`)
- 重启 VS Code
- 检查 Copilot 扩展已启用
