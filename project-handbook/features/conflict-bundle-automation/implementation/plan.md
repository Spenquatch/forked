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
- Support optional blob exports and deterministic exit codes.
- Add conflict handling knobs: `--on-conflict stop|bias|exec`.
- Document schema v1 and integration guidance.

## Work Breakdown
1. **Shared Conflict Collector**
   - [ ] Extract helper to gather conflict metadata (blob ids, diffs, precedence).
   - [ ] Implement serializer writing JSON bundle + optional blob directories.
   - [ ] Add unit tests covering precedence + command hints.
2. **Build Integration**
   - [ ] Add CLI options (`--emit-conflicts`, `--conflict-blobs-dir`, `--on-conflict`, `--on-conflict-exec`).
   - [ ] Hook collector into cherry-pick error path, ensure worktree resets on abort.
   - [ ] Exit `10` after successful bundle write; log bundle location.
3. **Sync Integration**
   - [ ] Extend rebase loop to invoke collector when `git rebase` stops.
   - [ ] Share bundle path computation + exit codes with build.
   - [ ] Support continuing/aborting sync via resume hints.
4. **Docs & Examples**
   - [ ] Add README section for conflict bundles (JSON snippet + blob directory layout).
   - [ ] Provide CI snippet demonstrating exit-code handling.
   - [ ] Update changelog + feature status accordingly.

## Validation
- Unit tests for serializer (sample conflict data → expected JSON).
- Integration test: intentionally create conflict during build; assert JSON file and exit 10.
- Integration test: conflict during sync rebase; confirm bundle and exit 10.
- Manual QA: run `forked build --emit-conflicts .forked/conflicts/test.json` and inspect blob exports.

## Deliverables
- Bundle schema markdown/README section.
- New CLI help text for conflict flags.
- Feature status and changelog updates.
