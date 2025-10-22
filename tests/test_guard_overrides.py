import json
from pathlib import Path

from typer.testing import CliRunner

from cli import app
from config import Feature, OverlayProfile, load_config, write_config, write_skeleton

runner = CliRunner()


def _prepare_guard_repo(git_repo, monkeypatch, *, allowed_values=None):
    monkeypatch.chdir(git_repo.path)
    write_skeleton()
    cfg = load_config()
    cfg.upstream.branch = "trunk"
    cfg.patches.order = ["patch/contract-update"]
    cfg.features = {"contract_update": Feature(patches=["patch/contract-update"])}
    cfg.overlays = {"dev": OverlayProfile(features=["contract_update"])}
    cfg.guards.sentinels.must_match_upstream = ["api/contracts/**"]
    cfg.policy_overrides.require_trailer = True
    cfg.policy_overrides.allowed_values = allowed_values or [
        "sentinel",
        "size",
        "both_touched",
        "all",
    ]
    write_config(cfg)
    git_repo.git("add", "forked.yml")
    git_repo.git("commit", "-m", "configure forked")

    # Base file tracked on trunk
    git_repo.write("api/contracts/service.yaml", "base\n")
    git_repo.git("add", "api/contracts/service.yaml")
    git_repo.git("commit", "-m", "add contract")
    git_repo.git("push", "upstream", "trunk")

    # Patch diverges from trunk
    git_repo.git("checkout", "-b", "patch/contract-update")
    git_repo.write("api/contracts/service.yaml", "base\nfeature change\n")
    git_repo.git("commit", "-am", "feature change")
    git_repo.git("checkout", "trunk")

    git_repo.git("push", "upstream", "patch/contract-update")

    result = runner.invoke(app, ["build", "--overlay", "dev", "--no-worktree"])
    assert result.exit_code == 0, result.stdout


def test_require_override_without_marker_fails(git_repo, monkeypatch):
    _prepare_guard_repo(git_repo, monkeypatch)

    result = runner.invoke(app, ["guard", "--overlay", "overlay/dev", "--mode", "require-override"])
    assert result.exit_code == 2
    assert "[guard] Override required" in result.output


def test_commit_override_allows_violation(git_repo, monkeypatch):
    _prepare_guard_repo(git_repo, monkeypatch)

    initial = runner.invoke(
        app, ["guard", "--overlay", "overlay/dev", "--mode", "require-override"]
    )
    assert initial.exit_code == 2

    git_repo.git("checkout", "overlay/dev")
    git_repo.git(
        "commit",
        "--allow-empty",
        "-m",
        "override commit\n\nForked-Override: sentinel",
    )
    git_repo.git("checkout", "trunk")

    result = runner.invoke(app, ["guard", "--overlay", "overlay/dev", "--mode", "require-override"])
    assert result.exit_code == 0, result.stdout

    payload = json.loads(Path(".forked/report.json").read_text())
    assert payload["report_version"] == 2
    assert payload["override"]["source"] == "commit"
    assert payload["override"]["values"] == ["sentinel"]
    assert payload["override"]["applied"] is True
    assert payload["features"]["values"] == ["contract_update"]


def test_disallowed_override_scope_fails(git_repo, monkeypatch):
    _prepare_guard_repo(git_repo, monkeypatch, allowed_values=["size"])

    git_repo.git("checkout", "overlay/dev")
    git_repo.git(
        "commit",
        "--allow-empty",
        "-m",
        "override commit\n\nForked-Override: sentinel",
    )
    git_repo.git("checkout", "trunk")

    result = runner.invoke(app, ["guard", "--overlay", "overlay/dev", "--mode", "require-override"])
    assert result.exit_code == 2
    assert "not permitted" in result.output


def test_tag_override_used_when_commit_missing(git_repo, monkeypatch):
    _prepare_guard_repo(git_repo, monkeypatch)

    failure = runner.invoke(
        app, ["guard", "--overlay", "overlay/dev", "--mode", "require-override"]
    )
    assert failure.exit_code == 2

    git_repo.git("tag", "-a", "override-tag", "overlay/dev", "-m", "Forked-Override: sentinel")

    result = runner.invoke(app, ["guard", "--overlay", "overlay/dev", "--mode", "require-override"])
    assert result.exit_code == 0

    payload = json.loads(Path(".forked/report.json").read_text())
    assert payload["override"]["source"] == "tag"
    assert payload["override"]["values"] == ["sentinel"]


def test_note_override_fallback(git_repo, monkeypatch):
    _prepare_guard_repo(git_repo, monkeypatch)

    _ = runner.invoke(app, ["guard", "--overlay", "overlay/dev", "--mode", "require-override"])

    note_path = Path("override-note.txt")
    note_path.write_text("Forked-Override: sentinel\n")
    git_repo.git(
        "notes",
        "--ref",
        "refs/notes/forked/override",
        "add",
        "-F",
        str(note_path),
        "overlay/dev",
    )
    note_path.unlink()

    result = runner.invoke(app, ["guard", "--overlay", "overlay/dev", "--mode", "require-override"])
    assert result.exit_code == 0

    payload = json.loads(Path(".forked/report.json").read_text())
    assert payload["override"]["source"] == "note"
    assert payload["override"]["values"] == ["sentinel"]
