---
title: Status JSON Testing Guide
type: testing
feature: status-json
date: 2025-10-20
tags: [testing]
---

# Testing Guide

## Automated
- `pytest tests/test_status_json.py -q`
- `pytest tests/test_provenance_integration.py -q`

## Manual
1. `forked status --json | jq` → confirm `status_version: 1`, `selection.source` set to `"provenance"` when log present.
2. `forked status --json --latest 2 | jq '.overlays'` → verify pagination and ISO `built_at` timestamps.
3. Run build without guard, inspect JSON (`both_touched_count: null`). Then run guard, rerun status to ensure count populated from report.
4. Remove provenance entry, rerun status: expect warning and `selection.source == "derived"`.

## Regression
- Ensure README/handbook schema snippets stay in sync with CLI output.
