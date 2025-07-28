import toml
import typer
import os
import re
import shutil
import subprocess

from git import Repo as GitRepo
from pathlib import Path

URL_PATTERN = re.compile(r"git\+ssh://(?:[^@]+@)?([^/]+)/([^@]+)")
BRANCH_PATTERN = re.compile(
    r"git\+ssh://git@github\.com/[^/]+/[^@]+@([a-zA-Z0-9_\-\.]+)\b"
)


class Repo:
    """
    Repo is a class that manages repository operations such as cloning, updating,
    and checking the status of repositories defined in a configuration file.
    It provides methods to handle various repository-related tasks.
    """

    def __init__(self, pyproject_file: Path = Path("pyproject.toml")):
        self.pyproject_file = pyproject_file
        self.config = self._load_config()
        self.path = Path(self.config["tool"]["django_mongodb_cli"]["path"])
        self.map = self.get_map()
        self.branch = None

    def _load_config(self) -> dict:
        return toml.load(self.pyproject_file)

    def clone_repo(self, repo_name: str) -> None:
        """
        Clone a repository into the specified path.
        If the repository already exists, it will skip cloning.
        """
        typer.echo(
            typer.style(f"Cloning repository: {repo_name}", fg=typer.colors.CYAN)
        )

        if repo_name not in self.map:
            typer.echo(
                typer.style(
                    f"Repository '{repo_name}' not found in configuration.",
                    fg=typer.colors.RED,
                )
            )
            return

        url = self.map[repo_name]
        path = self.get_repo_path(repo_name)
        branch = (
            BRANCH_PATTERN.search(url).group(1)
            if BRANCH_PATTERN.search(url)
            else "main"
        )
        url = URL_PATTERN.search(url).group(0)
        if os.path.exists(path):
            typer.echo(
                typer.style(
                    f"Repository '{repo_name}' already exists at path: {path}",
                    fg=typer.colors.YELLOW,
                )
            )
            return

        typer.echo(
            typer.style(
                f"Cloning {url} into {path} (branch: {branch})", fg=typer.colors.CYAN
            )
        )
        GitRepo.clone_from(url, path, branch=branch)

        # Install pre-commit hooks if config exists
        pre_commit_config = os.path.join(path, ".pre-commit-config.yaml")
        if os.path.exists(pre_commit_config):
            typer.echo(
                typer.style("Installing pre-commit hooks...", fg=typer.colors.CYAN)
            )
            try:
                subprocess.run(["pre-commit", "install"], cwd=path, check=True)
                typer.echo(
                    typer.style("Pre-commit hooks installed!", fg=typer.colors.GREEN)
                )
            except subprocess.CalledProcessError as e:
                typer.echo(
                    typer.style(
                        f"Failed to install pre-commit hooks for {repo_name}: {e}",
                        fg=typer.colors.RED,
                    )
                )
        else:
            typer.echo(
                typer.style(
                    "No .pre-commit-config.yaml found. Skipping pre-commit hook installation.",
                    fg=typer.colors.YELLOW,
                )
            )

    def delete_repo(self, repo_name: str) -> None:
        """
        Delete the specified repository.
        """
        typer.echo(
            typer.style(f"Deleting repository: {repo_name}", fg=typer.colors.CYAN)
        )

        path = self.get_repo_path(repo_name)
        if not os.path.exists(path):
            typer.echo(
                typer.style(
                    f"Repository '{repo_name}' not found at path: {path}",
                    fg=typer.colors.RED,
                )
            )
            return

        try:
            shutil.rmtree(path)
            typer.echo(
                typer.style(
                    f"✅ Successfully deleted {repo_name}.", fg=typer.colors.GREEN
                )
            )
        except Exception as e:
            typer.echo(
                typer.style(
                    f"❌ Failed to delete {repo_name}: {e}", fg=typer.colors.RED
                )
            )

    def get_map(self) -> dict:
        """
        Return a dict mapping repo_name to repo_url from repos in
        [tool.django_mongodb_cli.repos].
        """
        return {
            repo.split("@", 1)[0].strip(): repo.split("@", 1)[1].strip()
            for repo in self.config["tool"]["django_mongodb_cli"].get("repos", [])
            if "@" in repo
        }

    def get_repo_branches(self, repo_name: str) -> list:
        """
        Get a list of both local and remote branches for the specified repository.
        Optionally, if self.branch is set, switch to it (existing) or create new (checkout -b).
        """
        typer.echo(
            typer.style(
                f"Getting branches for repository: {repo_name}", fg=typer.colors.CYAN
            )
        )

        path = self.get_repo_path(repo_name)
        if not os.path.exists(path):
            typer.echo(
                typer.style(
                    f"Repository '{repo_name}' not found at path: {path}",
                    fg=typer.colors.RED,
                )
            )
            return []

        repo = self.get_repo(path)

        # Get local branches
        local_branches = [branch.name for branch in repo.branches]

        # Get remote branches; skip HEAD pointer
        remote_branches = [
            ref.name.replace("origin/", "")
            for ref in repo.remotes.origin.refs
            if ref.name != "origin/HEAD"
        ]

        # Merge, deduplicate, and sort
        all_branches = sorted(set(local_branches + remote_branches))

        typer.echo(
            typer.style(
                f"Branches in {repo_name}: {', '.join(all_branches)}",
                fg=typer.colors.GREEN,
            )
        )

        if getattr(self, "branch", None):
            if self.branch in local_branches:
                typer.echo(
                    typer.style(
                        f"Checking out existing branch '{self.branch}'",
                        fg=typer.colors.YELLOW,
                    )
                )
                repo.git.checkout(self.branch)
            else:
                typer.echo(
                    typer.style(
                        f"Branch '{self.branch}' does not exist. Creating and checking out new branch.",
                        fg=typer.colors.YELLOW,
                    )
                )
                repo.git.checkout("-b", self.branch)

        return all_branches

    def get_repo_origin(self, repo_name: str) -> str:
        """
        Get the origin URL of the specified repository.
        """
        typer.echo(
            typer.style(
                f"Getting origin for repository: {repo_name}", fg=typer.colors.CYAN
            )
        )

        path = self.get_repo_path(repo_name)
        if not os.path.exists(path):
            typer.echo(
                typer.style(
                    f"Repository '{repo_name}' not found at path: {path}",
                    fg=typer.colors.RED,
                )
            )
            return ""

        repo = self.get_repo(path)
        origin_url = repo.remotes.origin.url
        typer.echo(
            typer.style(
                f"Origin URL for {repo_name}: {origin_url}", fg=typer.colors.GREEN
            )
        )
        return origin_url

    def get_repo_path(self, name: str) -> Path:
        return (self.path / name).resolve()

    def get_repo(self, path: str) -> GitRepo:
        return GitRepo(path)

    def get_repo_status(self, repo_name: str) -> str:
        """
        Get the status of a repository.
        """
        typer.echo(
            typer.style(
                f"Getting status for repository: {repo_name}", fg=typer.colors.CYAN
            )
        )

        path = self.get_repo_path(repo_name)
        if not os.path.exists(path):
            typer.echo(
                typer.style(
                    f"Repository '{repo_name}' not found at path: {path}",
                    fg=typer.colors.RED,
                )
            )
            return
        typer.echo(
            typer.style(
                f"Repository '{repo_name}' found at path: {path}", fg=typer.colors.GREEN
            )
        )
        repo = self.get_repo(path)
        typer.echo(
            typer.style(f"On branch: {repo.active_branch}", fg=typer.colors.CYAN)
        )
        unstaged = repo.index.diff(None)
        if unstaged:
            typer.echo(
                typer.style("\nChanges not staged for commit:", fg=typer.colors.YELLOW)
            )
            for diff in unstaged:
                typer.echo(
                    typer.style(f"  modified: {diff.a_path}", fg=typer.colors.YELLOW)
                )
        staged = repo.index.diff("HEAD")
        if staged:
            typer.echo(typer.style("\nChanges to be committed:", fg=typer.colors.GREEN))
            for diff in staged:
                typer.echo(
                    typer.style(f"  staged: {diff.a_path}", fg=typer.colors.GREEN)
                )
        if repo.untracked_files:
            typer.echo(typer.style("\nUntracked files:", fg=typer.colors.MAGENTA))
            for f in repo.untracked_files:
                typer.echo(typer.style(f"  {f}", fg=typer.colors.MAGENTA))
        if not unstaged and not staged and not repo.untracked_files:
            typer.echo(
                typer.style(
                    "\nNothing to commit, working tree clean.", fg=typer.colors.GREEN
                )
            )

    def list_repos(self) -> None:
        """
        List all repositories found either in self.map or as directories in self.path.
        """
        typer.echo(typer.style("Listing repositories...", fg=typer.colors.CYAN))

        # Set from self.map
        map_repos = set(self.map.keys())

        # Set from filesystem
        try:
            fs_entries = os.listdir(self.path)
            fs_repos = {
                entry
                for entry in fs_entries
                if os.path.isdir(os.path.join(self.path, entry))
            }
        except Exception as e:
            typer.echo(
                typer.style(
                    f"❌ Failed to list repositories in filesystem: {e}",
                    fg=typer.colors.RED,
                )
            )
            return

        # Compute differences
        only_in_map = map_repos - fs_repos
        only_in_fs = fs_repos - map_repos
        in_both = map_repos & fs_repos

        # Output
        if in_both:
            typer.echo(
                typer.style(
                    "Repositories in both self.map and filesystem:",
                    fg=typer.colors.GREEN,
                )
            )
            for name in sorted(in_both):
                typer.echo(f"  - {name}")

        if only_in_map:
            typer.echo(
                typer.style("Repositories only in self.map:", fg=typer.colors.YELLOW)
            )
            for name in sorted(only_in_map):
                typer.echo(f"  - {name}")

        if only_in_fs:
            typer.echo(
                typer.style("Repositories only in filesystem:", fg=typer.colors.MAGENTA)
            )
            for name in sorted(only_in_fs):
                typer.echo(f"  - {name}")

        if not (in_both or only_in_map or only_in_fs):
            typer.echo("No repositories found.")

    def run_tests(self, repo_name: str) -> None:
        """
        Run tests for the specified repository.
        """
        typer.echo(
            typer.style(
                f"Running tests for repository: {repo_name}", fg=typer.colors.CYAN
            )
        )

        path = self.get_repo_path(repo_name)
        if not os.path.exists(path):
            typer.echo(
                typer.style(
                    f"Repository '{repo_name}' not found at path: {path}",
                    fg=typer.colors.RED,
                )
            )
            return

        Test().run_tests(repo_name)
        typer.echo(
            typer.style(
                f"✅ Tests completed successfully for {repo_name}.",
                fg=typer.colors.GREEN,
            )
        )

    def set_branch(self, branch: str) -> None:
        self.branch = branch

    def sync_repo(self, repo_name: str) -> None:
        """
        Synchronize the repository by pulling the latest changes.
        """
        typer.echo(typer.style("Synchronizing repository...", fg=typer.colors.CYAN))
        path = self.get_repo_path(repo_name)
        if not os.path.exists(path):
            typer.echo(
                typer.style(
                    f"Repository '{repo_name}' not found at path: {path}",
                    fg=typer.colors.RED,
                )
            )
            return
        try:
            repo = self.get_repo(path)
            typer.echo(
                typer.style(
                    f"Pulling latest changes for {repo_name}...", fg=typer.colors.CYAN
                )
            )
            repo.remotes.origin.pull()
            typer.echo(
                typer.style(
                    f"✅ Successfully synchronized {repo_name}.", fg=typer.colors.GREEN
                )
            )
        except Exception as e:
            typer.echo(
                typer.style(
                    f"❌ Failed to synchronize {repo_name}: {e}", fg=typer.colors.RED
                )
            )


class Package(Repo):
    def install_package(self, repo_name: str) -> None:
        """
        Install a package from the cloned repository.
        """
        typer.echo(
            typer.style(
                f"Installing package from repository: {repo_name}", fg=typer.colors.CYAN
            )
        )

        path = self.get_repo_path(repo_name)
        if not os.path.exists(path):
            typer.echo(
                typer.style(
                    f"Repository '{repo_name}' not found at path: {path}",
                    fg=typer.colors.RED,
                )
            )
            return

        try:
            subprocess.run(
                [os.sys.executable, "-m", "pip", "install", "-e", path],
                check=True,
            )
            typer.echo(
                typer.style(
                    f"✅ Successfully installed package from {repo_name}.",
                    fg=typer.colors.GREEN,
                )
            )
        except subprocess.CalledProcessError as e:
            typer.echo(
                typer.style(
                    f"❌ Failed to install package from {repo_name}: {e}",
                    fg=typer.colors.RED,
                )
            )

    def uninstall_package(self, repo_name: str) -> None:
        """
        Uninstall a package from the cloned repository.
        """
        typer.echo(
            typer.style(
                f"Uninstalling package from repository: {repo_name}",
                fg=typer.colors.CYAN,
            )
        )

        path = self.get_repo_path(repo_name)
        if not os.path.exists(path):
            typer.echo(
                typer.style(
                    f"Repository '{repo_name}' not found at path: {path}",
                    fg=typer.colors.RED,
                )
            )
            return

        try:
            subprocess.run(
                [os.sys.executable, "-m", "pip", "uninstall", "-y", repo_name],
                check=True,
            )
            typer.echo(
                typer.style(
                    f"✅ Successfully uninstalled package from {repo_name}.",
                    fg=typer.colors.GREEN,
                )
            )
        except subprocess.CalledProcessError as e:
            typer.echo(
                typer.style(
                    f"❌ Failed to uninstall package from {repo_name}: {e}",
                    fg=typer.colors.RED,
                )
            )


class Test(Repo):
    """
    Test is a subclass of Repo that provides additional functionality
    for running tests on repositories.
    It inherits methods from the Repo class and can be extended with
    more test-specific methods if needed.
    """

    def __init__(self, pyproject_file: Path = Path("pyproject.toml")):
        super().__init__(pyproject_file)
        self.modules = []
        self.keep_db = False
        self.keyword = None
        self.setenv = False

    def copy_settings(self, repo_name: str) -> None:
        """
        Copy test settings from this repository to the repository
        specified by repo_name.
        """
        source = self.test_settings["settings"]["test"]["source"]
        target = self.test_settings["settings"]["test"]["target"]
        shutil.copyfile(source, target)
        typer.echo(
            typer.style(
                f"Copied test settings from {source} to {target} for {repo_name}.",
                fg=typer.colors.CYAN,
            )
        )

    def copy_apps(self, repo_name: str) -> None:
        """
        Copy test settings from this repository to the repository
        specified by repo_name.
        """
        if "apps_file" not in self.test_settings:
            typer.echo(
                typer.style(
                    f"No apps_file settings found for {repo_name}.",
                    fg=typer.colors.YELLOW,
                )
            )
            return
        source = self.test_settings["apps_file"]["source"]
        target = self.test_settings["apps_file"]["target"]
        shutil.copyfile(source, target)
        typer.echo(
            typer.style(
                f"Copied apps from {source} to {target} for {repo_name}.",
                fg=typer.colors.CYAN,
            )
        )

    def copy_migrations(self, repo_name: str) -> None:
        """
        Copy migrations from this repository to the repository
        specified by repo_name.
        """
        source = self.test_settings["migrations_dir"]["source"]
        target = self.test_settings["migrations_dir"]["target"]

        if not os.path.exists(target):
            shutil.copytree(source, target)
            typer.echo(
                typer.style(
                    f"Copied migrations from {source} to {target} for {repo_name}.",
                    fg=typer.colors.CYAN,
                )
            )

    def run_tests(self, repo_name: str) -> None:
        self.test_settings = (
            self.config.get("tool", {})
            .get("django_mongodb_cli", {})
            .get("test", {})
            .get(repo_name, {})
        )
        if not self.test_settings:
            typer.echo(
                typer.style(
                    f"No test settings found for {repo_name}.", fg=typer.colors.YELLOW
                )
            )
            return
        test_dir = self.test_settings.get("test_dir")
        if not os.path.exists(test_dir):
            typer.echo(
                typer.style(
                    f"Test directory '{test_dir}' does not exist for {repo_name}.",
                    fg=typer.colors.RED,
                )
            )
            return
        self.copy_apps(repo_name)
        self.copy_migrations(repo_name)
        self.copy_settings(repo_name)
        test_options = self.test_settings.get("test_options")
        test_command = [self.test_settings.get("test_command")]
        settings_module = (
            self.test_settings.get("settings", {}).get("module", {}).get("test")
        )
        if test_options:
            test_command.extend(test_options)
        if settings_module and test_command == "./runtests.py":
            test_command.extend(["--settings", settings_module])
        if self.keep_db:
            test_command.extend("--keepdb")
        if self.keyword:
            test_command.extend(["-k", self.keyword])
        if self.modules:
            test_command.extend(self.modules)
        subprocess.run(
            test_command,
            cwd=test_dir,
        )

    def set_modules(self, modules: list) -> None:
        self.modules = modules

    def set_keep_db(self, keep_db: bool) -> None:
        """Set whether to keep the database after tests."""
        self.keep_db = keep_db

    def set_keyword(self, keyword: str) -> None:
        """Set a keyword to filter tests."""
        self.keyword = keyword

    def set_env(self, setenv: bool) -> None:
        """Set whether to set DJANGO_SETTINGS_MODULE environment variable."""
        self.setenv = setenv
