---
title: Status JSON Feature Status
type: status
feature: status-json
date: 2025-10-20
tags: [status]
---

# Status: Status JSON

## Summary
Plan v1.1 introduces a schema-backed `forked status --json` output so automation can ingest fork state, overlay provenance (features/patches/skip counts), patch drift, and guard-driven `both_touched` metrics. Implementation pending.

## Milestones
- [ ] Emit `status_version: 1` JSON from `forked status --json` (backed by provenance).
- [ ] Populate overlay `selection` (with `selection.source`) from `.forked/logs/forked-build.log` / notes; fall back gracefully when absent.
- [ ] Support `--latest N` overlays with sane defaults and empty-state messaging.
- [ ] Document schema and example usage in README.

## Metrics
- Story Points (planned): 2
- Critical Path: Build provenance integration
- Dependencies: feature-slice-workflows (for resolver metadata)

## Next Steps
1. Implement CLI flag + schema writer.
2. Extend build provenance logging utilities.
3. Add docs/tests and update release plan.
