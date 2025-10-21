---
title: Clean Command Testing Guide
type: testing
feature: clean-command
date: 2025-10-20
tags: [testing]
---

# Testing Guide

## Automated
- `pytest tests/test_clean_command.py -q` – verifies dry-run messaging, confirm-only execution, retention filters, worktree/conflict pruning, and log entries.

## Manual
1. Create sample overlays + worktrees (some tagged, some stale).
2. Run `forked clean --dry-run --overlays 30d --keep 2` and confirm only stale entries listed.
3. Run `forked clean --overlays 'overlay/tmp-*' --no-dry-run --confirm` and ensure matching branches deleted.
4. Test conflict pruning: touch `.forked/conflicts/*`, run `forked clean --conflicts --no-dry-run --confirm`.
5. Inspect `.forked/logs/clean.log` to confirm executed actions recorded.

## Regression
- Validate `forked clean` output is logged/communicated in release notes.
- `make validate` after updating documentation or examples.
