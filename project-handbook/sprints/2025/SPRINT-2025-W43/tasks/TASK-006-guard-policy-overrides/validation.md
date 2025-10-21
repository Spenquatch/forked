---
title: Guard Policy Overrides - Validation Guide
type: validation
date: 2025-10-20
task_id: TASK-006
tags: [validation]
links: []
---

# Validation Guide

## Automated
- [ ] `pytest tests/test_guard_overrides.py -q`
- [ ] `pytest tests/test_report_v2.py -q`
- [ ] `make validate`

## Manual
1. Run `forked guard --overlay overlay/dev --mode require-override` **without** override → expect exit `2` and message referencing missing override.
2. Add commit trailer (`Forked-Override: sentinel`) → rerun → expect exit `0`, `.forked/report.json.override.applied == true`, `override.source == "commit"`.
3. Remove trailer; add git note override → guard should succeed with `override.source == "note"`.
4. Add tag override while keeping note and confirm commit override still takes precedence (change commit trailer to allowed scope and ensure tag/note ignored).
5. Set `policy_overrides.allowed_values: ["size"]`, add trailer `Forked-Override: sentinel` → expect exit `2` and message about disallowed scope.
6. Verify `report_version == 2` and `.features` array populated from provenance log or fallback (and warning emitted when resolver used).

## Sign-off
- [ ] Overrides honoured for commit, tag, and note sources.
- [ ] Report schema updated with override + features fields and tests/fixtures adjusted.
- [ ] README/handbook updated (Task 005) to describe override workflow.
