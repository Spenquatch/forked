---
title: Task TASK-008 - Clean Command Implementation
type: task
date: 2025-10-20
task_id: TASK-008
feature: clean-command
tags: [task, clean-command]
links: [../../../features/clean-command/overview.md, ../../plan.md, ../../../../../Forked CLI Expansion Implementation Plan.md]
---

# Task TASK-008: Clean Command Implementation

## Overview
**Feature**: [clean-command](../../../features/clean-command/overview.md)  
**Decision**: ADR-0005 (Operational Tooling)  
**Story Points**: 3  
**Owner**: @ai-agent  
**Capacity Type**: planned  
**Backlog Reference**: FORKED_CLEAN-P2-20250922-1200

## Agent Navigation Rules
1. Update `task.yaml` status as you progress.
2. Work through `steps.md` in order (candidate discovery → dry-run output → confirm execution).
3. Use `commands.md` for sample dry-run/confirm invocations.
4. Validate behaviour via `validation.md` before requesting review.

## Context & Background
Adds a safe, dry-run-first `forked clean` command that prunes worktrees, overlays, and conflict bundles without manual scripts. The command must protect tagged/active overlays and log intended operations clearly.

## Quick Start
```bash
cd legacy-handbook/sprints/current/tasks/TASK-008-clean-command/
cat steps.md
```

## Dependencies
- TASK-003 supplies provenance data used to protect recent overlays.

## Acceptance Criteria
See `task.yaml` and `checklist.md`.
