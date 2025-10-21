---
title: Adopt src Layout - Implementation Steps
type: implementation
date: 2025-10-21
task_id: TASK-009
tags: [implementation]
links: []
---

# Implementation Steps: Adopt src/ Layout

## Step 1: File Tree Migration
- [ ] Create `src/` directory and move the existing `forked/` package into `src/forked/`.
- [ ] Update `__init__.py` paths, ensure package imports (e.g., `from forked import cli`) still resolve when run via Poetry.
- [ ] Adjust `.gitignore` entries if new build artifacts appear.

## Step 2: Packaging Metadata
- [ ] Update `pyproject.toml` so `Poetry` includes packages from `src` (`packages = [{ include = "forked", from = "src" }]`).
- [ ] Confirm console script entry points still reference `forked.cli:app`.

## Step 3: Import Path Audit
- [ ] Update tests to import using the installed package (`from forked.cli import app`) rather than relying on relative paths.
- [ ] Check scripts/automation (e.g., `project-handbook/process/automation`) for any direct filesystem imports that need adjustment.
- [ ] Ensure `PYTHONPATH` assumptions in make targets or scripts are removed/updated.

## Step 4: Tooling & Docs
- [ ] Verify `poetry run ruff check .` and `poetry run mypy ...` still succeed after the move.
- [ ] Update README/development docs to mention the `src/` layout and any command changes.
- [ ] Update sanity checklist if necessary (e.g., references to `src/forked/cli.py`).

## Step 5: Follow-up Checks
- [ ] Run existing tests (`poetry run pytest`).
- [ ] Execute sanity workflow (demo repo) to ensure CLI still functions.
