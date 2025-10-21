---
title: Clean Command Feature Status
type: status
feature: clean-command
date: 2025-10-20
tags: [status]
---

# Status: Clean Command

## Summary
`forked clean` provides maintainers with a dry-run-first cleanup workflow covering worktrees, overlay branches, and conflict bundles, enforcing confirmation and retention safeguards.

## Milestones
- [x] Implement CLI with `--dry-run`, `--confirm`, `--keep N`, `--overlays`, `--worktrees`, `--conflicts`.
- [x] Integrate safety rails (skip tagged overlays, respect provenance log keep window, append audit log).
- [x] Document output format (commands echoed) and recommended usage cadence.

## Metrics
- Story Points (planned): 3
- Critical Path: deletion safety + tests (complete)
- Dependencies: feature-slice provenance (identifying active overlays)

## Next Steps
1. Gather operator feedback from demo repos and adjust retention defaults if needed.
2. Wire command into release/CI checklists (follow-up task).
