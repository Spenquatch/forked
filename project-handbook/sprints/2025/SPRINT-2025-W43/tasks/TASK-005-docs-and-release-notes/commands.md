---
title: Docs & Release Notes - Command Snippets
type: reference
date: 2025-10-20
task_id: TASK-005
tags: [commands]
links: []
---

# Command Snippets

```bash
# open README for editing
nvim README.md

# update release changelog
nvim project-handbook/releases/CHANGELOG.md

# verify handbook links + formatting
make validate

# show diff for review summary
git diff README.md project-handbook/releases/CHANGELOG.md

# mark task ready for review
make task-status id=TASK-005 status=review
```
