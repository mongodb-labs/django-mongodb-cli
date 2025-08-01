import typer
import os

from .utils import Package, Repo, Test

repo = typer.Typer()


def repo_command(
    all_repos: bool,
    repo_name: str,
    all_msg: str,
    missing_msg: str,
    single_func,
    all_func,
    fg=typer.colors.CYAN,
    repo_list=None,
):
    if all_repos:
        if all_msg:
            typer.echo(typer.style(all_msg, fg=fg))
        for name in repo_list if repo_list is not None else Repo().map:
            all_func(name)
    elif repo_name:
        single_func(repo_name)
    else:
        typer.echo(typer.style(missing_msg, fg=typer.colors.YELLOW))


@repo.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    list_repos: bool = typer.Option(
        False, "--list-repos", "-l", help="List available repositories."
    ),
):
    if list_repos:
        Repo().list_repos()
        raise typer.Exit()  # End, no further action

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


@repo.command()
def branch(
    repo_name: str = typer.Argument(None),
    branch_name: str = typer.Argument(None),
    list_branches: bool = typer.Option(
        False, "--list-branches", "-l", help="List branches of the repository"
    ),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Show branches of all repositories"
    ),
):
    """
    Checkout or create a branch in a repository.
    If branch_name is provided, switch to that branch or create it if it doesn't exist.
    If --all-repos is used, show branches for all repositories.
    """
    repo = Repo()
    if branch_name:
        repo.set_branch(branch_name)

    # else:
    #     typer.echo(
    #         typer.style(
    #             "Create or set branch cannot be used with --all-repos.",
    #             fg=typer.colors.RED,
    #         )
    #     )
    #     return

    repo_command(
        all_repos,
        repo_name,
        all_msg="Showing branches for all repositories...",
        missing_msg="Please specify a repository name or use --all-repos to show branches of all repositories.",
        single_func=lambda repo_name: repo.get_repo_branch(repo_name),
        all_func=lambda repo_name: repo.get_repo_branch(repo_name),
    )


@repo.command()
def clone(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Clone all repositories"
    ),
    install: bool = typer.Option(
        False, "--install", "-i", help="Install after cloning"
    ),
):
    """
    Clone a repository.
    If --all-repos is used, clone all repositories.
    If --install is used, install the package after cloning.
    """

    def clone_repo(name):
        Repo().clone_repo(name)
        if install:
            Package().install_package(name)

    repo_command(
        all_repos,
        repo_name,
        all_msg="Cloning all repositories...",
        missing_msg="Please specify a repository name or use --all-repos to clone all repositories.",
        single_func=clone_repo,
        all_func=clone_repo,
    )


@repo.command()
def commit(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Commit all repositories"
    ),
    message: str = typer.Argument(None, help="Commit message"),
):
    """
    Commit changes in a repository with message provided or prompt for message.
    """

    if all_repos:
        typer.echo(
            typer.style("Commit cannot be used with --all-repos.", fg=typer.colors.RED)
        )

    def do_commit(name):
        Repo().commit_repo(name, message)

    repo_command(
        all_repos,
        repo_name,
        all_msg="Committing all repositories...",
        missing_msg="Please specify a repository name.",
        single_func=do_commit,
        all_func=do_commit,
    )


@repo.command()
def delete(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Delete all repositories"
    ),
    uninstall: bool = typer.Option(
        False, "--uninstall", "-u", help="Uninstall after deleting"
    ),
):
    """
    Delete the specified repository.
    If --all-repos is used, delete all repositories.
    If --uninstall is used, uninstall the package before deleting.
    """

    def do_delete(name):
        if uninstall:
            Package().uninstall_package(name)
        Repo().delete_repo(name)

    repo_command(
        all_repos,
        repo_name,
        all_msg="Deleting all repositories...",
        missing_msg="Please specify a repository name or use --all-repos to delete all repositories.",
        single_func=do_delete,
        all_func=do_delete,
        fg=typer.colors.RED,  # Red for delete
    )


@repo.command()
def install(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Install all repositories"
    ),
):
    """
    Install Python package found in the specified repository.
    If --all-repos is used, install packages for all repositories.
    """
    repo_command(
        all_repos,
        repo_name,
        all_msg="Installing all repositories...",
        missing_msg="Please specify a repository name or use --all-repos to install all repositories.",
        single_func=lambda repo_name: Package().install_package(repo_name),
        all_func=lambda repo_name: Package().install_package(repo_name),
    )


@repo.command()
def log(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Show logs of all repositories"
    ),
):
    """
    Show logs for the specified repository.
    If --all-repos is used, show logs for all repositories.
    """
    repo_command(
        all_repos,
        repo_name,
        all_msg="Showing logs for all repositories...",
        missing_msg="Please specify a repository name or use --all-repos to show logs of all repositories.",
        single_func=lambda repo_name: Repo().get_repo_log(repo_name),
        all_func=lambda repo_name: Repo().get_repo_log(repo_name),
    )


@repo.command()
def open(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Open all repositories"
    ),
):
    """
    Open the specified repository in the default web browser.
    If --all-repos is used, open all repositories.
    """
    repo_command(
        all_repos,
        repo_name,
        all_msg="Opening all repositories...",
        missing_msg="Please specify a repository name or use --all-repos to open all repositories.",
        single_func=lambda repo_name: Repo().open_repo(repo_name),
        all_func=lambda repo_name: Repo().open_repo(repo_name),
    )


@repo.command()
def origin(
    repo_name: str = typer.Argument(None),
    repo_user: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Show origin of all repositories"
    ),
):
    """
    Show or set the origin of a repository.
    """
    repo = Repo()
    if repo_user and all_repos:
        typer.echo(
            typer.style(
                "Set origin cannot be used with --all-repos.",
                fg=typer.colors.RED,
            )
        )
        return
    if repo_user:
        repo.set_user(repo_user)

    repo_command(
        all_repos,
        repo_name,
        all_msg="Showing origin for all repositories...",
        missing_msg="Please specify a repository name or use --all-repos to show origins of all repositories.",
        single_func=lambda name: repo.get_repo_origin(name),
        all_func=lambda repo_name: repo.get_repo_origin(repo_name),
    )


@repo.command()
def patch(
    repo_name: str = typer.Argument(None),
):
    """
    Create an evergreen patch for the specified repository.
    """
    repo_command(
        False,
        repo_name,
        all_msg="Running evergreen...",
        missing_msg="Please specify a repository name.",
        single_func=lambda repo_name: Test().patch_repo(repo_name),
        all_func=lambda repo_name: Test().patch_repo(repo_name),
    )


@repo.command()
def pr(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Create pull requests for all repositories"
    ),
):
    """
    Create a pull request for the specified repository.
    """
    repo_command(
        all_repos,
        repo_name,
        all_msg="Creating pull requests for all repositories...",
        missing_msg="Please specify a repository name or use --all-repos to create pull requests for all repositories.",
        single_func=lambda repo_name: Repo().create_pr(repo_name),
        all_func=lambda repo_name: Repo().create_pr(repo_name),
    )


@repo.command()
def reset(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Reset all repositories"
    ),
):
    """
    Reset a repository to its initial state.
    If --all-repos is used, reset all repositories.
    """

    def reset_repo(name):
        Repo().reset_repo(name)

    repo_command(
        all_repos,
        repo_name,
        all_msg="Resetting all repositories...",
        missing_msg="Please specify a repository name or use --all-repos to reset all repositories.",
        single_func=reset_repo,
        all_func=reset_repo,
    )


@repo.command()
def status(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Show status of all repos"
    ),
):
    """
    Show the status of a repository.
    If --all-repos is used, show the status for all repositories.
    """
    repo = Repo()
    repo_command(
        all_repos,
        repo_name,
        all_msg="Showing status for all repositories...",
        missing_msg="Please specify a repository name or use --all-repos to show all repositories.",
        single_func=lambda repo_name: repo.get_repo_status(repo_name),
        all_func=lambda repo_name: repo.get_repo_status(repo_name),
    )


@repo.command()
def sync(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Sync all repositories"
    ),
):
    """
    Sync a repository with its remote counterpart.
    If --all-repos is used, sync all repositories.
    """
    repo = Repo()
    if not repo.map:
        typer.echo(
            typer.style(
                f"No repositories found in {os.path.join(os.getcwd(), repo.pyproject_file)}.",
                fg=typer.colors.RED,
            )
        )
        raise typer.Exit()

    repo_command(
        all_repos,
        repo_name,
        all_msg="Syncing all repositories...",
        missing_msg="Please specify a repository name or use --all-repos to sync all repositories.",
        single_func=lambda repo_name: repo.sync_repo(repo_name),
        all_func=lambda repo_name: repo.sync_repo(repo_name),
    )


@repo.command()
def test(
    repo_name: str = typer.Argument(None),
    modules: list[str] = typer.Argument(None),
    keep_db: bool = typer.Option(
        False, "--keepdb", help="Keep the database after tests"
    ),
    keyword: str = typer.Option(
        None, "--keyword", "-k", help="Run tests with the specified keyword"
    ),
    list_tests: bool = typer.Option(
        False, "--list-tests", "-l", help="List tests instead of running them"
    ),
    setenv: bool = typer.Option(
        False,
        "--setenv",
        "-s",
        help="Set DJANGO_SETTINGS_MODULE environment variable",
    ),
):
    """
    Run tests for a repository.
    If --modules is provided, run tests for the specified modules.
    If --keepdb is used, keep the database after tests.
    If --keyword is provided, run tests with the specified keyword.
    If --setenv is used, set the DJANGO_SETTINGS_MODULE environment variable.
    """
    test_runner = Test()
    if modules:
        test_runner.set_modules(modules)
    if keep_db:
        test_runner.set_keep_db(keep_db)
    if keyword:
        test_runner.set_keyword(keyword)
    if setenv:
        test_runner.set_env(setenv)
    if list_tests:
        test_runner.set_list_tests(list_tests)

    repo_command(
        False,
        repo_name,
        all_msg=None,
        missing_msg="Please specify a repository name.",
        single_func=lambda repo_name: test_runner.run_tests(repo_name),
        repo_list=test_runner.map,
        all_func=None,
    )
