---
title: Handbook Conventions
type: process
date: 2025-09-12
tags: [conventions, validation]
links: []
---

# Conventions & Validation Rules

Front matter (all Markdown under `project-handbook/`)
```
---
title: <Title>
type: <adr|fdr|overview|architecture|implementation|api|testing|status|changelog|phase|process|release|roadmap>
date: 2025-09-12
tags: [<one-or-more>]
links: []
---
```

Decision Types
- ADR (global): `project-handbook/adr/0001-<slug>.md`, id `ADR-0001`.
- FDR (feature-local): `project-handbook/features/<feature>/fdr/0001-<slug>.md`, id `FDR-<feature>-0001`.
- Every task references exactly one controlling decision (ADR or FDR).

Features
- Location: `project-handbook/features/<feature>/`.
- Required files: `overview.md`, `architecture/ARCHITECTURE.md`, `implementation/IMPLEMENTATION.md`, `testing/TESTING.md`, `status.md`, `changelog.md`.
- `overview.md` front matter must include `feature: <feature>` and optional `dependencies: ["feature:other", "ADR-XXXX"]`.
- `risks.md` is the authoritative risk register for systemic risks.

Sprint Task Directories
- Location: `project-handbook/sprints/YYYY/SPRINT-YYYY-W##/tasks/TASK-XXX-name/`.
- Required: `task.yaml` (metadata with story_points, depends_on), `README.md`, `steps.md`, `commands.md`, `checklist.md`, `validation.md`.
- Optional: `references.md`, `source/` (templates, configs, examples).
- Dependencies: Only within current sprint scope (sprint-scoped validation).

Status Model
- Task: `todo -> doing -> review -> done` or `todo -> blocked -> todo/doing`.
- Sprint: `planned -> active -> completed`.
- Feature: `proposed -> approved -> developing -> complete -> live`.
- Decision: `draft -> accepted` (or `rejected`; `accepted -> superseded`).

Validation Gates (enforced by checks)
- Gate A (Decision): ADR/FDR exists, `status=accepted` before task creation.
- Gate B (Sprint Tasks): Each task has required files, valid story_points, sprint-scoped dependencies.
- Gate C (Feature Dependencies): Feature dependencies must be satisfied for task completion.
- Gate D (Daily Status): Daily status required on work days; sprint metrics updated.
- Gate E (Sprint Close): On sprint completion, retrospective generated and velocity calculated.

Backlog Items
- Location: `project-handbook/backlog/<type>/<ID>/`.
- Types: `bugs` (production issues), `wildcards` (urgent requests).
- ID format: `<TYPE>-P<0-4>-<YYYYMMDD>-<HHMM>` (e.g., `BUG-P0-20250922-1144`).
- Required files: `README.md` (issue description), `triage.md` (for P0 issues only).
- Severity levels: P0 (critical), P1 (high), P2 (medium), P3 (low), P4 (trivial).

Parking Lot Items
- Location: `project-handbook/parking-lot/<category>/<ID>/`.
- Categories: `features`, `research`, `technical-debt`, `ideas`.
- ID format: `<CATEGORY>-<YYYYMMDD>-<slug>` (e.g., `FEAT-20250922-oauth-integration`).
- Required files: `README.md` (concept description).
- Quarterly review cycle for promotion to roadmap or archive.

Linking
- Use relative links.
- Cross-reference ADRs/FDRs and tasks in changelogs and releases.
- Reference backlog items in feature overviews: `backlog_items: [BUG-P1-123]`.
- Track parking lot origins: `parking_lot_origin: FEAT-001`.

