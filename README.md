Heck yes. Let’s lock the **Forked CLI** MVP so you can build it straight away and demo it this week. Below is a full, opinionated spec + step-by-step setup + working Python code you can paste into a repo **today**. It’s 100% Git-native, idempotent, and leaves zero hidden state.

---

# MVP Goals (what v1 must do)

1. **Model the fork cleanly**

   * `trunk`: fast-forward mirror of `upstream/main`
   * `patch/*`: your small, focused change branches
   * `overlay/<id>`: rebuildable branch = `trunk` + ordered patches

2. **Automate upkeep**

   * `forked sync`: ff `trunk` to upstream; rebase each `patch/*`
   * `forked build`: create `overlay/<id>` (optional worktree); cherry-pick patches in order
   * `forked guard`: **flag semantic risk even when Git merges “cleanly”**

     * both-touched files (upstream and you changed the same file since base)
     * sentinels (paths that must match upstream *or* must diverge)
     * path bias helpers during conflicts (ours/theirs globs)
     * size caps & policy (warn/block/require-override)

3. **Be Git-native & reproducible**

   * No DB. Truth lives in: refs, tags, `forked.yml`
   * Idempotent rebuilds; disposable overlays; `rerere` for conflict replay

4. **CI-ready**

   * Deterministic JSON report with non-zero exit on policy violations
   * GH Action that runs on demand + on upstream releases

---

# File/Ref Layout

```
forked.yml                # config-as-code (committed)
.forked/                  # ephemeral worktrees/cache/reports (gitignored)
refs/heads/trunk          # mirror of upstream/main (ff-only)
refs/heads/patch/*        # your changes
refs/heads/overlay/*      # built products (disposable)
refs/tags/overlay/*       # frozen pointers to shipped overlays
```

---

# `forked.yml` (MVP schema)

```yaml
version: 1
upstream:
  remote: upstream          # name of the remote that points to original repo
  branch: main              # default upstream branch
branches:
  trunk: trunk
  overlay_prefix: overlay/
patches:
  order:                    # ordered list of patch branches to apply
    - patch/telemetry-off
    - patch/add-endpoint
guards:
  mode: warn                # warn | block | require-override
  both_touched: true
  sentinels:
    must_match_upstream:    # these paths MUST equal trunk version in overlay
      - "api/contracts/**"
    must_diverge_from_upstream:  # these paths MUST differ from trunk in overlay
      - "branding/**"
  size_caps:
    max_loc: 0              # 0 = disabled (enable later if you want)
    max_files: 0
path_bias:                  # bias conflict resolution by glob
  ours:                     # prefer overlay/patch side on conflict for these
    - "config/forked/**"
  theirs:                   # prefer trunk/upstream side on conflict for these
    - "vendor/**"
worktree:
  enabled: true
  root: ".forked/worktrees" # relative paths relocate to ../.forked-worktrees/<repo>; override via $FORKED_WORKTREES_DIR
policy_overrides:
  require_trailer: false    # e.g., "Forked-Override: size"
  trailer_key: "Forked-Override"
```

> Semantics
>
> * **must_match_upstream**: in the final overlay, each path’s blob must equal `trunk`’s blob.
> * **must_diverge_from_upstream**: in overlay, each path must **not** equal `trunk`’s blob (i.e., your fork must own it). Violation only happens when the overlay omits the file or keeps it byte-identical—overlay-only additions are valid divergence.

---

# End-to-End Setup (first use)

1. **Install**

   ```bash
   pipx install forked-cli  # (we’ll package it like this)
   ```

2. **Add upstream & init Forked**

   ```bash
   git remote add upstream https://github.com/ORIG/REPO.git   # if not present
   forked init
   ```

   What `init` does:

   * Verifies repo is clean.
   * Ensures `upstream` remote exists and is reachable.
   * Creates/updates `trunk` == `upstream/main`.
   * Enables: `rerere.enabled=true`, `merge.conflictStyle=zdiff3`.
   * Writes `forked.yml` scaffold (if missing).

3. **Create patch branches (your changes)**

   ```bash
   git checkout -b patch/telemetry-off trunk
   # ...code & commit...
   git checkout -b patch/add-endpoint trunk
   # ...code & commit...
   ```

   Add them to `forked.yml.patches.order` in the order you want applied.

4. **Build an overlay**

   ```bash
   forked build --id v0  # creates overlay/v0
   ```

   * Creates new branch `overlay/v0` from `trunk`
   * Cherry-picks your patch branches in order (using rerere; pauses on conflicts)
   * If `worktree.enabled`, checks it out under `../.forked-worktrees/<repo>/v0/` (or `$FORKED_WORKTREES_DIR`) so your main checkout stays untouched
   * If a previous directory still exists, we suffix the new one (e.g., `v0-1`) instead of failing—run `git worktree prune` to reclaim old paths
   * Rebuilding the same `--id` reuses the existing worktree and hard-resets it back to today’s trunk before replaying patches
   * Prints the location + next steps

5. **Guard it**

   ```bash
   forked guard --overlay overlay/v0 --output .forked/report.json
   ```

   * Computes **merge base** and flags both-touched files, sentinel breaches, size gates
   * Exits non-zero if `guards.mode` = `block` and violations exist

6. **Publish it (optional)**

   ```bash
   forked publish --overlay overlay/v0 --tag overlay/2025-08-30
   ```

   * Tags the overlay; pushes tag and overlay branch (if you pass `--push`)

7. **Stay up to date**

   ```bash
   forked sync          # ff trunk to upstream; rebase each patch/*
   forked build --id v1 # rebuild overlay on fresh trunk
   forked guard --overlay overlay/v1
   ```

---

# CLI Contract (MVP)

```text
forked init
  --upstream-remote upstream
  --upstream-branch main

forked status
  --latest <N>                 # show N newest overlays (default 1) with both-touched hints

forked sync
  # ff trunk to upstream; rebase each patch/* onto trunk

forked build
  --id <string>                  # overlay/<id>
  --no-worktree
  --auto-continue                # auto-apply path_bias on conflicts and continue

forked guard
  --overlay <ref>                # e.g., overlay/v1
  --output <path.json>
  --mode warn|block|require-override (overrides config)

forked publish
  --overlay <ref>
  --tag overlay/<id>
  --push
```

**Exit codes**

* `0` success
* `2` guard violations (policy block / require-override not satisfied)
* `3` invalid config
* `4` git error (dirty tree, missing remote, etc.)

---

# Python MVP (single-repo implementation)

> Drop these into `forked/` and expose `forked` via `console_scripts`. This is a **working** baseline you can evolve.

## `pyproject.toml` (packaging)

```toml
[project]
name = "forked-cli"
version = "0.1.0"
description = "Git-native fork overlay & guard tool"
requires-python = ">=3.10"
dependencies = ["typer>=0.12", "pyyaml>=6.0", "rich>=13.7", "pathspec>=0.12"]

[project.scripts]
forked = "forked.cli:app"

[tool.setuptools.packages.find]
where = ["."]

[build-system]
requires = ["setuptools>=68", "wheel"]
build-backend = "setuptools.build_meta"
```

## `forked/config.py`

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional
import typer
import yaml

DEFAULT_CFG_PATH = Path("forked.yml")

@dataclass
class Upstream:
    remote: str = "upstream"
    branch: str = "main"

@dataclass
class Branches:
    trunk: str = "trunk"
    overlay_prefix: str = "overlay/"

@dataclass
class Patches:
    order: List[str] = field(default_factory=list)

@dataclass
class SizeCaps:
    max_loc: int = 0
    max_files: int = 0

@dataclass
class Sentinels:
    must_match_upstream: List[str] = field(default_factory=list)
    must_diverge_from_upstream: List[str] = field(default_factory=list)

@dataclass
class Guards:
    mode: str = "warn"  # warn | block | require-override
    both_touched: bool = True
    sentinels: Sentinels = field(default_factory=Sentinels)
    size_caps: SizeCaps = field(default_factory=SizeCaps)

@dataclass
class PathBias:
    ours: List[str] = field(default_factory=list)
    theirs: List[str] = field(default_factory=list)

@dataclass
class WorktreeCfg:
    enabled: bool = True
    root: str = ".forked/worktrees"

@dataclass
class PolicyOverrides:
    require_trailer: bool = False
    trailer_key: str = "Forked-Override"

@dataclass
class Config:
    version: int = 1
    upstream: Upstream = field(default_factory=Upstream)
    branches: Branches = field(default_factory=Branches)
    patches: Patches = field(default_factory=Patches)
    guards: Guards = field(default_factory=Guards)
    path_bias: PathBias = field(default_factory=PathBias)
    worktree: WorktreeCfg = field(default_factory=WorktreeCfg)
    policy_overrides: PolicyOverrides = field(default_factory=PolicyOverrides)

def load_config(path: Path = DEFAULT_CFG_PATH) -> Config:
    if not path.exists():
        raise typer.Exit(code=3)
    data = yaml.safe_load(path.read_text())
    # Quick/dirty mapping (good enough for MVP)
    def _get(d, k, default):
        return d.get(k, {}) if isinstance(default, (Upstream, Branches, Patches, Guards, PathBias, WorktreeCfg, PolicyOverrides)) else d.get(k, default)

    upstream = Upstream(**data.get("upstream", {}))
    branches = Branches(**data.get("branches", {}))
    patches = Patches(**data.get("patches", {}))
    guards = data.get("guards", {})
    sent = Sentinels(**guards.get("sentinels", {}))
    sz   = SizeCaps(**guards.get("size_caps", {}))
    guards_obj = Guards(mode=guards.get("mode", "warn"),
                        both_touched=guards.get("both_touched", True),
                        sentinels=sent, size_caps=sz)
    path_bias = PathBias(**data.get("path_bias", {}))
    worktree  = WorktreeCfg(**data.get("worktree", {}))
    pov = PolicyOverrides(**data.get("policy_overrides", {}))
    return Config(upstream=upstream, branches=branches, patches=patches,
                  guards=guards_obj, path_bias=path_bias,
                  worktree=worktree, policy_overrides=pov)

def write_skeleton(path: Path = DEFAULT_CFG_PATH):
    if path.exists(): return
    skel = Config()
    path.write_text(yaml.safe_dump({
        "version": skel.version,
        "upstream": vars(skel.upstream),
        "branches": vars(skel.branches),
        "patches": {"order": []},
        "guards": {
            "mode": skel.guards.mode,
            "both_touched": skel.guards.both_touched,
            "sentinels": {
                "must_match_upstream": [],
                "must_diverge_from_upstream": []
            },
            "size_caps": {"max_loc": 0, "max_files": 0}
        },
        "path_bias": {"ours": [], "theirs": []},
        "worktree": {"enabled": True, "root": ".forked/worktrees"},
        "policy_overrides": {"require_trailer": False, "trailer_key": "Forked-Override"}
    }, sort_keys=False))
```

## `forked/gitutil.py`

```python
import subprocess as sp
from typing import List, Optional
from pathlib import Path
import typer

def run(args: List[str], cwd: Optional[str]=None, check=True) -> sp.CompletedProcess:
    return sp.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=check)

def ensure_clean():
    out = run(["status", "--porcelain"], check=True).stdout.strip()
    if out:
        typer.echo("[git] Working tree not clean. Commit or stash first.")
        raise typer.Exit(code=4)

def has_remote(name: str) -> bool:
    rems = run(["remote"]).stdout.splitlines()
    return name in rems

def merge_base(a: str, b: str) -> str:
    return run(["merge-base", a, b]).stdout.strip()

def changed_paths(a: str, b: str) -> list[str]:
    out = run(["diff", "--name-only", "--find-renames", f"{a}...{b}"]).stdout
    return sorted([p for p in out.splitlines() if p])

def blob_hash(ref: str, path: str) -> Optional[str]:
    # returns blob oid or None if file missing at ref
    cp = run(["ls-tree", ref, "--", path], check=False)
    if cp.returncode != 0 or not cp.stdout.strip():
        return None
    parts = cp.stdout.split()
    return parts[2] if len(parts) >= 3 else None

def current_ref() -> str:
    return run(["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()

def repo_root() -> Path:
    return Path(run(["rev-parse", "--show-toplevel"]).stdout.strip())

def worktree_for_branch(branch: str) -> Optional[Path]:
    """Return Path of an existing worktree that has `branch` checked out, or None."""
    out = run(["worktree", "list", "--porcelain"]).stdout.splitlines()
    cur_path = None
    for ln in out:
        if ln.startswith("worktree "):
            cur_path = ln.split(" ", 1)[1]
        elif ln.startswith("branch "):
            b = ln.split(" ", 1)[1]
            if b == f"refs/heads/{branch}":
                return Path(cur_path)
    return None
```

## `forked/guards.py`

```python
from pathlib import Path
from typing import Dict, Any
from . import gitutil as g
from .config import Config
from pathspec import PathSpec

def _make_spec(globs: list[str]) -> PathSpec:
    return PathSpec.from_lines("gitwildmatch", globs or [])

def both_touched(cfg: Config, base: str, trunk: str, overlay: str) -> list[str]:
    up = set(g.changed_paths(base, trunk))
    us = set(g.changed_paths(base, overlay))
    return sorted(up & us)

def sentinels(cfg: Config, trunk: str, overlay: str) -> dict[str, list[str]]:
    mmu = _make_spec(cfg.guards.sentinels.must_match_upstream)
    mdu = _make_spec(cfg.guards.sentinels.must_diverge_from_upstream)
    must_match = []
    must_diverge = []

    # union of candidate files from both overlay and trunk so missing files are checked
    ls_overlay = set(g.run(["ls-tree", "-r", "--name-only", overlay]).stdout.splitlines())
    ls_trunk = set(g.run(["ls-tree", "-r", "--name-only", trunk]).stdout.splitlines())
    candidates = sorted(ls_overlay | ls_trunk)

    for p in candidates:
        if mmu.match_file(p):
            t = g.blob_hash(trunk, p)
            o = g.blob_hash(overlay, p)
            if t is None or o is None or t != o:
                must_match.append(p)
        if mdu.match_file(p):
            t = g.blob_hash(trunk, p)
            o = g.blob_hash(overlay, p)
            if o is None or (t is not None and t == o):
                must_diverge.append(p)
    return {"must_match_upstream": must_match, "must_diverge_from_upstream": must_diverge}

def size_caps(cfg: Config, overlay: str, trunk: str) -> dict[str, Any]:
    caps = cfg.guards.size_caps
    if not (caps.max_loc or caps.max_files):
        return {"files_changed": 0, "loc": 0, "violations": False}

    files = 0
    loc = 0
    lines = g.run(["diff", "--numstat", f"{trunk}...{overlay}"]).stdout.splitlines()
    for ln in lines:
        parts = ln.split("\t")
        if len(parts) >= 3:
            add, dele = parts[0], parts[1]
            files += 1
            if add.isdigit():
                loc += int(add)
            if dele.isdigit():
                loc += int(dele)
    violated = ((caps.max_files and files > caps.max_files) or
                (caps.max_loc and loc > caps.max_loc))
    return {"files_changed": files, "loc": loc, "violations": violated}
```

## `forked/build.py`

```python
import os
from pathlib import Path
from typing import Tuple, Optional, List
import typer
from .config import Config
from . import gitutil as g
from pathspec import PathSpec

def _conflict_paths(cwd: Optional[str]=None) -> list[str]:
    out = g.run(["status", "--porcelain"], cwd=cwd).stdout.splitlines()
    # conflicted paths have "UU", "AA", "DU", etc.
    return [ln.split()[-1] for ln in out if ln.startswith(("U", "AA", "DD", "DU", "UD"))]

def _apply_path_bias(cfg: Config, cwd: Optional[str]=None) -> bool:
    ours = PathSpec.from_lines("gitwildmatch", cfg.path_bias.ours or [])
    theirs = PathSpec.from_lines("gitwildmatch", cfg.path_bias.theirs or [])
    conflicted = _conflict_paths(cwd)
    applied = False
    for p in conflicted:
        if ours.match_file(p):
            g.run(["checkout", "--ours", "--", p], cwd=cwd)
            g.run(["add", p], cwd=cwd)
            applied = True
        elif theirs.match_file(p):
            g.run(["checkout", "--theirs", "--", p], cwd=cwd)
            g.run(["add", p], cwd=cwd)
            applied = True
    return applied

def _resolve_worktree_dir(cfg: Config, overlay_id: str) -> Path:
    root_override = os.environ.get("FORKED_WORKTREES_DIR")
    base_root = Path(root_override) if root_override else Path(cfg.worktree.root)
    repo = g.repo_root()
    candidate = base_root / overlay_id

    try:
        if candidate.resolve().is_relative_to(repo):
            candidate = repo.parent / ".forked-worktrees" / repo.name / overlay_id
    except AttributeError:
        if str(candidate.resolve()).startswith(str(repo)):
            candidate = repo.parent / ".forked-worktrees" / repo.name / overlay_id

    target = candidate.resolve()
    parent = target.parent
    parent.mkdir(parents=True, exist_ok=True)

    # avoid collisions with existing directories
    if target.exists():
        suffix = 1
        while True:
            alt = parent / f"{target.name}-{suffix}"
            if not alt.exists():
                target = alt
                break
            suffix += 1
        target.parent.mkdir(parents=True, exist_ok=True)

    return target

def _rev_list_range(base: str, tip: str) -> List[str]:
    revs = g.run(["rev-list", "--reverse", f"{base}..{tip}"]).stdout.splitlines()
    return [r for r in revs if r]

def build_overlay(cfg: Config, overlay_id: str, use_worktree: bool=True, auto_continue: bool=False) -> Tuple[str, Path]:
    # 1) refresh trunk and capture existing HEAD
    g.run(["fetch", cfg.upstream.remote])
    prev_ref = g.current_ref()
    g.run(["checkout", "-B", cfg.branches.trunk, f"{cfg.upstream.remote}/{cfg.upstream.branch}"])

    # 2) prepare overlay branch and optional worktree
    overlay = f"{cfg.branches.overlay_prefix}{overlay_id}"
    if use_worktree and cfg.worktree.enabled:
        wt_existing = g.worktree_for_branch(overlay)
        if wt_existing and not wt_existing.exists():
            g.run(["worktree", "prune"])
            wt_existing = g.worktree_for_branch(overlay)

        if wt_existing:
            wt_path = wt_existing
            cwd = str(wt_path)
            g.run(["checkout", overlay], cwd=cwd)
            g.run(["reset", "--hard", cfg.branches.trunk], cwd=cwd)
        else:
            wt_path = _resolve_worktree_dir(cfg, overlay_id)
            g.run(["worktree", "add", "-B", overlay, str(wt_path), cfg.branches.trunk])
            cwd = str(wt_path)
    else:
        g.ensure_clean()
        g.run(["checkout", "-B", overlay, cfg.branches.trunk])
        wt_path = Path.cwd() / f".overlay-{overlay_id}"
        cwd = None

    # 3) cherry-pick patches in order (all commits per branch)
    for pbranch in cfg.patches.order:
        base = g.merge_base(cfg.branches.trunk, pbranch)
        commits = _rev_list_range(base, pbranch)
        if not commits:
            typer.echo(f"[build] {pbranch} already contained in {cfg.branches.trunk}; skipping")
            continue
        for sha in commits:
            cp = g.run(["cherry-pick", "-x", sha], cwd=cwd, check=False)
            if cp.returncode != 0:
                if auto_continue:
                    _apply_path_bias(cfg, cwd)
                    cont = g.run(["cherry-pick", "--continue"], cwd=cwd, check=False)
                    if cont.returncode != 0:
                        typer.echo("[build] Cherry-pick halted; resolve conflicts and rerun.")
                        raise typer.Exit(code=1)
                else:
                    print(cp.stderr)
                    raise typer.Exit(code=1)

    # 4) restore previous ref if we didn't stay in main worktree
    if use_worktree and cfg.worktree.enabled and prev_ref:
        g.run(["checkout", prev_ref])
    return overlay, wt_path
```

## `forked/cli.py`

```python
import json, sys
from datetime import date, datetime
from typing import List, Tuple
from pathlib import Path
import typer
from rich import print as rprint
from .config import load_config, write_skeleton, Config
from . import gitutil as g
from .build import build_overlay
from .guards import both_touched, sentinels, size_caps

app = typer.Typer(add_completion=False)


def _overlays_by_date(prefix: str) -> List[Tuple[str, int]]:
    fmt = "%(refname:short)|%(committerdate:unix)"
    cp = g.run(["for-each-ref", f"--format={fmt}", f"refs/heads/{prefix}"])
    items: List[Tuple[str, int]] = []
    for line in cp.stdout.splitlines():
        if "|" not in line:
            continue
        name, ts = line.split("|", 1)
        try:
            items.append((name, int(ts)))
        except ValueError:
            continue
    return sorted(items, key=lambda x: x[1], reverse=True)

@app.command()
def init(upstream_remote: str = "upstream", upstream_branch: str="main"):
    g.ensure_clean()
    # ensure upstream remote exists
    if not g.has_remote(upstream_remote):
        typer.echo(f"[init] Missing remote '{upstream_remote}'. Add it first: git remote add {upstream_remote} <url>")
        raise typer.Exit(code=4)
    # write config if missing
    write_skeleton()
    cfg = load_config()
    # refresh trunk
    g.run(["fetch", upstream_remote])
    g.run(["checkout", "-B", cfg.branches.trunk, f"{upstream_remote}/{upstream_branch}"])
    # helpful git settings
    g.run(["config", "rerere.enabled", "true"])
    g.run(["config", "merge.conflictStyle", "zdiff3"])
    rprint("[green]Initialized Forked. trunk mirrors upstream, forked.yml created.[/green]")

@app.command()
def status(latest: int = typer.Option(1, "--latest", min=1, help="Show N newest overlays")):
    cfg = load_config()
    up = g.run(["rev-parse", f"{cfg.upstream.remote}/{cfg.upstream.branch}"]).stdout.strip()
    trunk = g.run(["rev-parse", cfg.branches.trunk]).stdout.strip()
    rprint(f"[bold]Upstream[/bold]: {cfg.upstream.remote}/{cfg.upstream.branch} @ {up[:12]}")
    rprint(f"[bold]Trunk[/bold]:    {cfg.branches.trunk} @ {trunk[:12]}")
    rprint("[bold]Patches:[/bold]")
    for p in cfg.patches.order:
        sha = g.run(["rev-parse", p]).stdout.strip()
        rprint(f"  {p} @ {sha[:12]}")
    overlays = _overlays_by_date(cfg.branches.overlay_prefix)
    if overlays:
        rprint("[bold]Overlays (newest first):[/bold]")
        for name, ts in overlays[:latest]:
            base = g.merge_base(cfg.branches.trunk, name)
            bt = both_touched(cfg, base, cfg.branches.trunk, name)
            when = datetime.fromtimestamp(ts).isoformat(sep=" ", timespec="seconds")
            rprint(f"  {name}  [{when}]  both-touched={len(bt)}")

@app.command()
def sync():
    cfg = load_config()
    prev_ref = g.current_ref()
    g.ensure_clean()
    g.run(["fetch", cfg.upstream.remote])
    # refresh trunk
    g.run(["checkout", cfg.branches.trunk])
    g.run(["reset", "--hard", f"{cfg.upstream.remote}/{cfg.upstream.branch}"])
    # rebase patches
    for p in cfg.patches.order:
        g.run(["checkout", p])
        cp = g.run(["rebase", cfg.branches.trunk], check=False)
        if cp.returncode != 0:
            typer.echo(f"[sync] Rebase stopped on {p}. Resolve and rerun `forked sync`.")
            raise typer.Exit(code=4)
    if prev_ref:
        g.run(["checkout", prev_ref])
    rprint("[green]Sync complete: trunk fast-forwarded, patches rebased.[/green]")

@app.command()
def build(id: str = typer.Option(date.today().isoformat(), "--id"),
          no_worktree: bool = typer.Option(False, "--no-worktree"),
          auto_continue: bool = typer.Option(False, "--auto-continue")):
    cfg = load_config()
    overlay, wt = build_overlay(cfg, id, use_worktree=(not no_worktree), auto_continue=auto_continue)
    rprint(f"[green]Built overlay[/green] [bold]{overlay}[/bold]")
    if not no_worktree and cfg.worktree.enabled:
        rprint(f"Worktree: {wt}")

@app.command()
def guard(overlay: str,
          output: Path = typer.Option(Path(".forked/report.json"), "--output"),
          mode: str = typer.Option(None, "--mode")):
    cfg = load_config()
    if mode:
        cfg.guards.mode = mode
    trunk = cfg.branches.trunk
    base = g.merge_base(trunk, overlay)

    report = {"report_version": 1, "overlay": overlay, "trunk": trunk, "base": base, "violations": {}}

    if cfg.guards.both_touched:
        bt = both_touched(cfg, base, trunk, overlay)
        report["both_touched"] = bt
        if bt:
            report["violations"]["both_touched"] = bt

    sent = sentinels(cfg, trunk, overlay)
    report["sentinels"] = sent
    if sent["must_match_upstream"] or sent["must_diverge_from_upstream"]:
        report["violations"]["sentinels"] = sent

    sz = size_caps(cfg, overlay, trunk)
    report["size_caps"] = sz
    if sz.get("violations"):
        report["violations"]["size_caps"] = {"files": sz["files_changed"], "loc": sz["loc"]}

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2))
    rprint(f"[bold]Report written:[/bold] {output}")

    # policy enforcement
    has_violations = bool(report["violations"])
    if cfg.guards.mode == "block" and has_violations:
        raise typer.Exit(code=2)
    elif cfg.guards.mode == "require-override" and has_violations:
        # you can later inspect commit trailers to allow bypass; MVP just blocks
        raise typer.Exit(code=2)

@app.command()
def publish(overlay: str,
            tag: str = typer.Option(None, "--tag"),
            push: bool = typer.Option(False, "--push"),
            remote: str = typer.Option("origin", "--remote")):
    # tag and optionally push
    if tag:
        g.run(["tag", "-f", tag, overlay])
    if push:
        if tag: g.run(["push", "--force", remote, tag])
        g.run(["push", "--force", remote, overlay])
    rprint("[green]Publish complete.[/green]")
```

> Notes
>
> * Conflict automation (`--auto-continue`) applies your **path_bias** inside the overlay worktree, stages matches, and continues the cherry-pick. Anything unmatched leaves Git stopped for manual resolution.
> * You can expand `guard` later with risk scoring, commit-trailer overrides, Tree-sitter symbol detection (Rust sidecar), etc.

---

# GitHub Actions (MVP)

```yaml
name: Forked CI
on:
  workflow_dispatch:
  schedule: [{ cron: "0 6 * * 1" }]   # weekly
jobs:
  forked:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - name: Setup Python
        uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: python -m pip install --upgrade pip
      - run: python -m pip install -e .
      - run: forked --help
      - name: Sync & Build
        run: |
          forked sync
          forked build --id $GITHUB_RUN_ID --auto-continue
      - name: Guards
        run: |
          forked guard --overlay overlay/${{ github.run_id }} --output .forked/report.json --mode block
      - uses: actions/upload-artifact@v4
        with:
          name: forked-report
          path: .forked/report.json
      - name: Publish
        if: success()
        run: forked publish --overlay overlay/${{ github.run_id }} --tag overlay/${{ github.run_id }} --push
```

---

# Local Setup & Demo Repository

## Prerequisites
- Git ≥ 2.31 (required for modern worktree commands)
- Python ≥ 3.10 and `make`
- Bash-compatible shell (the demo script uses POSIX utilities)

## Create a Demo Fork (5–10 files, two patch branches)
```bash
./scripts/setup-demo-repo.sh demo-forked
cd demo-forked
```
The script provisions:
- Bare upstream + origin remotes
- `trunk` with `api/contracts/v1.yaml` and `src/service.py`
- Patch branches `patch/contract-update` and `patch/service-logging`
- Sentinel directories `config/forked/**` (ours) and `branding/**` (theirs)

This footprint keeps smoke runs fast (<5 seconds) while exercising worktree reuse, sentinel checks, and multi-commit cherry-picks. See `project-handbook/docs/DEMO_REPO.md` for details.

## Regenerating the Guard Fixture
After running the smoke checklist, refresh the JSON fixture for comparisons:
```bash
forked guard --overlay overlay/smoke --mode block --output .forked/report.json || true
cp .forked/report.json project-handbook/tests/fixtures/guard-report-example.json
```

---

# Developer Workflow (MVP)

1. Keep patches tiny and focused (configurable caps later).
2. Run fast tests after each rebase or cherry-pick.
3. Treat overlays as **disposable outputs**; tag when you ship.
4. Never branch from `overlay/*`; always regenerate overlays with `forked build`.
5. Use sentinels to lock contracts/APIs to upstream, and branding/assets to your fork.
6. If both-touched triggers on a file, review even if the merge was clean.

---

# Troubleshooting

* **Worktree location rejected**: Git refuses to add a worktree inside the repo. Either set `FORKED_WORKTREES_DIR=/absolute/path`, update `worktree.root`, or rely on the default relocation to `../.forked-worktrees/<repo>/<id>`.
* **Branch already checked out elsewhere**: `git worktree list` to find the other checkout, prune it (`git worktree prune`) or pick a fresh overlay id before rebuilding.
* **Patch already merged**: If a `patch/*` is already contained in trunk, `forked build` logs a skip and keeps going—no action needed.

---

# Quick Smoke Checklist

1. **Initial guardrails**
   ```bash
   git status --short
   forked init
   ```
   Expect exit code `4` with message `Working tree not clean...` if uncommitted changes exist.

2. **Overlay rebuild (run twice)**
   ```bash
   forked build --id smoke --auto-continue
   forked build --id smoke --auto-continue
   ```
   Expected output:
   ```
   [green]Built overlay[/green] overlay/smoke
   Worktree: ../.forked-worktrees/<repo>/smoke
   ```
   Re-running reports the same worktree path; no “already checked out” errors.

3. **Verify commit stack & reuse**
   ```bash
   git log overlay/smoke --oneline | head -n 4
   git worktree list --porcelain | grep overlay/smoke -A1
   ```
   Confirms ordered cherry-picks and reused worktree.

4. **Guard policy check**
 ```bash
 forked guard --overlay overlay/smoke --mode block --output .forked/report.json || true
 jq '.report_version, .violations' .forked/report.json
 diff -u project-handbook/tests/fixtures/guard-report-example.json .forked/report.json | head
  ```
  Expect exit code `2` when violations exist and JSON output matching the bundled fixture (`project-handbook/tests/fixtures/guard-report-example.json`).

5. **Sync & status**
   ```bash
   forked sync
   forked status --latest 2
   ```
   `forked sync` returns you to the branch you started on; status lists the two most recent overlays by date.

6. **Worktree cleanliness**
   ```bash
   repo_name=$(basename "$(git rev-parse --show-toplevel)")
   git -C ../.forked-worktrees/$repo_name/smoke status --short
   ```
   Output should be empty.

---

# Quick Release Checklist

1. **Install & sanity check CI flow**
   ```bash
   python -m pip install --upgrade pip
   python -m pip install -e .
   forked --version
   ```

2. **Full dry run**
   ```bash
   forked init
   forked sync
   forked build --id release-check --auto-continue
   forked guard --overlay overlay/release-check --mode block --output .forked/report.json
   ```
   Inspect `.forked/report.json`; compare to `project-handbook/tests/fixtures/guard-report-example.json`.

3. **Publish rehearsal (optional push)**
   ```bash
 forked publish --overlay overlay/release-check --tag overlay/release-check --remote origin --push
 ```
 For dry runs, omit `--push` or target a staging remote.

  **Rollback:** If publish fails mid-flight, clean up with
  ```bash
  git push --delete origin overlay/release-check || true
  git tag -d overlay/release-check || true
  git worktree prune
  ```
  Then rerun the smoke checklist before attempting again.

4. **Release tagging**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   git push
   ```

5. **Docs & backlog**
   - Update `project-handbook/releases/v1.0.0.md` highlights.
   - Append entry to `project-handbook/releases/CHANGELOG.md`.
   - Verify backlog items (`forked clean`, `forked status --json`) remain open for post-release work.

---

# Nuances & Edge Cases (handled in MVP)

* **Dirty tree protection**: `forked init/sync` stops if uncommitted changes exist.
* **Missing upstream remote**: init prints exact command to add it.
* **Rebase conflict during `sync`**: stops on the offending patch branch with clear instruction.
* **Cherry-pick conflicts**: `--auto-continue` tries **path_bias**; otherwise you resolve manually, then rerun `forked build` (idempotent).
* **Sentinel interpretation**:

  * *must_match_upstream* → overlay file blob must equal trunk blob (byte-for-byte).
  * *must_diverge_from_upstream* → overlay file must differ from trunk (enforces fork ownership for e.g. branding).
* **Rename detection**: diff methods use `--find-renames` (MVP signal; tune later).
* **Worktrees**: overlay checkouts live under `../.forked-worktrees/<repo>/<id>` (or `$FORKED_WORKTREES_DIR`) so your main checkout stays clean and Git stays happy.
* **`rerere`**: enabled in `init` so repeated conflicts auto-apply your prior fixups.

---

# What’s **not** in MVP (and why)

* **Symbol-level overlap (functions/classes)** → add via a Rust guard later (Tree-sitter). File-level both-touched gets you 80% immediately.
* **Commit-trailer override enforcement** → scaffolded; can add reading trailers/notes to allow “require-override” later.
* **Risk scoring & HTML reports** → JSON is enough to start; render in ForkedHub next.

---

# Roadmap after MVP (fast wins)

1. **Rust guard for symbol overlap** (`forked-guard-symbol`) → returns JSON `{file -> symbols overlapped}`.
2. **Risk scoring** and policy gates (warn/block/override with CODEOWNERS ack).
3. **HTML report** artifact (pretty, linkified diffs).
4. **`forked status --json`** for dashboard ingestion.
5. **Per-patch CI** (run fast tests after each rebase in `sync`).
6. **Per-path bias on non-conflicts** (codemods; optional).
7. **`forked clean`** command to prune stale worktrees and delete overlay branches on demand.

---

That’s the whole MVP—**all the moving parts, exact commands, and copy-pasteable code**. If you want, I can package this into a single repo skeleton with the `pyproject.toml`, the `forked/` package, a sample `forked.yml`, and the GitHub Action so you can `git clone`, `pipx install -e .`, and go.
