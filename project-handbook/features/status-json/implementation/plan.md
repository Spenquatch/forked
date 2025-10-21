---
title: Status JSON Implementation Plan
type: implementation-plan
feature: status-json
date: 2025-10-20
tags: [implementation, plan]
---

# Implementation Plan

## Scope
- Expose `forked status --json` with a documented schema (`status_version: 1`).
- Integrate build provenance (features, patches, timestamps) into status output.
- Provide overlay pagination (`--latest N`) and patch drift counters.

## Work Breakdown
1. **Schema Writer**
   - [ ] Add `--json` flag, defaulting to human-readable output when absent.
   - [ ] Emit upstream/trunk fields (remote, branch, SHAs).
   - [ ] List patches with `ahead/behind` counts (skip gracefully on errors and log at DEBUG).
2. **Overlay Metadata**
   - [ ] Extend build workflow to log selection metadata (`.forked/logs/forked-build.log`) and optional Git notes.
   - [ ] Read provenance to populate overlay `selection`, `built_at` (ISO 8601 UTC), and `both_touched_count` (from latest guard report when available, otherwise `null`).
   - [ ] Implement `--latest N` overlay window (default 5) and mark `selection.source` as `"provenance"` or `"derived"` when falling back.
3. **Validation & Docs**
   - [ ] Add unit/integration tests covering empty overlays, pagination, provenance fallback, and guard-report-driven counts.
   - [ ] Document JSON schema, fallback behaviour, and sample `jq` usage in README + handbook.

## Validation
- `pytest tests/test_status_json.py -q`
- Manual run: `forked status --json | jq`
- Ensure schema version and provenance linkage recorded in release notes.

## Risks & Mitigations
- **Risk**: Large overlay lists inflate output. Mitigation: default to latest 5 and document overrides.
- **Risk**: Missing provenance results in incomplete selection data. Mitigation: fall back to resolver and warn operator.
