import click
import os

from .repo import repo
from .startproject import startproject

if os.path.exists("manage.py"):
    from .createsuperuser import createsuperuser
    from .manage import manage
    from .runserver import runserver
    from .startapp import startapp


@click.group()
def cli():
    """Django MongoDB CLI"""


cli.add_command(repo)
cli.add_command(startproject)

if os.path.exists("manage.py"):
    cli.add_command(createsuperuser)
    cli.add_command(manage)
    cli.add_command(runserver)
    cli.add_command(startapp)
