---
title: Clean Command - Completion Checklist
type: checklist
date: 2025-10-20
task_id: TASK-008
tags: [checklist]
links: []
---

# Completion Checklist

- [ ] Dry-run output clearly lists candidates and pending commands.
- [ ] Destructive path gated behind `--no-dry-run --confirm` (explicit confirmation required).
- [ ] Overlay pruning respects `--keep`, `--overlays` (age/pattern), and skips tagged/active overlays.
- [ ] Worktree pruning uses Git + filesystem checks without touching active worktrees.
- [ ] Conflict bundle cleanup retains most recent bundle per overlay.
- [ ] Documentation updated with usage examples and safety notes.
- [ ] `make validate` passes.
