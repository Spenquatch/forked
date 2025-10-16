# Repository Guidelines

## Project Structure & Module Organization
- `README.md` — product spec and operational context for the Forked CLI MVP.
- `legacy-handbook/` — sprint-based project handbook (features, releases, sprints, backlog, docs, automation).
  - `features/` tracks overlay, guard, and release initiatives.
  - `releases/v1.0.0/` captures the current Forked CLI delivery plan.
  - `process/automation/` houses Python scripts invoked via `make`.
- `legacy-handbook/status/` and `status/daily/` store generated dashboards; treat them as build artifacts.

## Build, Test, and Development Commands
Run all commands from `legacy-handbook/` unless noted.
- `make help` – list available handbook automation targets.
- `make daily` – generate the Day N status file (skips weekends automatically).
- `make sprint-status` – show sprint health indicators (🟢/🟡/🔴).
- `make feature-update-status` – refresh feature status files from sprint data.
- `make validate` – run all handbook validators (links, schemas, front matter).
- `make road​map` / `make release-status` – inspect roadmap and release progress.

## Coding Style & Naming Conventions
- Markdown and YAML are the primary authoring formats; keep front matter fields in lowercase snake_case (e.g., `start_sprint`).
- Commit-created files follow kebab-case (`overlay-infrastructure/`), while automation-generated IDs use pattern `TASK-###-slug`.
- Python automation scripts target 4-space indentation and PEP 8 naming (`snake_case` for functions, `CapWords` for classes).

## Testing Guidelines
- Validation is performed through `make validate`; no separate unit test suite ships with the handbook.
- Before publishing status artifacts, run both `make validate` and `make status` to ensure generated JSON/Markdown remain consistent.
- Avoid manual edits inside `status/` or `releases/*/progress.md`; regenerate via the corresponding make targets if changes are required.

## Commit & Pull Request Guidelines
- Use imperative, descriptive commit summaries (e.g., `feat: harden overlay rebuild`).
- Reference relevant tasks or ADRs when applicable (`Refs: #TASK-001`, `ADR-0001`).
- Pull requests should include: purpose summary, affected directories, validation commands executed (e.g., `make validate`), and links to sprint tasks or release goals.
- Provide screenshots or diff excerpts when updating dashboards or generated artifacts to highlight the delta.
