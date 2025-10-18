# Forked CLI

Forked CLI lets you treat your fork like a product: keep `trunk` fast‑forwarded to upstream, stack patch branches in a reproducible overlay, and guard releases with deterministic policy checks. This repository contains the editable CLI implementation, automation scripts, and the project handbook that tracks sprint and release work.

---

## Table of Contents

1. [Concepts](#concepts)
2. [Repository Layout](#repository-layout)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Configuration (`forked.yml`)](#configuration-forkedyml)
6. [CLI Commands](#cli-commands)
7. [Guard Reports](#guard-reports)
8. [Logs & Generated Artifacts](#logs--generated-artifacts)
9. [Demo Repository](#demo-repository)
10. [Development Workflow](#development-workflow)
11. [Troubleshooting](#troubleshooting)

---

## Concepts

- **Upstream** – the canonical repository you track. `forked init` keeps a local branch named `trunk` fast‑forwarded to `upstream/<branch>`.
- **Patch branches** – lightweight topic branches (`patch/*`) stacked in `forked.yml.patches.order`. They are replayed during every build.
- **Overlay** – a disposable branch (`overlay/<id>`) that results from applying the ordered patch list on top of `trunk`. Optionally materialised via a Git worktree.
- **Guard** – policy checks (sentinels, both‑touched files, size caps) that validate the overlay and emit JSON reports for CI or local review.

Forked CLI coordinates those pieces so you can rebuild or guard your patch stack deterministically without mutating your day‑to‑day working tree.

---

## Repository Layout

```
.
├── forked/                    # CLI source code (typer-based)
├── pyproject.toml             # packaging metadata for editable install
├── scripts/setup-demo-repo.sh # helper to create a sandbox repo with patch branches
├── project-handbook/          # sprint/release handbook (Makefile-driven)
└── README.md                  # this document
```

Run-time artefacts are intentionally kept out of Git:

```
.forked/                       # logs, guard reports, and overlay worktrees
```

The directory is gitignored by default.

---

## Installation

You can install the CLI in editable mode while iterating locally:

```bash
python -m pip install --upgrade pip
python -m pip install -e .
```

Once published, the recommended user path will be:

```bash
pipx install forked-cli
```

The CLI requires:

- Git ≥ 2.31 (Git ≥ 2.38 unlocks the `zdiff3` conflict style automatically)
- Python ≥ 3.10

---

## Quick Start

```bash
# optional: create a sandbox fork with patch branches
./scripts/setup-demo-repo.sh demo-forked
cd demo-forked

# 1. Initialise Forked CLI in the repo
forked init

# 2. Configure patch order and optional sentinels in forked.yml
sed -i 's/order: \[\]/order:\n  - patch\/contract-update\n  - patch\/service-logging/' forked.yml

# 3. Build an overlay (creates overlay/<id> + optional worktree)
forked build --id smoke --auto-continue

# 4. Guard the overlay (generates .forked/report.json)
forked guard --overlay overlay/smoke --mode block

# 5. Sync trunk & rebase patch branches against upstream
forked sync
```

The key artefacts after a build/guard cycle:

- `.forked/worktrees/<id>/` – the reuseable overlay worktree.
- `.forked/logs/forked-build.log` – append-only JSON telemetry describing each build.
- `.forked/report.json` – deterministic guard report used by CI and local review.

---

## Configuration (`forked.yml`)

`forked.yml` is committed to your repository and controls upstream, patch ordering, guards, and worktree behaviour.

```yaml
version: 1
upstream:
  remote: upstream
  branch: main
branches:
  trunk: trunk
  overlay_prefix: overlay/
patches:
  order:
    - patch/contract-update
    - patch/service-logging
guards:
  mode: warn                # warn | block | require-override
  both_touched: true
  sentinels:
    must_match_upstream:
      - api/contracts/**
    must_diverge_from_upstream:
      - branding/**
  size_caps:
    max_loc: 0               # 0 disables the cap
    max_files: 0
path_bias:
  ours:
    - config/forked/**
  theirs:
    - vendor/**
worktree:
  enabled: true
  root: ".forked/worktrees"  # relative paths live under <repo>/.forked/worktrees/<id>
policy_overrides:
  require_trailer: false
  trailer_key: "Forked-Override"
```

Key behaviours:

- Relative `worktree.root` paths are relocated outside the Git repo to avoid nested worktrees.
- Setting `$FORKED_WORKTREES_DIR` overrides the root path. On POSIX platforms the CLI rejects Windows-style roots (`C:\…`) to prevent confusion.
- Sentinel sections determine whether specific paths must match or must diverge from upstream in the final overlay.

---

## CLI Commands

| Command | Purpose |
|---------|---------|
| [`forked init`](#forked-init) | Verify upstream remote, fast-forward `trunk`, scaffold config. |
| [`forked sync`](#forked-sync) | Fast-forward `trunk` to upstream and rebase every patch branch. |
| [`forked build`](#forked-build) | Rebuild an overlay branch (and optional worktree) from trunk + patches. |
| [`forked guard`](#forked-guard) | Evaluate policies against an overlay and write a JSON report. |
| [`forked status`](#forked-status) | Show trunk, patches, and the most recent overlays. |
| [`forked publish`](#forked-publish) | Tag and/or push an overlay branch. |

### `forked init`

```bash
forked init [--upstream-remote REMOTE] [--upstream-branch BRANCH]
```

Performs safety checks (clean working tree, remote exists), fetches from upstream, creates/updates the `trunk` branch, enables helpful Git settings (`rerere`, conflict style), and writes `forked.yml` if missing. On Git < 2.38 the CLI automatically falls back to `diff3` conflict style with a short notice.

### `forked sync`

```bash
forked sync
```

Fetches upstream, resets `trunk` to `upstream/<branch>`, then iterates through each patch listed in `forked.yml.patches.order` and rebases it onto trunk. If a rebase stops on conflicts, the command exits with code `4` and prints the branch to fix.

### `forked build`

```bash
forked build [--id ID] [--no-worktree] [--auto-continue]
```

- `--id` – overlay identifier (default: current date `YYYY-MM-DD`).
- `--no-worktree` – build directly in the current working tree instead of creating/reusing a worktree.
- `--auto-continue` – after a cherry-pick conflict, apply path-bias globs (`forked.yml.path_bias`) and continue automatically; otherwise the command stops and surfaces the Git error.

Behaviour highlights:

- Worktree directories are reused between builds. If a stale directory blocks reuse, the CLI suffixes the path (e.g., `test-1`) and prints a reminder to run `git worktree prune`.
- After each build the CLI prints a concise summary of applied patches and appends structured JSON telemetry to `.forked/logs/forked-build.log`.
- Cherry-picks cover the entire range from `merge-base(trunk, patch)` to the patch tip, preserving commit ordering.

### `forked guard`

```bash
forked guard --overlay OVERLAY [--output PATH] [--mode MODE] [--verbose]
```

- `--overlay` *(required)* – overlay branch/ref to analyse (e.g., `overlay/test`).
- `--output` – report destination (default `.forked/report.json`).
- `--mode` – overrides `guards.mode` (`warn`, `block`, or `require-override`).
- `--verbose` / `-v` – print sentinel matches and include extra debug data in the report/logs.

The report contains:

- `both_touched` – files changed in both trunk and overlay since the merge base.
- `sentinels.must_match_upstream` / `.must_diverge_from_upstream` – validation results for sentinel globs.
- `size_caps` – diff size metrics via `git diff --numstat`.
- `violations` – subset of the above that failed policy.

Exit codes:

- `0` – pass (or violations in `warn` mode).
- `2` – policy violations in `block`/`require-override` mode.
- `3` – configuration missing/invalid.
- `4` – Git failure (dirty tree, missing remote, etc.).

### `forked status`

```bash
forked status [--latest N]
```

Shows upstream and trunk SHAs, lists patches in order, and prints the newest overlays with timestamps and both-touched counts.

### `forked publish`

```bash
forked publish --overlay OVERLAY [--tag TAG] [--push] [--remote REMOTE]
```

Creates (or force-updates) a tag pointing at the overlay and optionally pushes the tag and overlay branch to a remote (default `origin`). Useful once a guarded overlay is ready to share.

---

## Guard Reports

Default location: `.forked/report.json`

Example (trimmed):

```json
{
  "report_version": 1,
  "overlay": "overlay/test",
  "trunk": "trunk",
  "base": "6c535ebe766748006eea7f5fc21d0eaa2bcf01a2",
  "violations": {
    "sentinels": {
      "must_match_upstream": ["api/contracts/v1.yaml"],
      "must_diverge_from_upstream": []
    }
  },
  "both_touched": ["src/service.py"],
  "size_caps": {
    "files_changed": 3,
    "loc": 42,
    "violations": true
  }
}
```

Downstream tooling (CI, bots) can parse `violations` to fail builds or surface guidance. The `report_version` field allows the format to evolve while preserving backwards compatibility.

---

## Logs & Generated Artifacts

| Path | Purpose |
|------|---------|
| `.forked/logs/forked-build.log` | Append-only JSON telemetry for each build (overlay id, reused path, per-branch commit summaries). |
| `.forked/logs/forked-guard.log` | Append-only JSON telemetry for guard runs (overlay, mode, violations, optional debug). |
| `.forked/report.json` | Latest guard report. |
| `.forked/worktrees/<overlay-id>/` | Reused worktree for the overlay (removed by `git worktree prune`). |

All of these paths are ignored via `.gitignore` so your repo stays clean.

---

## Demo Repository

Need a sandbox with realistic branches? Use the helper script:

```bash
./scripts/setup-demo-repo.sh demo-forked
cd demo-forked
forked init
# forked.yml now lists upstream, trunk, and patch branches created by the script
```

The script provisions:

- `patch/contract-update` and `patch/service-logging`
- sentinel-friendly directories (`config/forked/**`, `branding/**`)
- both upstream and origin bare remotes for push/pull simulation

---

## Development Workflow

```bash
# install dependencies and editable CLI
python -m pip install -e .

# run project handbook automation (e.g., sprint dashboards)
cd project-handbook
make help
```

Key handbook commands:

- `make task-list` – show current sprint tasks (`project-handbook/Makefile`).
- `make sprint-status` – current sprint health indicators.
- `make release-status` – release v1.0.0 progress overview.

When making CLI changes, regenerate the demo repo (script above), rerun `forked build` and `forked guard`, and inspect `.forked/logs/forked-build.log` to confirm logging.

---

## Troubleshooting

| Symptom | Resolution |
|---------|------------|
| `forked init` prints “Using diff3 merge conflict style…” | You are running Git < 2.38; the CLI falls back to a supported conflict style automatically. Upgrade Git if you want `zdiff3`. |
| Build warns about suffixing worktree directories | Run `git worktree prune` to remove stale entries, or delete the directory manually. |
| Guard exits with code `2` unexpectedly | Inspect `.forked/report.json` – look under `violations`. Run in `--mode warn` to explore without failing. |
| `forked build` applies no commits | Ensure `forked.yml.patches.order` lists your patch branches and that they diverge from trunk. |
| Guard report missing sentinel hits | Confirm the globs in `forked.yml.guards.sentinels` match actual file paths. |

---

Forked CLI is still evolving. If you have questions or ideas for the next iteration (better guard reporting, new commands, CI integrations), open an issue or capture it in the project handbook backlog. Happy overlaying! 🚀
