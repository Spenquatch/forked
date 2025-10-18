---
title: Overlay Infrastructure Testing Guide
type: testing
feature: overlay-infrastructure
date: 2025-09-22
tags: [testing, git, overlays]
---

# Testing Guide

## Preconditions
- Git ≥ 2.31 installed (`git --version`).
- Configured upstream remote (e.g., `origin` + `upstream`).
- `forked.yml` lists patch branches in desired order.

## Smoke Test (Local)
1. Ensure clean worktree: `git status --short` → empty.
2. Run `forked build --id smoke --auto-continue`.
3. Re-run the same command. Expect:
   - No “already checked out” errors.
   - Worktree path reused under `.forked/worktrees/smoke`.
4. Inspect worktree cleanliness:
   ```bash
   repo_name=$(basename "$(git rev-parse --show-toplevel)")
   git -C .forked/worktrees/smoke status --short
   ```
   Output should be empty.

## Regression Test (Patch Stack)
1. Create a temporary patch branch with two commits (`patch/test-multi`).
2. Add it to `forked.yml` order.
3. Run `forked build --id multi-check`.
4. Verify both commits exist in overlay:
   ```bash
   git log overlay/multi-check --oneline | head -n 5
   ```

## Failure Scenarios to Exercise
- Delete `.forked/worktrees/<id>` manually and rebuild: automation should suffix with `-1` rather than failing.
- Set `FORKED_WORKTREES_DIR=/tmp/forked` and repeat smoke test to validate absolute path handling.
- Introduce conflicting changes between trunk and patch branches; confirm path bias logs remaining conflicts for manual intervention.

## Automation Hooks
- Future CI step should run `forked build --id $RUN_ID --auto-continue` followed by guard checks; capture non-zero exit codes.
