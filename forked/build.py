"""Overlay build workflows."""

import json
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple
import typer
from pathspec import PathSpec
from .config import Config
from . import gitutil as g


def _conflict_paths(cwd: Optional[str] = None) -> list[str]:
    out = g.run(["status", "--porcelain"], cwd=cwd).stdout.splitlines()
    return [line.split()[-1] for line in out if line.startswith(("U", "AA", "DD", "DU", "UD"))]


def _apply_path_bias(cfg: Config, cwd: Optional[str] = None) -> bool:
    ours = PathSpec.from_lines("gitwildmatch", cfg.path_bias.ours or [])
    theirs = PathSpec.from_lines("gitwildmatch", cfg.path_bias.theirs or [])
    conflicted = _conflict_paths(cwd)
    applied = False
    for path in conflicted:
        if ours.match_file(path):
            g.run(["checkout", "--ours", "--", path], cwd=cwd)
            g.run(["add", path], cwd=cwd)
            applied = True
        elif theirs.match_file(path):
            g.run(["checkout", "--theirs", "--", path], cwd=cwd)
            g.run(["add", path], cwd=cwd)
            applied = True
    return applied


WINDOWS_ABS_PATTERN = re.compile(r"^[A-Za-z]:[\\/]")


def _looks_like_windows_absolute(raw: str) -> bool:
    return bool(WINDOWS_ABS_PATTERN.match(raw))


def _resolve_worktree_dir(cfg: Config, overlay_id: str) -> Path:
    root_override = os.environ.get("FORKED_WORKTREES_DIR")
    raw_root = root_override or cfg.worktree.root

    if _looks_like_windows_absolute(raw_root):
        if os.name != "nt":
            typer.echo(
                "[build] Provided worktree root looks like a Windows path but the current platform "
                "is POSIX. Set $FORKED_WORKTREES_DIR to an absolute POSIX path instead."
            )
            raise typer.Exit(code=4)

    base_root = Path(raw_root)
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

    if target.exists():
        typer.echo(
            f"[build] Worktree directory '{target}' already exists; suffixing. "
            "Run 'git worktree prune' to clean up stale entries."
        )
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
    return [rev for rev in revs if rev]


def build_overlay(
    cfg: Config,
    overlay_id: str,
    use_worktree: bool = True,
    auto_continue: bool = False,
) -> Tuple[str, Path]:
    g.run(["fetch", cfg.upstream.remote])
    prev_ref = g.current_ref()
    g.run(["checkout", "-B", cfg.branches.trunk, f"{cfg.upstream.remote}/{cfg.upstream.branch}"])

    overlay = f"{cfg.branches.overlay_prefix}{overlay_id}"
    wt_existing: Optional[Path] = None
    applied_commits: List[dict] = []
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

    for branch in cfg.patches.order:
        base = g.merge_base(cfg.branches.trunk, branch)
        commits = _rev_list_range(base, branch)
        if not commits:
            typer.echo(f"[build] {branch} already contained in {cfg.branches.trunk}; skipping")
            continue
        applied_commits.append({"branch": branch, "commits": commits})
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

    if use_worktree and cfg.worktree.enabled and prev_ref:
        g.run(["checkout", prev_ref])

    telemetry = {
        "event": "forked.build",
        "overlay": overlay,
        "worktree": str(wt_path),
        "reused_worktree": bool(wt_existing),
        "patches": applied_commits,
    }
    typer.echo(f"[build.log] {json.dumps(telemetry)}")
    return overlay, wt_path
