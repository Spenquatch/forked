---
title: Task TASK-002 - Guard CLI Contract
type: task
date: 2025-09-22
task_id: TASK-002
feature: guard-automation
tags: [task, guard-automation]
links: [../../../features/guard-automation/overview.md, ../../plan.md]
---

# Task TASK-002: Guard CLI Contract

## Overview
**Feature**: [guard-automation](../../../features/guard-automation/overview.md)
**Decision**: ADR-0002 (Guard exit-code contract)
**Story Points**: 3
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
This task finalizes the guard CLI behaviour described in the README, sprint plan, and release plan. It ensures sentinel logic, diff metrics, and exit codes align with release commitments.

## Quick Start
```bash
# Update status when starting
cd legacy-handbook/sprints/current/tasks/TASK-002-guard-cli-contract/
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
