---
title: Guard Policy Overrides - Completion Checklist
type: checklist
date: 2025-10-20
task_id: TASK-006
tags: [checklist]
links: []
---

# Completion Checklist

- [ ] Override discovery handles commit trailers, annotated tags, and git notes.
- [ ] `mode=require-override` fails without override and passes with allowed scope values.
- [ ] `policy_overrides.allowed_values` enforced with clear messaging.
- [ ] `.forked/report.json` bumped to `report_version: 2` with populated `override` + `features` sections.
- [ ] Tests updated (unit + integration) and fixtures regenerated.
- [ ] README/handbook references updated to document override usage.
- [ ] `make validate` passes.
