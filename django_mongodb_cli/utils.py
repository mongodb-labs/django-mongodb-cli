import click
import git
import os
import shutil
import sys
import toml
import re
import subprocess


from .config import test_settings_map


def apply_patches(repo_name):
    """Apply a patch file to the specified project directory."""
    repo_dir = test_settings_map[repo_name]["clone_dir"]
    patch_dir = os.path.join("patches", repo_name)
    if os.path.exists(patch_dir):
        for patch_file in os.listdir(patch_dir):
            shutil.copyfile(
                os.path.join(patch_dir, patch_file),
                os.path.join(repo_dir, patch_file),
            )
            click.echo(click.style(f"Applying patch {patch_file}", fg="blue"))
            # Ensure the repository is valid
            repo = git.Repo(repo_dir)
            if not repo.bare:
                try:
                    # Apply the patch
                    repo.git.apply(patch_file)
                    click.echo(
                        f"Patch {os.path.basename(patch_file)} applied successfully."
                    )
                except Exception as e:
                    click.echo(f"Failed to apply patch: {e}")
                    return
            else:
                click.echo("Not a valid Git repository.")
                return
            click.echo(click.style("Patch applied", fg="green"))


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


def get_repos(pyproject_path):
    with open(pyproject_path, "r") as f:
        pyproject_data = toml.load(f)
    repos = pyproject_data.get("tool", {}).get("django_mongodb_cli", {}).get("dev", [])

    url_pattern = re.compile(r"git\+ssh://(?:[^@]+@)?([^/]+)/([^@]+)")

    branch_pattern = re.compile(
        r"git\+ssh://git@github\.com/[^/]+/[^@]+@([a-zA-Z0-9_\-\.]+)\b"
    )
    upstream_pattern = re.compile(r"#\s*upstream:\s*([\w-]+)")
    return repos, url_pattern, branch_pattern, upstream_pattern


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


def repo_fetch(repo_entry, upstream_pattern, url_pattern, repo):
    """Helper function to fetch upstream remotes for a repository."""
    url_match = url_pattern.search(repo_entry)
    upstream_match = upstream_pattern.search(repo_entry)

    if not url_match or not upstream_match:
        return

    repo_url = url_match.group(0)
    repo_name = os.path.basename(repo_url)
    clone_path = os.path.join(repo.home, repo_name)

    if os.path.exists(clone_path):
        click.echo(f"Adding upstream remote for {repo_name}...")
        remote = f"https://github.com/{upstream_match.group(1)}/{repo_name}"
        if os.path.exists(clone_path):
            repo = git.Repo(clone_path)
            try:
                repo.create_remote("upstream", remote)
                click.echo(click.style(f"Added remote {remote}", fg="green"))
            except git.exc.GitCommandError:
                click.echo(
                    click.style(
                        f"Remote {repo.remotes.upstream.name} exists! {repo.remotes.upstream.url}",
                        fg="yellow",
                    )
                )
            repo.remotes.upstream.fetch()
            try:
                repo.git.rebase("upstream/main")
                click.echo(click.style(f"Rebased {repo_name}", fg="green"))
            except git.exc.GitCommandError:
                click.echo(click.style(f"Failed to rebase {repo_name}", fg="red"))
        else:
            click.echo(click.style(f"Skipping {remote}", fg="yellow"))
    else:
        click.echo(f"Skipping {repo_name}: Repository not found at {clone_path}")


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
        click.echo(f"Status of {repo_name}...")
        try:
            repo = git.Repo(clone_path)
            if reset:
                click.echo(click.style(repo.git.reset("--hard"), fg="blue"))
            else:
                click.echo(click.style(repo.git.status(), fg="blue"))
        except git.exc.NoSuchPathError:
            click.echo("Not a valid Git repository.")
    else:
        click.echo(f"Skipping {repo_name}: Repository not found at {clone_path}")
