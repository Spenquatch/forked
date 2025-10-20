---
title: Feature Slice Workflows Implementation Plan
type: implementation-plan
feature: feature-slice-workflows
date: 2025-10-20
tags: [implementation, plan]
---

# Implementation Plan

## Scope
- Expand `forked build` with selective overlay flags and include/exclude filters.
- Persist feature + overlay definitions in `forked.yml` with schema validation.
- Introduce `forked feature create` and `forked feature status` commands.
- Capture build provenance (features, patches, commit ranges) and optional git notes.
- Add opt-in `--skip-upstream-equivalents` to filter upstream-identical commits while logging skips.
- Provide feature metadata to guard/status consumers via provenance.

## Work Breakdown
1. **Configuration & Resolver**
   - [ ] Extend config dataclasses to load `features` and `overlays`.
   - [ ] Validate feature patches exist in `patches.order`; ensure overlays resolve to known features.
   - [ ] Implement resolver producing ordered patch list + active feature set.
   - [ ] Add unit tests covering overlays, feature unions, include/exclude precedence, and error conditions.
2. **Build Command Enhancements**
   - [ ] Wire `--overlay`, `--features`, `--include`, `--exclude` into build command.
   - [ ] Surface active feature summary in build logs + JSON metadata; persist provenance to `.forked/logs/forked-build.log` and git notes.
   - [ ] Document precedence rules, provenance schema, and default overlay naming.
3. **Feature Management CLI & Skip Optimisations**
   - [ ] Implement `forked feature create --slices`.
   - [ ] Update `forked.yml` atomically with new feature entries and patch slices.
   - [ ] Build `feature status` summary with ahead/behind metrics.
   - [ ] Implement `--skip-upstream-equivalents` (via `git cherry -v`) and log skipped commits per patch.
   - [ ] Ensure commands exit non-zero on config conflicts or branch collisions.
4. **Integration Points**
   - [ ] Feed provenance data to guard/report/status consumers (coordinate with guard-automation task).
   - [ ] Update README and help docs with examples of feature-aware guard usage and provenance inspection.

## Validation
- Unit tests for resolver, CLI argument parsing, config validation.
- Integration tests using demo repo covering profile build, feature status, and guard output.
- Manual workflow: create new feature, commit on slice, build overlay, run guard, inspect JSON.

## Deliverables
- Updated README sections ("Feature slices", build/guard usage).
- CLI help text for new subcommands + options.
- Feature status page and changelog revisions.
