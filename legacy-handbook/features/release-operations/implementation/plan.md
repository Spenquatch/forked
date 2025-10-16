---
title: Release Operations Implementation Plan
type: implementation-plan
feature: release-operations
date: 2025-09-22
tags: [implementation, plan]
---

# Implementation Plan

## Scope
- Align handbook planning artifacts with README requirements.
- Ensure CI pipeline instructions match local release workflow.
- Capture backlog of near-term QoL follow-ups.

## Work Breakdown
1. **Documentation**
   - [ ] Add smoke + release checklists to README.
   - [ ] Clarify sentinel behaviour and worktree reuse.
   - [ ] Publish release highlights in `legacy-handbook/releases/v0.1.0.md`.
2. **Planning Artifacts**
   - [ ] Update release plan, sprint plan, feature assignments (this change).
   - [ ] Refresh sprint tasks to reflect release readiness work.
3. **Automation**
   - [ ] Update GitHub Action to editable install + smoke run.
   - [ ] Capture command snippet for quick sanity run in docs (stretch).

## Validation
- Cross-check README checklists with sprint tasks and release plan.
- Run `make dashboard` (once automation is available) to ensure new feature entries appear.
- Confirm backlog captures follow-up items.

## Risks & Mitigations
- **Risk**: Planning docs drift from actual work. Mitigation: treat README checklists as acceptance criteria; keep features updated post-release.
