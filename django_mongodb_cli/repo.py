import os
import subprocess

import click
from .config import test_settings_map
from .utils import (
    copy_mongo_apps,
    copy_mongo_migrations,
    copy_mongo_settings,
    get_management_command,
    get_repos,
    repo_clone,
    repo_install,
    repo_status,
    repo_update,
)


class Repo:
    def __init__(self):
        self.home = "src"
        self.config = {}

    def set_config(self, key, value):
        self.config[key] = value

    def __repr__(self):
        return f"<Repo {self.home}>"


pass_repo = click.make_pass_decorator(Repo)


@click.group(invoke_without_command=True)
@click.option(
    "-l",
    "--list-repos",
    is_flag=True,
    help="List all repositories in `pyproject.toml`.",
)
@click.pass_context
def repo(ctx, list_repos):
    """
    Run Django fork and third-party library tests.
    """
    ctx.obj = Repo()
    repos, url_pattern, branch_pattern = get_repos("pyproject.toml")
    if list_repos:
        for repo_entry in repos:
            click.echo(repo_entry)
        return
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@repo.command()
@click.argument("repo_names", nargs=-1, required=False)
@click.option(
    "-a",
    "--all-repos",
    is_flag=True,
)
@click.option(
    "-i",
    "--install",
    is_flag=True,
)
@click.pass_context
@pass_repo
def clone(repo, ctx, repo_names, all_repos, install):
    """Clone repositories from `pyproject.toml`."""
    repos, url_pattern, branch_pattern = get_repos("pyproject.toml")

    if repo_names:
        for repo_name in repo_names:
            not_found = set()
            for repo_entry in repos:
                if (
                    os.path.basename(url_pattern.search(repo_entry).group(0))
                    == repo_name
                ):
                    repo_clone(repo_entry, url_pattern, branch_pattern, repo)
                    if install:
                        clone_path = os.path.join(ctx.obj.home, repo_name)
                        if os.path.exists(clone_path):
                            repo_install(clone_path)
                    return
                else:
                    not_found.add(repo_name)
            click.echo(f"Repository '{not_found.pop()}' not found.")
        return

    if all_repos:
        click.echo(f"Cloning {len(repos)} repositories...")
        for repo_entry in repos:
            repo_clone(repo_entry, url_pattern, branch_pattern, repo)
        return

    if ctx.args == []:
        click.echo(ctx.get_help())


@repo.command()
@click.option(
    "-a",
    "--all-repos",
    is_flag=True,
)
@click.argument("repo_names", nargs=-1)
@click.pass_context
@pass_repo
def install(repo, ctx, repo_names, all_repos):
    """Install cloned repositories with `pip install -e`."""

    if repo_names:
        for repo_name in repo_names:
            clone_path = os.path.join(ctx.obj.home, repo_name)
            if os.path.exists(clone_path):
                repo_install(clone_path)
            else:
                click.echo(f"Repository '{repo_name}' not found.")
        return

    if all_repos:
        repos, url_pattern, branch_pattern = get_repos("pyproject.toml")
        for repo_entry in repos:
            url_match = url_pattern.search(repo_entry)
            if url_match:
                repo_url = url_match.group(0)
                repo_name = os.path.basename(repo_url)
                clone_path = os.path.join(ctx.obj.home, repo_name)
                if os.path.exists(clone_path):
                    repo_install(clone_path)
        return

    if ctx.args == []:
        click.echo(ctx.get_help())


@repo.command()
@click.argument("repo_names", nargs=-1)
@click.option(
    "-a",
    "--all-repos",
    is_flag=True,
)
@click.pass_context
@pass_repo
def update(repo, ctx, repo_names, all_repos):
    """Update cloned repositories with `git pull`."""
    repos, url_pattern, _ = get_repos("pyproject.toml")
    if repo_names:
        for repo_name in repo_names:
            for repo_entry in repos:
                if (
                    os.path.basename(url_pattern.search(repo_entry).group(0))
                    == repo_name
                ):
                    repo_update(repo_entry, url_pattern, repo)
                    return
            click.echo(f"Repository '{repo_name}' not found.")
        return

    if all_repos:
        click.echo(f"Updating {len(repos)} repositories...")
        for repo_entry in repos:
            repo_update(repo_entry, url_pattern, repo)
        return

    if ctx.args == []:
        click.echo(ctx.get_help())


@repo.command(context_settings={"ignore_unknown_options": True})
@click.argument("repo_name", required=False)
@click.argument("args", nargs=-1)
@click.pass_context
def makemigrations(
    ctx,
    repo_name,
    args,
):
    """Run `makemigrations` for cloned repositories."""

    repos, url_pattern, branch_pattern = get_repos("pyproject.toml")
    if repo_name:
        for repo_entry in repos:
            url_match = url_pattern.search(repo_entry)
            if url_match:
                repo_url = url_match.group(0)
                if (
                    repo_name in test_settings_map.keys()
                    and repo_name == os.path.basename(repo_url)
                ):
                    try:
                        copy_mongo_apps(repo_name)
                        copy_mongo_settings(
                            test_settings_map[repo_name]["settings"]["migrations"][
                                "source"
                            ],
                            test_settings_map[repo_name]["settings"]["migrations"][
                                "target"
                            ],
                        )
                    except FileNotFoundError:
                        click.echo(
                            click.style(
                                f"Settings for '{repo_name}' not found.", fg="red"
                            )
                        )
                        return
                    command = get_management_command("makemigrations")
                    command.extend(
                        [
                            "--settings",
                            test_settings_map[repo_name]["settings"]["module"][
                                "migrations"
                            ],
                        ]
                    )
                    if not repo_name == "django-filter":
                        command.extend(
                            [
                                "--pythonpath",
                                os.path.join(
                                    os.getcwd(),
                                    test_settings_map[repo_name]["test_dir"],
                                ),
                            ]
                        )
                    click.echo(f"Running command {' '.join(command)} {' '.join(args)}")
                    subprocess.run(command + [*args])
        return
    if ctx.args == []:
        click.echo(ctx.get_help())


@repo.command()
@click.argument("repo_name", required=False)
@click.argument("modules", nargs=-1)
@click.option("-k", "--keyword", help="Filter tests by keyword")
@click.option("-l", "--list-tests", help="List tests", is_flag=True)
@click.option("-s", "--setup", help="Setup tests (pymongo only)", is_flag=True)
@click.option("--show", help="Show settings", is_flag=True)
@click.pass_context
def test(
    ctx,
    repo_name,
    modules,
    keyword,
    list_tests,
    setup,
    show,
):
    """
    Run tests for Django fork and third-party libraries.
    """
    repos, url_pattern, branch_pattern = get_repos("pyproject.toml")
    if repo_name:
        # Show test settings
        if show:
            if repo_name in test_settings_map.keys():
                from rich import print
                from black import format_str as format
                from black import Mode

                click.echo(
                    print(
                        format(
                            str(dict(sorted(test_settings_map[repo_name].items()))),
                            mode=Mode(),
                        )
                    )
                )
                return
            else:
                click.echo(
                    click.style(f"Settings for '{repo_name}' not found.", fg="red")
                )
                return
        for repo_entry in repos:
            url_match = url_pattern.search(repo_entry)
            repo_url = url_match.group(0)
            if repo_name == os.path.basename(repo_url):
                if repo_name in test_settings_map.keys():
                    test_dirs = test_settings_map[repo_name]["test_dirs"]
                    if list_tests:
                        for test_dir in test_dirs:
                            click.echo(click.style(f"{test_dir}", fg="blue"))
                            try:
                                modules = sorted(os.listdir(test_dir))
                                count = 0
                                for module in modules:
                                    count += 1
                                    if (
                                        module != "__pycache__"
                                        and module != "__init__.py"
                                    ):
                                        if count == len(modules):
                                            click.echo(f"    └── {module}")
                                        else:
                                            click.echo(f"    ├── {module}")
                                click.echo()
                            except FileNotFoundError:
                                click.echo(
                                    click.style(
                                        f"Directory '{test_dir}' not found.", fg="red"
                                    )
                                )
                        return
                    # Copy settings for test run
                    if "settings" in test_settings_map[repo_name]:
                        if os.path.exists(os.path.join(ctx.obj.home, repo_name)):
                            copy_mongo_settings(
                                test_settings_map[repo_name]["settings"]["test"][
                                    "source"
                                ],
                                test_settings_map[repo_name]["settings"]["test"][
                                    "target"
                                ],
                            )
                        else:
                            click.echo(
                                click.style(
                                    f"Repository '{repo_name}' not found.", fg="red"
                                )
                            )
                            return
                    command = [test_settings_map[repo_name]["test_command"]]
                    copy_mongo_migrations(repo_name)
                    copy_mongo_apps(repo_name)

                    # Configure test command
                    if (
                        test_settings_map[repo_name]["test_command"] == "./runtests.py"
                        and repo_name != "django-rest-framework"
                    ):
                        command.extend(
                            [
                                "--settings",
                                test_settings_map[repo_name]["settings"]["module"][
                                    "test"
                                ],
                                "--parallel",
                                "1",
                                "--verbosity",
                                "3",
                                "--debug-sql",
                                "--noinput",
                            ]
                        )
                    if keyword:
                        command.extend(["-k", keyword])
                    if (
                        repo_name == "django-debug-toolbar"
                        or repo_name == "django-allauth"
                        or repo_name == "django-mongodb-extensions"
                    ):
                        os.environ["DJANGO_SETTINGS_MODULE"] = test_settings_map[
                            repo_name
                        ]["settings"]["module"]["test"]

                        command.extend(
                            [
                                "--continue-on-collection-errors",
                                "--html=report.html",
                                "--self-contained-html",
                            ]
                        )
                    elif repo_name == "mongo-python-driver":
                        command.extend(["test", "-s"])

                    command.extend(modules)
                    if os.environ.get("DJANGO_SETTINGS_MODULE"):
                        click.echo(
                            click.style(
                                f"DJANGO_SETTINGS_MODULE={os.environ['DJANGO_SETTINGS_MODULE']}",
                                fg="blue",
                            )
                        )
                    click.echo(click.style(f"Running {' '.join(command)}", fg="blue"))
                    # Run test command
                    subprocess.run(
                        command, cwd=test_settings_map[repo_name]["test_dir"]
                    )
                else:
                    click.echo(f"Settings for '{repo_name}' not found.")
        return
    if ctx.args == []:
        click.echo(ctx.get_help())


@repo.command()
@click.argument("repo_names", nargs=-1)
@click.option(
    "-a",
    "--all-repos",
    is_flag=True,
)
@click.option(
    "-r",
    "--reset",
    is_flag=True,
)
@click.option(
    "-d",
    "--diff",
    is_flag=True,
)
@click.pass_context
@pass_repo
def status(repo, ctx, repo_names, all_repos, reset, diff):
    """Repository status."""
    repos, url_pattern, _ = get_repos("pyproject.toml")
    if repo_names:
        for repo_name in repo_names:
            not_found = set()
            for repo_entry in repos:
                if (
                    os.path.basename(url_pattern.search(repo_entry).group(0))
                    == repo_name
                ):
                    repo_status(repo_entry, url_pattern, repo, reset=reset, diff=diff)
                    return
                else:
                    not_found.add(repo_name)
            click.echo(f"Repository '{not_found.pop()}' not found.")
        return

    if all_repos:
        click.echo(f"Status of {len(repos)} repositories...")
        for repo_entry in repos:
            repo_status(repo_entry, url_pattern, repo, reset=reset, diff=diff)
        return

    if ctx.args == []:
        click.echo(ctx.get_help())
