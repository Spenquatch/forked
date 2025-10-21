---
title: Status JSON Feature Status
type: status
feature: status-json
date: 2025-10-20
tags: [status]
---

# Status: Status JSON

## Summary
`forked status --json` now emits the `status_version: 1` schema with upstream/trunk drift, overlay provenance, and guard-derived metrics. Provenance falls back gracefully and documentation includes runnable `jq` snippets.

## Milestones
- [x] Emit `status_version: 1` JSON from `forked status --json` (backed by provenance).
- [x] Populate overlay `selection` (with `selection.source`) from `.forked/logs/forked-build.log` / notes; fall back gracefully when absent.
- [x] Support `--latest N` overlays with sane defaults and empty-state messaging.
- [x] Document schema and example usage in README.

## Metrics
- Story Points (planned): 2
- Critical Path: Build provenance integration
- Dependencies: feature-slice-workflows (for resolver metadata)

## Next Steps
1. Align guard `report_version: 2` work so status and guard share provenance helpers.
2. Capture dashboard consumers that rely on the new schema (`status_version: 1`) for regression alerts.
