---
id: ADR-0005
title: Operational Tooling Enhancements
type: adr
status: accepted
date: 2025-10-20
supersedes: null
superseded_by: null
tags: [status, housekeeping]
links: [../features/status-json/overview.md, ../features/clean-command/overview.md]
---

## Context
Maintainers need machine-readable fork status for dashboards/automation and a safe way to prune stale overlays, worktrees, and conflict artefacts. Ad-hoc scripts are error-prone and lack consistent safety rails.

## Decision
- Add `forked status --json` (schema versioned) providing upstream/trunk info, patch drift, and overlay selections derived from build provenance.
- Introduce `forked clean` command with dry-run default, confirmation gating, retention knobs (`--keep`, `--overlays`, `--worktrees`, `--conflicts`), and protections for tagged/active overlays.
- Persist overlay provenance (features, patches, timestamps) in `.forked/logs/forked-build.log` and optional git notes, enabling both features to share context.

## Consequences
**Positive**
- Operators can automate reporting and housekeeping safely without bespoke scripts.
- Guard/report pipelines reuse provenance metadata instead of recomputing selections.

**Negative**
- Additional CLI surface requires documentation and maintenance.
- Provenance log/notes introduce lightweight state that must be kept consistent.

## Rollout & Reversibility
- Ships with release v1.1.0 alongside related CLI enhancements.
- Backwards compatible: existing `forked status` behaviour preserved when `--json` absent; `forked clean` is additive.
- Reversal path: disable commands via feature flags and document deprecation if needed.
