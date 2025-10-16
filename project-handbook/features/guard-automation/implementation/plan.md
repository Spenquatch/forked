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
   - [ ] Replace legacy `SystemExit` calls with `typer.Exit(code)` across guard entry points; assert codes `0/2/4` in integration tests.
   - [ ] Add `"report_version": 1` to the generated JSON and document schema in README + testing guide.
   - [ ] Update README guard section with exit-code table and example output snippet.
2. **Sentinels**
   - [ ] Refactor sentinel collection to gather the union of trunk/overlay paths (handle missing files gracefully).
   - [ ] Adjust `must_diverge_from_upstream` to treat overlay-only files as compliant while flagging missing overlay paths.
   - [ ] Log sentinel matches with path lists for easier debugging (consider `--verbose` flag).
3. **Size Caps & Reporting**
   - [ ] Replace `--shortstat` parsing with `git diff --numstat` aggregation; ensure binary (`-`) entries increment file counts.
   - [ ] Produce a golden `.forked/report.json` fixture from the sample repo and store under `tests/fixtures/` for future comparison.
4. **Automation Hooks**
   - [ ] Add guard invocation to CI template (post-build) and document required environment variables.
   - [ ] Capture guard artefacts via `make release-status` and surface in release notes.

## Validation
- Run `forked guard --overlay overlay/test --mode block` to confirm exit 2 on violations.
- Inspect generated `.forked/report.json` for `"report_version": 1`.
- Verify sentinel coverage by deleting a trunk-owned file in overlay and rerunning guard.

## Risks & Mitigations
- **Risk**: Binary diffs produce `-` entries. Mitigation: treat `-` as change (documented).
- **Risk**: Large overlays slow guard runs. Mitigation: add future path filters, but out-of-scope for v0.1.0.
