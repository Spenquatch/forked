---
title: Feature Resolver & CLI - Implementation Steps
type: implementation
date: 2025-10-20
task_id: TASK-003
tags: [implementation]
links: []
---

# Implementation Steps: Feature Resolver & CLI

## Prerequisites
- [ ] Working tree clean.
- [ ] Latest upstream synced via `forked sync`.
- [ ] Tests + lint tooling ready (`pytest`, `make validate`).

## Step 1: Config Schema & Resolver
**Timebox**: 1 day  
**Actions**
- [ ] Extend config dataclasses/models to include `features` + `overlays`.
- [ ] Implement validation helpers (unknown patch, unknown feature, duplicates).
- [ ] Build resolver returning ordered patch list + active feature set for logging/guard.
- [ ] Add unit tests for resolver precedence (overlay profile, features, include/exclude).
**Outcome**
- Resolver returns deterministic ordered lists and raises descriptive errors on invalid config.

## Step 2: Build Command Integration
**Timebox**: 0.5 day  
**Actions**
- [ ] Wire new flags into Typer command (help text, mutual exclusivity, defaults).
- [ ] Update build execution to consume resolver output and surface selected features.
- [ ] Record active feature list in overlay metadata and `.forked/logs/forked-build.log`.
- [ ] Write optional git notes (`refs/notes/forked-meta`) with patches/features summary.
- [ ] Document new options in README + CLI help.
**Outcome**
- `forked build` accepts new flags and persists provenance for downstream consumers.

## Step 3: Feature Commands & Skip Optimisations
**Timebox**: 1 day  
**Actions**
- [ ] Implement `forked feature create --slices` (branch creation + config updates).
- [ ] Add `forked feature status` to print ahead/behind summary.
- [ ] Introduce `--skip-upstream-equivalents` (using `git cherry -v`) and log skipped commits per patch.
- [ ] Ensure provenance entries capture resolver source, commit ranges, and skip counts.
- [ ] Update docs/tests accordingly.
**Outcome**
- Feature management commands operational; builds can skip upstream duplicates while logging full provenance.

## Notes
- Capture edge cases (invalid overlay name, duplicate slices) in tests + docs.
- Ensure CLI exit codes remain stable (non-zero on config errors).
