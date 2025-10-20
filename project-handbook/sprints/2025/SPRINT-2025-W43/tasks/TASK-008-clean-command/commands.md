---
title: Clean Command - Command Snippets
type: reference
date: 2025-10-20
task_id: TASK-008
tags: [commands]
links: []
---

# Command Snippets

## Dry-Run Examples
```bash
# list candidates without executing
forked clean --dry-run --overlays 30d --keep 2 --worktrees --conflicts
```

## Confirmed Cleanup
```bash
# remove tmp overlays matching pattern after review
forked clean --overlays 'overlay/tmp-*' --confirm

# prune worktrees only
forked clean --worktrees --confirm
```

## Tests
```bash
pytest tests/test_clean_command.py -q
```
