---
title: Sprint Plan - SPRINT-2025-W43
type: sprint-plan
date: 2025-10-20
sprint: SPRINT-2025-W43
start: 2025-10-20
end: 2025-10-24
tags: [sprint, planning]
release: v1.1.0
---

# Sprint Plan: SPRINT-2025-W43

## Release Context
**Release**: v1.1.0 (Feature Slice + Conflict Bundles)
**Features in scope**:
- feature-slice-workflows (critical path)
- conflict-bundle-automation (critical path)
- release-operations (supporting)

## Sprint Duration
- Start: Monday, October 20, 2025
- End: Friday, October 24, 2025

## Sprint Goals
1. [ ] Feature resolver + CLI commands ready (`feature-slice-workflows`, provenance logging, skip upstream equivalents)
2. [ ] Build/sync emit conflict bundles with schema v2 & multi-wave handling (`conflict-bundle-automation`)
3. [ ] Guard overrides + report v2 implemented (`guard-automation`)
4. [ ] `forked status --json` + `forked clean` delivered with docs (`status-json`, `clean-command`)
5. [ ] Docs + release notes updated for all new workflows (`release-operations`)

## Task Creation Guide
Create tasks for this sprint using:
```bash
make task-create title="Task Name" feature=feature-name decision=ADR-XXX points=5
```

## Capacity Planning
- **Team Size**: 1 developer
- **Sprint Days**: 5 (Monday-Friday)
- **Historical Velocity**: 10 pts/sprint
- **Available Points**: 21 pts (stretch to cover addendum scope)
- **Buffer (20%)**: 4 pts reserved
- **Net Capacity**: 17 pts committed (split across feature, guard, and tooling streams)

## Feature Work Priorities
- **feature-slice-workflows** (P0): deliver resolver + new Typer commands + provenance + skip upstream equivalents.
- **conflict-bundle-automation** (P0): implement shared bundle writer v2, multi-wave support, sync auto-continue policy.
- **guard-automation** (P0): enforce policy overrides, report v2, provenance integration.
- **status-json** (P0): expose `forked status --json` schema and pagination.
- **clean-command** (P0): build safe housekeeping CLI with dry-run/confirm semantics.
- **release-operations** (P1): capture documentation updates, changelog, and CI snippets.

## Dependencies & Risks
- Shared config/parser updates must land before CLI commands wire through.
- Exit code changes require coordination with existing automation scripts.
- Integration tests rely on demo repo updates; schedule time early in sprint.

## Success Criteria
- [ ] `forked build` honors overlay profiles/feature lists, logs provenance, and supports `--skip-upstream-equivalents`.
- [ ] Conflict bundle JSON schema v2 emitted for build + sync (binary support, multi-wave numbering, sync auto-continue logging).
- [ ] Guard `require-override` mode enforces overrides and emits `report_version: 2` with override metadata.
- [ ] `forked status --json` + `forked clean` available with documented usage and safety rails.
- [ ] README/handbook updated with overrides, status JSON, clean, skip-upstream, sync policy, and CI examples.

## Sprint Retrospective Planning
- How intuitive is the feature selection UX for first-time users?
- Did conflict bundles reduce manual resolution time?
- Are overrides/status/clean workflows intuitive, and what automation hooks should we prioritize next?
