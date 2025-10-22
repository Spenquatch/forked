# Forked Operations Guide for LLM Agents

Use this checklist when automating work inside repositories that depend on Forked. Follow the order unless a human asks for something different.

---

## 1. Environment & Safety
1. **Prerequisites**
   - Ensure Git ≥ 2.31, Python ≥ 3.10, and Forked installed (`pip install forked` or `pipx install forked`).
2. **Never touch generated artefacts manually**
   - Treat `.forked/**`, `status/daily/**`, and build logs as read-only; regenerate via CLI commands.
3. **Run commands from repo root**
   - Assume the working directory is the target project (not this CLI repo).

---

## 2. First-Time Setup in a Fork
1. Add upstream remote if missing:
   ```bash
   git remote add upstream <canonical-repo-url>
   git fetch upstream
   ```
2. Initialise Forked:
   ```bash
   forked init --upstream-remote upstream --upstream-branch main
   ```
3. Edit `forked.yml` if patches/features/overlays need configuring; commit the file.

---

## 3. Daily Commands Cheat Sheet
| Task | Command | Notes |
|------|---------|-------|
| Build overlay | `forked build --overlay <profile>` | Add `--emit-conflicts-path …` to log bundle. |
| Guard overlay | `forked guard --overlay overlay/<id> --mode block` | Use `--mode require-override` when policy demands a trailer. |
| Status snapshot | `forked status --json --latest 5` | Redirect to `reports/status.json` if asked. |
| Sync patches | `forked sync --emit-conflicts --on-conflict stop` | Switch to `bias` or `exec` per instructions. |
| Clean artefacts | `forked clean --dry-run --overlays 'overlay/tmp-*' --worktrees --conflicts` | Re-run with `--no-dry-run --confirm` only when cleared to delete. |
| Feature slices | `forked feature status` / `forked feature create <name> --slices N` | Keep `forked.yml` in sync. |

---

## 4. Handling Conflicts
1. Build or sync with conflict flags (`--emit-conflicts-path`, optional `--emit-conflict-blobs`).
2. Inspect bundles:
   ```bash
   jq '.context, .files[].precedence' .forked/conflicts/<name>-1.json
   ```
3. Apply recommended resolutions (ours/theirs) or run provided exec command.
4. Resume Git operation (`git cherry-pick --continue` or `git rebase --continue`).
5. Re-run `forked guard` and `forked status --json` to confirm clean state.

---

## 5. Reporting & Outputs
- Keep artefacts in `.forked/` and attach copies as requested (`report.json`, conflict bundles, status JSON).
- For publish workflows:
  1. Run lint/type/test (`poetry run ruff check .`, `poetry run mypy`, `poetry run pytest` if available).
  2. `poetry build` (or `forked status --json` per spec).
  3. Provide a summary of key outputs (paths, exit codes).

---

## 6. Important Rules for Agents
1. **Never rewrite history** unless explicitly authorised. Prefer creating new commits/branches.
2. **Ask before deleting** overlays, worktrees, or conflict bundles unless instructions include `--no-dry-run --confirm`.
3. **Log commands** in responses so humans can reproduce the steps.
4. **Surface warnings** (yellow `[status]` / `[build]`) in the report, even if exit code is zero.
5. If a command fails, stop and request guidance. Do not guess reversible fixes.

Following this guide ensures your actions stay predictable, auditable, and reversible while working with Forked-enabled repositories.
