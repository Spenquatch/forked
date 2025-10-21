---
title: Status JSON CLI - Validation Guide
type: validation
date: 2025-10-20
task_id: TASK-007
tags: [validation]
links: []
---

# Validation Guide

## Automated
- [ ] `pytest tests/test_status_json.py -q`
- [ ] `pytest tests/test_provenance_integration.py -q`
- [ ] `make validate`

## Manual
1. Run `forked status --json | jq '.status_version'` → expect `1`.
2. Verify `overlays[0].selection.features` matches provenance from latest build log entry.
3. Run `forked status --json --latest 1` after multiple builds → ensure only the newest overlay returned.
4. Delete provenance log entry temporarily → ensure CLI falls back to resolver, sets `selection.source == "derived"`, and logs warning (stderr).

## Sign-off
- [ ] JSON schema matches spec and passes tests.
- [ ] Documentation updated with schema and examples.
- [ ] Task checklist satisfied.
