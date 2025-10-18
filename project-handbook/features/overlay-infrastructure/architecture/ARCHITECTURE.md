---
title: Overlay Infrastructure Architecture
type: architecture
feature: overlay-infrastructure
date: 2025-09-22
tags: [architecture, git, overlays]
---

# Overlay Infrastructure Architecture

## Branch Model
- `trunk` mirrors `upstream/<default>` (fast-forward only).
- `patch/*` branches hold fork-specific modifications authored in small, reviewable chunks.
- `overlay/<id>` branches are build artefacts composed of `trunk` + ordered `patch/*`.
- Tags `overlay/<id>` freeze the state of a published overlay for release validation.

## Worktree Layout
```
repo/
├── .forked/
│   └── worktrees/              # overlay worktrees (one directory per overlay id)
│   └── <repo-name>/<overlay-id>/  # overlay-specific worktree checkout
└── (repo files...)
```
- Relative `worktree.root` values land under `.forked/worktrees/<id>`; users can override the location via `$FORKED_WORKTREES_DIR` if needed.
- Rebuilds reuse existing worktrees when present; the automation resets them to `trunk` before cherry-picking.

## Build Flow Overview
1. Fetch + fast-forward `trunk`.
2. Resolve overlay worktree (reuse/prune if needed).
3. Cherry-pick complete commit ranges for each `patch/*` in order (`merge-base..branch`).
4. Apply path bias heuristics for conflicts, then surface remaining conflicts for manual resolution.
5. Run guard checks and publish overlay/tag if policy passes.

## Failure & Recovery Considerations
- If Git version < 2.31 lacks reliable `worktree list --porcelain`, rebuild falls back to fresh worktree creation and surfaces a warning.
- Rebuild scripts abort if the worktree is dirty after `reset --hard`; contributors must resolve manual edits before re-running.
- All automation assumes POSIX path separators; Windows contributors should set `FORKED_WORKTREES_DIR` to an absolute path (e.g., `C:/forked-worktrees`).
