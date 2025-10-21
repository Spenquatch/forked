import json
from pathlib import Path

from build import build_overlay
from config import Config, Feature, OverlayProfile
from resolver import resolve_selection


def _prepare_feature_branch(git_repo):
    # Create feature branch with one unique commit and one commit matching trunk.
    git_repo.git("checkout", "-b", "patch/payments/01")
    git_repo.write("unique.txt", "unique\n")
    git_repo.git("add", "unique.txt")
    git_repo.git("commit", "-m", "unique feature work")

    git_repo.git("checkout", "trunk")
    git_repo.write("shared.txt", "shared\n")
    git_repo.git("add", "shared.txt")
    git_repo.git("commit", "-m", "shared change")
    shared_sha = git_repo.git("rev-parse", "trunk", capture_output=True).stdout.strip()
    git_repo.git("push", "upstream", "trunk")

    git_repo.git("checkout", "patch/payments/01")
    git_repo.git("cherry-pick", shared_sha)
    git_repo.git("checkout", "trunk")


def _make_config() -> Config:
    cfg = Config()
    cfg.patches.order = ["patch/payments/01"]
    cfg.features = {"payments": Feature(patches=["patch/payments/01"])}
    cfg.overlays = {"dev": OverlayProfile(features=["payments"])}
    cfg.worktree.enabled = False
    cfg.upstream.branch = "trunk"
    return cfg


def test_build_overlay_logs_selection_and_features(git_repo, monkeypatch):
    monkeypatch.chdir(git_repo.path)
    _prepare_feature_branch(git_repo)

    cfg = _make_config()
    selection = resolve_selection(cfg, overlay="dev")

    overlay_branch, worktree, telemetry = build_overlay(
        cfg,
        overlay_id="dev",
        selection=selection,
        use_worktree=False,
        skip_upstream_equivalents=True,
        write_git_note=False,
    )

    assert overlay_branch == f"{cfg.branches.overlay_prefix}dev"
    assert worktree == Path.cwd() / ".overlay-dev"
    assert telemetry["selection"]["features"] == ["payments"]
    assert telemetry["selection"]["patches"] == ["patch/payments/01"]
    assert telemetry["selection"]["skip_upstream_equivalents"] is True

    log_path = Path(".forked/logs/forked-build.log")
    assert log_path.exists()
    entries = [json.loads(line) for line in log_path.read_text().splitlines() if line.strip()]
    assert entries[-1]["overlay"] == overlay_branch
    assert entries[-1]["selection"]["features"] == ["payments"]

    # Ensure we return to trunk for subsequent operations.
    git_repo.git("checkout", "trunk")
