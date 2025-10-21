---
title: Clean Command Overview
type: overview
feature: clean-command
date: 2025-10-20
tags: [overview, cli]
links: [./implementation/plan.md, ./status.md, ./risks.md]
dependencies: []
backlog_items: [../backlog/feature/FORKED_CLEAN-P2-20250922-1200/README.md]
capacity_impact: planned
---

# Clean Command

Purpose
- Provide a safe `forked clean` command to prune stale worktrees, overlay branches, and conflict bundles with explicit dry-run and confirmation gating.

Outcomes
- Operators can run clean-up routines without hand-written shell loops and retain an audit trail in `.forked/logs/clean.log`.
- Tagged/active overlays remain untouched; retention policy enforced via `--keep`.
- Conflict bundles and worktrees are tidied on a predictable cadence.

State
- Stage: maintained
- Owner: @ai-agent

Key Links
- Implementation: ./implementation/plan.md
- Status: ./status.md
- Risks: ./risks.md
- Testing: ./testing/TESTING.md
- Changelog: ./changelog.md
