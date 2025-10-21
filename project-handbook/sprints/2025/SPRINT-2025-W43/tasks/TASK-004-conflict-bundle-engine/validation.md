---
title: Conflict Bundle Engine - Validation Guide
type: validation
date: 2025-10-20
task_id: TASK-004
tags: [validation]
links: []
---

# Validation Guide

## Automated
- [ ] `pytest tests/test_conflict_bundle_v2.py -q`
- [ ] `pytest tests/test_sync_conflict_autocontinue.py -q`
- [ ] `make validate`

## Manual
1. Run `forked build --emit-conflicts` in demo repo with forced conflict.
   - Confirm exit code `10`.
   - Open JSON; verify `schema_version == 2`, `wave == 1`, `shell == "posix"`, context.mode == `"build"`, file entries include precedence + commands.
2. Run `forked sync --emit-conflicts` with upstream conflict (default stop mode).
   - Confirm exit code `10`.
   - JSON should reference patch branch, commit SHA, `wave`, and resume commands.
3. Re-run sync with auto-continue:
   ```bash
   forked sync --emit-conflicts .forked/conflicts/sync-continue.json --auto-continue --on-conflict bias
   ```
   - Verify bias actions logged and next bundle increments `wave` and filename (`-2.json`).
4. Enable blob export: `--conflict-blobs-dir .forked/conflicts/blobs`.
   - Ensure base/ours/theirs files created per path and referenced in JSON when diffs are null/binary.
5. Test `--on-conflict exec` to ensure CLI propagates script exit codes and bundle path logging.
6. Follow README CI snippet to ensure docs instructions align with behavior (including Windows POSIX note).

## Sign-off
- [ ] Bundles generated for build + sync share schema v2 and include wave/binary metadata.
- [ ] README/handbook updated with schema + CI example.
- [ ] Task checklist complete; attach sample bundle or logs in daily status.
