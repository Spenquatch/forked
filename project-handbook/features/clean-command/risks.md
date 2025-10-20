---
title: Clean Command Risks
type: risks
feature: clean-command
date: 2025-10-20
tags: [risks]
---

# Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| User forgets `--confirm` and assumes work was performed | Low | Print explicit reminder when exiting dry-run; return non-zero unless `--confirm` used? (TBD). |
| Tagged or active overlays removed inadvertently | High | Detect tags/current worktree/provenance usage and block deletions. |
| Deleting conflict bundles needed for audit | Medium | Keep latest bundle per overlay and allow age-based filters (`--conflicts --age`). |

# Open Questions
- Should `--confirm` imply non-dry-run or require both flags? (Current plan: dry-run default, omit `--dry-run` + supply `--confirm` to execute.)
- Do we track clean operations in a log for auditing?
