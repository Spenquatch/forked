---
title: Status JSON Testing Guide
type: testing
feature: status-json
date: 2025-10-20
tags: [testing]
---

# Testing Guide

## Automated
- `pytest tests/test_status_json.py -q` – unit tests for schema structure and ahead/behind calculations.
- `pytest tests/test_provenance_integration.py -q` – ensures overlay selection metadata is sourced from logs/notes.

## Manual
1. `forked build --overlay dev --id dev-test` (ensure provenance logged).
2. `forked status --json | jq '.overlays[0]'` – verify `selection.features`, `patches`, `built_at`.
3. `forked status --json --latest 1` – confirm pagination.
4. Delete provenance entry and re-run to observe fallback behaviour/warning.

## Regression
- Run `make validate` to ensure documentation references remain intact.
- Guard pipeline should show `report.features` populated from status provenance.
