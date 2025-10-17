---
title: Overlay Infrastructure Implementation Plan
type: implementation-plan
feature: overlay-infrastructure
date: 2025-09-22
tags: [implementation, plan]
---

# Implementation Plan

## Scope
- Update worktree resolution to create siblings to the repo and suffix clashes.
- Detect/reuse existing overlay worktrees, ensuring they reset to `trunk` before replay.
- Iterate over full patch ranges (`merge-base..branch`) with bias-assisted cherry-picks.

## Work Breakdown
1. **Path Resolution**
   - [x] Update `_resolve_worktree_dir` to normalise the desired root, relocate relative paths to `../.forked-worktrees/<repo>/<id>`, and ensure parent directories exist.
   - [x] Honor `$FORKED_WORKTREES_DIR` when provided; add unit guard for absolute Windows-style paths.
   - [x] Implement collision handling by suffixing `<id>-N` when the target directory already exists; add warning log advising `git worktree prune`.
2. **Worktree Reuse**
   - [x] Implement `gitutil.worktree_for_branch()` (parse `worktree list --porcelain`) and return `Path`.
   - [x] If a listed path is missing on disk, run `git worktree prune` once and re-query before falling back to fresh add.
   - [x] When a worktree exists, execute `git checkout overlay && git reset --hard trunk` within the worktree and verify a clean status.
3. **Cherry-pick Reliability**
   - [x] Replace single-commit cherry-picks with ordered ranges from `merge-base(trunk, patch)..patch` using `_rev_list_range`.
   - [x] After each cherry-pick failure, apply path bias globs within the worktree; if conflicts remain, surface clear guidance and abort.
   - [x] Emit structured logging (overlay ID, applied commits, reused path) for smoke checklist verification and future telemetry hooks.

## Validation
- Run `forked build --id test --auto-continue` twice to confirm reuse.
- Inspect `.forked-worktrees/<repo>/<id>` to ensure location and cleanup semantics.
- Execute quick smoke checklist (see README) to cover rebuild + guard path.

## Risks & Mitigations
- **Risk**: Worktree prune may remove active directories. Mitigate by pruning only when a reused entry path does not exist.
- **Risk**: Git versions prior to required features. Mitigate by documenting minimum version in README appendix (future task).
