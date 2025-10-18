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
Forked CLI rebuilds overlays by creating additional Git worktrees. Early prototypes placed worktrees inside the repository root, which clashed with Git's expectations and made cleanup noisy. Keeping ephemeral state scoped under a predictable directory simplifies reuse and troubleshooting.

## Decision
- Relocate relative worktree roots to `<repo>/.forked/worktrees/<overlay-id>` (or `$FORKED_WORKTREES_DIR` when provided).
- Allow override through `$FORKED_WORKTREES_DIR`.
- When the target directory already exists, suffix `-N` (e.g., `v0-1`) rather than failing.
- When an overlay branch already has a worktree, reuse it after pruning stale entries and performing `git checkout overlay && git reset --hard trunk` inside that worktree.
- Cherry-pick full branch ranges (`merge-base..branch`) so multi-commit patch stacks rebuild faithfully.

## Consequences
**Positive**
- Rebuilds are idempotent and behave consistently in CI and local runs.
- Users can safely re-run `forked build --id <x>` without manually deleting directories.
- All overlay artefacts live under `.forked/`, keeping the repository tidy and making cleanup a single command.

**Negative**
- Slightly longer setup when pruning stale worktree entries.
- Requires Git ≥ 2.31 for reliable `worktree list --porcelain` output.

## Rollout & Reversibility
- Changes land in Forked CLI v0.1.0.
- README smoke checklist documents expected behaviour.
- If issues arise, fallback is to disable worktree reuse and require manual cleanup (documented in troubleshooting).
