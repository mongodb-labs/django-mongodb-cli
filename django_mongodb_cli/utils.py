import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import toml
import typer
from git import GitCommandError
from git import Repo as GitRepo


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
        self.ctx = None

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

    def run(
        self,
        args,
        cwd: Path | str | None = None,
        check: bool = True,
        env: dict[str, str] | None = None,
    ) -> bool:
        """Run a subprocess with optional working directory and environment.

        Args:
            args: Command and arguments to run.
            cwd: Optional working directory.
            check: Whether to raise on non-zero exit code.
            env: Optional environment mapping to pass to the subprocess.
        """
        try:
            subprocess.run(args, cwd=str(cwd) if cwd else None, check=check, env=env)
            return True
        except subprocess.CalledProcessError as e:
            self.err(f"Command failed: {' '.join(str(a) for a in args)} ({e})")
            return False

    def ensure_repo(
        self, repo_name: str, must_exist: bool = True
    ) -> tuple[Path | None, GitRepo | None]:
        path = self.get_repo_path(repo_name)
        if must_exist and not path.exists():
            if self.ctx and not self.ctx.obj.get("quiet", True):
                self.err(f"Repository '{repo_name}' not found at path: {path}")
            return None, None
        repo = self.get_repo(str(path)) if path.exists() else None
        return path, repo

    @property
    def tool_cfg(self) -> dict:
        return self._tool_cfg

    def test_cfg(self, repo_name: str) -> dict:
        return self.tool_cfg.get("test", {}).get(repo_name, {}) or {}

    def run_cfg(self, repo_name: str) -> dict:
        """Return configuration for arbitrary repo commands.

        The config is read from [tool.django-mongodb-cli.run.<repo_name>] in
        pyproject.toml and can contain keys like ``env_vars``.
        """
        return self.tool_cfg.get("run", {}).get(repo_name, {}) or {}

    def evergreen_cfg(self, repo_name: str) -> dict:
        return self.tool_cfg.get("evergreen", {}).get(repo_name, {}) or {}

    def origin_cfg(self) -> dict:
        return self.tool_cfg.get("origin", {}) or {}

    @staticmethod
    def parse_git_url(raw: str) -> tuple[str, str]:
        branch = "main"
        url = raw

        # Check for branch specified at the end of the URL, e.g., '...repo.git@my-branch'
        match_branch = re.search(r"@([a-zA-Z0-9_\-\.]+)*$", url)
        if match_branch:
            branch = match_branch.group(1)
            url = url[: match_branch.start()]  # Remove branch part from URL

        # Remove 'git+' prefix if present
        if url.startswith("git+"):
            url = url[4:]

        # Remove duplicate 'https://' or 'http://'
        # This handles cases like 'https://https://github.com/...' or 'http://http://github.com'
        url = re.sub(r"^(http(s)?://)(http(s)?://)", r"\1", url)

        return url, branch

    def copy_file(
        self, src: str | Path, dst: str | Path, what: str, repo_name: str
    ) -> None:
        shutil.copyfile(src, dst)
        self.info(f"Copied {what} from {src} to {dst} for {repo_name}.")

    # -----------------------------
    # Repo operations
    # -----------------------------

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
            self.err(f"❌ Failed to delete {repo_name}: path not found.")
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

    def get_repo_log(self, repo_name: str, max_lines: int | None = None) -> None:
        """Print the commit log for the specified repository.

        Args:
            repo_name: Logical name of the repository.
            max_lines: Maximum number of log entries to display. If ``None``,
                a default of 10 entries is used.
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
            log_max = max_lines if max_lines is not None else 10
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

        quiet = self.ctx.obj.get("quiet", True) if self.ctx else True
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

    def get_groups(self) -> dict:
        """
        Return a dict mapping group_name to list of repo names from
        [tool.django-mongodb-cli.groups].
        """
        return self.tool_cfg.get("groups", {}) or {}

    def get_group_repos(self, group_name: str) -> list:
        """
        Get the list of repository names for a specific group.
        Returns an empty list if the group doesn't exist.
        """
        groups = self.get_groups()
        return groups.get(group_name, [])

    def list_groups(self) -> None:
        """
        List all available repository groups.
        """
        groups = self.get_groups()
        if not groups:
            self.warn("No repository groups configured.")
            return

        self.info("Available repository groups:")
        for group_name, repos in groups.items():
            repo_list = ", ".join(repos)
            self.ok(f"  {group_name}: {repo_list}")

    def get_group_remotes(self, group_name: str) -> dict:
        """
        Get remote configuration for repos in a group.
        Returns a dict mapping repo_name to dict of remote_name -> remote_url.
        """
        remotes_cfg = self.tool_cfg.get("remotes", {}).get(group_name, {}) or {}
        return remotes_cfg

    def setup_repo_remotes(self, repo_name: str, group_name: str) -> None:
        """
        Set up git remotes for a repository based on group configuration.
        """
        remotes_cfg = self.get_group_remotes(group_name)
        repo_remotes = remotes_cfg.get(repo_name, {})

        if not repo_remotes:
            self.warn(
                f"No remote configuration found for {repo_name} in group {group_name}"
            )
            return

        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return

        self.info(f"Setting up remotes for {repo_name}:")
        # Create a mapping from remote names to remote objects for easy lookup
        existing_remotes = {r.name: r for r in repo.remotes}
        for remote_name, remote_url in repo_remotes.items():
            try:
                # Parse the URL to remove git+ prefix if present
                url, parsed_branch = self.parse_git_url(remote_url)

                # Check if remote already exists
                if remote_name in existing_remotes:
                    existing_remote = existing_remotes[remote_name]
                    current_url = existing_remote.url

                    # Update if URL is different
                    if current_url != url:
                        existing_remote.set_url(url)
                        self.ok(
                            f"  Updated remote '{remote_name}': {url} (was: {current_url})"
                        )
                    else:
                        self.info(
                            f"  Remote '{remote_name}' already configured with correct URL"
                        )
                else:
                    # Add new remote
                    repo.create_remote(remote_name, url)
                    self.ok(f"  Added remote '{remote_name}': {url}")
            except Exception as e:
                self.err(f"  Failed to configure remote '{remote_name}': {e}")

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

    def show_commit(self, repo_name: str, commit_hash: str) -> None:
        """Show the diff for a specific commit hash in the given repository."""
        self.info(f"Showing diff for {repo_name}@{commit_hash}")
        path, repo = self.ensure_repo(repo_name)
        if not repo or not path:
            return

        try:
            output = repo.git.show(commit_hash)
            typer.echo(output)
        except GitCommandError as e:
            self.err(f"❌ Failed to show commit {commit_hash}: {e}")

    def _list_repos(self) -> tuple[set, set]:
        map_repos = set(self.map.keys())

        try:
            fs_entries = os.listdir(self.path)
            fs_repos = {entry for entry in fs_entries if (self.path / entry).is_dir()}
        except Exception as e:
            self.err(f"❌ Failed to list repositories in filesystem: {e}")
            return set(), set()

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

        If the repository directory does not exist, emit a clear error message and
        exit with a non-zero status code so callers can detect the failure.
        """
        self.info(f"Opening repository: {repo_name}")

        path, _ = self.ensure_repo(repo_name)
        if not path:
            # `ensure_repo` may already have printed something depending on the
            # current "quiet" setting, but for an explicit "open" request we
            # always want a visible error and a failing exit code.
            self.err(
                f"❌ Repository '{repo_name}' does not exist at {self.get_repo_path(repo_name)}"
            )
            raise typer.Exit(code=1)

        if self.run(["gh", "browse"], cwd=path):
            self.ok(f"✅ Successfully opened {repo_name} in browser.")

    def reset_repo(self, repo_name: str) -> None:
        _, repo = self.ensure_repo(repo_name)
        quiet = self.ctx.obj.get("quiet", True) if self.ctx else True
        if not quiet:
            self.info(f"Resetting repository: {repo_name}")
        if not repo:
            if not quiet:
                self.err(f"❌ Failed to reset {repo_name}: path not found.")
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
        if not self.ctx:
            self.err("Context not initialized. Cannot add remote.")
            return
        repo_name = self.ctx.obj.get("repo_name")
        if not repo_name:
            self.err("Repository name not found in context.")
            return
        self.info(f"Adding remote '{remote_name}' to repository: {repo_name}")
        _, repo = self.ensure_repo(repo_name)
        if not repo:
            return

        try:
            repo.create_remote(remote_name, remote_url)
            self.ok(
                f"Successfully added remote '{remote_name}' with URL '{remote_url}'."
            )
        except Exception:
            self.info(f"Removing remote '{remote_name}' from repository: {repo_name}")
            repo.delete_remote(remote_name)
            repo.create_remote(remote_name, remote_url)
            self.ok(
                f"Successfully added remote '{remote_name}' with URL '{remote_url}'."
            )

    def remote_remove(self, remote_name: str) -> None:
        """
        Remove a remote from the specified repository.
        """
        if not self.ctx:
            self.err("Context not initialized. Cannot remove remote.")
            return
        repo_name = self.ctx.obj.get("repo_name")
        if not repo_name:
            self.err("Repository name not found in context.")
            return
        self.info(f"Removing remote '{remote_name}' from repository: {repo_name}")
        _, repo = self.ensure_repo(repo_name)
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

        This uses the GitHub CLI (`gh repo set-default`). If the repository
        directory does not exist or the `gh` binary is missing/fails, emit a
        clear error and exit with a non-zero status instead of raising a
        traceback.
        """
        self.info(f"Setting default repository to: {repo_name}")
        if repo_name not in self.map:
            self.err(f"Repository '{repo_name}' not found in configuration.")
            raise typer.Exit(code=1)

        path = self.get_repo_path(repo_name)
        if not path.exists():
            self.err(
                f"❌ Repository directory '{path}' does not exist. Clone it first with `dm repo clone {repo_name}`."
            )
            raise typer.Exit(code=1)

        try:
            subprocess.run(
                ["gh", "repo", "set-default"],
                cwd=path,
                check=True,
            )
            self.ok(f"✅ Default repository set to: {repo_name}.")
        except FileNotFoundError:
            # Either the `gh` executable or the repo path is missing; by this
            # point we have already validated the path, so treat it as a
            # missing GitHub CLI binary.
            self.err(
                "❌ Failed to set default repository: GitHub CLI 'gh' was not found. "
                "Install it from https://cli.github.com/ and ensure 'gh' is on your PATH."
            )
            raise typer.Exit(code=1)
        except subprocess.CalledProcessError as e:
            self.err(f"❌ Failed to set default repository via 'gh': {e}")
            raise typer.Exit(code=1)
        except Exception as e:
            self.err(f"❌ Failed to set default repository: {e}")
            raise typer.Exit(code=1)


class Package(Repo):
    def install_package(self, repo_name: str) -> None:
        """
        Install a package from the cloned repository.
        """
        self.info(f"Installing {repo_name}")
        path, _ = self.ensure_repo(repo_name)
        if not path:
            return

        install_cfg = self.tool_cfg.get("install", {}).get(repo_name, {})
        install_dir = install_cfg.get("install_dir")
        if install_dir:
            path = Path(path / install_dir).resolve()
            self.info(f"Using custom install directory: {path}")

        env = os.environ.copy()
        env_vars_list = install_cfg.get("env_vars")
        if env_vars_list:
            typer.echo("Setting environment variables for installation:")
            typer.echo(env_vars_list)
            env.update({item["name"]: str(item["value"]) for item in env_vars_list})

        # Install the base package
        if not self.run(["uv", "pip", "install", "-e", str(path)], env=env):
            self.err(f"Failed to install {repo_name}")
            return

        self.ok(f"Installed {repo_name}")

        # Install optional extras if specified
        extras = install_cfg.get("extras")
        if extras:
            if not isinstance(extras, list):
                self.warn(
                    f"'extras' for {repo_name} should be a list, got {type(extras).__name__}"
                )
            else:
                for extra in extras:
                    # Validate extra name contains only safe characters (alphanumeric, dash, underscore, dot)
                    if not isinstance(extra, str) or not re.match(
                        r"^[a-zA-Z0-9._-]+$", extra
                    ):
                        self.warn(f"Skipping invalid extra name: {extra}")
                        continue

                    self.info(f"Installing optional extra: {extra}")
                    # Install extras using the standard [extra] syntax with uv
                    extra_path = f"{path}[{extra}]"
                    if self.run(["uv", "pip", "install", "-e", extra_path], env=env):
                        self.ok(f"Installed {repo_name}[{extra}]")
                    else:
                        self.warn(f"Failed to install {repo_name}[{extra}]")

        # Install dependency groups if specified (PEP 735)
        # Note: Using pip instead of uv because uv doesn't support --group yet
        groups = install_cfg.get("groups")
        if groups:
            if not isinstance(groups, list):
                self.warn(
                    f"'groups' for {repo_name} should be a list, got {type(groups).__name__}"
                )
            else:
                # Check if pyproject.toml exists in the path
                pyproject_path = path / "pyproject.toml"
                if not pyproject_path.exists():
                    self.warn(
                        f"No pyproject.toml found at {path}, skipping dependency groups"
                    )
                else:
                    for group in groups:
                        # Validate group name contains only safe characters (alphanumeric, dash, underscore, dot)
                        if not isinstance(group, str) or not re.match(
                            r"^[a-zA-Z0-9._-]+$", group
                        ):
                            self.warn(f"Skipping invalid group name: {group}")
                            continue

                        self.info(f"Installing dependency group: {group}")
                        # Use pip install --group with pyproject.toml:group format
                        # (requires pip 25.3+ for PEP 735 support)
                        group_arg = f"{pyproject_path}:{group}"
                        if self.run(["pip", "install", "--group", group_arg], env=env):
                            self.ok(
                                f"Installed dependency group {group} for {repo_name}"
                            )
                        else:
                            self.warn(
                                f"Failed to install dependency group {group} for {repo_name}"
                            )

    def uninstall_package(self, repo_name: str) -> None:
        """
        Uninstall a package from the cloned repository.
        """
        self.info(f"Uninstalling package from repository: {repo_name}")
        path, _ = self.ensure_repo(repo_name)
        if not path:
            return

        if self.run([sys.executable, "-m", "pip", "uninstall", "-y", repo_name]):
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
        test_config = self.tool_cfg.get("test", {}).get(repo_name, {})
        test_dirs = test_config.get("test_dirs", [])

        if not test_dirs:
            self.err(f"No test directories configured for {repo_name}.")
            return

        self.info(
            f"Listing tests for repository `{repo_name}` in {len(test_dirs)} directory(ies):"
        )

        try:
            found_any = False
            for test_dir in test_dirs:
                if not os.path.exists(test_dir):
                    self.warn(
                        f"Test directory '{test_dir}' does not exist for {repo_name}."
                    )
                    continue

                self.ok(f"\n📁 {test_dir}")

                for root, dirs, files in os.walk(test_dir):
                    # Ignore __pycache__ dirs
                    dirs[:] = [d for d in dirs if not d.startswith("__")]
                    dirs.sort()

                    rel_path = os.path.relpath(root, test_dir)
                    display_path = "." if rel_path == "." else rel_path

                    test_files = [
                        f for f in files if f.endswith(".py") and not f.startswith("__")
                    ]
                    quiet = self.ctx.obj.get("quiet", True) if self.ctx else True

                    if not quiet or test_files:
                        self.ok(f"\n  📂 {display_path}")

                    if test_files:
                        found_any = True
                        for test_file in sorted(test_files):
                            typer.echo(f"    - {test_file}")
                    else:
                        if not quiet:
                            typer.echo("    (no test files)")

            if not found_any:
                self.warn(
                    f"No Python test files found in configured test directories for {repo_name}."
                )
        except Exception as e:
            self.err(f"❌ Failed to list tests for {repo_name}: {e}")

    def _run_tests(self, repo_name: str) -> None:
        self.test_settings = self.test_cfg(repo_name)
        if not self.test_settings:
            self.warn(f"No test settings found for {repo_name}.")
            return

        # Determine the working directory for running tests
        # Priority: clone_dir > current working directory (repo root)
        clone_dir = self.test_settings.get("clone_dir")
        test_dirs = self.test_settings.get("test_dirs", [])

        # Determine cwd (current working directory)
        if clone_dir and os.path.exists(clone_dir):
            cwd = clone_dir
        else:
            # Use current working directory (repository root) when clone_dir is not specified
            cwd = os.getcwd()

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
            # Add --continue-on-collection-errors to allow tests to continue running
            # even when some test modules fail to import (e.g., due to missing dependencies)
            test_command.extend(["-v", "--continue-on-collection-errors"])

        if test_options:
            test_command.extend(test_options)
        if self.keep_db:
            test_command.extend(["--keepdb"])
        if self.keyword:
            test_command.extend(["-k", self.keyword])

        # Prepare environment variables
        env = os.environ.copy()
        env_vars_list = self.tool_cfg.get("test", {}).get(repo_name, {}).get("env_vars")
        if env_vars_list:
            env.update({item["name"]: str(item["value"]) for item in env_vars_list})

        if self.modules:
            test_command.extend(self.modules)
        elif test_command and test_command[0] == "pytest" and test_dirs:
            # When no specific modules are provided, run pytest separately for each test_dir
            # This avoids import errors when one test directory has problematic imports
            # but allows all tests to run
            for test_dir in test_dirs:
                test_cmd = test_command.copy()
                test_cmd.append(test_dir)
                self.info(f"Running tests in {cwd} with command: {' '.join(test_cmd)}")
                result = subprocess.run(test_cmd, cwd=cwd, env=env)
                if result.returncode != 0:
                    self.warn(
                        f"Tests in {test_dir} failed with return code {result.returncode}"
                    )
            return  # Early return since we already ran the tests

        self.info(f"Running tests in {cwd} with command: {' '.join(test_command)}")
        subprocess.run(test_command, cwd=cwd, env=env)

    def run_tests(self, repo_name: str) -> None:
        """
        Run tests for the specified repository.
        """
        if self.list_tests:
            self._list_tests(repo_name)
            return

        path, _ = self.ensure_repo(repo_name)
        if not path:
            self.err(f"❌ Failed to run tests for {repo_name}: path not found.")
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
