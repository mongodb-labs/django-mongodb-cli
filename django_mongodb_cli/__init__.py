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

dm.add_typer(repo, name="repo")
