import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from cli import app


def _configure_sync(repo_path: Path, patch_branch: str) -> None:
    config_path = repo_path / "forked.yml"
    data = yaml.safe_load(config_path.read_text())
    data["upstream"]["branch"] = "trunk"
    data["patches"]["order"] = [patch_branch]
    data["guards"]["sentinels"]["must_match_upstream"] = ["app.py"]
    data["features"] = {
        "conflict_feature": {
            "patches": [patch_branch],
            "sentinels": {
                "must_match_upstream": ["app.py"],
                "must_diverge_from_upstream": [],
            },
        }
    }
    config_path.write_text(yaml.safe_dump(data, sort_keys=False))


def test_sync_conflict_auto_continue(git_repo, monkeypatch):
    monkeypatch.chdir(git_repo.path)
    runner = CliRunner()

    app_path = Path("app.py")
    app_path.write_text("print('base')\\n")
    git_repo.git("add", "app.py")
    git_repo.git("commit", "-m", "add app")
    git_repo.git("push", "upstream", "trunk")

    git_repo.git("checkout", "-b", "patch/conflict")
    app_path.write_text("print('feature change')\\n")
    git_repo.git("commit", "-am", "feature change")
    git_repo.git("push", "upstream", "patch/conflict")

    git_repo.git("checkout", "trunk")
    app_path.write_text("print('upstream change')\\n")
    git_repo.git("commit", "-am", "upstream change")
    git_repo.git("push", "upstream", "trunk")

    result = runner.invoke(app, ["init", "--upstream-branch", "trunk"], catch_exceptions=False)
    assert result.exit_code == 0

    _configure_sync(Path.cwd(), "patch/conflict")
    Path(".gitignore").write_text(".forked/\\n")
    git_repo.git("add", "forked.yml", ".gitignore")
    git_repo.git("commit", "-m", "configure forked")

    result = runner.invoke(
        app,
        [
            "sync",
            "--emit-conflicts-path",
            ".forked/conflicts/sync",
            "--on-conflict",
            "bias",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 0

    bundle_path = Path(".forked/conflicts/sync-1.json")
    assert bundle_path.exists()
    bundle = json.loads(bundle_path.read_text())
    assert bundle["schema_version"] == 2
    assert bundle["context"]["mode"] == "sync"
    assert bundle["files"][0]["precedence"]["recommended"] == "ours"

    log_lines = Path(".forked/logs/forked-build.log").read_text().splitlines()
    log_entry = json.loads(log_lines[-1])
    assert log_entry["event"] == "forked.sync"
    assert log_entry["status"] == "success"
    assert log_entry["conflicts"][0]["result"] == "auto-continued"
