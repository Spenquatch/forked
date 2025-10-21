import os
import time
from pathlib import Path

from typer.testing import CliRunner

from cli import app
from config import load_config, write_config, write_skeleton

runner = CliRunner()


def _configure_repo(git_repo, monkeypatch):
    monkeypatch.chdir(git_repo.path)
    write_skeleton()
    cfg = load_config()
    cfg.patches.order = ["patch/contract-update"]
    write_config(cfg)
    git_repo.git("add", "forked.yml")
    git_repo.git("commit", "-m", "add forked config")


def _create_overlay_branch(git_repo, name: str):
    git_repo.git("checkout", "-b", name)
    git_repo.git("commit", "--allow-empty", "-m", f"create {name}")
    git_repo.git("checkout", "trunk")


def test_clean_dry_run_skips_tagged_overlay(git_repo, monkeypatch):
    _configure_repo(git_repo, monkeypatch)
    _create_overlay_branch(git_repo, "overlay/tmp-old")
    _create_overlay_branch(git_repo, "overlay/tmp-keep")
    git_repo.git("tag", "-a", "keep-tag", "overlay/tmp-keep", "-m", "keep")

    result = runner.invoke(app, ["clean", "--overlays", "overlay/tmp-*"])
    assert result.exit_code == 0, result.stdout
    assert "delete overlay/tmp-old" in result.stdout
    assert "skip overlay/tmp-keep (tagged" in result.stdout
    assert "Dry-run mode; no changes made" in result.stdout


def test_clean_overlays_delete_when_confirmed(git_repo, monkeypatch):
    _configure_repo(git_repo, monkeypatch)
    _create_overlay_branch(git_repo, "overlay/tmp-old")
    git_repo.git("checkout", "-b", "overlay/tmp-keep")
    git_repo.git("commit", "--allow-empty", "-m", "keep")
    git_repo.git("checkout", "trunk")

    result = runner.invoke(
        app,
        ["clean", "--overlays", "overlay/tmp-*", "--no-dry-run", "--confirm"],
    )
    assert result.exit_code == 0, result.stdout
    assert "Cleanup complete" in result.stdout

    branches = git_repo.git(
        "branch", "--list", "overlay/tmp-old", capture_output=True
    ).stdout.strip()
    assert not branches

    log_path = Path(".forked/logs/clean.log")
    assert log_path.exists()
    assert "git branch -D overlay/tmp-old" in log_path.read_text()


def test_clean_respects_keep_window(git_repo, monkeypatch):
    _configure_repo(git_repo, monkeypatch)
    _create_overlay_branch(git_repo, "overlay/tmp-old")
    git_repo.git("checkout", "-b", "overlay/tmp-new")
    git_repo.git("commit", "--allow-empty", "-m", "new")
    git_repo.git("checkout", "trunk")

    result = runner.invoke(
        app,
        [
            "clean",
            "--overlays",
            "overlay/tmp-*",
            "--keep",
            "1",
            "--no-dry-run",
            "--confirm",
        ],
    )
    assert result.exit_code == 0, result.stdout

    remaining = git_repo.git(
        "branch", "--list", "overlay/tmp-new", capture_output=True
    ).stdout.strip()
    assert "overlay/tmp-new" in remaining


def test_clean_worktrees_prunes_stale_dir(git_repo, monkeypatch, tmp_path):
    _configure_repo(git_repo, monkeypatch)
    stale_dir = Path(".forked/worktrees/stale")
    stale_dir.mkdir(parents=True, exist_ok=True)

    result = runner.invoke(app, ["clean", "--worktrees", "--no-dry-run", "--confirm"])
    assert result.exit_code == 0, result.stdout
    assert not stale_dir.exists()


def test_clean_conflict_pruning(git_repo, monkeypatch):
    _configure_repo(git_repo, monkeypatch)
    conflicts_dir = Path(".forked/conflicts")
    conflicts_dir.mkdir(parents=True, exist_ok=True)
    old_json = conflicts_dir / "overlay-dev-1.json"
    old_json.write_text("{}")
    old_dir = conflicts_dir / "overlay-dev-1"
    old_dir.mkdir()
    latest_json = conflicts_dir / "overlay-dev-2.json"
    latest_json.write_text("{}")

    old_time = time.time() - (20 * 24 * 3600)
    os.utime(old_json, (old_time, old_time))
    os.utime(old_dir, (old_time, old_time))

    result = runner.invoke(app, ["clean", "--conflicts", "--no-dry-run", "--confirm"])
    assert result.exit_code == 0, result.stdout
    assert not old_json.exists()
    assert not old_dir.exists()
    assert latest_json.exists()
