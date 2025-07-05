import click
import git
import os
import shutil
import string
import sys
import toml
import random
import re
import subprocess


from .settings import test_settings_map


DELETE_DIRS_AND_FILES = {
    ".babelrc": os.path.isfile,
    ".dockerignore": os.path.isfile,
    ".browserslistrc": os.path.isfile,
    ".eslintrc": os.path.isfile,
    ".nvmrc": os.path.isfile,
    ".stylelintrc.json": os.path.isfile,
    "Dockerfile": os.path.isfile,
    "apps": os.path.isdir,
    "home": os.path.isdir,
    "backend": os.path.isdir,
    "db.sqlite3": os.path.isfile,
    "frontend": os.path.isdir,
    "manage.py": os.path.isfile,
    "package-lock.json": os.path.isfile,
    "package.json": os.path.isfile,
    "postcss.config.js": os.path.isfile,
    "requirements.txt": os.path.isfile,
    "search": os.path.isdir,
}


def random_app_name(prefix="app_", length=6):
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return prefix + suffix


def copy_mongo_apps(repo_name):
    """
    Copy the appropriate mongo_apps file based on the repo name.

    Requires test_settings_map[repo_name]['apps_file']['source'] and
    test_settings_map[repo_name]['apps_file']['target'] to be defined.
    """
    settings = test_settings_map.get(repo_name)
    if not settings or "apps_file" not in settings or repo_name == "django":
        return  # Nothing to copy for this repo

    apps_file = settings["apps_file"]
    source = apps_file.get("source")
    target = apps_file.get("target")

    if not source or not target:
        click.echo(
            click.style(
                f"[copy_mongo_apps] Source or target path missing for '{repo_name}'.",
                fg="yellow",
            )
        )
        return

    try:
        click.echo(click.style(f"Copying {source} → {target}", fg="blue"))
        shutil.copyfile(source, target)
        click.echo(
            click.style(f"Copied {source} to {target} successfully.", fg="green")
        )
    except FileNotFoundError as e:
        click.echo(click.style(f"File not found: {e.filename}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"Failed to copy: {e}", fg="red"))


def copy_mongo_migrations(repo_name):
    """
    Copy mongo_migrations to the specified test directory for this repo.

    test_settings_map[repo_name]['migrations_dir']['source'] and
    test_settings_map[repo_name]['migrations_dir']['target'] must be defined.
    Does nothing if 'migrations_dir' not present.
    """
    settings = test_settings_map.get(repo_name)
    if not settings or "migrations_dir" not in settings:
        click.echo(click.style("No migrations to copy.", fg="yellow"))
        return

    migrations = settings["migrations_dir"]
    source = migrations.get("source")
    target = migrations.get("target")

    if not source or not target:
        click.echo(
            click.style(
                f"[copy_mongo_migrations] Source/target path missing for '{repo_name}'.",
                fg="yellow",
            )
        )
        return

    if not os.path.exists(source):
        click.echo(
            click.style(
                f"Source migrations directory does not exist: {source}", fg="red"
            )
        )
        return

    if os.path.exists(target):
        click.echo(
            click.style(
                f"Target migrations already exist: {target} (skipping copy)", fg="cyan"
            )
        )
        return

    try:
        click.echo(
            click.style(f"Copying migrations from {source} to {target}", fg="blue")
        )
        shutil.copytree(source, target)
        click.echo(
            click.style(f"Copied migrations to {target} successfully.", fg="green")
        )
    except Exception as e:
        click.echo(click.style(f"Failed to copy migrations: {e}", fg="red"))


def copy_mongo_settings(source, target):
    """
    Copy mongo_settings to the specified test directory.

    Args:
        source (str): Path to the source settings file.
        target (str): Path to the target location.

    Shows a message and handles errors gracefully.
    """
    if not source or not target:
        click.echo(click.style("Source or target not specified.", fg="yellow"))
        return
    if not os.path.exists(source):
        click.echo(click.style(f"Source file does not exist: {source}", fg="red"))
        exit(1)

    try:
        click.echo(click.style(f"Copying {source} → {target}", fg="blue"))
        shutil.copyfile(source, target)
        click.echo(click.style(f"Copied settings to {target}.", fg="green"))
    except Exception as e:
        click.echo(click.style(f"Failed to copy settings: {e}", fg="red"))


def get_management_command(command=None, *args):
    """
    Construct a Django management command suitable for subprocess execution.

    If 'manage.py' exists in the current directory, use it; otherwise, fall back to 'django-admin'.
    Commands in REQUIRES_MANAGE_PY require 'manage.py' to be present.
    Pass additional arguments via *args for command options.
    """
    REQUIRES_MANAGE_PY = {
        "createsuperuser",
        "migrate",
        "runserver",
        "shell",
        "startapp",
    }
    manage_py = "manage.py"
    manage_py_exists = os.path.isfile(manage_py)

    if not manage_py_exists and (command is None or command in REQUIRES_MANAGE_PY):
        raise click.ClickException(
            "manage.py is required to run this command. "
            "Please run this command in the project directory."
        )

    base_command = [sys.executable, manage_py] if manage_py_exists else ["django-admin"]

    if command:
        full_command = base_command + [command]
    else:
        full_command = base_command

    if args:
        # *args allows for further options/args (e.g. get_management_command("makemigrations", "--verbosity", "2"))
        full_command.extend(args)

    return full_command


URL_PATTERN = re.compile(r"git\+ssh://(?:[^@]+@)?([^/]+)/([^@]+)")
BRANCH_PATTERN = re.compile(
    r"git\+ssh://git@github\.com/[^/]+/[^@]+@([a-zA-Z0-9_\-\.]+)\b"
)


def get_repos(pyproject_path, section="dev"):
    """
    Load repository info from a pyproject.toml file.

    Args:
        pyproject_path (str): Path to the pyproject.toml file.
        section (str): Which section ('dev', etc.) of [tool.django_mongodb_cli] to use.

    Returns:
        repos (list): List of repository spec strings.
        url_pattern (Pattern): Compiled regex to extract repo basename.
        branch_pattern (Pattern): Compiled regex to extract branch from url.
    """
    try:
        with open(pyproject_path, "r") as f:
            pyproject_data = toml.load(f)
    except FileNotFoundError:
        raise click.ClickException(f"Could not find {pyproject_path}")
    except toml.TomlDecodeError as e:
        raise click.ClickException(f"Failed to parse TOML: {e}")

    tool_section = pyproject_data.get("tool", {}).get("django_mongodb_cli", {})
    repos = tool_section.get(section, [])
    if not isinstance(repos, list):
        raise click.ClickException(
            f"Expected a list of repos in [tool.django_mongodb_cli.{section}]"
        )

    return repos, URL_PATTERN, BRANCH_PATTERN


def clone_repo(repo_entry, url_pattern, branch_pattern, repo):
    """
    Clone a single repository into repo.home given a repo spec entry.
    If the repo already exists at the destination, skips.
    Tries to check out a branch if one is found in the entry, defaults to 'main'.
    """
    url_match = url_pattern.search(repo_entry)
    if not url_match:
        click.echo(click.style(f"Invalid repository entry: {repo_entry}", fg="red"))
        return

    repo_url = url_match.group(0)
    repo_name = os.path.basename(repo_url)
    branch = (
        branch_pattern.search(repo_entry).group(1)
        if branch_pattern.search(repo_entry)
        else "main"
    )
    clone_path = os.path.join(repo.home, repo_name)

    if os.path.exists(clone_path):
        click.echo(
            click.style(
                f"Skipping {repo_name}: already exists at {clone_path}", fg="yellow"
            )
        )
        return

    click.echo(
        click.style(
            f"Cloning {repo_name} from {repo_url} into {clone_path} (branch: {branch})",
            fg="blue",
        )
    )
    try:
        git.Repo.clone_from(repo_url, clone_path, branch=branch)
    except git.exc.GitCommandError as e:
        click.echo(
            click.style(
                f"Warning: Failed to clone branch '{branch}'. Trying default branch instead... ({e})",
                fg="yellow",
            )
        )
        try:
            git.Repo.clone_from(repo_url, clone_path)
        except git.exc.GitCommandError as e2:
            click.echo(click.style(f"Failed to clone repository: {e2}", fg="red"))
            return

    # Optionally install pre-commit hooks if available
    pre_commit_cfg = os.path.join(clone_path, ".pre-commit-config.yaml")
    if os.path.exists(pre_commit_cfg):
        click.echo(
            click.style(f"Installing pre-commit hooks for {repo_name}...", fg="green")
        )
        result = subprocess.run(["pre-commit", "install"], cwd=clone_path)
        if result.returncode == 0:
            click.echo(click.style("pre-commit installed successfully.", fg="green"))
        else:
            click.echo(click.style("pre-commit installation failed.", fg="red"))
    else:
        click.echo(
            click.style(f"No pre-commit config found in {repo_name}.", fg="yellow")
        )


def get_repo_name_map(repos, url_pattern):
    """Return a dict mapping repo_name to repo_url from a list of repo URLs."""
    return {
        os.path.basename(url_pattern.search(url).group(0)): url
        for url in repos
        if url_pattern.search(url)
    }


def install_package(clone_path):
    """
    Install a package from the given clone path.

    - If clone_path ends with 'mongo-arrow' or 'libmongocrypt', the actual install path is 'bindings/python' inside it.
    - Tries editable install via pip if pyproject.toml exists.
    - Tries setup.py develop if setup.py exists.
    - Installs from requirements.txt if available.
    - Warns the user if nothing can be installed.
    """
    # Special case for known subdir installs
    if clone_path.endswith(("mongo-arrow", "libmongocrypt")):
        install_path = os.path.join(clone_path, "bindings", "python")
    else:
        install_path = clone_path

    if os.path.exists(os.path.join(install_path, "pyproject.toml")):
        click.echo(
            click.style(
                f"Installing (editable) with pyproject.toml: {install_path}", fg="blue"
            )
        )
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", install_path]
        )
    elif os.path.exists(os.path.join(install_path, "setup.py")):
        click.echo(
            click.style(
                f"Installing (develop) with setup.py in {install_path}", fg="blue"
            )
        )
        result = subprocess.run(
            [sys.executable, "setup.py", "develop"], cwd=install_path
        )
    elif os.path.exists(os.path.join(install_path, "requirements.txt")):
        click.echo(
            click.style(f"Installing requirements.txt in {install_path}", fg="blue")
        )
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            cwd=install_path,
        )
    else:
        click.echo(
            click.style(
                f"No valid installation method found for {install_path}", fg="red"
            )
        )
        return

    if "result" in locals():
        if result.returncode == 0:
            click.echo(
                click.style(f"Install successful in {install_path}.", fg="green")
            )
        else:
            click.echo(click.style(f"Install failed in {install_path}.", fg="red"))


def repo_update(repo_entry, url_pattern, clone_path):
    """
    Update a single git repository at clone_path.

    Args:
        repo_entry (str): The repository entry string (e.g. repo URL).
        url_pattern (Pattern): Compiled regex to extract repo name from URL.
        clone_path (str): Path where the repository is cloned.

    If the repo doesn't exist, skips it. Handles and reports errors.
    """
    url_match = url_pattern.search(repo_entry)
    if not url_match:
        click.echo(click.style(f"Invalid repository entry: {repo_entry}", fg="red"))
        return

    repo_url = url_match.group(0)
    repo_name = os.path.basename(repo_url)

    if not os.path.exists(clone_path):
        click.echo(
            click.style(
                f"Skipping {repo_name}: {clone_path} does not exist.", fg="yellow"
            )
        )
        return

    try:
        # Check if clone_path is a git repo
        repo = git.Repo(clone_path)
        click.echo(click.style(f"Updating 📦 {repo_name}...", fg="blue"))
        pull_output = repo.git.pull()
        click.echo(
            click.style(f"Pull result for {repo_name}:\n{pull_output}", fg="green")
        )
    except git.exc.NoSuchPathError:
        click.echo(
            click.style(f"Not a valid Git repository at {clone_path}.", fg="red")
        )
    except git.exc.GitCommandError as e:
        click.echo(click.style(f"Failed to update {repo_name}: {e}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"Unexpected error updating {repo_name}: {e}", fg="red"))


def get_status(
    repo_entry,
    url_pattern,
    repo,
    reset=False,
    diff=False,
    branch=False,
    update=False,
    log=False,
):
    """
    Show status (and optionally reset/update/log/diff/branch) for a single repo.

    Args:
        repo_entry (str): The repository entry spec (from pyproject.toml).
        url_pattern (Pattern): Regex to extract basename from URL.
        repo (object): Repo context with .home attribute.
        reset (bool): If True, hard-reset the repo.
        diff (bool): If True, show git diff.
        branch (bool): If True, show all branches.
        update (bool): If True, run repo_update().
        log (bool): If True, show formatted log.

    Outputs status/log info with color and error reporting.
    """
    url_match = url_pattern.search(repo_entry)
    if not url_match:
        click.echo(click.style(f"Invalid repository entry: {repo_entry}", fg="red"))
        return

    repo_url = url_match.group(0)
    repo_name = os.path.basename(repo_url)
    clone_path = os.path.join(repo.home, repo_name)

    if not os.path.exists(clone_path):
        click.echo(click.style(f"Skipping 📦 {repo_name} (not cloned)", fg="yellow"))
        return

    try:
        repo_obj = git.Repo(clone_path)
        click.echo(click.style(f"\n📦 {repo_name}", fg="blue", bold=True))

        if reset:
            click.echo(
                click.style(f"Resetting {repo_name} to HEAD (hard)...", fg="red")
            )
            out = repo_obj.git.reset("--hard")
            click.echo(out)
            click.echo()  # Space

        else:
            # Print remote info
            for remote in repo_obj.remotes:
                click.echo(
                    click.style(f"Remote: {remote.name} @ {remote.url}", fg="blue")
                )

            # Print branch info
            current_branch = (
                repo_obj.active_branch.name
                if repo_obj.head.is_valid()
                else "<detached HEAD>"
            )
            click.echo(click.style(f"On branch: {current_branch}", fg="magenta"))

            status = repo_obj.git.status()
            click.echo(status)

            # Show diff if requested
            if diff:
                diff_output = repo_obj.git.diff()
                if diff_output.strip():
                    click.echo(click.style("Diff:", fg="yellow"))
                    click.echo(click.style(diff_output, fg="red"))
                else:
                    click.echo(click.style("No diff output", fg="green"))

            # Show branches if requested
            if branch:
                click.echo(click.style("Branches:", fg="blue"))
                click.echo(repo_obj.git.branch("--all"))

            # Show log if requested
            if log:
                click.echo(click.style("Git log:", fg="blue"))
                click.echo(
                    repo_obj.git.log("--pretty=format:%h - %an, %ar : %s", "--graph")
                )

            # Run update if requested (AFTER showing status etc)
            if update:
                repo_update(repo_entry, url_pattern, clone_path)

        click.echo()  # Add extra space after each repo status for legibility

    except git.exc.InvalidGitRepositoryError:
        click.echo(
            click.style(f"{clone_path} is not a valid Git repository.", fg="red")
        )
    except Exception as e:
        click.echo(click.style(f"An error occurred for {repo_name}: {e}", fg="red"))
