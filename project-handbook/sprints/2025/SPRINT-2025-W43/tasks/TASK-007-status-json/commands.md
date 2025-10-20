---
title: Status JSON CLI - Command Snippets
type: reference
date: 2025-10-20
task_id: TASK-007
tags: [commands]
links: []
---

# Command Snippets

## Generate Sample Data
```bash
forked build --overlay dev --id dev-json
```

## Status JSON Output
```bash
forked status --json | jq
forked status --json --latest 2 | jq '.overlays'
```

## Tests
```bash
pytest tests/test_status_json.py -q
pytest tests/test_provenance_integration.py -q
```
