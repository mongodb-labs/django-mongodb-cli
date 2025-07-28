import os
import typer

from .repo import repo

help_text = (
    """
Django MongoDB CLI

System executable:
"""
    + os.sys.executable
)

dm = typer.Typer(
    help=help_text,
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@dm.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit()


dm.add_typer(repo, name="repo")
