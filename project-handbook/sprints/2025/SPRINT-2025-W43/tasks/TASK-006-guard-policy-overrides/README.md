---
title: Task TASK-006 - Guard Policy Overrides & Report v2
type: task
date: 2025-10-20
task_id: TASK-006
feature: guard-automation
tags: [task, guard-automation]
links: [../../../features/guard-automation/overview.md, ../../plan.md, ../../../../../Forked CLI Expansion Implementation Plan.md]
---

# Task TASK-006: Guard Policy Overrides & Report v2

## Overview
**Feature**: [guard-automation](../../../features/guard-automation/overview.md)  
**Decision**: ADR-0002 (Guard CLI Contract)  
**Story Points**: 3  
**Owner**: @ai-agent  
**Capacity Type**: planned  
**Backlog Reference**: None (promotion from addendum)

## Agent Navigation Rules
1. Update `task.yaml` status as you work (`doing`/`review`/`done`).
2. Follow `steps.md` for sequencing (overrides → schema → docs/tests).
3. Use `commands.md` to simulate override flows (commit, tag, note).
4. Capture verification in `validation.md` and tick `checklist.md` items before handoff.

## Context & Background
Addendum v1.1 requires guard runs in `mode=require-override` to validate explicit escalation markers, bump the report schema to version 2, and surface provenance-driven feature lists. The override logic pulls from commit trailers, annotated tags, and `git notes` (commit → tag → note precedence).

## Quick Start
```bash
cd legacy-handbook/sprints/current/tasks/TASK-006-guard-policy-overrides/
cat steps.md
```

## Dependencies
- TASK-003 provides provenance logging (`features` list) consumed by guard.

## Acceptance Criteria
See `task.yaml` and `checklist.md` for full details.
