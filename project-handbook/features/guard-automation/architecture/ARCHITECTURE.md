---
title: Guard Automation Architecture
type: architecture
feature: guard-automation
date: 2025-09-22
tags: [architecture, guard]
---

# Guard Automation Architecture

## Guard Workflow
1. Determine merge base between `trunk` and `overlay/<id>`.
2. Collect signals:
   - Both-touched files (`git diff --find-renames`).
   - Sentinel policies (`must_match_upstream`, `must_diverge_from_upstream`).
   - Size caps (files changed, LOC).
3. Emit a JSON report (`.forked/report.json`) with `report_version`, violations, and aggregated metrics.
4. Exit with policy-aware codes: `0` pass, `2` violation, `4` configuration/system error.

## Sentinel Evaluation
- Sentinels examine the union of trunk and overlay file listings via `git ls-tree -r`.
- `must_match_upstream`: overlay blob hash must equal trunk hash. Missing overlay files trigger violations.
- `must_diverge_from_upstream`: overlay blob must differ from trunk; overlay-only files are treated as valid divergence, while missing overlay files or identical blobs violate the rule.

## Size Measurement
- Use `git diff --numstat trunk...overlay` to sum insertions/deletions. Binary files (`-`) count as changes but do not contribute LOC totals.
- Stack-level thresholds (max files/LOC) drive violation flags and summary metrics.

## Exit-Code Contract
- All public CLI exits use `typer.Exit(code)` for deterministic error handling within automation and CI.
- `guards.mode` (`warn`, `block`, `require-override`) gates whether violations convert to exit code `2` or remain informational.

## Extensibility Hooks
- Future work: attach per-file risk scores, integrate symbol-level analysis, or accept precomputed metrics via STDIN for distributed guard runs.
