from pathlib import Path

from forked.build import _upstream_equivalent_commits, build_overlay
from forked.resolver import resolve_selection

from .test_build_provenance import _make_config, _prepare_feature_branch


def test_skip_upstream_equivalents_omits_duplicate_commits(git_repo, monkeypatch):
    monkeypatch.chdir(git_repo.path)
    _prepare_feature_branch(git_repo)

    cfg = _make_config()
    selection = resolve_selection(cfg, overlay="dev")

    skip = _upstream_equivalent_commits("trunk", "patch/payments/01")
    assert skip, "expected to detect upstream-equivalent commits"

    _, _, telemetry = build_overlay(
        cfg,
        overlay_id="skip-test",
        selection=selection,
        use_worktree=False,
        skip_upstream_equivalents=True,
        write_git_note=False,
    )

    patch_entry = telemetry["patches"][0]
    assert patch_entry["commit_count"] == 1
    assert patch_entry["skipped_count"] == 1
    assert len(patch_entry["skipped_commits"]) == 1

    overlay_branch = telemetry["overlay"]
    overlay_tip = Path(".git") / "refs" / "heads" / overlay_branch
    assert overlay_tip.exists()
