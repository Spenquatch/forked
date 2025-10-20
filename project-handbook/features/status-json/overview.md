---
title: Status JSON Overview
type: overview
feature: status-json
date: 2025-10-20
tags: [overview, cli]
links: [./implementation/plan.md, ./status.md, ./risks.md]
dependencies: []
backlog_items: [../backlog/feature/FORKED_STATUS_JSON-P2-20250922-1201/README.md]
capacity_impact: planned
---

# Status JSON

Purpose
- Provide a machine-readable `forked status --json` output capturing upstream/trunk info, patch drift (`ahead/behind`), and recent overlay selections (features, patches, build timestamps).
- Feed dashboards, guard provenance, and CI workflows with stable schema (`status_version: 1`).

Outcomes
- Status command emits JSON alongside human-readable output.
- Overlay metadata is sourced from build provenance logs/notes.
- Consumers can request latest N overlays (`--latest`) for reporting.

State
- Stage: planned
- Owner: @ai-agent

Key Links
- Implementation: ./implementation/plan.md
- Status: ./status.md
- Risks: ./risks.md
- Testing: ./testing/TESTING.md
- Changelog: ./changelog.md
