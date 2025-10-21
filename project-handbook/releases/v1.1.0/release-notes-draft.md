---
title: v1.1.0 Draft Release Notes (Tasks 003-004)
type: release-notes
date: 2025-10-21
tags: [release, draft]
---

# Draft Release Notes – v1.1.0 (Tasks 003 & 004)

## Overview
The first wave of v1.1.0 work lands two pillar capabilities:

1. **Feature-Sliced Workflows** (TASK-003) – Overlay builds can now be driven by feature definitions with provenance-aware logging and new feature management commands.
2. **Conflict Bundle Engine v2** (TASK-004) – Build and sync commands emit schema v2 conflict bundles with binary awareness, multi-wave numbering, and deterministic exit codes.

Subsequent tasks (guard overrides, status JSON, clean command) will extend these notes. This draft captures the changes already merged to keep documentation fresh while the remaining work is underway.

## Highlights

### Feature Resolver & CLI (TASK-003)
- `forked.yml` gains `features` and `overlays` sections so teams can define feature slices once and reuse them across builds.
- `forked build` supports new selectors: `--overlay`, `--features`, `--include`, `--exclude`, and `--skip-upstream-equivalents`. The resolver preserves global patch order, warns on unmatched filters, and logs provenance (features, patches, filters) to `.forked/logs/forked-build.log` plus optional git notes.
- New commands:
  - `forked feature create <name> --slices N` scaffolds numbered patch branches rooted at the current trunk tip and updates `forked.yml`.
  - `forked feature status` shows ahead/behind information for each slice, highlighting merged or lagging patches.
- Build telemetry now records the active feature set, enabling guard/status tooling and CI bots to understand overlay provenance.

### Conflict Bundle Engine (TASK-004)
- `forked build` and `forked sync` accept conflict options:
  - `--emit-conflicts [PATH]` writes schema v2 bundles (binary detection, multi-wave numbering, POSIX shell note).
  - `--conflict-blobs-dir [DIR]` exports base/ours/theirs blobs for each conflicted file (always used for binary/large diffs).
  - `--on-conflict <stop|bias|exec>` controls behaviour:
    - `stop` (default) writes the bundle and exits with code 10.
    - `bias` applies recommended ours/theirs decisions based on sentinels/path bias before attempting `--continue`, logging actions and emitting additional waves if conflicts remain.
    - `exec` runs an external command (using `{json}` placeholder) and exits with the command’s status.
  - `--on-conflict-exec` provides the external command string for `exec` mode.
- Bundles include patch branch, commit SHA, merge base, feature attribution, recommended resolutions, POSIX commands, and resume instructions. Multi-wave conflicts append `-2.json`, `-3.json`, etc., with wave info logged to `.forked/logs/forked-build.log`.
- Sync integration mirrors build behaviour, returning to the previous ref on success and defaulting to stop-on-conflict unless `--auto-continue` / `--on-conflict bias` is specified.

## Upgrade Notes
- Update existing `forked.yml` files to include `features` and `overlays`. The resolver ignores missing entries but new CLI options expect them for provenance logging.
- CI workflows that wrap `forked build` or `forked sync` should watch for exit code `10` when conflicts are emitted and surface the bundle path in job logs/artifacts.
- Bundles assume a POSIX shell for command snippets; Windows environments should run under Git Bash/WSL or translate the commands accordingly.

## Pending Items
- Guard policy overrides/report v2 (TASK-006), status JSON (TASK-007), and clean command (TASK-008) will extend these notes. Final release copy will roll up all features once the remaining tasks land.

