---
title: Sprint Plan - SPRINT-2025-W39
type: sprint-plan
date: 2025-09-22
sprint: SPRINT-2025-W39
start: 2025-09-22
end: 2025-09-26
tags: [sprint, planning]
release: v0.1.0
---

# Sprint Plan: SPRINT-2025-W39

## Release Context
**Release**: v0.1.0 (Forked CLI MVP)
**Features in scope**:
- overlay-infrastructure (critical path)
- guard-automation (critical path)
- release-operations (supporting)

## Sprint Duration
- Start: Monday, September 22, 2025
- End: Friday, September 26, 2025

## Sprint Goals
1. [ ] Overlay rebuild is deterministic and reuses safe worktrees (overlay-infrastructure)
2. [ ] Guard CLI emits stable policy reports with documented exit codes (guard-automation)
3. [ ] Documentation + release checklist ready for live demo (release-operations)

## Task Creation Guide
Create tasks for this sprint using:
```bash
make task-create title="Task Name" feature=feature-name decision=ADR-XXX points=5
```

## Capacity Planning
- **Team Size**: 1 developer
- **Sprint Days**: 5 (Monday-Friday)
- **Historical Velocity**: 10 pts/sprint (placeholder)
- **Available Points**: 10 pts
- **Buffer (20%)**: 2 pts reserved
- **Net Capacity**: 8 pts committed (overlay + guard work)

## Feature Work Priorities
- **overlay-infrastructure** (P0): must finish for release
- **guard-automation** (P0): must finish for release
- **release-operations** (P1): close docs/checklists, nice-to-have backlog captured


## Dependencies & Risks
- **External Dependencies**: Git >=2.31 on target machines
- **Cross-Team Dependencies**: None
- **Technical Risks**: Path resolution edge cases, sentinel performance
- **Capacity Risks**: Solo sprint — keep stretch goal optional

## Success Criteria
- [ ] Overlay rebuild passes smoke checklist twice consecutively
- [ ] Guard CLI returns correct exit codes and JSON metadata
- [ ] Quick release checklist executed end-of-week
- [ ] Backlog updated with remaining QoL items

## Sprint Retrospective Planning
- What worked about reusable worktrees?
- Should guard automation gain fixtures?
- Did release checklist catch surprises?
