"""Lightweight Git helpers for Forked CLI."""

from pathlib import Path
import subprocess as sp
from typing import List, Optional
import typer


def run(args: List[str], cwd: Optional[str] = None, check: bool = True) -> sp.CompletedProcess:
    """Run a git command and return the completed process."""
    return sp.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=check,
    )


def ensure_clean():
    """Ensure the current repository has no staged or unstaged changes."""
    out = run(["status", "--porcelain"], check=True).stdout.strip()
    if out:
        typer.echo("[git] Working tree not clean. Commit or stash first.")
        raise typer.Exit(code=4)


def has_remote(name: str) -> bool:
    """Return True if the specified remote exists."""
    remotes = run(["remote"]).stdout.splitlines()
    return name in remotes


def merge_base(a: str, b: str) -> str:
    """Compute merge base between two refs."""
    return run(["merge-base", a, b]).stdout.strip()


def changed_paths(a: str, b: str) -> list[str]:
    """List paths changed between two refs."""
    out = run(["diff", "--name-only", "--find-renames", f"{a}...{b}"]).stdout
    return sorted(p for p in out.splitlines() if p)


def blob_hash(ref: str, path: str) -> Optional[str]:
    """Return the blob hash for ``path`` at ``ref`` (or None if absent)."""
    cp = run(["ls-tree", ref, "--", path], check=False)
    if cp.returncode != 0 or not cp.stdout.strip():
        return None
    parts = cp.stdout.split()
    return parts[2] if len(parts) >= 3 else None


def current_ref() -> str:
    """Return the current checked out branch/reference."""
    return run(["rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()


def repo_root() -> Path:
    """Return the repository root path."""
    return Path(run(["rev-parse", "--show-toplevel"]).stdout.strip())


def worktree_for_branch(branch: str) -> Optional[Path]:
    """Return the path of an existing worktree that has ``branch`` checked out."""
    out = run(["worktree", "list", "--porcelain"]).stdout.splitlines()
    cur_path = None
    for line in out:
        if line.startswith("worktree "):
            cur_path = line.split(" ", 1)[1]
        elif line.startswith("branch "):
            ref = line.split(" ", 1)[1]
            if ref == f"refs/heads/{branch}":
                return Path(cur_path)
    return None
