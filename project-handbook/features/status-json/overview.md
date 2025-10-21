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
- Provide a machine-readable `forked status --json` output capturing upstream/trunk info, patch drift (`ahead/behind`), recent overlay selections (features, patches, build timestamps, skip counts), and guard-derived both_touched metrics.
- Feed dashboards, guard provenance, and CI workflows with stable schema (`status_version: 1`).

Outcomes
- Status command emits JSON alongside human-readable output.
- Overlay metadata is sourced from build provenance logs/notes.
- Consumers can request latest N overlays (`--latest`, default 5) for reporting.
- Downstream tooling can parse a stable schema including `selection` provenance and `both_touched_count` (nullable when guard has not yet run).

State
- Stage: in-progress
- Owner: @ai-agent

Usage
- `forked status --json | jq '.patches[] | {name, ahead, behind}'` surfaces drift across patch branches.
- `forked status --json --latest 1 | jq '.overlays[0].selection.features'` inspects the newest overlay’s provenance.
- Fallback behaviour logs a warning and marks `selection.source: "derived"` when build logs/notes are unavailable.

Schema Snapshot (`status_version: 1`)

```json
{
  "status_version": 1,
  "upstream": {"remote": "upstream", "branch": "trunk", "sha": "<12 chars>"},
  "trunk": {"name": "trunk", "sha": "<12 chars>"},
  "patches": [{"name": "patch/foo/01", "sha": "<sha>", "ahead": 1, "behind": 0}],
  "overlays": [
    {
      "name": "overlay/dev",
      "built_at": "2025-10-20T18:45:02Z",
      "selection": {"source": "provenance-log", "features": ["foo"], "patches": ["patch/foo/01"]},
      "both_touched_count": 2
    }
  ]
}
```

Key Links
- Implementation: ./implementation/plan.md
- Status: ./status.md
- Risks: ./risks.md
- Testing: ./testing/TESTING.md
- Changelog: ./changelog.md
