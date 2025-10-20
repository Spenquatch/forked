---
title: Conflict Bundle Automation Status
type: status
feature: conflict-bundle-automation
date: 2025-10-20
tags: [status]
---

# Status: Conflict Bundle Automation

## Summary
Designing a shared conflict reporter for `forked build` and `forked sync` that emits schema v2 bundles (binary awareness, multi-wave numbering), optional blob archives, and deterministic exit codes. Provides machine-parseable guidance for manual or automated resolution flows, with sync defaulting to stop-on-conflict unless `--auto-continue` is supplied.

## Milestones
- [ ] Shared conflict inspection utility captures blob IDs, diffs, wave metadata, and recommended resolution.
- [ ] `forked build --emit-conflicts/--conflict-blobs-dir` writes schema v2 bundles, handles binary/large files, and exits 10 on stop.
- [ ] `forked sync` supports the same flags, honours `--auto-continue`, and logs bias applications plus multi-wave bundles.
- [ ] `--on-conflict exec/bias` hooks allow optional automation with safe defaults documented.
- [ ] JSON schema v2 documented and referenced from README + tests (maintaining backwards compatibility guidance).

## Metrics
- Planned Story Points: 5 (est.)
- Critical Path: ingesting `git ls-files -u` output reliable across platforms.
- Dependencies: Feature-slice resolver for feature attribution field.

## Next Steps
1. Build conflict metadata collector + serializer (binary + wave support).
2. Integrate with build workflow, ensure cleanup + messaging, log provenance.
3. Extend sync rebase loop to share conflict handling and default stop-on-conflict.
4. Add docs/tests validating schema v2, multi-wave numbering, Windows notes.

## Active Work (auto-generated)
*No active tasks yet.*
