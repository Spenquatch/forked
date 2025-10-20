---
title: Clean Command Feature Status
type: status
feature: clean-command
date: 2025-10-20
tags: [status]
---

# Status: Clean Command

## Summary
`forked clean` will provide maintainers with a dry-run-first cleanup workflow covering worktrees, overlay branches, and conflict bundles. Implementation planned for v1.1.0.

## Milestones
- [ ] Implement CLI with `--dry-run`, `--confirm`, `--keep N`, `--overlays`, `--worktrees`, `--conflicts`.
- [ ] Integrate safety rails (skip tagged overlays, respect provenance log keep window).
- [ ] Document output format (commands echoed) and recommended usage cadence.

## Metrics
- Story Points (planned): 3
- Critical Path: deletion safety + tests
- Dependencies: feature-slice provenance (identifying active overlays)

## Next Steps
1. Design candidate selection logic (age, glob, keep).
2. Implement dry-run outputs and gating.
3. Add integration tests and documentation updates.
