---
title: Guard Policy Overrides - Implementation Steps
type: implementation
date: 2025-10-20
task_id: TASK-006
tags: [implementation]
links: []
---

# Implementation Steps: Guard Policy Overrides & Report v2

## Step 1: Override Discovery
- [ ] Parse overlay tip commit trailers for `Forked-Override` key (configurable).
- [ ] If publish tag supplied, inspect annotated tag message trailers.
- [ ] Read `git notes --ref=refs/notes/forked/override` when trailers absent.
- [ ] Normalize values (split comma/space, lowercase) and compare to `allowed_values`.

## Step 2: Enforcement Logic
- [ ] Wire override checks into guard execution path when `guards.mode == "require-override"`.
- [ ] Fail with exit code 2 when violations exist without valid override; succeed with override and record `override.applied=true`.
- [ ] Provide clear messaging when override values fall outside `allowed_values`.

## Step 3: Report v2 & Provenance
- [ ] Bump `report_version` to 2, append `override` block (`enabled`, `source`, `values`, `applied`).
- [ ] Inject `features` list from provenance log/notes; fall back to resolver if unavailable.
- [ ] Update fixtures/tests to match new schema and ensure backwards compatibility (still include prior fields).

## Step 4: Tests & Docs
- [ ] Add unit/integration tests covering commit/tag/note overrides, allowed/disallowed scopes.
- [ ] Document override workflow in README + handbook (Task 005 dependency).
- [ ] Update changelog references and guard feature status.

## Notes
- Treat empty `allowed_values` as "allow all".
- Preserve legacy behaviour for `mode=block|warn`; override logic only runs for `require-override`.
