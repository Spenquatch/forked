---
title: Clean Command Testing Guide
type: testing
feature: clean-command
date: 2025-10-20
tags: [testing]
---

# Testing Guide

## Automated
- `pytest tests/test_clean_command.py -q` – verifies dry-run messaging, confirm-only execution, retention filters.
- `pytest tests/test_clean_conflict_dir.py -q` – ensures conflict bundle pruning respects age/keep rules.

## Manual
1. Create sample overlays + worktrees (some tagged, some stale).
2. Run `forked clean --dry-run --overlays 30d --keep 2` and confirm only stale entries listed.
3. Run `forked clean --overlays 'overlay/tmp-*' --confirm` and ensure matching branches deleted.
4. Test conflict pruning: touch `.forked/conflicts/*`, run `forked clean --conflicts --confirm`.

## Regression
- Validate `forked clean` output is logged/communicated in release notes.
- `make validate` after updating documentation or examples.
