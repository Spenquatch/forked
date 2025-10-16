---
title: Guard Automation Changelog
type: changelog
feature: guard-automation
date: 2025-09-22
tags: [changelog]
---

# Changelog

## 2025-10-16
- Hardened guard CLI exit codes with `typer.Exit` (0 success, 2 violations, 3 config errors, 4 git issues).
- Added `"report_version": 1` field and diff metrics sourced from `git diff --numstat`.
- Updated sentinel union logic to treat overlay-only paths as compliant divergence and documented schema updates.

## 2025-09-22
- Documented guard workflow, sentinel logic, and test matrix.
- Updated implementation plan to cover exit codes, `report_version`, and `--numstat` aggregation.
