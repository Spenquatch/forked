---
title: Guard Automation Status
type: status
feature: guard-automation
date: 2025-10-16
tags: [status]
---

# Status: Guard Automation

## Summary
Guard CLI contract from [ADR-0002](../../adr/0002-guard-cli-contract.md) is implemented: exit codes flow through `typer.Exit`, sentinel checks operate on trunk/overlay union, and JSON reports expose versioned metrics.

## Milestones
- [x] Implement `typer.Exit` contract + exit code handling
- [x] Emit `"report_version": 1` and document schema
- [x] Update sentinel logic to use union file tree + overlay-only allowance
- [x] Switch diff sizing to `--numstat` aggregation
- [x] Capture golden guard JSON fixture for regression tests

## Metrics
- Policy coverage: 100% of documented guard checks
- CI readiness: pending pipeline dry run (guard not yet wired into CI template)

## Next Steps
1. Dry-run GitHub Action guard step with editable install.
2. Capture guard artefacts via handbook automation (`make release-status`).

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
