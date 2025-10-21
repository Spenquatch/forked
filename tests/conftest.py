import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import pytest


@dataclass
class GitRepo:
    path: Path

    def git(self, *args: str, check: bool = True, capture_output: bool = False):
        return subprocess.run(
            ["git", *args],
            cwd=self.path,
            check=check,
            text=True,
            capture_output=capture_output,
        )

    def write(self, relative: str, content: str):
        target = self.path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)


@pytest.fixture
def git_repo(tmp_path: Path) -> GitRepo:
    repo_path = tmp_path / "repo"
    repo_path.mkdir()
    subprocess.run(["git", "init"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.email", "ci@example.com"], cwd=repo_path, check=True)
    subprocess.run(["git", "config", "user.name", "CI"], cwd=repo_path, check=True)

    (repo_path / "README.md").write_text("initial\n")
    subprocess.run(["git", "add", "README.md"], cwd=repo_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=repo_path, check=True)
    subprocess.run(["git", "branch", "-M", "trunk"], cwd=repo_path, check=True)

    remote_path = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", str(remote_path)], check=True)
    subprocess.run(["git", "remote", "add", "upstream", str(remote_path)], cwd=repo_path, check=True)
    subprocess.run(["git", "push", "upstream", "trunk"], cwd=repo_path, check=True)

    return GitRepo(repo_path)
