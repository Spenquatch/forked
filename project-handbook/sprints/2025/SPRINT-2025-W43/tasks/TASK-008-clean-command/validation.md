---
title: Clean Command - Validation Guide
type: validation
date: 2025-10-20
task_id: TASK-008
tags: [validation]
links: []
---

# Validation Guide

## Automated
- [ ] `pytest tests/test_clean_command.py -q`
- [ ] `make validate`

## Manual
1. Create sample overlays (`overlay/tmp-a`, `overlay/tmp-b`) and tag one of them.
2. Run `forked clean --dry-run --overlays 'overlay/tmp-*' --keep 1` → ensure tagged overlay reported as skipped.
3. Execute `forked clean --overlays 'overlay/tmp-*' --keep 1 --confirm` → confirm only untagged, old overlays deleted.
4. Create stale worktree directories; run `forked clean --worktrees --confirm` → ensure active worktree preserved.
5. Touch conflict bundles >14 days old (adjust mtime) → run `forked clean --conflicts --confirm` and verify cleanup.

## Sign-off
- [ ] Dry-run output matches executed operations.
- [ ] Safety rails (tags, keep window, provenance) verified.
- [ ] Documentation updated with usage guidance.
