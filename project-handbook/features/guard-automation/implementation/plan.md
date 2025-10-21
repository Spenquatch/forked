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
- Enforce policy overrides (`mode=require-override`) using trailers/notes.
- Persist overlay provenance and expose feature context in reports.

## Work Breakdown
1. **CLI Contract**
   - [x] Replace legacy `SystemExit` calls with `typer.Exit(code)` across guard entry points; assert codes `0/2/4` in integration tests.
   - [x] Add `"report_version": 1` to the generated JSON and document schema in README + testing guide.
   - [x] Update README guard section with exit-code table and example output snippet.
2. **Sentinels**
   - [x] Refactor sentinel collection to gather the union of trunk/overlay paths (handle missing files gracefully).
   - [x] Adjust `must_diverge_from_upstream` to treat overlay-only files as compliant while flagging missing overlay paths.
   - [x] Log sentinel matches with path lists for easier debugging (`--verbose` flag).
3. **Size Caps & Reporting**
   - [x] Replace `--shortstat` parsing with `git diff --numstat` aggregation; ensure binary (`-`) entries increment file counts.
   - [x] Produce a golden `.forked/report.json` fixture from the sample repo and store under `tests/fixtures/` for future comparison.
4. **Automation Hooks**
   - [ ] Add guard invocation to CI template (post-build) and document required environment variables.
   - [ ] Capture guard artefacts via `make release-status` and surface in release notes.
5. **Policy Overrides & Report v2**
   - [x] Parse override trailers from overlay tip commits, publish tags, and `refs/notes/forked/override`.
   - [x] Honor `policy_overrides.require_trailer`, validate scope against `allowed_values`, and exit appropriately in `require-override` mode.
   - [x] Bump `report_version` to 2 with an `override` block and provenance-driven `features` list.
6. **Provenance Integration**
   - [x] Read `.forked/logs/forked-build.log` / overlay notes to attribute guard results per feature.
   - [x] Fall back to CLI selection when provenance missing; log warning for telemetry.

## Validation
- Run `forked guard --overlay overlay/test --mode block` to confirm exit 2 on violations.
- Run `forked guard --overlay overlay/test --mode require-override` with and without trailers to confirm exit codes and report override metadata.
- Inspect generated `.forked/report.json` for `"report_version": 2` plus `override` and `features` sections.
- Verify sentinel coverage by deleting a trunk-owned file in overlay and rerunning guard.

## Risks & Mitigations
- **Risk**: Binary diffs produce `-` entries. Mitigation: treat `-` as change (documented).
- **Risk**: Large overlays slow guard runs. Mitigation: add future path filters, but out-of-scope for v0.1.0.
- **Risk**: Overrides consumed from the wrong commit/tag. Mitigation: document discovery order and add unit tests that pin each source.
