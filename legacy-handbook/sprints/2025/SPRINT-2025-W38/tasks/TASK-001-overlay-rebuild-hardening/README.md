---
title: Task TASK-001 - Overlay Rebuild Hardening
type: task
date: 2025-09-22
task_id: TASK-001
feature: overlay-infrastructure
tags: [task, overlay-infrastructure]
links: [../../../features/overlay-infrastructure/overview.md, ../../plan.md]
---

# Task TASK-001: Overlay Rebuild Hardening

## Overview
**Feature**: [overlay-infrastructure](../../../features/overlay-infrastructure/overview.md)
**Decision**: ADR-0001 (Overlay worktree contract)
**Story Points**: 5
**Owner**: @ai-agent
**Capacity Type**: planned (80% allocation)
**Backlog Reference**: None (planned work)

## Agent Navigation Rules
1. **Start work**: Update `task.yaml` status to "doing"
2. **Read first**: `steps.md` for implementation sequence
3. **Use commands**: Copy-paste from `commands.md`
4. **Validate progress**: Follow `validation.md` guidelines
5. **Check completion**: Use `checklist.md` before marking done
6. **Update status**: Set to "review" when ready for review

## Context & Background
This task implements the overlay worktree guarantees called out by the README MVP goals, sprint plan, and release plan. It ensures repeated builds reuse/reset the same overlay worktree and that cherry-picks apply complete branch ranges.

## Quick Start
```bash
# Update status when starting
cd legacy-handbook/sprints/current/tasks/TASK-001-overlay-rebuild-hardening/
# Edit task.yaml: status: doing

# Follow implementation
cat steps.md              # Read implementation steps
cat commands.md           # Copy-paste commands
cat validation.md         # Validation approach
```

## Dependencies
Review `task.yaml` for any `depends_on` tasks that must be completed first.

## Acceptance Criteria
See `task.yaml` acceptance section and `checklist.md` for completion requirements.
