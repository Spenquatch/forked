---
id: ADR-0001
title: Overlay Worktree Contract
type: adr
status: accepted
date: 2025-09-22
supersedes: null
superseded_by: null
tags: [overlay, worktrees]
links: [../features/overlay-infrastructure/overview.md]
---

## Context
Forked CLI rebuilds overlays by creating additional Git worktrees. The default template located worktrees inside the repo, causing Git errors and leaving dirty directories when rebuilding the same overlay ID.

## Decision
- Relocate relative worktree roots to `../.forked-worktrees/<repo>/<overlay-id>`.
- Allow override through `$FORKED_WORKTREES_DIR`.
- When the target directory already exists, suffix `-N` (e.g., `v0-1`) rather than failing.
- When an overlay branch already has a worktree, reuse it after pruning stale entries and performing `git checkout overlay && git reset --hard trunk` inside that worktree.
- Cherry-pick full branch ranges (`merge-base..branch`) so multi-commit patch stacks rebuild faithfully.

## Consequences
**Positive**
- Rebuilds are idempotent and behave consistently in CI and local runs.
- Users can safely re-run `forked build --id <x>` without manually deleting directories.
- Overlay worktrees never reside inside the Git repository, avoiding upstream restrictions.

**Negative**
- Slightly longer setup when pruning stale worktree entries.
- Requires Git ≥ 2.31 for reliable `worktree list --porcelain` output.

## Rollout & Reversibility
- Changes land in Forked CLI v0.1.0.
- README smoke checklist documents expected behaviour.
- If issues arise, fallback is to disable worktree reuse and require manual cleanup (documented in troubleshooting).
