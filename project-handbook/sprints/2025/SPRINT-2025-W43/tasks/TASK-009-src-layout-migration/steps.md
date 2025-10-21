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
- [ ] Move all runtime modules so they live directly under `src/` (remove the nested `forked/` directory).
- [ ] Update any `__init__.py` shims and adjust imports to use top-level modules (e.g., `import cli`).
- [ ] Adjust `.gitignore` entries if new build artifacts appear.

## Step 2: Packaging Metadata
- [ ] Update `pyproject.toml` so Poetry includes the flattened modules (e.g., `packages = [{ include = "*", from = "src" }]`).
- [ ] Confirm console script entry points reference the new module path (`forked = "cli:app"`).

## Step 3: Import Path Audit
- [ ] Update tests to import the new top-level modules (`from cli import app`, etc.).
- [ ] Check scripts/automation (e.g., `project-handbook/process/automation`) for any direct filesystem imports that need adjustment.
- [ ] Ensure `PYTHONPATH` assumptions in make targets or scripts are removed/updated.

## Step 4: Tooling & Docs
- [ ] Verify `poetry run ruff check .` and `poetry run mypy` still succeed after the move.
- [ ] Update README/development docs to mention the flattened `src/` layout and any command changes.
- [ ] Update sanity checklist if necessary (e.g., references to `src/cli.py`).

## Step 5: Follow-up Checks
- [ ] Run existing tests (`poetry run pytest`).
- [ ] Execute sanity workflow (demo repo) to ensure CLI still functions.
