---
title: Status JSON CLI - Implementation Steps
type: implementation
date: 2025-10-20
task_id: TASK-007
tags: [implementation]
links: []
---

# Implementation Steps: Status JSON CLI

## Step 1: Schema Writer
- [ ] Add `--json` flag and schema writer emitting `status_version: 1`.
- [ ] Populate upstream/trunk SHAs and patch list with ahead/behind counts (handle missing gracefully).

## Step 2: Overlay Provenance
- [ ] Read `.forked/logs/forked-build.log` / git notes to assemble recent overlay entries.
- [ ] Implement `--latest N` option (default 5) and include `built_at`, `selection.features`, `selection.patches`, `both_touched_count`.
- [ ] Handle empty results (no overlays) with empty array + message to stderr.

## Step 3: Tests & Docs
- [ ] Create unit/integration tests for schema, pagination, and provenance fallback.
- [ ] Document schema and example usage (README + handbook feature page).
- [ ] Update changelog + release notes entry.

## Notes
- Preserve existing human-readable output when `--json` absent.
- Ensure JSON output is newline-terminated to aid piping.
