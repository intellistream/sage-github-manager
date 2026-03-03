# GitHub Issues Manager Copilot Instructions

## Scope
- `sage-github-manager` is a standalone CLI for GitHub issue management.
- Main usage targets SAGE issue workflows, but code remains reusable.

## Critical rules
- No fallback logic: fail fast with explicit error messages.
- Keep dependencies declared in `pyproject.toml`; no ad-hoc manual dependency drift.
- Do not create new local virtual environments (`venv`/`.venv`) in this repo; use the existing configured Python environment.
- Preserve config/data conventions under `~/.github-manager/...`.
- Keep typed APIs and clear CLI behavior (`github-manager` / `gh-issues`).

## Implementation focus
- CLI in `src/sage_github/cli.py`; orchestration in `manager.py`; persistence in `issue_data_manager.py`.
- Helpers in `src/sage_github/helpers/` should stay single-purpose.

## Workflow
1. Implement focused changes and keep command UX stable.
2. Add tests under `tests/` for new behavior.
3. Run lint/type/test checks before handoff.

## Polyrepo coordination (mandatory)

- This repository is an independent SAGE sub-repository and is developed/released independently.
- Do not assume sibling source directories exist locally in `intellistream/SAGE`.
- For cross-repo rollout, publish this repo/package first, then bump the version pin in `SAGE/packages/sage/pyproject.toml` when applicable.
- Do not add local editable installs of other SAGE sub-packages in setup scripts or docs.

## 🚫 NEVER_CREATE_DOT_VENV_MANDATORY

- 永远不要创建 `.venv` 或 `venv`（无任何例外）。
- NEVER create `.venv`/`venv` in this repository under any circumstance.
- 必须复用当前已配置的非-venv Python 环境（如现有 conda 环境）。
- If any script/task suggests creating a virtualenv, skip that step and continue with the existing environment.
