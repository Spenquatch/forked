---
title: Overlay Infrastructure Overview
type: overview
feature: overlay-infrastructure
date: 2025-09-22
tags: [overview]
links: [./implementation/plan.md, ./risks.md, ./status.md]
dependencies: []
backlog_items: []
capacity_impact: planned
---

# Overlay Infrastructure

Purpose
- Guarantee overlay rebuilds run in isolated worktrees, reuse existing checkouts safely, and replay full patch ranges without manual cleanup.

Outcomes
- Worktree roots resolve outside the primary repo.
- Rebuilding the same overlay ID resets any existing worktree to `trunk` before reapplying patches.
- Cherry-picks cover full branch history with deterministic conflict handling.

State
- Stage: in-progress
- Owner: @ai-agent

Backlog Integration
- Related Issues: []
- Capacity Type: planned

Key Links
- Implementation: ./implementation/plan.md
- Status: ./status.md
- Risks: ./risks.md
- Changelog: ./changelog.md
