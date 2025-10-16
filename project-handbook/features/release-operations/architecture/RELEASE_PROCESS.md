---
title: Release Operations Architecture
type: architecture
feature: release-operations
date: 2025-09-22
tags: [architecture, release]
---

# Release Operations Architecture

## Release Flow (v1.0.0)
1. **Plan** – Maintain `releases/v1.0.0/plan.md` with goals, success metrics, and feature alignment (overlay, guard, release ops).
2. **Build** – Use `forked build --id <run>` to generate overlay branches/worktrees.
3. **Guard** – Execute `forked guard --overlay overlay/<run> --mode block`; capture JSON artefacts.
4. **Publish** – Tag overlays (`forked publish --overlay overlay/<run> --tag overlay/<run> --push --remote origin`).
5. **Document** – Update release notes (`releases/v1.0.0.md`), changelog, and dashboard via `make release-status`.

## Key Artefacts
- `README.md` smoke + release checklists.
- `legacy-handbook/releases/v1.0.0/` plan, feature allocation, and progress file (auto-generated).
- `legacy-handbook/status/current.json` – aggregated sprint + feature status for dashboards.

## Automation Entry Points
- `make release-plan version=v1.0.0` – initialize release metadata.
- `make release-status` – recompute progress and highlight blockers.
- `make status` / `make dashboard` – generate project-wide views (includes release health).

## Roles & Responsibilities
- **Engineering** – ensure overlay + guard features meet success criteria, run smoke checklist before tagging.
- **Release Ops** – confirm documentation is current, update changelog, and coordinate final tagging/publishing.
- **CI/CD** – execute build + guard commands per run; upload guard report artefacts.

## Future Enhancements
- Automate guard artefact upload in GitHub Actions.
- Generate HTML release notes from Markdown templates.
- Introduce signed tags for published overlays.
