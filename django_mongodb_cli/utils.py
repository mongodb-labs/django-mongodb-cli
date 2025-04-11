import click
import git
import os
import shutil
import sys
import toml
import re
import subprocess


from .config import test_settings_map


def copy_mongo_apps(repo_name):
    """Copy the appropriate mongo_apps file based on the repo name."""
    if "apps_file" in test_settings_map[repo_name] and repo_name != "django":
        click.echo(
            click.style(
                f"Copying {os.path.join(test_settings_map[repo_name]['apps_file']['source'])} to {os.path.join(test_settings_map[repo_name]['apps_file']['target'])}",
                fg="blue",
            )
        )
        shutil.copyfile(
            os.path.join(test_settings_map[repo_name]["apps_file"]["source"]),
            os.path.join(test_settings_map[repo_name]["apps_file"]["target"]),
        )


def copy_mongo_migrations(repo_name):
    """Copy mongo_migrations to the specified test directory."""
    if "migrations_dir" in test_settings_map[repo_name]:
        if not os.path.exists(test_settings_map[repo_name]["migrations_dir"]["target"]):
            click.echo(
                click.style(
                    f"Copying migrations from {test_settings_map[repo_name]['migrations_dir']['source']} to {test_settings_map[repo_name]['migrations_dir']['target']}",
                    fg="blue",
                )
            )
            shutil.copytree(
                test_settings_map[repo_name]["migrations_dir"]["source"],
                test_settings_map[repo_name]["migrations_dir"]["target"],
            )
    else:
        click.echo(click.style("No migrations to copy", fg="yellow"))


def copy_mongo_settings(source, target):
    """Copy mongo_settings to the specified test directory."""
    click.echo(click.style(f"Copying {source} to {target}", fg="blue"))
    shutil.copyfile(source, target)


def get_management_command(command=None):
    REQUIRES_MANAGE_PY = {
        "createsuperuser",
        "migrate",
        "runserver",
        "shell",
        "startapp",
    }
    manage_py_exists = os.path.exists("manage.py")

    if not manage_py_exists and (command is None or command in REQUIRES_MANAGE_PY):
        exit(
            click.style(
                "manage.py is required to run this command. Please run this command in the project directory.",
                fg="red",
            )
        )

    base_command = (
        [sys.executable, "manage.py"] if manage_py_exists else ["django-admin"]
    )

    if command:
        full_command = base_command + [command]
        return full_command

    return base_command


def get_databases(app):
    """Get the databases configuration for the specified app."""
    import django_mongodb_backend

    DATABASE_URL = os.environ.get(
        "MONGODB_URI", f"mongodb://localhost:27017/{app}_tests"
    )
    DATABASES = {"default": django_mongodb_backend.parse_uri(DATABASE_URL)}
    return DATABASES


def get_repos(pyproject_path):
    with open(pyproject_path, "r") as f:
        pyproject_data = toml.load(f)
    repos = pyproject_data.get("tool", {}).get("django_mongodb_cli", {}).get("dev", [])

    url_pattern = re.compile(r"git\+ssh://(?:[^@]+@)?([^/]+)/([^@]+)")

    branch_pattern = re.compile(
        r"git\+ssh://git@github\.com/[^/]+/[^@]+@([a-zA-Z0-9_\-\.]+)\b"
    )
    return repos, url_pattern, branch_pattern


def repo_clone(repo_entry, url_pattern, branch_pattern, repo):
    """Helper function to clone a single repo entry."""
    url_match = url_pattern.search(repo_entry)
    branch_match = branch_pattern.search(repo_entry)
    if not url_match:
        click.echo(f"Invalid repository entry: {repo_entry}")
        return

    repo_url = url_match.group(0)
    repo_name = os.path.basename(repo_url)
    branch = branch_match.group(1) if branch_match else "main"
    clone_path = os.path.join(repo.home, repo_name)

    if os.path.exists(clone_path):
        click.echo(f"Skipping: {repo_name} already exists.")
    else:
        click.echo(
            f"Cloning {repo_name} from {repo_url} into {clone_path} (branch: {branch})"
        )
        if not os.path.exists(clone_path):
            click.echo(f"Cloning {repo_url} into {clone_path} (branch: {branch})")
            try:
                git.Repo.clone_from(repo_url, clone_path, branch=branch)
            except git.exc.GitCommandError:
                try:
                    git.Repo.clone_from(repo_url, clone_path)
                except git.exc.GitCommandError as e:
                    click.echo(f"Failed to clone repository: {e}")
            subprocess.run(["pre-commit", "install"], cwd=clone_path)
        else:
            click.echo(f"Skipping {repo_url} in {clone_path} (branch: {branch})")


def repo_install(clone_path):
    if os.path.exists(os.path.join(clone_path, "pyproject.toml")):
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", clone_path])
    elif os.path.exists(os.path.join(clone_path, "setup.py")):
        subprocess.run([sys.executable, "setup.py", "develop"], cwd=clone_path)
    elif os.path.exists(os.path.join(clone_path, "requirements.txt")):
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            cwd=clone_path,
        )
    else:
        click.echo(
            click.style(
                f"No valid installation method found for {clone_path}", fg="red"
            )
        )


def repo_update(repo_entry, url_pattern, repo):
    """Helper function to update a single repository."""
    url_match = url_pattern.search(repo_entry)
    if not url_match:
        return

    repo_url = url_match.group(0)
    repo_name = os.path.basename(repo_url)
    clone_path = os.path.join(repo.home, repo_name)

    if os.path.exists(clone_path):
        click.echo(f"Updating {repo_name}...")
        try:
            repo = git.Repo(clone_path)
            click.echo(click.style(repo.git.pull(), fg="blue"))
        except git.exc.NoSuchPathError:
            click.echo("Not a valid Git repository.")
        except git.exc.GitCommandError:
            click.echo(click.style(f"Failed to update {repo_name}", fg="red"))
    else:
        click.echo(f"Skipping {repo_name}: Repository not found at {clone_path}")


def repo_status(repo_entry, url_pattern, repo, reset=False):
    """Helper function to update a single repository."""
    url_match = url_pattern.search(repo_entry)
    if not url_match:
        return

    repo_url = url_match.group(0)
    repo_name = os.path.basename(repo_url)
    clone_path = os.path.join(repo.home, repo_name)

    if os.path.exists(clone_path):
        try:
            repo = git.Repo(clone_path)
            click.echo(click.style(f"Status for {repo_name}:", fg="blue"))
            if reset:
                click.echo(click.style(repo.git.reset("--hard"), fg="blue"))
            else:
                click.echo()
                click.echo(
                    click.style(
                        "".join(
                            [f"{remote.name}:{remote.url}" for remote in repo.remotes]
                        ),
                        fg="blue",
                    )
                )
                click.echo()
                click.echo(click.style(repo.git.status(), fg="blue"))
                click.echo()
                click.echo()
                click.echo()
        except git.exc.NoSuchPathError:
            click.echo("Not a valid Git repository.")
    else:
        click.echo(f"Skipping {repo_name}: Repository not found at {clone_path}")
