"""Lightweight Git helpers for Forked CLI."""

import subprocess as sp
from pathlib import Path

import typer


def run(args: list[str], cwd: str | None = None, check: bool = True) -> sp.CompletedProcess:
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
        typer.echo("[forked] Current forked working tree is not clean. Commit or stash first.")
        staged: list[str] = []
        unstaged: list[str] = []
        untracked: list[str] = []
        for line in out.splitlines():
            if line.startswith("??"):
                untracked.append(line[3:])
            else:
                staged_flag, unstaged_flag = line[0], line[1]
                path = line[3:]
                if staged_flag != " ":
                    staged.append(path)
                if unstaged_flag != " ":
                    unstaged.append(path)

        if staged:
            typer.echo("[git] Staged changes:")
            for path in staged:
                typer.secho(f"  {path}", fg=typer.colors.GREEN)
        if unstaged:
            typer.echo("[git] Unstaged changes:")
            for path in unstaged:
                typer.secho(f"  {path}", fg=typer.colors.RED)
        if untracked:
            typer.echo("[git] Untracked files:")
            for path in untracked:
                typer.secho(f"  {path}", fg=typer.colors.RED)
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


def blob_hash(ref: str, path: str) -> str | None:
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


def worktree_for_branch(branch: str) -> Path | None:
    """Return the path of an existing worktree that has ``branch`` checked out."""
    out = run(["worktree", "list", "--porcelain"]).stdout.splitlines()
    cur_path = None
    for line in out:
        if line.startswith("worktree "):
            cur_path = line.split(" ", 1)[1]
        elif line.startswith("branch "):
            ref = line.split(" ", 1)[1]
            if ref == f"refs/heads/{branch}" and cur_path is not None:
                return Path(cur_path)
    return None
