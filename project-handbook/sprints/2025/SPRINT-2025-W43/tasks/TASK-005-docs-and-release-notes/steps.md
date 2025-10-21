---
title: Docs & Release Notes - Implementation Steps
type: implementation
date: 2025-10-20
task_id: TASK-005
tags: [implementation]
links: []
---

# Implementation Steps: Docs & Release Notes Refresh

## Step 1: README Updates
- [ ] Add/refresh sections for feature slice workflows (config schema, provenance, `--skip-upstream-equivalents`).
- [ ] Document conflict bundle v2 (binary handling, wave numbering, Windows POSIX note) with CLI snippets.
- [ ] Document guard overrides (`mode=require-override`) and override discovery order.
- [ ] Document `forked status --json` schema + examples and `forked clean` workflow (dry-run/confirm semantics).
- [ ] Update quickstart / smoke checklist if new steps required.

## Step 2: Handbook Refresh
- [ ] Link new feature pages from relevant sections (roadmap already updated, verify cross-links).
- [ ] Ensure implementation plans referenced where appropriate.
- [ ] Capture new tasks/features in any status dashboards if manual docs mention them.

## Step 3: Release Notes
- [ ] Expand `project-handbook/releases/CHANGELOG.md` with final wording for v1.1.0.
- [ ] Prepare release announcement bullet list aligning with sprint output.

## Step 4: Validation
- [ ] Run `make validate`.
- [ ] Spot-check formatting/links.
- [ ] Update task status and communicate summary in daily note.
