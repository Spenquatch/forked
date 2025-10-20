---
title: Conflict Bundle Automation Risks
type: risks
feature: conflict-bundle-automation
date: 2025-10-20
tags: [risks]
---

# Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Bundle schema drifts between build and sync implementations | Medium | Centralize serializer in shared module and add contract tests for both commands. |
| Blob export increases disk usage in CI | Low | Default blobs dir off; allow opt-in and document cleanup (`rm -rf .forked/conflicts/*`). |
| Exit code 10 conflicts with existing automation | Low | Document new exit codes and provide upgrade notes; keep legacy codes untouched. |
| Auto-resolve mode applies incorrect bias | High | Keep default `stop`; gate bias/exec behind explicit flag and log recommendations. |

# Open Questions
- Should we compress blob directories before uploading artifacts?
- Do we need a CLI to re-open or summarize bundles post hoc?
