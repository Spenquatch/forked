---
title: Adopt src Layout - Completion Checklist
type: checklist
date: 2025-10-21
task_id: TASK-009
tags: [checklist]
links: []
---

# Completion Checklist

- [ ] Runtime package lives under `src/forked/` (no stray modules at repo root).
- [ ] Poetry configuration updated (`packages = [{ include = "forked", from = "src" }]`).
- [ ] Imports/tests/scripts adjusted to use package imports (no reliance on repo root).
- [ ] Ruff, mypy, pytest, and sanity workflow pass post-migration.
- [ ] Documentation (README, development workflow, sanity checklist) updated with new layout instructions.
