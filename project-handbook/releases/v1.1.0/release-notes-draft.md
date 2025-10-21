---
title: v1.1.0 Draft Release Notes (Tasks 003-008)
type: release-notes
date: 2025-10-21
tags: [release, draft]
---

# Draft Release Notes – v1.1.0 (Tasks 003–008)

## Overview
The v1.1.0 release delivers the full operational tooling stack planned for this cycle:

1. **Feature-Sliced Workflows** (TASK-003) – Overlay builds can be driven by feature definitions with provenance-aware logging and new feature management commands.
2. **Conflict Bundle Engine v2** (TASK-004) – Build and sync commands emit schema v2 conflict bundles with binary awareness, multi-wave numbering, and deterministic exit codes.
3. **Guard Policy Overrides & Report v2** (TASK-006) – `mode=require-override` enforces escalation trailers/notes while bumping guard reports to `report_version: 2`.
4. **Status JSON CLI** (TASK-007) – `forked status --json` exposes a machine-readable snapshot for dashboards and automation.
5. **Clean Command** (TASK-008) – `forked clean` introduces dry-run-first maintenance for overlays, worktrees, and conflict bundles.

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
  - `--emit-conflicts` writes schema v2 bundles to the default location (binary detection, multi-wave numbering, POSIX shell note).
  - `--emit-conflicts-path PATH` stores bundles at a caller-provided path.
  - `--conflict-blobs-dir [DIR]` exports base/ours/theirs blobs for each conflicted file (always used for binary/large diffs).
  - `--on-conflict <stop|bias|exec>` controls behaviour:
    - `stop` (default) writes the bundle and exits with code 10.
    - `bias` applies recommended ours/theirs decisions based on sentinels/path bias before attempting `--continue`, logging actions and emitting additional waves if conflicts remain.
    - `exec` runs an external command (using `{json}` placeholder) and exits with the command’s status.
  - `--on-conflict-exec` provides the external command string for `exec` mode.
- Bundles include patch branch, commit SHA, merge base, feature attribution, recommended resolutions, POSIX commands, and resume instructions. Multi-wave conflicts append `-2.json`, `-3.json`, etc., with wave info logged to `.forked/logs/forked-build.log`.
- Sync integration mirrors build behaviour, returning to the previous ref on success and defaulting to stop-on-conflict unless `--auto-continue` / `--on-conflict bias` is specified.

### Guard Policy Overrides & Report v2 (TASK-006)
- `forked guard --mode require-override` now validates escalation trailers in precedence order: overlay tip commit → annotated tags → `refs/notes/forked/override`.
- Overrides are compared against the configured `allowed_values` (e.g., `sentinel`, `size`, `both_touched`, `all`). Missing or disallowed scopes keep the run in failure (`exit 2`) with explicit messaging.
- Guard reports move to `report_version: 2`, adding an `override` block (source, values, allowed list, `applied` flag) plus a `features` block that replays provenance from build logs/notes (or resolver fallback when provenance is missing).
- Logs include the override and feature metadata so CI and dashboards share the same context as the human-readable output.

### Status JSON CLI (TASK-007)
- `forked status --json` produces a `status_version: 1` payload with upstream/trunk SHAs, per-patch ahead/behind counts, and the latest overlays (default window = 5).
- Overlay entries include `selection` provenance (features, patches, resolver source, include/exclude filters) and `both_touched_count` sourced from the latest guard report when available.
- CLI logs provenance fallbacks when build notes/logs are missing, marking `selection.source: "derived"` so consumers know when metadata was reconstructed.
- Inline docs and handbook updates showcase common `jq` snippets for dashboards (e.g., top drifting patches, newest overlays).

### Clean Command (TASK-008)
- `forked clean` defaults to dry-run mode, summarising targets grouped by overlays, worktrees, and conflicts. No destructive action occurs until the operator supplies **both** `--no-dry-run` and `--confirm`.
- Overlay pruning honours age specs/globs, retention via `--keep N`, tagged overlays, active worktrees, and provenance referenced within the keep window. Deletions are executed with `git branch -D`.
- Worktree cleanup combines `git worktree prune` with filesystem checks to remove orphaned `.forked/worktrees/<id>` directories.
- Conflict bundle cleanup removes aged JSON + blob directories while retaining the newest bundle per overlay id. All executed actions are appended to `.forked/logs/clean.log` for auditability.

## Upgrade Notes
- Update existing `forked.yml` files to include `features` and `overlays`. The resolver ignores missing entries but new CLI options expect them for provenance logging.
- CI workflows that wrap `forked build` or `forked sync` should watch for exit code `10` when conflicts are emitted and surface the bundle path in job logs/artifacts.
- Bundles assume a POSIX shell for command snippets; Windows environments should run under Git Bash/WSL or translate the commands accordingly.
- Guard automation adopters should set `policy_overrides.require_trailer`, `trailer_key`, and (optionally) `allowed_values` in `forked.yml`. Existing reports remain backwards compatible, but downstream tooling can now rely on the `override` and `features` blocks.
- Dashboards or guard pipelines that previously parsed human-readable `forked status` output can switch to `forked status --json` for stable machine-readable state.
- Operators should introduce `forked clean --dry-run` into their maintenance checklist (weekly or post-release), reviewing the plan before re-running with `--no-dry-run --confirm`.
