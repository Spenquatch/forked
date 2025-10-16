---
title: Guard Automation Testing Guide
type: testing
feature: guard-automation
date: 2025-09-22
tags: [testing, guard]
---

# Testing Guide

## Manual Regression Suite
1. Prepare overlay with known violations:
   - Delete a trunk-owned sentinel file → expect `must_match_upstream` violation.
   - Leave overlay-only file in `must_diverge_from_upstream` path → expect **no** violation.
2. Run `forked guard --overlay overlay/test --mode block`.
   - Exit code should be `2`.
   - `.forked/report.json` must include `"report_version": 1` and violation details.
3. Re-run with `--mode warn`; exit should be `0` while violations remain reported.

## Size Cap Verification
1. Create overlay with >N files changed (configure `size_caps.max_files=1`).
2. Execute guard and ensure `violations.size_caps` includes aggregated file and LOC counts.

## JSON Schema Spot Check
```bash
jq '.report_version, .violations' .forked/report.json
diff -u project-handbook/tests/fixtures/guard-report-example.json .forked/report.json | head
```
- Confirm `report_version == 1`.
- Ensure sentinel and size cap sections map to lists/dicts as documented.

## Automation Smoke Test
- Invoke guard from CI after every overlay build: `forked guard --overlay overlay/$RUN_ID --mode block`.
- Capture guard output artefact via `make status` or direct upload.

## Future Enhancements
- Add unit tests around sentinel helpers (`gitutil.blob_hash`, `_make_spec`).
- Consider golden JSON fixtures to prevent schema drift.
