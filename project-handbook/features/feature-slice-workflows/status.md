---
title: Feature Slice Workflows Status
type: status
feature: feature-slice-workflows
date: 2025-10-20
tags: [status]
---

# Status: Feature Slice Workflows

## Summary
Planning new CLI capabilities that allow selective overlays (`--overlay`, `--features`, include/exclude globs), feature scaffolding commands, provenance logging, and optional `--skip-upstream-equivalents`. Configuration schema changes introduce `features` and `overlays` maps plus optional per-feature sentinel overrides that guard consumes via provenance.

## Milestones
- [ ] CLI resolves overlay profiles and feature lists when building.
- [ ] `forked feature create` scaffolds numbered patch branches and updates `forked.yml`.
- [ ] `forked feature status` reports slice drift versus `trunk`.
- [ ] Provenance recorded in `.forked/logs/forked-build.log` + git notes (`patches`, `features`, commit ranges).
- [ ] `--skip-upstream-equivalents` filters upstream-identical commits and logs skipped counts.
- [ ] Documentation and examples cover the expanded schema, provenance, and skip flag.

## Metrics
- Planned Story Points: 8 (est.)
- Critical Path: `forked build` resolver + config validation
- Dependencies: Config parser refactor from v1.0.0 release

## Next Steps
1. Implement resolver + schema validation for features and overlays.
2. Deliver Typer commands for feature management.
3. Persist provenance + skip metrics for guard/status consumers.

## Active Work (auto-generated)
*No tasks scheduled yet. Will populate once sprint starts.*
