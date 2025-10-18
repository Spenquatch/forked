"""Overlay build workflows."""

import json
import os
import re
from datetime import datetime, timezone
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

    repo = g.repo_root()
    base_root = Path(raw_root)
    if not base_root.is_absolute():
        base_root = (repo / base_root).resolve()
    else:
        base_root = base_root.resolve()
    candidate = base_root / overlay_id

    target = candidate
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
    applied_branches: List[dict] = []
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
        commit_details = []
        for sha in commits:
            summary = g.run(["show", "-s", "--format=%s", sha]).stdout.strip()
            commit_details.append({"sha": sha, "summary": summary})
        applied_branches.append(
            {
                "branch": branch,
                "commit_count": len(commit_details),
                "commits": commit_details,
            }
        )
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

    repo = g.repo_root()
    logs_dir = repo / ".forked" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    if applied_branches:
        typer.echo("[build] Applied patches:")
        for entry in applied_branches:
            count = entry["commit_count"]
            commits_preview = entry["commits"][:3]
            preview_text = ", ".join(f"{c['sha'][:7]} {c['summary']}" for c in commits_preview)
            remaining = count - len(commits_preview)
            if remaining > 0:
                preview_text += f", … +{remaining}"
            plural = "s" if count != 1 else ""
            typer.echo(f"  • {entry['branch']} (+{count} commit{plural}): {preview_text}")
    else:
        typer.echo("[build] No patches applied; overlay matches trunk.")

    telemetry = {
        "event": "forked.build",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overlay": overlay,
        "worktree": str(wt_path),
        "reused_worktree": bool(wt_existing),
        "patches": applied_branches,
        "trunk": cfg.branches.trunk,
        "upstream": f"{cfg.upstream.remote}/{cfg.upstream.branch}",
    }
    log_path = logs_dir / "forked-build.log"
    with log_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(telemetry) + "\n")
    return overlay, wt_path
