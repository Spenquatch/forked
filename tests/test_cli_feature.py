from pathlib import Path

import yaml
from typer.testing import CliRunner

from forked.cli import app
from forked.config import write_skeleton

runner = CliRunner()


def test_feature_create_updates_config_and_branches(git_repo, monkeypatch):
    monkeypatch.chdir(git_repo.path)
    write_skeleton()
    git_repo.git("add", "forked.yml")
    git_repo.git("commit", "-m", "add forked config")

    result = runner.invoke(app, ["feature", "create", "payments", "--slices", "2"])
    assert result.exit_code == 0, result.stdout

    data = yaml.safe_load(Path("forked.yml").read_text())
    assert data["features"]["payments"]["patches"] == [
        "patch/payments/01",
        "patch/payments/02",
    ]
    branches = git_repo.git("branch", "--list", capture_output=True).stdout
    assert "patch/payments/01" in branches
    assert "patch/payments/02" in branches

    status = runner.invoke(app, ["feature", "status"])
    assert status.exit_code == 0, status.stdout
    assert "payments" in status.stdout
    assert "merged" in status.stdout

    # Make the first slice diverge to verify ahead/behind reporting.
    git_repo.git("checkout", "patch/payments/01")
    git_repo.write("feature.txt", "feature work\n")
    git_repo.git("add", "feature.txt")
    git_repo.git("commit", "-m", "feature work")
    git_repo.git("checkout", "trunk")

    status_after = runner.invoke(app, ["feature", "status"])
    assert status_after.exit_code == 0, status_after.stdout
    assert "1 ahead / 0 behind" in status_after.stdout
