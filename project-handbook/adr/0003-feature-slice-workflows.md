---
id: ADR-0003
title: Feature Slice Workflows
type: adr
status: accepted
date: 2025-10-20
supersedes: null
superseded_by: null
tags: [features, overlays, guard]
links: [../features/feature-slice-workflows/overview.md]
---

## Context
Forked CLI v1.0.0 builds overlays from a single global patch stack. Teams need a repeatable way to combine subsets of patches into reusable overlay profiles, scaffold feature branches, and surface guard insights scoped to the active feature set. Manual cherry-pick reordering and ad-hoc scripts are brittle, slow, and difficult to automate in CI.

## Decision
- Extend `forked.yml` with `features` (named slice definitions) and `overlays` (profile shortcuts) while keeping `patches.order` the source of truth.
- Update `forked build` to accept `--overlay`, `--features`, `--include`, and `--exclude` flags that resolve to an ordered list of patch branches based on the new configuration.
- Ship `forked feature create` to scaffold numbered patch slices rooted at `trunk`, and `forked feature status` to report each slice’s drift relative to `trunk`.
- Merge feature-level sentinel rules into guard execution and annotate risk (`violations_by_feature`, `both_touched_by_feature`) in the JSON report.
- Document the workflow (config schema, CLI help, guard usage) so feature slices become the default collaboration model.

## Consequences
**Positive**
- Overlay construction is declarative and reproducible for dev/staging profiles.
- Feature onboarding is faster with CLI scaffolding and visibility into slice health.
- Guard reports highlight risk per feature, reducing triage noise.

**Negative**
- Configuration parsing becomes more complex and requires additional validation.
- Users must migrate configs when adopting feature slices (though backwards compatibility is maintained).

## Rollout & Reversibility
- Landing in release v1.1.0.
- Backwards compatible: forks without `features`/`overlays` fields continue to behave as before.
- Reversal path: remove CLI flags and schema extensions, reverting to global stack behaviour (not expected).
