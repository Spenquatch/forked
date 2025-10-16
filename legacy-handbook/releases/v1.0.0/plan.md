---
title: Release v1.0.0 Plan
type: release-plan
version: v1.0.0
start_sprint: SPRINT-2025-W39
end_sprint: SPRINT-2025-W39
planned_sprints: 1
status: in-progress
date: 2025-09-22
tags: [release, planning]
links: []
---

# Release v1.0.0

## Release Summary
Ship Forked CLI 1.0.0 with reliable overlay rebuilds, actionable guard automation, and documentation that makes demo installs trivial.

## Release Goals
1. **Primary Goal**: Harden overlay management (safe worktree paths, branch reuse, deterministic rebuilds)
2. **Secondary Goal**: Ship guard and sentinel improvements with JSON policy reports
3. **Stretch Goal**: Finalize release ergonomics (status UX, publish remote flag, checklists)

## Sprint Timeline
- **SPRINT-2025-W39** (Sprint 1 of 1): Polish overlays/guards and prep demo release


## Feature Assignments
| Feature | Priority | Notes |
|---------|----------|-------|
| overlay-infrastructure | P0 | Worktree relocation, branch reuse, range cherry-picks |
| guard-automation | P0 | Sentinel fixes, size caps, exit-code hardening |
| release-operations | P1 | README finalization, quick release checklist, publish UX |

## Success Criteria
- [ ] Overlay rebuild reproduces the patch stack with zero manual steps
- [ ] Guard report exits with documented codes and `"report_version": 1`
- [ ] README quick smoke + release checklists verified for demo

## Risk Management
- **Critical path**: Overlay worktree reuse; if it regresses we block release
- **Dependencies**: Git 2.31+ behaviour for worktrees; Typer CLI contract
- **Capacity**: Solo sprint, keep stretch goal optional

## Release Notes Draft
- Overlay branches now rebuild in isolated worktrees and reuse existing checkouts safely  
- Guards compute sentinel equality across missing files and summarize diff size via `--numstat`  
- `forked status --latest` highlights freshest overlays; `forked publish` supports custom remotes  
- README documents smoke + release checklists for CI and demo readiness
