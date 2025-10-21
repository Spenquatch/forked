---
title: Conflict Bundle Automation Implementation Plan
type: implementation-plan
feature: conflict-bundle-automation
date: 2025-10-20
tags: [implementation, plan]
---

# Implementation Plan

## Scope
- Provide consistent conflict bundle generation for build and sync flows.
- Support optional blob exports, deterministic exit codes, and multi-wave numbering.
- Document schema v2 (binary handling, shell metadata) and sync auto-continue policy.

## Work Breakdown
1. **Shared Conflict Collector**
   - [ ] Gather conflict metadata (blob ids, diffs, precedence) and include `wave`, `binary`, `size_bytes`, `shell` fields.
   - [ ] Handle binary/large files via blob dumps and diff suppression (`diffs.* = null`).
   - [ ] Emit bundles under `.forked/conflicts/<overlay-id>-<wave>.json`; append entries to `.forked/logs/forked-build.log` with wave info.
   - [ ] Add POSIX shell metadata and note for Windows guidance.
2. **Build Integration**
   - [ ] Wire CLI options (`--emit-conflicts`/`--emit-conflicts-path`, `--emit-conflict-blobs`/`--conflict-blobs-dir`, `--on-conflict`, `--on-conflict-exec`).
   - [ ] Hook collector into cherry-pick failure path; log bundle location and wave number.
   - [ ] Exit code `10` on conflict bundles; propagate child status for `--on-conflict exec`.
3. **Sync Integration**
   - [ ] Share collector; default to stop-on-conflict.
   - [ ] Implement `--auto-continue` bias loop (apply path bias, log actions, increment wave).
   - [ ] Ensure context fields (`patch_branch`, `patch_commit`, `merge_base`) populated per wave.
4. **Docs & Tests**
   - [ ] Update README/handbook with schema v2, wave numbering, Windows note, and CI example.
   - [ ] Add unit/integration tests for binary files, multi-wave scenarios, exec hooks, and sync auto-continue.

## Validation
- `pytest tests/test_conflict_bundle_v2.py -q`
- `pytest tests/test_sync_conflict_autocontinue.py -q`
- Manual validation per sprint task.

## Risks & Mitigations
- **Risk**: Large blobs inflate storage. Mitigation: keep blob-export optional and document cleanup.
- **Risk**: Multi-wave numbering confusion. Mitigation: log wave info and suffix filenames consistently.
- **Risk**: Platform differences. Mitigation: document POSIX shell requirement for commands.
