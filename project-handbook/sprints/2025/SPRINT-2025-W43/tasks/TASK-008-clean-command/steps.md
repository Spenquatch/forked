---
title: Clean Command - Implementation Steps
type: implementation
date: 2025-10-20
task_id: TASK-008
tags: [implementation]
links: []
---

# Implementation Steps: Clean Command

## Step 1: Candidate Discovery
- [ ] Enumerate worktree candidates via `git worktree list --porcelain` and `.forked/worktrees/*` directories.
- [ ] List overlay branches with age metadata (`git for-each-ref`) and cross-check tags/provenance.
- [ ] Identify conflict bundle directories with timestamps (default prune threshold 14d).

## Step 2: Dry-Run Renderer
- [ ] Implement dry-run summary grouped by worktrees/overlays/conflicts.
- [ ] Print exact commands to be executed (e.g., `git branch -D ...`, `rm -rf ...`).
- [ ] Exit non-zero (or emit warning) when run without `--confirm` to remind operators nothing was deleted.

## Step 3: Execution Path
- [ ] Gate destructive actions behind `--confirm` (or re-run without `--dry-run`).
- [ ] Apply `--keep N`, `--overlays <age|pattern>`, `--worktrees`, `--conflicts` options.
- [ ] Ensure tagged overlays, current overlay, and recently-built overlays (per provenance) cannot be deleted.

## Step 4: Tests & Docs
- [ ] Add unit/integration tests simulating stale worktrees and overlays.
- [ ] Document command usage and safety rails in README + handbook feature page.
- [ ] Update release notes and changelog entries.

## Notes
- Consider logging actions taken (or skipped) to `.forked/logs/clean.log` for audit (optional nice-to-have).
- Keep command idempotent: running twice with same flags should result in no-op the second time.
