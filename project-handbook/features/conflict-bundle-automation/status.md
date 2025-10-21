---
title: Conflict Bundle Automation Status
type: status
feature: conflict-bundle-automation
date: 2025-10-20
tags: [status]
---

# Status: Conflict Bundle Automation

## Summary
Shared collector now drives `forked build` and `forked sync`, emitting schema v2 bundles (binary awareness, multi-wave numbering), optional blob archives, and deterministic exit codes. Sync defaults to stop-on-conflict unless `--auto-continue`/`--on-conflict bias` is supplied.

## Milestones
- [x] Shared conflict inspection utility captures blob IDs, diffs (with binary detection), wave metadata, and recommended resolution.
- [x] `forked build --emit-conflicts`/`--emit-conflicts-path` with optional `--emit-conflict-blobs`/`--conflict-blobs-dir` writes schema v2 bundles, handles binary/large files, and exits 10 on stop.
- [x] `forked sync` supports the same flags, honours `--auto-continue`, and logs bias applications plus multi-wave bundles.
- [x] `--on-conflict exec/bias` hooks allow optional automation with safe defaults documented.
- [x] JSON schema v2 documented and referenced from README + tests (maintaining backwards compatibility guidance).

## Metrics
- Planned Story Points: 5 (est.)
- Critical Path: ingesting `git ls-files -u` output reliable across platforms.
- Dependencies: Feature-slice resolver for feature attribution field.

## Next Steps
1. Monitor downstream adoption (bots/CI) and gather feedback on exit codes & schema fields.
2. Evaluate plan for Windows-friendly command hints or PowerShell equivalents if needed.

## Active Work (auto-generated)
*No active tasks yet.*
