# Cross-Platform Manual Test Plan

This guide validates the published `forked` CLI across Windows 11, macOS Sonoma, and Ubuntu 22.04 using both the bundled demo repo and real GitHub codebases.

---

## 1. Prerequisites
- Git ≥ 2.38, Python 3.10+, `pipx` (or `python -m pip install -e .` for editable mode)
- Install the PyPI package: `pipx install forked` (or `python -m pip install forked`)
- GitHub personal fork access and forked repos (see Section 3)
- Optional: Poetry for local builds (`pip install poetry`)

## 2. Baseline Smoke (All Platforms)
1. Checkout this repo.
2. Run `./scripts/setup-demo-repo.sh demo-feature-run`.
3. Follow the full workflow in `sanity_check.md` (init, build, guard, status, clean, feature). Capture outputs per platform.

Store raw logs under `testing/reports/<os>/demo-feature-run/`.

---

## 3. Real Repository Setup
For each OS, fork and clone:

| Repo | Purpose | Local Clone Path |
|------|---------|------------------|
| `github.com/tpope/vim-sensible` | Small tree | `~/fork-tests/vim-sensible` |
| `github.com/psf/requests` | Medium Python project | `~/fork-tests/requests` |
| `github.com/python/cpython` (shallow) | Large history stress test | `~/fork-tests/cpython` (use `--depth 1`) |

Ensure remotes:
```bash
git remote add upstream <upstream-url>
git remote add origin   <fork-url>
```
Use `git fetch --all` before testing.

---

## 4. Test Matrix & Steps

### 4.1 Initialization
For each repo (and OS):
```bash
forked init --upstream-remote upstream --upstream-branch main
```
Verify:
- `forked.yml` created with default scaffolding.
- `.forked/` directory exists (gitignored).
- Commit the config (optional).

### 4.2 Configuration
1. Edit `forked.yml` to add:
   - Two patch branches pointing at divergent commits.
   - Features referencing those patches.
   - Sentinels in `guards.sentinels`.
2. Commit the changes.

### 4.3 Build Scenarios
Run these commands, recording stdout, stderr, exit codes:

| Scenario | Command |
|----------|---------|
| Overlay profile | `forked build --overlay dev` |
| Feature list with includes | `forked build --features feature_a --include patch/extra --id dev-extra` |
| Exclude branch | `forked build --overlay dev --exclude patch/legacy` |
| Skip equivalents | `forked build --overlay dev --skip-upstream-equivalents` |
| Conflict bundle stop | `forked build --overlay dev --emit-conflicts-path .forked/conflicts/dev --on-conflict stop` |
| Auto-continue bias | `forked build --overlay dev --auto-continue --on-conflict bias` |
| Exec hook | `forked build --overlay dev --emit-conflicts-path .forked/conflicts/exec --on-conflict exec --on-conflict-exec "./scripts/auto-resolve.sh"` (create a dummy script returning success) |

Record:
- `.forked/logs/forked-build.log`
- `.forked/conflicts/*.json` (inspect wave numbering and metadata)
- Worktree directories under `.forked/worktrees/`

### 4.4 Guard Modes
Create sentinel-triggering changes per repo, then run:
```bash
forked guard --overlay overlay/dev --mode warn
forked guard --overlay overlay/dev --mode block
forked guard --overlay overlay/dev --mode require-override
```
- Capture `.forked/report.json`.
- Test override sources: commit trailer, annotated tag, git note.
- Confirm exit codes (0 for warn, 2 for block/require-override without marker, 0 with valid override).

### 4.5 Status Output
1. `forked status --latest 5`
2. `forked status --json --latest 3 | jq`
3. Remove `.forked/logs/forked-build.log` and git note, rerun `--json` to confirm derived selection warning and fallback.

### 4.6 Clean Command
1. Create dummy overlays/worktrees/conflict bundles.
2. Run:
```bash
forked clean --dry-run --overlays 'overlay/tmp-*' --worktrees --conflicts
forked clean --no-dry-run --confirm --overlays 'overlay/tmp-*'
forked clean --no-dry-run --confirm --worktrees
forked clean --no-dry-run --confirm --conflicts --conflicts-age 1
```
Verify deleted artefacts and `.forked/logs/clean.log` entries.

### 4.7 Sync Workflow
1. Introduce upstream changes causing patch conflicts.
2. Execute:
```bash
forked sync --emit-conflicts-path .forked/conflicts/sync --on-conflict stop
forked sync --emit-conflict-blobs --emit-conflicts-path .forked/conflicts/sync-bias --on-conflict bias --auto-continue
forked sync --emit-conflicts-path .forked/conflicts/sync-exec --on-conflict exec --on-conflict-exec "./scripts/sync-resolver.sh"
```
Confirm conflict bundles, wave numbering, exit codes, and `.forked/logs/forked-build.log` entries tagged `forked.sync`.

### 4.8 Feature CLI
```bash
forked feature status
forked feature create checkout --slices 2
forked feature remove checkout
```
Check slice branch creation and status output.

### 4.9 Packaging Check (Optional)
```bash
poetry build
poetry publish --dry-run --build
```

---

## 5. Reporting
- For each OS and repo, create a subdirectory under `testing/reports/<os>/<repo>/`.
- Save command transcripts, JSON outputs, conflict bundles, and log excerpts.
- Include `summary.md` per repo noting pass/fail results, anomalies, timing issues.
- Highlight platform-specific quirks (e.g., path separators, shell quoting) and open Git issues where necessary.

---

## 6. Automation Helpers
- Consider authoring platform-specific wrapper scripts (`testing/scripts/*.sh` / `.ps1`) that run the common command sequences, pausing for manual conflict setup where needed.
- Use environment variables (`FORKED_WORKTREES_DIR`, etc.) to surface configuration problems.

With this plan, every CLI surface area is validated across Windows, macOS, and Linux using both controlled (demo) and real-world repositories, ensuring confidence in the published `forked` package.
