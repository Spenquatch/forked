---
title: Overlay Rebuild Hardening - Implementation Steps
type: implementation
date: 2025-09-22
task_id: TASK-001
tags: [implementation]
links: []
---

# Implementation Steps: Overlay Rebuild Hardening

## Overview
Detailed step-by-step guide to finish the overlay infrastructure work required for the v0.1.0 release.

## Prerequisites
- [ ] All dependent tasks completed (check task.yaml depends_on)
- [ ] Development environment ready
- [ ] Required permissions/access available

## Step 1: Analysis & Planning
**Estimated Time**: 1-2 hours

### Actions
- [ ] Review `README.md` MVP goals for overlay build expectations
- [ ] Read feature plan at `features/overlay-infrastructure/implementation/plan.md`
- [ ] Confirm acceptance criteria in `task.yaml`
- [ ] Sketch validation strategy (smoke checklist + guard run)

### Expected Outcome
- Clear understanding of requirements
- Implementation approach decided
- Test plan outlined

## Step 2: Core Implementation
**Estimated Time**: 4-6 hours

### Actions
- [ ] Ensure `_resolve_worktree_dir` relocates roots + suffixes collisions
- [ ] Implement `worktree_for_branch` + reuse flow in `build_overlay`
- [ ] Reset reused worktree to trunk before cherry-picks
- [ ] Iterate through `_rev_list_range` for full branch coverage
- [ ] Update README/explanatory comments if behaviour changes

### Expected Outcome
- Rebuilding same overlay ID reuses/resets worktree without errors
- Cherry-pick loop applies every commit and honours path bias
- Docs reference reuse behaviour

## Step 3: Integration & Validation
**Estimated Time**: 1-2 hours

### Actions
- [ ] Run `forked build --id test --auto-continue` twice (expect reuse)
- [ ] Inspect `.forked-worktrees/<repo>/test` location and cleanliness
- [ ] Execute README smoke checklist steps covering build + guard
- [ ] Capture notes for release plan + changelog

### Expected Outcome
- Smoke checklist passes without manual clean-up
- Worktree path matches plan (`../.forked-worktrees/...`)
- Release plan + feature status updated
- Ready for review

## Notes
- Update task.yaml status as you progress through steps
- Document any blockers or decisions in daily status
- Link any PRs/commits back to this task
