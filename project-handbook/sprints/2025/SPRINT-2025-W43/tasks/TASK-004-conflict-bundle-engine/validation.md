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
   - Open JSON; verify `schema_version == 2`, `wave == 1`, context.mode == `"build"`, file entries include precedence + commands.
2. Run `forked sync --emit-conflicts` with upstream conflict.
   - Confirm exit code `10`.
   - JSON should reference patch branch, commit SHA, `wave`, and resume commands; `--auto-continue` logs bias actions.
3. Enable blob export: `--conflict-blobs-dir .forked/conflicts/blobs`.
   - Ensure base/ours/theirs files created per path and referenced in JSON when diffs are null.
4. Trigger second conflict wave (bias applied then new conflict) to confirm numbered bundle (`-2.json`) created and log entry appended.
5. Test `--on-conflict exec` to ensure CLI propagates script exit codes and bundle path logging.
6. Follow README CI snippet to ensure docs instructions align with behavior.

## Sign-off
- [ ] Bundles generated for build + sync share schema v2 and include wave/binary metadata.
- [ ] README/handbook updated with schema + CI example.
- [ ] Task checklist complete; attach sample bundle or logs in daily status.
