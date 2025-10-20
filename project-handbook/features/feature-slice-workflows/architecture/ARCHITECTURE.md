---
title: Feature Slice Workflows Architecture
type: architecture
feature: feature-slice-workflows
date: 2025-10-20
tags: [architecture, cli]
---

# Feature Slice Workflows Architecture

## Configuration Model
- Extend `forked.yml` with `features` map (feature name → ordered patch list + optional sentinels).
- Add `overlays` map (profile name → ordered list of features and/or explicit patches).
- Validation layer ensures:
  - Every feature patch exists in `patches.order`.
  - Overlay profiles reference known features or patch globs.
  - Feature-level sentinels merge without conflicting with global policies (conflicts flagged early).

## Build Resolver
1. Start from global `patches.order` to preserve deterministic cherry-pick sequence.
2. Collect selection sources:
   - Overlay profile (`--overlay`) expands to a union of referenced features.
   - Explicit feature list (`--features`) merges patch sets.
   - `--include` appends additional matching patch branches.
   - `--exclude` removes matches from the final ordered list.
3. Resolver returns the de-duplicated ordered slice list for the cherry-pick loop and the active feature set for guard.

## Feature Management Commands
- `forked feature create <name> --slices N`
  - Derives base commit from `trunk`.
  - Creates `patch/<name>/<NN>-<slug>` branches.
  - Updates config maps atomically (write temp file + replace).
- `forked feature status`
  - Walks feature → patch mapping.
  - Uses `git rev-list --left-right --count trunk...patch` to surface ahead/behind counts.
  - Summarizes commit SHAs and merge state.

## Guard Integration
- Guard loads active feature set from build metadata (overlay profile or explicit list).
- Merges global `guards.sentinels` with any `feature.sentinels`.
- Feeds feature attribution into JSON report:
  - `violations_by_feature`
  - `both_touched_by_feature`
  - Risk severity escalates when sentinel violations occur.

## Documentation & Help
- Typer command groups gain new options with detailed help text describing precedence rules.
- README examples show:
  - Declaring features/overlays in `forked.yml`.
  - Building overlays for dev/staging profiles.
  - Inspecting slice status prior to publish.
