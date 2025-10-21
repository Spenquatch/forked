---
title: Guard Policy Overrides - Completion Checklist
type: checklist
date: 2025-10-20
task_id: TASK-006
tags: [checklist]
links: []
---

# Completion Checklist

- [x] Override discovery handles commit trailers, annotated tags, and git notes with documented precedence (commit → tag → note).
- [x] `mode=require-override` fails without override and passes with allowed scope values.
- [x] `policy_overrides.allowed_values` enforced with clear messaging.
- [x] `.forked/report.json` bumped to `report_version: 2` with populated `override` + `features` sections.
- [x] Tests updated (unit + integration) and fixtures regenerated.
- [x] README/handbook references updated to document override usage.
- [x] `make validate` passes.
