# Repository Guidelines

## Project Structure & Module Organization
- `src/` – CLI source modules (`cli.py`, `build.py`, `config.py`, etc.).
- `tests/` – Pytest suite covering CLI flows, conflict bundles, guards, and provenance.
- `project-handbook/` – Sprint assets, ADRs, and automation (run `make -C project-handbook …`).
- `scripts/` – Developer utilities (e.g., `setup-demo-repo.sh` for sandbox repos).
- Runtime artefacts live under `.forked/` (logs, worktrees, guard reports) and are gitignored.

## Build, Test, and Development Commands
- `poetry install --with dev` – Sync dependencies inside the virtualenv.
- `python -m pip install -e .` – Editable install for invoking the global `forked` CLI.
- `poetry run ruff check .` / `poetry run ruff format --check .` – Lint and formatting audits.
- `poetry run mypy` – Type-check the entire `src/` tree (untyped defs included).
- `poetry run pytest` – Execute the full test suite.
- `poetry build` / `poetry publish --build` – Produce and ship PyPI artefacts (set `POETRY_PYPI_TOKEN_PYPI`).
- `poetry run make -C project-handbook help` – Discover handbook automation (dashboards, status, etc.).
- GitHub Actions publishes automatically on `v*` tags using `.github/workflows/publish.yml`; add `PYPI_API_TOKEN` to repo secrets first.

## Coding Style & Naming Conventions
- Python 3.10+, 4-space indentation, 100-character line limit (enforced by Ruff).
- Prefer type hints; mypy runs with `check_untyped_defs`.
- Modules live under `src/forked/`; avoid duplicating top-level modules that could collide with third-party packages.
- Use descriptive snake_case for variables/functions, CapWords for classes.

## Testing Guidelines
- Write Pytest tests under `tests/`, mirroring module names (e.g., `test_status_json.py` for `cli.status`).
- Keep fixtures in `tests/conftest.py`; reuse the sandbox git repo helper when possible.
- Validate changes with `poetry run pytest` plus targeted commands (e.g., `pytest tests/test_guard_report_v2.py -q`).

## Commit & Pull Request Guidelines
- Commit messages: imperative present tense (`feat: add status json flag`).
- Reference related work items or ADRs when applicable (`Refs: TASK-007`, `ADR-0004`).
- Pull requests should summarize purpose, list affected directories, and note validation commands executed.
- Include screenshots or JSON snippets when modifying `.forked/` outputs or handbook dashboards.

## Agent-Specific Tips
- Regenerate demo repos via `./scripts/setup-demo-repo.sh demo-forked` before sanity runs.
- Never edit generated artefacts (`.forked/**`, `status/daily/**`) manually—use the corresponding CLI or Make targets.
