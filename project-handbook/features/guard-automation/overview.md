---
title: Guard Automation Overview
type: overview
feature: guard-automation
date: 2025-09-22
tags: [overview]
links: [./implementation/plan.md, ./status.md, ./risks.md]
dependencies: []
backlog_items: []
capacity_impact: planned
---

# Guard Automation

Purpose
- Ensure `forked guard` enforces sentinel policies, reports deterministic JSON, and returns documented exit codes for CI.

Outcomes
- Sentinel checks catch missing overlay files and diverged blobs accurately.
- Size caps rely on locale-safe `--numstat` aggregation.
- CLI exits with `typer.Exit` codes surfaced in README checklists.
- Policy overrides honour commit/tag/note trailers in precedence order and surface an `override` + `features` block in `report_version: 2`.

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
