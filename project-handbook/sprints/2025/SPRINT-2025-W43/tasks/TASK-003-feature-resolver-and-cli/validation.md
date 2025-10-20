---
title: Feature Resolver & CLI - Validation Guide
type: validation
date: 2025-10-20
task_id: TASK-003
tags: [validation]
links: []
---

# Validation Guide

## Automated Checks
- [ ] `pytest tests/test_config_features.py tests/test_cli_feature.py tests/test_build_provenance.py -q`
- [ ] `pytest tests/test_skip_upstream_equivalents.py -q`
- [ ] `make validate`

## Manual Walkthrough
1. **Overlay Profile Build**
   - Run `forked build --overlay dev --id dev-test`.
   - Confirm build log reports features resolved (dev → `[payments_v2, branding]`).
2. **Feature List Build**
   - `forked build --features payments_v2 --exclude 'patch/branding/*'`.
   - Ensure resulting overlay contains only payments_v2 patches.
3. **Feature Management Commands**
   - `forked feature create checkout --slices 2` → verify branches + config entry.
   - Commit on slice; run `forked feature status` to confirm ahead count displays.
4. **Provenance Log**
   - Inspect `.forked/logs/forked-build.log` and optional git note for overlay to confirm patches/features/skip counts recorded.
5. **Skip Upstream Equivalents**
   - Craft a patch branch with upstream-identical commit; run `forked build --features payments_v2 --skip-upstream-equivalents`.
   - Confirm cherry-pick skips the commit and logs skip count.

## Sign-off Checklist
- [ ] All acceptance criteria satisfied.
- [ ] Docs updated (README, help text, feature status).
- [ ] Task checklist completed and attached evidence noted in daily status.
