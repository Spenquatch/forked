---
title: Status JSON Risks
type: risks
feature: status-json
date: 2025-10-20
tags: [risks]
---

# Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Provenance missing for historical overlays | Medium | Fall back to resolver + flag `selection.source=derived`; encourage re-build for missing metadata. |
| JSON output grows large in repos with many overlays | Low | Limit default window, add CLI flag to control `--latest`. |
| Schema drift breaks downstream tooling | High | Version via `status_version`, add contract tests, keep additions backwards compatible. |

# Open Questions
- Should we expose task backlog counts alongside overlays?
- Do we need a separate `--summary` mode for extremely large repos?
