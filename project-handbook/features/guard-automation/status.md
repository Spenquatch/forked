---
title: Guard Automation Status
type: status
feature: guard-automation
date: 2025-10-20
tags: [status]
---

# Status: Guard Automation

## Summary
Guard CLI contract from [ADR-0002](../../adr/0002-guard-cli-contract.md) is implemented. Addendum v1.1 introduces policy override enforcement (`mode=require-override`), provenance-backed feature attribution, and `report_version: 2` while keeping legacy consumers compatible.

## Milestones
- [x] Implement `typer.Exit` contract + exit code handling
- [x] Emit `"report_version": 1` and document schema
- [x] Update sentinel logic to use union file tree + overlay-only allowance
- [x] Switch diff sizing to `--numstat` aggregation
- [x] Capture golden guard JSON fixture for regression tests
- [ ] Parse override trailers/notes and enforce `policy_overrides` contract
- [ ] Bump report schema to v2 with override + feature metadata

## Metrics
- Policy coverage: 100% of documented guard checks (v1), override support pending
- CI readiness: follow-up item captured in backlog (consider CI wiring in future iteration)

## Next Steps
1. Land override parsing, provenance integration, and schema bump.
2. Conduct smoke testing against real remote repos to validate ergonomics.

## Active Work (auto-generated)
*Last updated: 2025-10-16*

### Current Sprint (SPRINT-2025-W42)
- No active tasks in current sprint

### Metrics
- **Total Story Points**: 3 (planned)
- **Completed Points**: 3 (100%)
- **Remaining Points**: 0
- **Estimated Completion**: n/a (feature dev complete; follow-ups tracked separately)
- **Average Velocity**: 21 points/sprint
