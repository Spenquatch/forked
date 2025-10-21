from pathlib import Path
import json

import yaml
from typer.testing import CliRunner

from forked.cli import app


def _configure_forked(repo_path: Path, patches: list[str]) -> None:
    config_path = repo_path / "forked.yml"
    data = yaml.safe_load(config_path.read_text())
    data["upstream"]["branch"] = "trunk"
    data["patches"]["order"] = patches
    data["guards"]["sentinels"]["must_match_upstream"] = ["app.py"]
    data["features"] = {
        "conflict_feature": {
            "patches": patches,
            "sentinels": {
                "must_match_upstream": ["app.py"],
                "must_diverge_from_upstream": [],
            },
        }
    }
    data["overlays"] = {"dev": {"features": ["conflict_feature"]}}
    config_path.write_text(yaml.safe_dump(data, sort_keys=False))


def test_conflict_bundle_v2_build(git_repo, monkeypatch):
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

    _configure_forked(Path.cwd(), ["patch/conflict"])
    Path(".gitignore").write_text(".forked/\\n")
    git_repo.git("add", "forked.yml", ".gitignore")
    git_repo.git("commit", "-m", "configure forked")

    result = runner.invoke(
        app,
        [
            "build",
            "--features",
            "conflict_feature",
            "--id",
            "test",
            "--emit-conflicts",
            ".forked/conflicts/test",
            "--on-conflict",
            "stop",
        ],
        catch_exceptions=False,
    )
    assert result.exit_code == 10

    bundle_path = Path(".forked/conflicts/test-1.json")
    assert bundle_path.exists()
    bundle = json.loads(bundle_path.read_text())
    assert bundle["schema_version"] == 2
    assert bundle["wave"] == 1
    assert bundle["context"]["mode"] == "build"
    assert bundle["context"]["patch_branch"] == "patch/conflict"
    assert bundle["resume"]["continue"] == "git cherry-pick --continue"
    file_entry = bundle["files"][0]
    assert file_entry["precedence"]["recommended"] == "ours"
    assert file_entry["binary"] is False

    log_lines = Path(".forked/logs/forked-build.log").read_text().splitlines()
    log_entry = json.loads(log_lines[-1])
    assert log_entry["event"] == "forked.build"
    assert log_entry["status"] == "conflict"
    assert log_entry["conflicts"][0]["bundle"].endswith("test-1.json")
