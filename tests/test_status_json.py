import json
from pathlib import Path

from typer.testing import CliRunner

from cli import app
from config import Feature, load_config, write_config, write_skeleton

runner = CliRunner()


def _prepare_status_repo(git_repo):
    write_skeleton()
    cfg = load_config()
    cfg.upstream.branch = "trunk"
    cfg.patches.order = ["patch/payments/01"]
    cfg.features = {"payments": Feature(patches=["patch/payments/01"])}
    write_config(cfg)
    git_repo.git("add", "forked.yml")
    git_repo.git("commit", "-m", "add forked config")

    git_repo.write("shared.txt", "base\n")
    git_repo.git("add", "shared.txt")
    git_repo.git("commit", "-m", "add shared file")
    git_repo.git("push", "upstream", "trunk")

    git_repo.git("checkout", "-b", "patch/payments/01")
    git_repo.write("shared.txt", "base\nfeature change\n")
    git_repo.git("commit", "-am", "feature change")
    git_repo.git("checkout", "trunk")

    build = runner.invoke(app, ["build", "--id", "dev", "--no-worktree"])
    assert build.exit_code == 0, build.stdout
    git_repo.git("checkout", "trunk")


def test_status_json_includes_provenance(git_repo, monkeypatch):
    monkeypatch.chdir(git_repo.path)
    _prepare_status_repo(git_repo)
    assert Path.cwd() == git_repo.path
    assert Path("forked.yml").exists()

    result = runner.invoke(app, ["status", "--json"])
    assert result.exit_code == 0, result.stdout

    payload = json.loads(result.stdout)
    assert payload["status_version"] == 1
    assert payload["upstream"]["remote"] == "upstream"
    assert payload["trunk"]["name"] == "trunk"

    patches = {entry["name"]: entry for entry in payload["patches"]}
    assert patches["patch/payments/01"]["ahead"] == 1
    assert patches["patch/payments/01"]["behind"] == 0

    overlays = payload["overlays"]
    assert len(overlays) == 1
    overlay = overlays[0]
    assert overlay["name"] == "overlay/dev"
    assert overlay["selection"]["source"] == "provenance-log"
    assert overlay["selection"]["features"] == ["payments"]
    assert overlay["selection"]["patches"] == ["patch/payments/01"]
    assert overlay["both_touched_count"] is None
    assert overlay["built_at"].endswith("Z")


def test_status_json_reflects_guard_report(git_repo, monkeypatch):
    monkeypatch.chdir(git_repo.path)
    _prepare_status_repo(git_repo)

    initial = runner.invoke(app, ["status", "--json"])
    payload = json.loads(initial.stdout)
    assert payload["overlays"][0]["both_touched_count"] is None

    guard = runner.invoke(app, ["guard", "--overlay", "overlay/dev"])
    assert guard.exit_code == 0, guard.stdout

    after_guard = runner.invoke(app, ["status", "--json"])
    guard_payload = json.loads(after_guard.stdout)
    assert guard_payload["overlays"][0]["both_touched_count"] == 0


def test_status_json_derives_selection_without_provenance(git_repo, monkeypatch):
    monkeypatch.chdir(git_repo.path)
    _prepare_status_repo(git_repo)

    repo_root = Path(git_repo.path)
    log_path = repo_root / ".forked" / "logs" / "forked-build.log"
    if log_path.exists():
        log_path.unlink()
    git_repo.git("notes", "--ref", "refs/notes/forked-meta", "remove", "overlay/dev", check=False)

    derived = runner.invoke(app, ["status", "--json"])
    assert derived.exit_code == 0, derived.stdout

    payload = json.loads(derived.stdout)
    overlay = payload["overlays"][0]
    assert overlay["selection"]["source"] == "derived"
    assert overlay["selection"]["patches"] == ["patch/payments/01"]
    assert overlay["selection"]["features"] == ["payments"]
