---
title: Guard CLI Contract - Implementation Steps
type: implementation
date: 2025-09-22
task_id: TASK-002
tags: [implementation]
links: []
---

# Implementation Steps: Guard CLI Contract

## Overview
Steps to harden guard CLI behaviour for the v0.1.0 release.

## Prerequisites
- [ ] All dependent tasks completed (check task.yaml depends_on)
- [ ] Development environment ready
- [ ] Required permissions/access available

## Step 1: Analysis & Planning
**Estimated Time**: 1-2 hours

### Actions
- [ ] Review `features/guard-automation/implementation/plan.md`
- [ ] Confirm README checklist expectations for guard
- [ ] Inspect existing guard code paths (exit codes, sentinel, size caps)
- [ ] Decide validation approach (manual guard run + JSON inspection)

### Expected Outcome
- Clear understanding of requirements
- Implementation approach decided
- Test plan outlined

## Step 2: Core Implementation
**Estimated Time**: 4-6 hours

### Actions
- [ ] Replace lingering `SystemExit` calls with `typer.Exit`
- [ ] Set `"report_version": 1` in emitted JSON
- [ ] Adjust sentinel logic to treat overlay-only files as divergence success
- [ ] Switch size-cap summary to `--numstat` totals
- [ ] Update README + feature docs with behaviour summary

### Expected Outcome
- Guard returns documented exit codes
- JSON output contains report version and accurate metrics
- README/feature docs reflect final behaviour

## Step 3: Integration & Validation
**Estimated Time**: 1-2 hours

### Actions
- [ ] Run `forked guard --overlay overlay/test --mode block` to verify exit 2
- [ ] Capture `.forked/report.json` and inspect metadata
- [ ] Delete trunk file in overlay to confirm sentinel detection
- [ ] Update feature status + changelog

### Expected Outcome
- Guard CLI validated against acceptance criteria
- Documentation updates complete
- Ready for review

## Notes
- Update task.yaml status as you progress through steps
- Document any blockers or decisions in daily status
- Link any PRs/commits back to this task
