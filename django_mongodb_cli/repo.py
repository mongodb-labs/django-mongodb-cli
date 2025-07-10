import typer

from .utils import Repo, Test

repo = typer.Typer()


@repo.command()
def status(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Show status of all repos"
    ),
):
    """Show the status of the specified Git repository."""
    if all_repos:
        typer.echo(
            typer.style("Showing status for all repositories...", fg=typer.colors.CYAN)
        )
        for repo_name in Repo().map:
            Repo().get_repo_status(repo_name)
    elif repo_name:
        Repo().get_repo_status(repo_name)
    else:
        typer.echo(
            typer.style(
                "Please specify a repository name or use --all-repos to show all repositories.",
                fg=typer.colors.YELLOW,
            )
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
    """Clone the specified Git repository."""
    if all_repos:
        typer.echo(typer.style("Cloning all repositories...", fg=typer.colors.CYAN))
        for repo_name in Repo().map:
            Repo().clone_repo(repo_name)
            if install:
                Repo().install_package(repo_name)
    elif repo_name:
        Repo().clone_repo(repo_name)
        if install:
            Repo().install_package(repo_name)
    else:
        typer.echo(
            typer.style(
                "Please specify a repository name or use --all-repos to clone all repositories.",
                fg=typer.colors.YELLOW,
            )
        )


@repo.command()
def install(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Install all repositories"
    ),
):
    """Install the specified Git repository."""
    if all_repos:
        typer.echo(typer.style("Installing all repositories...", fg=typer.colors.CYAN))
        for repo_name in Repo().map:
            Repo().install_package(repo_name)
    elif repo_name:
        Repo().install_package(repo_name)
    else:
        typer.echo(
            typer.style(
                "Please specify a repository name or use --all-repos to install all repositories.",
                fg=typer.colors.YELLOW,
            )
        )


@repo.command()
def sync(
    repo_name: str = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Sync all repositories"
    ),
):
    """Sync the specified Git repository."""
    if all_repos:
        typer.echo(typer.style("Syncing all repositories...", fg=typer.colors.CYAN))
        for repo_name in Repo().map:
            Repo().sync_repo(repo_name)
    elif repo_name:
        Repo().sync_repo(repo_name)
    else:
        typer.echo(
            typer.style(
                "Please specify a repository name or use --all-repos to sync all repositories.",
                fg=typer.colors.YELLOW,
            )
        )


@repo.command()
def test(
    repo_name: str = typer.Argument(None),
    modules: list[str] = typer.Argument(None),
    all_repos: bool = typer.Option(
        False, "--all-repos", "-a", help="Sync all repositories"
    ),
    keep_db: bool = typer.Option(
        False, "--keepdb", help="Keep the database after tests"
    ),
    keyword: str = typer.Option(
        None, "--keyword", "-k", help="Run tests with the specified keyword"
    ),
    setenv: bool = typer.Option(
        False,
        "--setenv",
        "-s",
        help="Set DJANGO_SETTINGS_MODULE" " environment variable",
    ),
):
    """Run tests for the specified Git repository."""
    repo = Test()
    if modules:
        repo.set_modules(modules)
    if keep_db:
        repo.set_keep_db(keep_db)
    if keyword:
        repo.set_keyword(keyword)
    if setenv:
        repo.set_env(setenv)
    if all_repos:
        typer.echo(
            typer.style("Running tests for all repositories...", fg=typer.colors.CYAN)
        )
        for repo_name in repo.map:
            repo.run_tests(repo_name)
    elif repo_name:
        repo.run_tests(repo_name)
    else:
        typer.echo(
            typer.style(
                "Please specify a repository name or use --all-repos to run tests for all repositories.",
                fg=typer.colors.YELLOW,
            )
        )
