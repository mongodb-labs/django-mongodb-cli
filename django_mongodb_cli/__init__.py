import click
import os
import sys

from .repo import repo
from .startproject import startproject

if os.path.exists("manage.py"):
    from .createsuperuser import createsuperuser
    from .manage import manage
    from .runserver import runserver
    from .startapp import startapp


def get_help_text():
    help_text = """
    Django MongoDB CLI
    """
    return f"\n\n{help_text.strip()}\n\nSystem executable:\n\n{sys.executable}\n"


@click.group(help=get_help_text())
def cli():
    """Django MongoDB CLI"""


cli.add_command(repo)
cli.add_command(startproject)

if os.path.exists("manage.py"):
    cli.add_command(createsuperuser)
    cli.add_command(manage)
    cli.add_command(runserver)
    cli.add_command(startapp)
