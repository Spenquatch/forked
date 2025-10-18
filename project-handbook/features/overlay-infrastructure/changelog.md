---
title: Overlay Infrastructure Changelog
type: changelog
feature: overlay-infrastructure
date: 2025-10-16
tags: [changelog]
---

# Changelog

## 2025-10-16
- Shipped ADR-0001 overlay contract: overlays now live under `.forked/worktrees/`, reuse reset flow, and merge-range cherry-picks with path-bias support.
- Verified smoke checklist (double rebuild + guard) and updated README guard/build documentation.

## 2025-09-22
- Documented target architecture, smoke tests, and implementation steps for worktree relocation/reuse.
- Updated implementation plan to cover range cherry-picks, reuse logging, and suffix strategy.

## 2025-09-20
- Drafted requirements from README MVP goals.
