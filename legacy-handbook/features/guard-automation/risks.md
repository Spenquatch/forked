---
title: Guard Automation Risks
type: risks
feature: guard-automation
date: 2025-09-22
tags: [risks]
---

# Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Guard runtime slows significantly on very large overlays | Medium | Document expectation, optionally add `--paths-from-file` filter in future release |
| Sentinel union pulls in git-submodule entries | Low | Skip tree entries with type `commit`, log warning |
| Exit-code regressions break CI pipeline | High | Add quick smoke command to release checklist, capture JSON fixture |

# Notes
- No external dependencies; purely Git + Typer behaviour.
