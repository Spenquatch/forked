---
title: Forked CLI Roadmap
type: roadmap
date: 2025-09-22
tags: [roadmap]
links: []
---

# Forked CLI – Now / Next / Later

## Now
- feature-slice-workflows: ship selective overlays, provenance logging, and skip-upstream option ([status](../features/feature-slice-workflows/status.md))
- conflict-bundle-automation: provide JSON bundles (schema v2) + sync auto-continue policy ([status](../features/conflict-bundle-automation/status.md))
- guard-automation: enforce policy overrides + report v2 ([status](../features/guard-automation/status.md))
- status-json: deliver `forked status --json` for dashboards ([status](../features/status-json/status.md))
- clean-command: add dry-run-first housekeeping CLI ([status](../features/clean-command/status.md))

## Next
- release-operations: refresh docs, changelog, and CI examples for overrides/status/clean ([status](../features/release-operations/status.md))
- Backlog grooming for post-v1.1.0 items (guard fixtures, agent integrations)

## Later
- Automate guard fixture generation & CI comparisons
- Add optional smoke test suites for large overlay stacks
- Explore AI-assisted conflict resolution leveraging bundle schema
