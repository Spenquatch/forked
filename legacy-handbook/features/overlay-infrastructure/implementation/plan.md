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
   - [ ] Read `$FORKED_WORKTREES_DIR` override.
   - [ ] Relocate relative roots to `../.forked-worktrees/<repo>/<id>`.
   - [ ] Suffix existing directories instead of failing.
2. **Worktree Reuse**
   - [ ] Parse `git worktree list --porcelain` for existing overlay branch matches.
   - [ ] Prune stale entries before reuse.
   - [ ] Hard-reset reused worktrees to `trunk` prior to cherry-picks.
3. **Cherry-pick Reliability**
   - [ ] Use `_rev_list_range` to gather commits in order.
   - [ ] Apply path bias within overlay worktree after conflicts.
   - [ ] Capture rebuild stats for smoke checklist.

## Validation
- Run `forked build --id test --auto-continue` twice to confirm reuse.
- Inspect `.forked-worktrees/<repo>/<id>` to ensure location and cleanup semantics.
- Execute quick smoke checklist (see README) to cover rebuild + guard path.

## Risks & Mitigations
- **Risk**: Worktree prune may remove active directories. Mitigate by pruning only when a reused entry path does not exist.
- **Risk**: Git versions prior to required features. Mitigate by documenting minimum version in README appendix (future task).
