---
title: Guard Automation Changelog
type: changelog
feature: guard-automation
date: 2025-09-22
tags: [changelog]
---

# Changelog

## 2025-09-22
- Moved guard CLI exits to `typer.Exit` with documented codes.
- Updated sentinel evaluation to treat overlay-only files as valid divergence.
- Replaced `--shortstat` parsing with `--numstat` aggregation.
- Added `"report_version": 1` to JSON output.
