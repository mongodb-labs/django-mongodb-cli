import sys
import typer

from .app import app
from .frontend import frontend
from .project import project
from .repo import repo

help_text = (
    """
Django MongoDB CLI

System executable:
"""
    + sys.executable
)

dm = typer.Typer(
    help=help_text,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@dm.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


dm.add_typer(app, name="app")
dm.add_typer(frontend, name="frontend")
dm.add_typer(project, name="project")
dm.add_typer(repo, name="repo")
