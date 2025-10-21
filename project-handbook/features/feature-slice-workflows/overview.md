---
title: Feature Slice Workflows Overview
type: overview
feature: feature-slice-workflows
date: 2025-10-20
tags: [overview]
links: [./implementation/plan.md, ./status.md, ./risks.md]
dependencies: []
backlog_items: []
capacity_impact: planned
---

# Feature Slice Workflows

Purpose
- Model fork work as feature slices with explicit patch lists, reusable overlay profiles, and guard policies that understand the active feature set.

Outcomes
- `forked build` can target named overlay profiles, ad-hoc feature sets, include/exclude patch globs, and optionally skip upstream-equivalent commits while retaining global order.
- Developers scaffold feature slice branches via `forked feature create` and inspect drift with `forked feature status`.
- Guard execution merges global/feature-level sentinels, ingests provenance for feature context, and reports risk per feature.
- `forked.yml` schema captures features, overlays, and optional per-feature sentinel rules with validation.

State
- Stage: planned
- Owner: @ai-agent

Backlog Integration
- Related Issues: []
- Capacity Type: planned

Key Links
- Implementation: ./implementation/plan.md
- Status: ./status.md
- Risks: ./risks.md
- Changelog: ./changelog.md
