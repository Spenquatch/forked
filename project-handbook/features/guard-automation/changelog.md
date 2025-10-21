---
title: Guard Automation Changelog
type: changelog
feature: guard-automation
date: 2025-10-16
tags: [changelog]
---

# Changelog

## 2025-10-21
- Implemented policy override enforcement (`mode=require-override`) with commit/tag/note precedence and `policy_overrides.allowed_values` validation.
- Bumped guard report to `report_version: 2`, adding `override` and `features` blocks populated from provenance or resolver fallback.
- Added automated coverage for override sources, disallowed scopes, and provenance fallbacks.

## 2025-10-16
- Hardened guard CLI exit codes with `typer.Exit` (0 success, 2 violations, 3 config errors, 4 git issues).
- Added `"report_version": 1` field and diff metrics sourced from `git diff --numstat`.
- Updated sentinel union logic to treat overlay-only paths as compliant divergence and documented schema updates.
- Introduced `--verbose` guard mode plus `.forked/logs/forked-guard.log` telemetry for deeper diagnostics.

## 2025-09-22
- Documented guard workflow, sentinel logic, and test matrix.
- Updated implementation plan to cover exit codes, `report_version`, and `--numstat` aggregation.
