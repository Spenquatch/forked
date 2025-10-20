---
title: Conflict Bundle Automation Overview
type: overview
feature: conflict-bundle-automation
date: 2025-10-20
tags: [overview]
links: [./implementation/plan.md, ./status.md, ./risks.md]
dependencies: []
backlog_items: []
capacity_impact: planned
---

# Conflict Bundle Automation

Purpose
- Capture merge conflicts from `forked build` and `forked sync` as machine-readable bundles with blob snapshots, precedence hints, and resume instructions.

Outcomes
- `--emit-conflicts` writes JSON bundles with schema v2 (wave numbering, binary metadata) plus optional blob directories.
- `--conflict-blobs-dir` exports base/ours/theirs files for every conflicted path, especially binaries/large diffs.
- `--on-conflict` adds deterministic exit codes (10) and optional scripted resolution hooks; `--auto-continue` for sync logs bias decisions and subsequent waves.
- Guardrails ensure sync and build share the same conflict writer, provenance logs, and platform notes.

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
