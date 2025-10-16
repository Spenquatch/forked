---
title: Guard Automation Implementation Plan
type: implementation-plan
feature: guard-automation
date: 2025-09-22
tags: [implementation, plan]
---

# Implementation Plan

## Scope
- Align guard CLI behaviour with README contract and CI automation.
- Improve sentinel detection for missing overlay files.
- Replace locale-sensitive diff parsing with deterministic metrics.

## Work Breakdown
1. **CLI Contract**
   - [ ] Swap `SystemExit` for `typer.Exit` with explicit codes.
   - [ ] Include `"report_version": 1` metadata.
   - [ ] Document guard exit codes in README checklists.
2. **Sentinels**
   - [ ] Union trunk/overlay file lists to catch deletions and additions.
   - [ ] Treat overlay-only files as valid divergence.
3. **Size Caps**
   - [ ] Parse `--numstat` output to total LOC/files.
   - [ ] Store sample report for regression tests.
4. **Automation**
   - [ ] Wire guard run into CI workflow smoke job (post-release task).

## Validation
- Run `forked guard --overlay overlay/test --mode block` to confirm exit 2 on violations.
- Inspect generated `.forked/report.json` for `"report_version": 1`.
- Verify sentinel coverage by deleting a trunk-owned file in overlay and rerunning guard.

## Risks & Mitigations
- **Risk**: Binary diffs produce `-` entries. Mitigation: treat `-` as change (documented).
- **Risk**: Large overlays slow guard runs. Mitigation: add future path filters, but out-of-scope for v0.1.0.
