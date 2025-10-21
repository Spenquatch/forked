---
title: Conflict Bundle Engine - Implementation Steps
type: implementation
date: 2025-10-20
task_id: TASK-004
tags: [implementation]
links: []
---

# Implementation Steps: Conflict Bundle Engine

## Step 1: Collector Library
- [ ] Implement helper to read index stages, compute diffs, and build precedence metadata.
- [ ] Detect binary/large files, set `diffs.* = null`, add `binary/size_bytes`, and always write blobs when needed.
- [ ] Add optional blob writer (base/ours/theirs) behind CLI flag.
- [ ] Unit test precedence logic, schema v2 structure (wave, shell note), and blob export.

## Step 2: Build Integration
- [ ] Extend `forked build` parser with conflict flags (`--emit-conflicts`/`--emit-conflicts-path`, `--emit-conflict-blobs`/`--conflict-blobs-dir`, `--on-conflict`, `--on-conflict-exec`).
- [ ] Hook collector into cherry-pick failure path; ensure cleanup/abort messaging.
- [ ] Generate wave-numbered bundle filenames when multiple conflict cycles occur; append entries to `.forked/logs/forked-build.log`.
- [ ] Exit code `10` when bundle generated; respect exec return code overrides.

## Step 3: Sync Integration
- [ ] Instrument rebase loop to capture conflicts in the same way.
- [ ] Ensure context fields capture `patch_branch`, `patch_commit`, and `merge_base`.
- [ ] Default to stop-on-conflict; add `--auto-continue` handling with bias logs and wave numbering.
- [ ] Support bias/exec modes consistently; document differences if any.

## Step 4: Documentation & Examples
- [ ] Update README with schema snippet, CLI usage, and CI example.
- [ ] Capture sample bundle for handbook/testing reference if useful.
- [ ] Update changelog + feature status.

## Notes
- Keep bundle writer idempotent; repeated conflicts should append wave suffix (`-1.json`, `-2.json`).
- Log emitted bundle path and shell requirements for quick discovery.
