---
title: Conflict Bundle Engine - Completion Checklist
type: checklist
date: 2025-10-20
task_id: TASK-004
tags: [checklist]
links: []
---

# Completion Checklist

- [ ] Shared collector outputs schema v2 JSON (precedence, binary metadata, wave, commands).
- [ ] Build command surfaces new flags, logs bundle path(s), exits 10 on conflict, and handles multi-wave numbering.
- [ ] Sync command reuses collector, honours `--auto-continue`, and logs bias applications.
- [ ] Optional blob export writes base/ours/theirs files per conflict, especially for binary/large files.
- [ ] README includes bundle schema summary + CI snippet.
- [ ] Unit + integration tests updated for conflict bundles.
- [ ] `make validate` passes.
