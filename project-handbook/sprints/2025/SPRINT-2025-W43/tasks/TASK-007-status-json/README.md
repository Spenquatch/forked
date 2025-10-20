---
title: Task TASK-007 - Status JSON CLI
type: task
date: 2025-10-20
task_id: TASK-007
feature: status-json
tags: [task, status-json]
links: [../../../features/status-json/overview.md, ../../plan.md, ../../../../../Forked CLI Expansion Implementation Plan.md]
---

# Task TASK-007: Status JSON CLI

## Overview
**Feature**: [status-json](../../../features/status-json/overview.md)  
**Decision**: ADR-0005 (Operational Tooling)  
**Story Points**: 2  
**Owner**: @ai-agent  
**Capacity Type**: planned  
**Backlog Reference**: FORKED_STATUS_JSON-P2-20250922-1201

## Agent Navigation Rules
1. Update `task.yaml` status as progress is made.
2. Follow `steps.md` for recommended sequence.
3. Use `commands.md` for sanity checks and schema dumps.
4. Validate output via `validation.md` before marking `review`.

## Context & Background
Adds a `--json` mode to `forked status`, enabling dashboards and guard workflows to consume consistent machine-readable output that includes overlay selection provenance and patch drift metrics.

## Quick Start
```bash
cd legacy-handbook/sprints/current/tasks/TASK-007-status-json/
cat steps.md
```

## Dependencies
- TASK-003 must land to ensure provenance logging is available.

## Acceptance Criteria
See `task.yaml` and `checklist.md`.
