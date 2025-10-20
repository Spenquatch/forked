---
title: Status JSON CLI - Completion Checklist
type: checklist
date: 2025-10-20
task_id: TASK-007
tags: [checklist]
links: []
---

# Completion Checklist

- [ ] `forked status --json` emits `status_version: 1` schema with upstream/trunk/patch data.
- [ ] Overlay selection metadata populated from provenance (features, patches, timestamps).
- [ ] `--latest N` respected with sensible defaults and empty-state handling.
- [ ] Tests updated/added and fixtures stored as needed.
- [ ] README/handbook updated with schema documentation and examples.
- [ ] `make validate` passes.
