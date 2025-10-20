---
title: Task TASK-003 - Feature Resolver & CLI
type: task
date: 2025-10-20
task_id: TASK-003
feature: feature-slice-workflows
tags: [task, feature-slice-workflows]
links: [../../../features/feature-slice-workflows/overview.md, ../../plan.md, ../../../../Forked CLI Expansion Implementation Plan.md]
---

# Task TASK-003: Feature Resolver & CLI

## Overview
**Feature**: [feature-slice-workflows](../../../features/feature-slice-workflows/overview.md)  
**Decision**: ADR-0003 (Feature Slice Workflows; see Forked CLI Expansion Implementation Plan)  
**Story Points**: 4  
**Owner**: @ai-agent  
**Capacity Type**: planned (critical path)  
**Backlog Reference**: N/A (planned sprint work)

## Agent Navigation Rules
1. Set `task.yaml` status to `doing` when starting.
2. Review `steps.md` for breakdown and sequencing.
3. Use `commands.md` as copy/paste reference for git + CLI usage.
4. Validate progress following `validation.md`.
5. Confirm `checklist.md` before requesting review.
6. Update status to `review` (then `done`) once acceptance criteria satisfied.

## Context & Background
Implements feature-driven overlays described in the expansion plan. Work spans config parsing, build command wiring, new Typer subcommands, and guard attribution updates.

## Quick Start
```bash
cd legacy-handbook/sprints/current/tasks/TASK-003-feature-resolver-and-cli/
cat steps.md
```

## Dependencies
- None (must land early to unblock conflict bundle integration and docs)

## Acceptance Criteria
See `task.yaml` and `checklist.md` for detailed requirements.
