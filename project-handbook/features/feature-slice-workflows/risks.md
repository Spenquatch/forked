---
title: Feature Slice Workflows Risks
type: risks
feature: feature-slice-workflows
date: 2025-10-20
tags: [risks]
---

# Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Config schema drift between versions | Medium | Maintain backwards-compatible defaults; add validation that warns without breaking older configs. |
| Feature resolver misorders patches | High | Reuse existing global `patches.order` as single source of truth and add unit tests for mixed feature selection. |
| Guard attribution mislabels feature ownership | Medium | Track patch-to-feature mapping centrally and include audit logging when annotations are emitted. |
| CLI UX confusion when both `--overlay` and `--features` provided | Low | Define clear precedence (profile expands to features; explicit list overrides) and document in help text. |

# Open Questions
- Should `forked feature create` prompt for slice slugs or default to numeric-only names?
- Do we need JSON output for `forked feature status` in the first iteration?
