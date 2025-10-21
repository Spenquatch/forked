import json
from pathlib import Path

from typer.testing import CliRunner

from forked.cli import app
from forked.config import Feature, OverlayProfile, load_config, write_config, write_skeleton

runner = CliRunner(mix_stderr=False)


def _prepare_repo(git_repo, monkeypatch):
    monkeypatch.chdir(git_repo.path)
    write_skeleton()
    cfg = load_config()
    cfg.upstream.branch = "trunk"
    cfg.patches.order = ["patch/contract-update"]
    cfg.features = {"contract_update": Feature(patches=["patch/contract-update"])}
    cfg.overlays = {"dev": OverlayProfile(features=["contract_update"])}
    cfg.guards.sentinels.must_match_upstream = ["api/contracts/**"]
    cfg.policy_overrides.require_trailer = False
    write_config(cfg)
    git_repo.git("add", "forked.yml")
    git_repo.git("commit", "-m", "configure forked")

    git_repo.write("api/contracts/service.yaml", "base\n")
    git_repo.git("add", "api/contracts/service.yaml")
    git_repo.git("commit", "-m", "add contract")
    git_repo.git("push", "upstream", "trunk")

    git_repo.git("checkout", "-b", "patch/contract-update")
    git_repo.write("api/contracts/service.yaml", "base\nfeature change\n")
    git_repo.git("commit", "-am", "feature change")
    git_repo.git("checkout", "trunk")
    git_repo.git("push", "upstream", "patch/contract-update")

    build = runner.invoke(app, ["build", "--overlay", "dev", "--no-worktree"])
    assert build.exit_code == 0, build.stdout


def test_report_includes_features_from_provenance(git_repo, monkeypatch):
    _prepare_repo(git_repo, monkeypatch)

    result = runner.invoke(app, ["guard", "--overlay", "overlay/dev", "--mode", "warn"])
    assert result.exit_code == 0, result.stdout

    payload = json.loads(Path(".forked/report.json").read_text())
    assert payload["report_version"] == 2
    assert payload["features"]["values"] == ["contract_update"]
    assert payload["features"]["source"] == "provenance-log"
    assert payload["override"]["source"] == "none"


def test_report_uses_resolver_when_provenance_missing(git_repo, monkeypatch):
    _prepare_repo(git_repo, monkeypatch)

    log_path = Path(".forked/logs/forked-build.log")
    if log_path.exists():
        backup = Path(".forked/logs/forked-build.log.bak")
        backup.write_text(log_path.read_text())
        log_path.unlink()
    else:
        backup = None

    git_repo.git(
        "notes",
        "--ref",
        "refs/notes/forked-meta",
        "remove",
        "overlay/dev",
        check=False,
    )

    result = runner.invoke(app, ["guard", "--overlay", "overlay/dev", "--mode", "warn"])
    assert result.exit_code == 0, result.stdout

    payload = json.loads(Path(".forked/report.json").read_text())
    assert payload["features"]["source"] == "derived"
    assert payload["features"]["values"] == ["contract_update"]

    if backup:
        log_path.write_text(backup.read_text())
        backup.unlink()
