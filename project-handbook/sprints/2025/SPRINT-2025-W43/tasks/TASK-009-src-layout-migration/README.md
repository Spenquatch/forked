---
title: Task TASK-009 - Adopt src Layout
type: task
date: 2025-10-21
task_id: TASK-009
feature: release-operations
tags: [task, tooling]
links: [../../../features/release-operations/overview.md, ../../plan.md]
---

# Task TASK-009: Adopt src/ Layout

## Overview
**Goal**: Transition the Python package to the recommended `src/` layout so runtime code is isolated from tests/docs and installation mirrors production usage.

This change involves moving the existing `forked/` package under `src/forked/`, updating build/packaging metadata, adjusting imports/scripts/tests, and verifying the CLI still resolves correctly.

## Why
- Prevents accidental imports from the checkout (ensures `python -m forked` loads the installed package).
- Aligns with Poetry’s best practices and simplifies future packaging/distribution.
- Makes it easier to publish to PyPI if/when desired.

## Deliverables
- All runtime modules relocated to `src/forked/`.
- Updated `pyproject.toml` package includes (Poetry read packages from `src`).
- Tests, scripts, and handbook automation use package imports instead of relative path tricks.
- README and development docs updated with the new layout instructions.

See `steps.md`, `commands.md`, and `validation.md` for detailed guidance.
