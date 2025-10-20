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
1. **Command Skeleton**
   - [ ] Add Typer command with options: `--dry-run` (default true), `--confirm`, `--keep`, `--overlays`, `--worktrees`, `--conflicts`, `--age`.
   - [ ] Enumerate candidates (worktrees from `git worktree list`, overlays via Git refs, conflicts from filesystem).
2. **Safety & Execution**
   - [ ] Skip overlay branches referenced by tags, current worktree, or provenance log within keep window.
   - [ ] Print intended actions (git delete branch, rm dir) before execution.
   - [ ] Execute commands only when `--confirm` (or re-run without `--dry-run`) is supplied.
3. **Integration**
   - [ ] Hook into release process (documentation + changelog).
   - [ ] Add integration tests using temp repos to verify dry-run vs confirm behaviour.

## Validation
- `pytest tests/test_clean_command.py -q`
- Manual: run dry-run and confirm modes; verify overlay protection.
- `make validate` after documentation updates.

## Risks & Mitigations
- **Risk**: Accidental deletion of useful overlays. Mitigation: default dry-run, explicit confirm, respect tags + keep window.
- **Risk**: Cross-platform filesystem quirks. Mitigation: rely on Git for branch deletion; use Python for directory removal with error handling.
