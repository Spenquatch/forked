---
title: Release v1.1.0 Plan
type: release-plan
version: v1.1.0
start_sprint: SPRINT-2025-W43
end_sprint: SPRINT-2025-W43
planned_sprints: 1
status: planned
date: 2025-10-20
tags: [release, planning]
links: []
---

# Release v1.1.0

## Release Summary
Deliver feature-sliced workflows, guard policy overrides, conflict bundle automation v2, and operational tooling (`status --json`, `forked clean`) so teams can compose overlays by feature, resolve conflicts faster, and automate maintenance safely.

## Release Goals
1. **Primary Goal**: Enable selective overlay builds driven by feature definitions, provenance logging, and optional skip-upstream optimisation.
2. **Secondary Goal**: Emit structured conflict bundles (schema v2) for build and sync with deterministic exit codes and multi-wave support.
3. **Supporting Goal**: Enforce guard policy overrides + report v2 and upgrade `status/clean` ergonomics so CI + operators have machine-readable artifacts.

## Sprint Timeline
- **SPRINT-2025-W43** (Sprint 1 of 1): Implement feature slice resolver + commands, build/sync conflict bundles, update guard + docs.

## Feature Assignments
| Feature | Owner | Priority | Notes |
|---------|-------|----------|-------|
| feature-slice-workflows | @ai-agent | P0 | Resolver, provenance logging, feature commands, `--skip-upstream-equivalents`. |
| conflict-bundle-automation | @ai-agent | P0 | Shared bundle writer v2 (binary handling, waves, shell note) + sync auto-continue policy. |
| guard-automation | @ai-agent | P0 | Policy overrides, report v2, provenance-driven feature attribution. |
| status-json (FORKED_STATUS_JSON) | @ai-agent | P0 | Deliver `forked status --json` schema + overlay window controls. |
| clean-command (FORKED_CLEAN) | @ai-agent | P0 | Ship `forked clean` with dry-run/confirm, retention, worktree/conflict pruning. |
| release-operations | @ai-agent | P1 | Update README/handbook references post-implementation (overrides, status JSON, clean, CI snippets). |

- [ ] CLI resolves overlay profiles and feature sets via config and logs provenance.
- [ ] Feature management commands scaffold slices, report status, and support skip-upstream flag.
- [ ] Conflict bundles emit schema v2 JSON, support binary/large files, multi-wave numbering, and sync parity.
- [ ] Guard enforces policy overrides, exposes feature metadata, and documents report v2.
- [ ] `forked status --json` and `forked clean` deliver the QoL workflow with documentation.
- [ ] Documentation + release notes updated for new workflows and schemas.

## Traceability
- Implementation plan: `features/feature-slice-workflows/implementation/plan.md`
- Conflict bundles: `features/conflict-bundle-automation/implementation/plan.md`
- Guard overrides: `features/guard-automation/implementation/plan.md`
- Status JSON: backlog item `backlog/feature/FORKED_STATUS_JSON-P2-20250922-1201/README.md`
- Clean command: backlog item `backlog/feature/FORKED_CLEAN-P2-20250922-1200/README.md`
- Docs alignment: `features/release-operations/status.md`

## Risk Management
- Shared serializer must stay consistent across commands; integration tests required.
- Config migration support documented to avoid breaking existing forks.
- Exit code/report schema changes communicated via changelog + README upgrade notes.
- `forked clean` must never remove protected overlays; dry-run+confirm gating enforced.
- Overrides must always default-safe (require explicit trailers when enabled).

## Release Notes Draft
- Feature-sliced overlays: `forked build --overlay/--features`, include/exclude globs, skip-upstream optimisation, provenance logging in build logs + git notes, and new `forked feature create/status` commands.
- Conflict bundle engine v2 across build + sync with `--emit-conflicts`, `--conflict-blobs-dir`, `--on-conflict <stop|bias|exec>`, binary-aware diffs, multi-wave numbering, and deterministic exit codes.
- Guard overrides/report v2, status JSON, and clean command entries to be appended once corresponding tasks land.
- Draft notes tracked in `releases/v1.1.0/release-notes-draft.md` (updated after each feature lands).
