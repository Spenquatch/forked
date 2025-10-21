---
title: Adopt src Layout - Completion Checklist
type: checklist
date: 2025-10-21
task_id: TASK-009
tags: [checklist]
links: []
---

# Completion Checklist

- [ ] Runtime modules live directly under `src/` (no nested `forked/` directory remains).
- [ ] Poetry configuration updated for module distribution (`packages = [{ include = "*", from = "src" }]`).
- [ ] Imports/tests/scripts updated to reference top-level modules (no reliance on `forked.` package paths).
- [ ] Ruff, mypy, pytest, and sanity workflow pass post-migration.
- [ ] Documentation (README, development workflow, sanity checklist) updated with new layout instructions.
