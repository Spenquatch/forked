---
title: Project Changelog
type: changelog
date: 2025-09-12
tags: [changelog]
links: []
---

## [Unreleased]

### Added
- Pending updates post v1.1.0 planning

## [1.1.0] - 2025-10-31
### Added
- Feature slice workflows (`forked build --overlay/--features`, feature scaffolding commands, provenance logging, `--skip-upstream-equivalents`).
- Guard policy overrides (`mode=require-override`) with trailer/note detection and `report_version: 2`.
- Conflict bundle automation v2 (binary handling, multi-wave bundles, sync auto-continue policy).
- Operational tooling: `forked status --json` (`status_version: 1`) and `forked clean` with dry-run + confirm safety rails.
- README + CLI docs covering overrides, status JSON, clean workflow, and updated CI snippets.

## [1.0.0] - 2025-09-27
### Added
- Hardened overlay infrastructure (ADR-0001)
- Guard CLI contract with deterministic exit codes and report versioning (ADR-0002)
- Release operations docs + CI updates
