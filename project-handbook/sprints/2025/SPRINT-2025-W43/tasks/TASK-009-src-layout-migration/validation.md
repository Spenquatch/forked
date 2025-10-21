---
title: Adopt src Layout - Validation Guide
type: validation
date: 2025-10-21
task_id: TASK-009
tags: [validation]
links: []
---

# Validation Guide

## Automated
- [ ] `poetry run ruff check .`
- [ ] `poetry run ruff format --check .`
- [ ] `poetry run mypy --config-file pyproject.toml forked/cli.py`
- [ ] `poetry run pytest`

## Manual
1. Run the sanity workflow (demo repo) to ensure CLI commands work as expected (`forked init`, `forked build`, `forked guard`, `forked status`, `forked clean`).
2. Confirm `poetry run forked --help` works within and outside `poetry shell`.
3. Verify handbook automation (`poetry run make -C project-handbook sprint-status`) still functions.

## Regression
- Update README/handbook references; ensure links to code paths reflect the new `src/` structure.
- Confirm CI or scripts invoking `/forked/` files are updated.
