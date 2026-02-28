---
name: sage-github-manager
description: Agent for GitHub issue management CLI behavior, storage, and command UX.
argument-hint: Provide command path, issue behavior, and expected CLI output.
tools: ['vscode', 'execute', 'read', 'agent', 'edit', 'search', 'web', 'todo', 'vscode.mermaid-chat-features/renderMermaidDiagram', 'github.vscode-pull-request-github/issue_fetch', 'github.vscode-pull-request-github/suggest-fix', 'github.vscode-pull-request-github/searchSyntax', 'github.vscode-pull-request-github/doSearch', 'github.vscode-pull-request-github/renderIssues', 'github.vscode-pull-request-github/activePullRequest', 'github.vscode-pull-request-github/openPullRequest', 'ms-azuretools.vscode-containers/containerToolsConfig', 'ms-python.python/getPythonEnvironmentInfo', 'ms-python.python/getPythonExecutableCommand', 'ms-python.python/installPythonPackage', 'ms-python.python/configurePythonEnvironment', 'ms-toolsai.jupyter/configureNotebook', 'ms-toolsai.jupyter/listNotebookPackages', 'ms-toolsai.jupyter/installNotebookPackages', 'ms-vscode.cpp-devtools/Build_CMakeTools', 'ms-vscode.cpp-devtools/RunCtest_CMakeTools', 'ms-vscode.cpp-devtools/ListBuildTargets_CMakeTools', 'ms-vscode.cpp-devtools/ListTests_CMakeTools']
---

# Sage GitHub Manager Agent

## Scope
- CLI and orchestration in `src/sage_github/`.
- Persistence and helper modules under same package.

## Rules
- Keep fail-fast behavior; no silent fallbacks.
- Keep dependency declarations in `pyproject.toml`.
- Do not create new local virtual environments (`venv`/`.venv`); use the existing configured Python environment.
- Preserve UX contracts for `github-manager` / `gh-issues`.
- Keep helpers single-purpose and typed.

## Workflow
1. Implement focused fix/feature.
2. Add/update tests under `tests/`.
3. Validate lint/type/tests before handoff.

## Polyrepo coordination rules

- Treat this repository as the only local source tree; do not assume sibling repositories exist.
- If a task spans multiple repositories, implement only this repo and explicitly list follow-up repo/version-bump actions.
- Do not create `venv`/`.venv`; always use the existing configured Python environment.
