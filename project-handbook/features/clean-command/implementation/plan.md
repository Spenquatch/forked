---
title: Clean Command Implementation Plan
type: implementation-plan
feature: clean-command
date: 2025-10-20
tags: [implementation, plan]
---

# Implementation Plan

## Scope
- Build `forked clean` CLI with dry-run default and confirmation gating.
- Support pruning of worktrees, overlay branches (age/glob/keep), and conflict bundles.
- Ensure tagged/active overlays remain untouched.

## Work Breakdown
1. **Candidate Discovery**
   - [ ] Enumerate worktree candidates via `git worktree list --porcelain` and `.forked/worktrees/*` directories.
   - [ ] List overlay branches with age metadata (`git for-each-ref`) and cross-check tags/provenance logs (protect default/active overlays).
   - [ ] Identify conflict bundle directories with timestamps (default prune threshold 14d) and matching blob subdirectories.
2. **Dry-Run Renderer**
   - [ ] Implement dry-run summary grouped by worktrees/overlays/conflicts (dry-run default).
   - [ ] Print exact commands to be executed (e.g., `git branch -D ...`, `rm -rf ...`) and append to `.forked/logs/clean.log`.
   - [ ] Emit clear message when destructive actions skipped because `--confirm` absent (exit remains 0).
3. **Execution Path**
   - [ ] Gate destructive actions behind `--no-dry-run --confirm`.
   - [ ] Apply `--keep N`, `--overlays <age|pattern>`, `--worktrees`, `--conflicts` options.
   - [ ] Match overlays to provenance (branch name + latest build log entry) to protect recently-built overlays and the configured default; skip tagged overlays.
   - [ ] Remove conflict bundles and their blob directories when eligible while retaining the most recent per overlay.
4. **Tests & Docs**
   - [ ] Add unit/integration tests simulating stale worktrees, overlays, and conflict bundles.
   - [ ] Document command usage, safety rails, and audit logging in README + handbook feature page.
   - [ ] Update release notes and changelog entries.

## Validation
- `pytest tests/test_clean_command.py -q`
- Manual: dry-run vs confirm scenarios per validation guide
- `make validate`

## Risks & Mitigations
- **Risk**: Accidental deletion of useful overlays. Mitigation: default dry-run, explicit confirm, honour tags/provenance keep window.
- **Risk**: Cross-platform filesystem quirks. Mitigation: rely on Git for branch deletion; use Python for directory removal with error handling.
- **Risk**: Audit gap. Mitigation: append executed actions to `.forked/logs/clean.log`.
