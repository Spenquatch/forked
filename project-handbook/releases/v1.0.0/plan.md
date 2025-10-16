---
title: Release v1.0.0 Plan
type: release-plan
version: v1.0.0
start_sprint: SPRINT-2025-W42
end_sprint: SPRINT-2025-W42
planned_sprints: 1
status: in-progress
date: 2025-10-16
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
- **SPRINT-2025-W42** (Sprint 1 of 1): Polish overlays/guards and prep demo release


## Feature Assignments
| Feature | Owner | Priority | Notes |
|---------|-------|----------|-------|
| overlay-infrastructure | @ai-agent | P0 | Implement ADR-0001 (worktree relocation, reuse, range cherry-picks) |
| guard-automation | @ai-agent | P0 | Implement ADR-0002 (exit codes, sentinel union, `--numstat`) |
| release-operations | @ai-agent | P1 | Align README, release notes, CI workflow, backlog follow-ups |

- [x] ADR-0001 implementation completed and verified via smoke checklist (`forked build --id smoke` twice, clean status)
- [x] ADR-0002 guard CLI contract delivered (exit codes, sentinel union, `--numstat`)
- [ ] README + release notes updated with final commands, outputs, and post-tag communication plan
- [ ] Backlog items (`forked clean`, `forked status --json`) prioritised and linked from release retrospective

## Traceability
- ADR-0001 → Sprint task `TASK-001` (Overlay Rebuild Hardening) → Feature `overlay-infrastructure`
- ADR-0002 → Sprint task `TASK-002` (Guard CLI Contract) → Feature `guard-automation`
- Release operations documentation → Feature `release-operations` → README & changelog updates

## Risk Management
- **Critical path**: Overlay worktree reuse; if it regresses we block release
- **Dependencies**: Git 2.31+ behaviour for worktrees; Typer CLI contract
- **Capacity**: Solo sprint, keep stretch goal optional

## Release Notes Draft
- Overlay branches now rebuild in isolated worktrees and reuse existing checkouts safely  
- Guards compute sentinel equality across missing files and summarize diff size via `--numstat`  
- `forked status --latest` highlights freshest overlays; `forked publish` supports custom remotes  
- README documents smoke + release checklists for CI and demo readiness
