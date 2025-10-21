---
title: Clean Command Changelog
type: changelog
feature: clean-command
date: 2025-10-20
tags: [changelog]
---

# Changelog

## 2025-10-21
- Delivered `forked clean` with dry-run default, explicit `--no-dry-run --confirm` execution gate, and audit logging to `.forked/logs/clean.log`.
- Added overlay pruning filters (age/pattern), retention window via `--keep N`, and protections for tagged/current worktrees.
- Implemented worktree pruning (`--worktrees`) and conflict bundle cleanup (`--conflicts`, `--conflicts-age`) retaining the newest bundles per overlay.
- Documented usage patterns and safety rails in README, handbook sanity checklist, and testing guides.
