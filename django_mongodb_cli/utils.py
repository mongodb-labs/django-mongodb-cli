import os
import re
import shutil
import subprocess
from pathlib import Path

import toml
import typer
from git import GitCommandError
from git import Repo as GitRepo

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
        self._tool_cfg = self.config.get("tool", {}).get("django-mongodb-cli", {}) or {}
        self.path = Path(self._tool_cfg.get("path", ".")).resolve()
        self.map = self.get_map()
        self.user = None
        self.reset = False

    # -----------------------------
    # Core utilities / helpers
    # -----------------------------
    def _load_config(self) -> dict:
        return toml.load(self.pyproject_file)

    def _msg(self, text: str, fg) -> None:
        typer.echo(typer.style(text, fg=fg))

    def info(self, text: str) -> None:
        self._msg(text, typer.colors.CYAN)

    def warn(self, text: str) -> None:
        self._msg(text, typer.colors.YELLOW)

    def ok(self, text: str) -> None:
        self._msg(text, typer.colors.GREEN)

    def err(self, text: str) -> None:
        self._msg(text, typer.colors.RED)

    def title(self, text: str) -> None:
        typer.echo(text)

    def run(self, args, cwd: Path | str | None = None, check: bool = True) -> bool:
        try:
            subprocess.run(args, cwd=str(cwd) if cwd else None, check=check)
            return True
        except subprocess.CalledProcessError as e:
            self.err(f"Command failed: {' '.join(str(a) for a in args)} ({e})")
            return False

    def ensure_repo(
        self, repo_name: str, must_exist: bool = True
    ) -> tuple[Path | None, GitRepo | None]:
        path = self.get_repo_path(repo_name)
        if must_exist and not path.exists():
            if not self.ctx.obj.get("quiet", False):
                self.err(f"Repository '{repo_name}' not found at path: {path}")
            return None, None
        repo = self.get_repo(str(path)) if path.exists() else None
        return path, repo

    @property
    def tool_cfg(self) -> dict:
        return self._tool_cfg

    def test_cfg(self, repo_name: str) -> dict:
        return self.tool_cfg.get("test", {}).get(repo_name, {}) or {}

    def evergreen_cfg(self, repo_name: str) -> dict:
        return self.tool_cfg.get("evergreen", {}).get(repo_name, {}) or {}

    def origin_cfg(self) -> dict:
        return self.tool_cfg.get("origin", {}) or {}

    @staticmethod
    def parse_git_url(raw: str) -> tuple[str, str]:
        m_branch = BRANCH_PATTERN.search(raw)
        branch = m_branch.group(1) if m_branch else "main"
        m_url = URL_PATTERN.search(raw)
        url = m_url.group(0) if m_url else raw
        return url, branch

    def copy_file(
        self, src: str | Path, dst: str | Path, what: str, repo_name: str
    ) -> None:
        shutil.copyfile(src, dst)
        self.info(f"Copied {what} from {src} to {dst} for {repo_name}.")

    # -----------------------------
    # Repo operations
    # -----------------------------

    def cd_repo(self, repo_name: str) -> None:
        """
        Change directory to the specified repository.
        """
        self.info(f"Changing directory to repository: {repo_name}")
        path, _ = self.ensure_repo(repo_name)
        if not path:
            return

        try:
            os.chdir(path)
            self.ok(f"✅ Changed directory to {path}.")
            subprocess.run(os.environ.get("SHELL", "/bin/zsh"))
        except Exception as e:
            self.err(f"❌ Failed to change directory: {e}")

    def checkout_branch(self, repo_name: str, branch_name) -> None:
        _, repo = self.ensure_repo(repo_name)
        try:
            self.info(f"Checking out branch: {branch_name}")
            repo.git.checkout(branch_name)
            self.ok(branch_name)
        except GitCommandError:
            self.warn(f"Branch '{branch_name}' does not exist. Creating new branch.")
            repo.git.checkout("-b", branch_name)
            self.err(branch_name)

    def clone_repo(self, repo_name: str) -> None:
        """
        Clone a repository into the specified path.
        If the repository already exists, it will skip cloning.
        """
        self.info(f"Cloning {repo_name}")

        if repo_name not in self.map:
            self.err(f"Repository '{repo_name}' not found in configuration.")
            return

        raw = self.map[repo_name]
        url, branch = self.parse_git_url(raw)

        path, _ = self.ensure_repo(repo_name, must_exist=False)
        if not path:
            return
        if path.exists():
            self.warn(f"Repository '{repo_name}' already exists at path: {path}")
            return

        self.info(f"Cloning {url} into {path} (branch: {branch})")
        GitRepo.clone_from(url, str(path), branch=branch)

        # Install pre-commit hooks if config exists
        pc_cfg = path / ".pre-commit-config.yaml"
        if pc_cfg.exists():
            self.info("Installing pre-commit hooks...")
            if self.run(["pre-commit", "install", "-t", "pre-commit"], cwd=path):
                self.ok("Pre-commit hooks installed!")
        else:
            self.warn(
                "No .pre-commit-config.yaml found. Skipping pre-commit hook installation."
            )

    def commit_repo(self, repo_name: str) -> None:
        """
        Commit changes to the specified repository with a commit message.
        If no message is given, open editor for the commit message.
        """
        self.info(f"Committing changes to repository: {repo_name}")
        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return
        try:
            repo.git.add(A=True)
            repo.git.commit()
            self.ok("✅ Commit created.")
        except GitCommandError as e:
            self.err(f"❌ Failed to commit changes: {e}")

    def create_pr(self, repo_name: str) -> None:
        """
        Create a pull request for the specified repository.
        """
        self.info(f"Creating pull request for repository: {repo_name}")
        path, repo = self.ensure_repo(repo_name)
        if not repo or not path:
            return
        try:
            repo.git.push("origin", repo.active_branch.name)
        except GitCommandError as e:
            self.err(f"❌ Failed to push branch: {e}")
            return

        if self.run(["gh", "pr", "create"], cwd=path):
            self.ok(f"✅ Pull request created for {repo_name}.")

    def delete_branch(self, repo_name: str, branch_name: str) -> None:
        """
        Delete the specified branch from the repository.
        """
        self.info(f"Deleting branch '{branch_name}' from repository: {repo_name}")
        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return
        try:
            repo.git.branch("-D", branch_name)
            self.ok(f"✅ Successfully deleted branch '{branch_name}' from {repo_name}.")
        except GitCommandError as e:
            self.err(f"❌ Failed to delete branch '{branch_name}': {e}")

    def delete_repo(self, repo_name: str) -> None:
        """
        Delete the specified repository.
        """
        self.info(f"Deleting repository: {repo_name}")
        path, _ = self.ensure_repo(repo_name)
        if not path:
            return
        try:
            shutil.rmtree(path)
            self.ok(f"✅ Successfully deleted {repo_name}.")
        except Exception as e:
            self.err(f"❌ Failed to delete {repo_name}: {e}")

    def fetch_repo(self, repo_name: str) -> None:
        """
        Fetch updates from the remote repository.
        """
        self.info(f"Fetching updates for repository: {repo_name}")
        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return
        try:
            for remote in repo.remotes:
                self.info(f"Fetching from remote: {remote.name}")
                fetched = remote.fetch()
                self.ok(f"Fetched {len(fetched)} objects from {remote.name}.")
                for ref in fetched:
                    self.info(f"  - {ref.commit.summary} ({ref.name})")
            self.ok(f"✅ Successfully fetched updates for {repo_name}.")
        except GitCommandError as e:
            self.err(f"❌ Failed to fetch updates: {e}")

    def get_repo_log(self, repo_name: str) -> None:
        """
        Get the commit log for the specified repository.
        """
        self.info(f"Getting commit log for repository: {repo_name}")
        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return
        try:
            log_entries = repo.git.log(
                "--pretty=format:%h - %an, %ar : %s",
                "--abbrev-commit",
                "--date=relative",
                "--graph",
            ).splitlines()
            log_max = 10
            for count, entry in enumerate(log_entries, start=1):
                typer.echo(f"  - {entry}")
                if count >= log_max:
                    break
        except GitCommandError as e:
            self.err(f"❌ Failed to get log: {e}")

    def get_repo_remote(self, repo_name: str) -> None:
        """
        Get the remote URL of the specified repository.
        """
        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return

        quiet = self.ctx.obj.get("quiet", False)
        self.info(f"Remotes for {repo_name}:")
        for remote in repo.remotes:
            try:
                self.ok(f"- {remote.name} {remote.url}")
            except Exception as e:
                if not quiet:
                    self.err(f"Could not get remote URL: {e}")

    def get_map(self) -> dict:
        """
        Return a dict mapping repo_name to repo_url from repos in
        [tool.django-mongodb-cli.repos].
        """
        repos = self.tool_cfg.get("repos", []) or []
        result = {}
        for repo in repos:
            if "@" in repo:
                name, url = repo.split("@", 1)
                result[name.strip()] = url.strip()
        return result

    def get_repo_branch(self, repo_name: str, branch_name: str) -> list:
        """
        Get branches for the specified repository.
        If no branch is specified, return all local and remote branches.
        If the repository does not exist, return an empty list.
        If a branch is specified, switch to it (if it exists) or create it (checkout -b).
        """
        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return []

        if branch_name:
            # Specific branch requested → switch to it (existing) or create new (checkout -b)
            self.info(f"Switching to branch '{branch_name}' for {repo_name}")
            try:
                self.checkout_branch(repo_name, branch_name)
                return [branch_name]
            except Exception as e:
                self.err(f"Could not switch/create branch '{branch_name}': {e}")
                return []

        # No specific branch requested → list local + remote branches
        self.info(f"{repo_name}:")
        try:
            # Local branches
            local_branches = [head.name for head in repo.heads]

            # Remote branches
            remote_branches = []
            for remote in repo.remotes:
                remote_branches.extend([ref.name for ref in remote.refs])

            # Combine & remove duplicates
            all_branches = sorted(set(local_branches + remote_branches))
        except Exception as e:
            self.warn(f"Could not list branches: {e}")
            return []

        self.ok("\n".join(f"- {branch}" for branch in all_branches))
        return all_branches

    def get_repo_branches(self, repo_name: str) -> list:
        """
        Get a list of both local and remote branches for the specified repository.
        Optionally, if self.branch is set, switch to it (existing) or create new (checkout -b).
        """
        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return []

        # Get local branches
        local_branches = [branch.name for branch in repo.branches]

        # Get remote branches; skip HEAD pointer
        remote_branches = []
        try:
            remote_branches = [
                ref.name.replace("origin/", "")
                for ref in repo.remotes.origin.refs
                if ref.name != "origin/HEAD"
            ]
        except Exception:
            pass

        self.info(f"Getting branches for repository: {repo_name}")
        all_branches = sorted(set(local_branches + remote_branches))
        for name in all_branches:
            typer.echo(f"  - {name}")
        return all_branches

    def get_repo_origin(self, repo_name: str) -> str:
        """
        Get the origin URL of the specified repository.
        """
        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return ""

        origin_url = repo.remotes.origin.url
        overrides = self.origin_cfg().get(repo_name, [])
        if self.user and isinstance(overrides, list):
            for entry in overrides:
                if entry.get("user") == self.user:
                    new_url = entry.get("repo")
                    if new_url:
                        repo.remotes.origin.set_url(new_url)
                        origin_url = new_url
                        self.ok(f"Setting origin URL for {repo_name}: {origin_url}")
                    break

        self.info(f"Origin URL: {origin_url}")
        return origin_url

    def get_repo_path(self, repo_name: str) -> Path:
        return (self.path / repo_name).resolve()

    def get_repo(self, path: str) -> GitRepo:
        return GitRepo(path)

    def get_repo_status(self, repo_name: str) -> None:
        """
        Get the status of a repository.
        """
        path, repo = self.ensure_repo(repo_name)
        if not repo or not path:
            return

        self.title(f"{repo_name}")
        self.info(f"On branch: {repo.active_branch}")

        # Show origin
        self.get_repo_origin(repo_name)

    def get_repo_diff(self, repo_name: str) -> None:
        """
        Get the diff of a repository.
        """

        path, repo = self.ensure_repo(repo_name)
        if not repo or not path:
            return

        self.title(f"{repo_name}:")
        unstaged = repo.index.diff(None)
        if unstaged:
            self.warn("\nChanges not staged for commit:")
            for diff in unstaged:
                self.warn(f"  modified: {diff.a_path}")

        staged = repo.index.diff("HEAD")
        if staged:
            self.ok("\nChanges to be committed:")
            for diff in staged:
                self.ok(f"  staged: {diff.a_path}")

        if repo.untracked_files:
            self._msg("\nUntracked files:", typer.colors.MAGENTA)
            for f in repo.untracked_files:
                self._msg(f"  {f}", typer.colors.MAGENTA)

        if not unstaged and not staged and not repo.untracked_files:
            self.ok("\nNothing to commit, working tree clean.")

        try:
            working_tree_diff = repo.git.diff()
            if working_tree_diff:
                self.warn("\nWorking tree differences:")
                typer.echo(working_tree_diff)
        except GitCommandError as e:
            self.err(f"❌ Failed to diff working tree: {e}")

    def _list_repos(self) -> set:
        map_repos = set(self.map.keys())

        try:
            fs_entries = os.listdir(self.path)
            fs_repos = {entry for entry in fs_entries if (self.path / entry).is_dir()}
        except Exception as e:
            self.err(f"❌ Failed to list repositories in filesystem: {e}")
            return

        return map_repos, fs_repos

    def list_repos(self) -> None:
        """
        List all repositories found either in self.map or as directories in self.path.
        """
        self.info("Listing repositories...")

        map_repos, fs_repos = self._list_repos()

        only_in_map = map_repos - fs_repos
        only_in_fs = fs_repos - map_repos
        in_both = map_repos & fs_repos

        if in_both:
            self.ok("Repositories in pyproject.toml and on filesystem:")
            for name in sorted(in_both):
                typer.echo(f"  - {name}")

        if only_in_map:
            self.ok("Repositories only in pyproject.toml:")
            for name in sorted(only_in_map):
                typer.echo(f"  - {name}")

        if only_in_fs:
            self._msg("Repositories only on filesystem:", typer.colors.MAGENTA)
            for name in sorted(only_in_fs):
                typer.echo(f"  - {name}")

        if not (in_both or only_in_map or only_in_fs):
            typer.echo("No repositories found.")

    def open_repo(self, repo_name: str) -> None:
        """
        Open the specified repository with `gh browse` command.
        """
        self.info(f"Opening repository: {repo_name}")
        path, _ = self.ensure_repo(repo_name)
        if not path:
            return

        if self.run(["gh", "browse"], cwd=path):
            self.ok(f"✅ Successfully opened {repo_name} in browser.")

    def reset_repo(self, repo_name: str) -> None:
        self.info(f"Resetting repository: {repo_name}")
        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return
        try:
            repo.git.reset("--hard")
            self.ok(f"✅ Repository {repo_name} has been reset.")
        except GitCommandError as e:
            self.err(f"❌ Failed to reset {repo_name}: {e}")

    def set_branch(self, branch: str) -> None:
        self.branch = branch

    def set_reset(self, reset: bool) -> None:
        self.reset = reset

    def set_user(self, user: str) -> None:
        self.user = user

    def pull(self, repo_name: str) -> None:
        """
        Pull the latest changes
        """
        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return

        try:
            repo.remotes.origin.pull()
            self.ok(f"✅ Successfully pulled latest changes for {repo_name}.")

        except Exception as e:
            self.err(f"❌ Failed to pull {repo_name}: {e}")

    def push(self, repo_name: str) -> None:
        """
        Push the latest commits to the remote repository.
        """

        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return

        try:
            current_branch = repo.active_branch.name
            repo.remotes.origin.push(refspec=current_branch)
            self.ok(f"✅ Successfully pushed latest commits to {repo_name}.")
        except Exception as e:
            self.err(f"❌ Failed to push {repo_name}: {e}")

    def remote_add(self, remote_name: str, remote_url: str) -> None:
        """
        Add a new remote to the specified repository.
        """
        self.info(
            f"Adding remote '{remote_name}' to repository: {self.ctx.obj.get('repo_name')}"
        )
        _, repo = self.ensure_repo(self.ctx.obj.get("repo_name"))
        if not repo:
            return

        try:
            repo.create_remote(remote_name, remote_url)
            self.ok(
                f"✅ Successfully added remote '{remote_name}' with URL '{remote_url}'."
            )
        except Exception:
            self.info(
                f"Removing remote '{remote_name}' from repository: {self.ctx.obj.get('repo_name')}"
            )
            repo.delete_remote(remote_name)
            repo.create_remote(remote_name, remote_url)
            self.ok(
                f"✅ Successfully added remote '{remote_name}' with URL '{remote_url}'."
            )

    def remote_remove(self, remote_name: str) -> None:
        """
        Remove a remote from the specified repository.
        """
        self.info(
            f"Removing remote '{remote_name}' from repository: {self.ctx.obj.get('repo_name')}"
        )
        _, repo = self.ensure_repo(self.ctx.obj.get("repo_name"))
        if not repo:
            return

        try:
            repo.delete_remote(remote_name)
            self.ok(f"✅ Successfully removed remote '{remote_name}'.")
        except Exception as e:
            self.err(f"❌ Failed to remove remote '{remote_name}': {e}")

    def set_default_repo(self, repo_name: str) -> None:
        """
        Set the default repository in the configuration file.
        """
        self.info(f"Setting default repository to: {repo_name}")
        if repo_name not in self.map:
            self.err(f"Repository '{repo_name}' not found in configuration.")
            return
        subprocess.run(
            ["gh", "repo", "set-default"],
            cwd=self.get_repo_path(repo_name),
            check=True,
        )


class Package(Repo):
    def install_package(self, repo_name: str) -> None:
        """
        Install a package from the cloned repository.
        """
        self.info(f"Installing {repo_name}")
        path, _ = self.ensure_repo(repo_name)
        if not path:
            return

        install_dir = (
            self.tool_cfg.get("install", {}).get(repo_name, {}).get("install_dir")
        )
        if install_dir:
            path = Path(path / install_dir).resolve()
            self.info(f"Using custom install directory: {path}")

        if self.run(["uv", "pip", "install", "-e", str(path)]):
            self.ok(f"Installed {repo_name}")

    def uninstall_package(self, repo_name: str) -> None:
        """
        Uninstall a package from the cloned repository.
        """
        self.info(f"Uninstalling package from repository: {repo_name}")
        path, _ = self.ensure_repo(repo_name)
        if not path:
            return

        if self.run([os.sys.executable, "-m", "pip", "uninstall", "-y", repo_name]):
            self.ok(f"✅ Successfully uninstalled package from {repo_name}.")


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
        self.list_tests = False
        self.test_settings = {}

    def copy_settings(self, repo_name: str) -> None:
        """
        Copy test settings from this repository to the repository
        specified by repo_name.
        """
        settings = self.test_settings.get("settings")
        if not settings:
            self.warn("'settings' is missing in test_settings")
            return
        source = settings["test"]["source"]
        target = settings["test"]["target"]
        self.copy_file(source, target, "test settings", repo_name)

    def copy_apps(self, repo_name: str) -> None:
        """
        Copy apps file configuration for tests.
        """
        apps = self.test_settings.get("apps_file")
        if not apps:
            self.warn(f"No apps_file settings found for {repo_name}.")
            return
        self.copy_file(apps["source"], apps["target"], "apps", repo_name)

    def copy_migrations(self, repo_name: str) -> None:
        """
        Copy migrations from this repository to the repository
        specified by repo_name.
        """
        migrations_dir = self.test_settings.get("migrations_dir")
        if not migrations_dir:
            self.warn("'migrations_dir' is missing in test_settings")
            return

        source = migrations_dir.get("source")
        target = migrations_dir.get("target")
        if not source or not target:
            raise KeyError(
                "'source' or 'target' is missing under 'migrations_dir' in test_settings"
            )

        self.info(f"Copying migrations from {source} to {target} for repo {repo_name}")
        if not os.path.exists(target):
            shutil.copytree(source, target)
            self.info(f"Copied migrations from {source} to {target} for {repo_name}.")

    def patch_repo(self, repo_name: str) -> None:
        """
        Run evergreen patching operations on the specified repository.
        """
        self.info(f"Running `evergreen patch` for: {repo_name}")
        project_name = self.evergreen_cfg(repo_name).get("project_name")
        if not project_name:
            self.err(f"❌ No evergreen project_name configured for {repo_name}.")
            return
        self.run(
            ["evergreen", "patch", "-p", project_name, "-u"],
            cwd=self.get_repo_path(repo_name),
        )

    def _list_tests(self, repo_name: str) -> None:
        """
        List all test files (recursively) and subdirectories for the specified repository.
        """
        test_dir = self.tool_cfg.get("test", {}).get(repo_name, {}).get("test_dir")

        self.info(f"Listing tests for repository `{repo_name}` in `{test_dir}`:")

        if not test_dir or not os.path.exists(test_dir):
            self.err(f"Test directory '{test_dir}' does not exist for {repo_name}.")
            return

        try:
            found_any = False
            for root, dirs, files in os.walk(test_dir):
                # Ignore __pycache__ dirs
                dirs[:] = [d for d in dirs if not d.startswith("__")]
                dirs.sort()

                rel_path = os.path.relpath(root, test_dir)
                display_path = "." if rel_path == "." else rel_path

                test_files = [
                    f for f in files if f.endswith(".py") and not f.startswith("__")
                ]
                quiet = self.ctx.obj.get("quiet", False)

                if not quiet or test_files:
                    self.ok(f"\n📂 {display_path}")

                if test_files:
                    found_any = True
                    for test_file in sorted(test_files):
                        typer.echo(f"  - {test_file}")
                else:
                    if not quiet:
                        typer.echo("  (no test files)")

            if not found_any:
                self.warn(
                    f"No Python test files found in {test_dir} (including subdirectories) for {repo_name}."
                )
        except Exception as e:
            self.err(f"❌ Failed to list tests for {repo_name}: {e}")

    def _run_tests(self, repo_name: str) -> None:
        self.test_settings = self.test_cfg(repo_name)
        if not self.test_settings:
            self.warn(f"No test settings found for {repo_name}.")
            return

        test_dir = self.test_settings.get("test_dir")
        if not test_dir or not os.path.exists(test_dir):
            self.err(f"Test directory '{test_dir}' does not exist for {repo_name}.")
            return

        # Prepare environment/files
        self.copy_apps(repo_name)
        self.copy_migrations(repo_name)
        self.copy_settings(repo_name)

        test_command_name = self.test_settings.get("test_command")
        test_command = [test_command_name] if test_command_name else ["pytest"]

        test_options = self.test_settings.get("test_options") or []
        test_settings_module = (
            self.test_settings.get("settings", {}).get("module", {}).get("test")
        )

        if test_command_name == "./runtests.py" and test_settings_module:
            test_command.extend(["--settings", test_settings_module])

        if test_command_name == "pytest":
            test_command.extend(["-v"])

        if test_options:
            test_command.extend(test_options)
        if self.keep_db:
            test_command.extend(["--keepdb"])
        if self.keyword:
            test_command.extend(["-k", self.keyword])
        if self.modules:
            test_command.extend(self.modules)

        env = os.environ.copy()
        env_vars_list = self.tool_cfg.get("test", {}).get(repo_name, {}).get("env_vars")
        if env_vars_list:
            env.update({item["name"]: str(item["value"]) for item in env_vars_list})
        self.info(f"Running tests in {test_dir} with command: {' '.join(test_command)}")

        subprocess.run(test_command, cwd=test_dir, env=env)

    def run_tests(self, repo_name: str) -> None:
        """
        Run tests for the specified repository.
        """
        if self.list_tests:
            self._list_tests(repo_name)
            return

        self.info(f"Running tests for repository: {repo_name}")
        path, _ = self.ensure_repo(repo_name)
        if not path:
            return

        self._run_tests(repo_name)

    def set_modules(self, modules: list) -> None:
        self.modules = modules

    def set_keep_db(self, keep_db: bool) -> None:
        """Set whether to keep the database after tests."""
        self.keep_db = keep_db

    def set_keyword(self, keyword: str) -> None:
        """Set a keyword to filter tests."""
        self.keyword = keyword

    def set_list_tests(self, list_tests: bool) -> None:
        """Set whether to list tests instead of running them."""
        self.list_tests = list_tests

    def set_env(self, setenv: bool) -> None:
        """Set whether to set DJANGO_SETTINGS_MODULE environment variable."""
        self.setenv = setenv
