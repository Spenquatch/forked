---
title: Overlay Infrastructure Risks
type: risks
feature: overlay-infrastructure
date: 2025-09-22
tags: [risks]
---

# Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Git worktree behaviour differs on older versions | Medium | Document minimum supported Git (>=2.31) and add version check in CLI init |
| Reused worktree still dirty from manual edits | High | Explicit `reset --hard trunk` before every cherry-pick loop; fail if `status --porcelain` non-empty afterwards |
| Path relocation mis-detects repo parents on Windows | Medium | Normalize paths before comparison and add README guidance for `FORKED_WORKTREES_DIR` |

# Open Questions
- Should we add automated pruning after publish to reclaim disk?
- Do we need user-configurable suffix strategy for parallel overlays?
