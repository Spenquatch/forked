---
title: Adopt src Layout - Command Snippets
type: reference
date: 2025-10-21
task_id: TASK-009
tags: [commands]
links: []
---

# Command Snippets

## Flatten Package Layout
```bash
mv src/forked/*.py src/
rmdir src/forked
```

## Update Poetry Configuration
```bash
poetry check
poetry run ruff check .
poetry run mypy
```

## Tests & Sanity Workflow
```bash
poetry run pytest
# optional: re-run sanity_check steps using demo repo
```
