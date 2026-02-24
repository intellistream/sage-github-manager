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
