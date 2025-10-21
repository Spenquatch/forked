---
title: Conflict Bundle Automation Changelog
type: changelog
feature: conflict-bundle-automation
date: 2025-10-20
tags: [changelog]
---

# Changelog

## 2025-10-21
- Implemented schema v2 conflict bundles for both `forked build` and `forked sync`, including binary detection, multi-wave numbering, and blob exports.
- Added `--emit-conflicts`/`--emit-conflicts-path`, `--emit-conflict-blobs`/`--conflict-blobs-dir`, `--on-conflict`, and `--on-conflict-exec` options; preserved `--auto-continue` as a bias alias.
- Standardised exit code `10` for unresolved conflicts and logged wave metadata to `.forked/logs/forked-build.log`.
- Updated README with bundle schema summary, CI usage example, and usage docs; added regression tests covering build + sync flows.

## Planned
- Collect real-world feedback on bundle consumers (bots/CI) and iterate on schema extensions if needed.
- Explore PowerShell-friendly command snippets for Windows-first teams.
