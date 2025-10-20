---
title: Feature Resolver & CLI - Completion Checklist
type: checklist
date: 2025-10-20
task_id: TASK-003
tags: [checklist]
links: []
---

# Completion Checklist

- [ ] Resolver unit tests cover overlay profiles, feature lists, include/exclude precedence.
- [ ] `forked build` accepts new flags, logs selected patches/features, and writes provenance entries.
- [ ] `forked feature create` creates numbered slices and updates `forked.yml`.
- [ ] `forked feature status` displays ahead/behind info for sample repo.
- [ ] `forked build --skip-upstream-equivalents` skips upstream commits and reports counts.
- [ ] README + CLI help updated with new commands and flags.
- [ ] `make validate` passes.
