---
title: Overlay Rebuild Hardening - References
type: references
date: 2025-09-22
task_id: TASK-001
tags: [references]
links: []
---

# References: Overlay Rebuild Hardening

## Internal References

### Decision Context
- **Decision**: ADR-0001 (pending overlay worktree decision doc)
- **Feature**: [Overlay infrastructure overview](../../../features/overlay-infrastructure/overview.md)
- **Implementation Plan**: [Overlay infrastructure plan](../../../features/overlay-infrastructure/implementation/plan.md)
- **Release Plan**: [v0.1.0 release](../../../releases/current/plan.md)

### Sprint Context
- **Sprint Plan**: [Current sprint](../../plan.md)
- **Sprint Tasks**: [All sprint tasks](../)
- **Daily Progress**: [Daily status](../../daily/)

## External References

### Documentation
- [Git worktree docs](https://git-scm.com/docs/git-worktree)
- [Git rev-list docs](https://git-scm.com/docs/git-rev-list)

### Code Examples
- [Git worktree reuse patterns](https://stackoverflow.com/questions/49959330/how-to-check-if-branch-is-checked-out-in-another-worktree)

### Tools & Resources
- `git worktree list --porcelain`
- `forked build`, `forked guard` CLI commands

## Learning Resources
- [Git rerere documentation](https://git-scm.com/docs/git-rerere)

## Related Work
- Follow-up: add automated cleanup command (`forked clean`) — see BACKLOG.md
- Related feature: guard-automation (ensures rebuild output passes policies)

## Notes
Keep this file updated as you discover useful resources during implementation.
Link back to this task from any PRs or external discussions.
