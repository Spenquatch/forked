---
title: Status JSON Changelog
type: changelog
feature: status-json
date: 2025-10-20
tags: [changelog]
---

# Changelog

## Planned
- Add `forked status --json` with `status_version: 1` schema (upstream, trunk, patches, overlays).
- Record overlay selection (features, patches, timestamps, skip counts) from provenance logs.
- Support `--latest N` overlay window with sensible defaults and guard-report derived `both_touched_count` (null when unavailable).
- Document schema and provide example tooling (`jq`, dashboards).
