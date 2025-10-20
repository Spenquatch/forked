---
title: Conflict Bundle Automation Changelog
type: changelog
feature: conflict-bundle-automation
date: 2025-10-20
tags: [changelog]
---

# Changelog

## Planned
- Add shared conflict bundle writer with schema v2 (wave numbering, binary metadata) and blob exports.
- Introduce `--emit-conflicts`, `--conflict-blobs-dir`, `--on-conflict=<mode|exec>`, and sync `--auto-continue` options to build + sync.
- Emit exit code `10` when conflicts are captured (bias/exec overrides supported) and log provenance entries per wave.
- Document bundle structure, examples, CI snippets, and Windows POSIX shell note in README.
