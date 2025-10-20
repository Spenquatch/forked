---
title: Feature Slice Workflows Changelog
type: changelog
feature: feature-slice-workflows
date: 2025-10-20
tags: [changelog]
---

# Changelog

## Planned
- Add `features` and `overlays` sections to `forked.yml` with validation for patch ordering and sentinel overrides.
- Extend `forked build` with `--overlay`, `--features`, `--include`, and `--exclude`.
- Ship `forked feature create` and `forked feature status` commands for slice management.
- Update guard to respect feature-scoped sentinels and emit per-feature risk summaries.
- Persist overlay provenance (features, patches, commit ranges) to `.forked/logs/forked-build.log` and optional git notes.
- Add `--skip-upstream-equivalents` flag to filter upstream-identical commits and log skip counts.
- Document feature workflow usage in README and CLI help.
