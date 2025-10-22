# Forked Operations Guide for LLM Agents

Give this document to any automated assistant working inside a Forked-enabled repository. Follow the sequence unless a maintainer instructs otherwise.

---

## 1. Environment & Safety
1. **Prerequisites**
   - Git ≥ 2.31, Python ≥ 3.10, Forked installed (`pip install forked` or `pipx install forked`).
2. **Treat generated artefacts as read-only**
   - Never hand-edit `.forked/**`, `status/daily/**`, or log files; regenerate via CLI commands.
3. **Work from the repository root**
   - Run `git status` first: ensure the workspace is clean and on the expected branch.
4. **Capture outputs**
   - Save command transcripts and JSON artefacts under `testing/reports/<os>/<repo>/` when asked.

---

## 2. First-Time Setup in a Fork
1. Add the canonical remote if missing:
   ```bash
   git remote add upstream <canonical-url>
   git fetch upstream
   ```
2. Initialise Forked:
   ```bash
   forked init --upstream-remote upstream --upstream-branch main
   ```
3. Edit `forked.yml` to define patch order, features, and overlays; commit the file.
4. Refer to `docs/commands/init.md` for additional detail if required.

---

## 3. Command Cheat Sheet
| Task | Command | Notes |
|------|---------|-------|
| Build overlay | `forked build --overlay <profile>` | Add `--emit-conflicts-path …` to capture bundles. |
| Guard overlay | `forked guard --overlay overlay/<id> --mode block` | Use `--mode require-override` when overrides are mandatory. |
| Status snapshot | `forked status --json --latest 5` | Pipe to `jq` or write to `reports/status.json`. |
| Sync patches | `forked sync --emit-conflicts --on-conflict stop` | Switch to `bias` or `exec` based on instructions. |
| Clean resources | `forked clean --dry-run --overlays 'overlay/tmp-*' --worktrees --conflicts` | Only add `--no-dry-run --confirm` when authorised. |
| Manage features | `forked feature status` / `forked feature create <name> --slices N` | Keep `forked.yml` aligned with CLI changes. |

Command references live in `docs/commands/`.

---

## 4. Handling Conflicts
1. Run `forked build` or `forked sync` with `--emit-conflicts-path` (and optional `--emit-conflict-blobs`).
2. Review the bundle:
   ```bash
   jq '.context, .files[].precedence' .forked/conflicts/<name>-1.json
   ```
3. Apply recommended resolutions (ours/theirs) or execute the provided `--on-conflict-exec` hook.
4. Resume the Git operation (`git cherry-pick --continue` or `git rebase --continue`).
5. Re-run `forked guard` and `forked status --json` to confirm clean state.

---

## 5. Reporting & Artefacts
- Keep originals inside `.forked/`; copy required files to `reports/` or attach them to task comments.
- When following the cross-platform plan, populate `testing/reports/<os>/<repo>/` with logs, status JSON, and bundles.
- For release/publish flows:
  1. `poetry run ruff check .`
  2. `poetry run mypy`
  3. `poetry run pytest` (if tests exist)
  4. `poetry build`
  5. Summarise exit codes and artefact paths.

---

## 6. Mandatory Rules
1. **Do not rewrite history** unless explicitly authorised. Create new commits or branches instead.
2. **Ask before deleting** overlays, worktrees, or conflict bundles unless instructions include `--no-dry-run --confirm`.
3. **Echo every command executed** in the response for reproducibility.
4. **Highlight warnings** (yellow `[status]`, `[build]`, etc.) even when exit codes are zero.
5. **Stop on failure**—request guidance instead of guessing fixes.
6. **Link to docs when relevant** (`docs/commands/...`, `docs/workflows/...`) so humans can follow up.

Following this checklist keeps automated actions predictable, auditable, and easy for maintainers to review.
