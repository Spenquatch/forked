---
title: Feature Slice Workflows Testing Guide
type: testing
feature: feature-slice-workflows
date: 2025-10-20
tags: [testing, cli]
---

# Testing Guide

## Resolver & CLI Flags
1. Configure demo repo with two features and overlay profiles in `forked.yml`.
2. Run:
   ```bash
   forked build --overlay dev --emit-metadata .forked/dev.json
   forked build --features payments_v2,branding
   forked build --features payments_v2 --exclude 'patch/branding/*'
   ```
3. Inspect build log / metadata to confirm selected patches match expectations and order respects `patches.order`.
4. Verify providing an unknown overlay exits with code `3` and helpful message.

## Feature Management Commands
1. `forked feature create checkout --slices 2`
   - Ensure branches `patch/checkout/01-checkout` + `02-checkout` exist.
   - Confirm `forked.yml.features.checkout.patches` updated with those slices.
2. Commit on each slice, then run `forked feature status`:
   - Output should list ahead counts relative to `trunk`.
   - After syncing trunk to include changes, status should mark slices as “merged upstream”.

## Guard Attribution
1. Build overlay with subset of features.
2. Run `forked guard --overlay overlay/dev --mode block`.
3. Inspect `.forked/report.json` and confirm:
   - `violations_by_feature` contains only active features.
   - Feature-scoped sentinel violations appear under the owning feature.

## Schema Validation
- Run `forked config validate` (or equivalent helper) on upgraded config to ensure new schema passes existing validators.
- Execute unit tests that intentionally violate schema (missing feature patch, overlay referencing unknown feature) and assert descriptive errors.

## Regression
- Execute `make validate` to confirm handbook references render after documentation updates.
